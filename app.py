import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timezone

from flask import Flask, flash, redirect, render_template, request, session, url_for
from supabase import create_client, Client



app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def db_ready():
    return supabase is not None


def current_user():
    if "user_id" not in session:
        return None
    return {
        "id": session["user_id"],
        "email": session.get("email", "")
    }


def require_login():
    if not current_user():
        flash("Please log in to use the app.", "error")
        return redirect(url_for("login"))
    return None


@app.route("/")
def index():
    if not current_user():
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not db_ready():
            flash("Database is not configured yet. Add the Supabase environment variables.", "error")
            return render_template("register.html")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or len(password) < 6:
            flash("Enter a valid email and a password with at least 6 characters.", "error")
            return render_template("register.html")

        try:
            result = supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            # If email confirmation is disabled in Supabase, a session is returned.
            if result.session and result.user:
                session["user_id"] = result.user.id
                session["email"] = result.user.email
                flash("Account created. Welcome to FocusFlow!", "success")
                return redirect(url_for("dashboard"))

            flash("Account created. Check your email to confirm your account, then log in.", "success")
            return redirect(url_for("login"))

        except Exception as exc:
            flash(f"Registration failed: {exc}", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not db_ready():
            flash("Database is not configured yet. Add the Supabase environment variables.", "error")
            return render_template("login.html")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if result.user:
                session["user_id"] = result.user.id
                session["email"] = result.user.email
                flash("Logged in successfully.", "success")
                return redirect(url_for("dashboard"))

            flash("Login failed. Check your email and password.", "error")

        except Exception as exc:
            flash("Login failed. Check your email/password and confirm your email if required.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    blocked = require_login()
    if blocked:
        return blocked

    tasks = []
    sessions = []

    try:
        tasks_result = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", current_user()["id"])
            .order("created_at", desc=True)
            .execute()
        )
        tasks = tasks_result.data or []

        sessions_result = (
            supabase.table("pomodoro_sessions")
            .select("*")
            .eq("user_id", current_user()["id"])
            .order("completed_at", desc=True)
            .limit(10)
            .execute()
        )
        sessions = sessions_result.data or []

    except Exception as exc:
        flash(f"Could not load saved data: {exc}", "error")

    completed_count = sum(1 for task in tasks if task.get("completed"))
    return render_template(
        "dashboard.html",
        user=current_user(),
        tasks=tasks,
        sessions=sessions,
        completed_count=completed_count
    )


@app.route("/tasks/add", methods=["POST"])
def add_task():
    blocked = require_login()
    if blocked:
        return blocked

    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "Normal")

    if not title:
        flash("Task name cannot be empty.", "error")
        return redirect(url_for("dashboard"))

    try:
        supabase.table("tasks").insert({
            "user_id": current_user()["id"],
            "title": title,
            "priority": priority,
            "completed": False
        }).execute()
        flash("Task added.", "success")
    except Exception as exc:
        flash(f"Could not add task: {exc}", "error")

    return redirect(url_for("dashboard"))


@app.route("/tasks/<task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    blocked = require_login()
    if blocked:
        return blocked

    try:
        existing = (
            supabase.table("tasks")
            .select("completed")
            .eq("id", task_id)
            .eq("user_id", current_user()["id"])
            .single()
            .execute()
        )

        new_value = not bool(existing.data["completed"])
        supabase.table("tasks").update({
            "completed": new_value
        }).eq("id", task_id).eq("user_id", current_user()["id"]).execute()

    except Exception as exc:
        flash(f"Could not update task: {exc}", "error")

    return redirect(url_for("dashboard"))


@app.route("/tasks/<task_id>/delete", methods=["POST"])
def delete_task(task_id):
    blocked = require_login()
    if blocked:
        return blocked

    try:
        supabase.table("tasks").delete().eq(
            "id", task_id
        ).eq("user_id", current_user()["id"]).execute()
        flash("Task deleted.", "success")
    except Exception as exc:
        flash(f"Could not delete task: {exc}", "error")

    return redirect(url_for("dashboard"))


@app.route("/pomodoro/complete", methods=["POST"])
def complete_pomodoro():
    blocked = require_login()
    if blocked:
        return blocked

    data = request.get_json(silent=True) or {}
    minutes = int(data.get("minutes", 25))
    task_id = data.get("task_id") or None

    if minutes < 1 or minutes > 120:
        return {"ok": False, "message": "Invalid timer length."}, 400

    try:
        supabase.table("pomodoro_sessions").insert({
            "user_id": current_user()["id"],
            "task_id": task_id,
            "duration_minutes": minutes,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "message": str(exc)}, 500


if __name__ == "__main__":
    app.run(debug=True)
