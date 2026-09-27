# FocusFlow — Pomodoro Timer

FocusFlow is a simple web application built for ED2: Build Software with AI. It combines a Pomodoro focus timer with a task manager, user authentication, a cloud database, and session history.

## Features

- User registration and login
- Secure password authentication through Supabase Auth
- 25-minute, 50-minute, and 5-minute timer presets
- Start, pause, and reset controls
- Task creation, reading, completion toggle, and deletion
- Task priorities
- Saved Pomodoro session history
- Progress statistics
- Responsive HTML interface
- Python Flask backend
- Supabase PostgreSQL database
- Deployable as a Python web service

## Technologies

- Python
- Flask
- Supabase Auth
- Supabase PostgreSQL
- HTML
- Inline CSS
- Inline JavaScript for the countdown timer
- Gunicorn for production
- Render for deployment

## Project structure

```text
pomodoro_timer_ed2/
├── app.py
├── requirements.txt
├── render.yaml
├── supabase_schema.sql
├── .env.example
├── .gitignore
├── README.md
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    └── dashboard.html
```

## Local setup

1. Install Python 3.13.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a Supabase project.
5. Open Supabase SQL Editor and run `supabase_schema.sql`.
6. In Supabase Auth settings, enable Email/Password.
7. If you want the simplest classroom demo, disable mandatory email confirmation temporarily; otherwise users can confirm their email before logging in.
8. Create environment variables:

```text
FLASK_SECRET_KEY=your-secret
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

9. Start the app:

```bash
python app.py
```

10. Open the local address shown by Flask.

## Important security note

The `SUPABASE_SERVICE_ROLE_KEY` is a server-only secret. It must never be placed in HTML/JavaScript or committed to GitHub. Store it as an environment variable in local development and in Render's environment settings.

## Deployment

This project is configured for Render.

- Connect the public GitHub repository to Render.
- Choose a Python Web Service.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` as environment variables.
- Add a generated `FLASK_SECRET_KEY`.
- Deploy and test the public URL.

## ED2 requirements checklist

### 1. Pick an idea
Pomodoro productivity timer + task manager.

### 2. Use AI tools
AI was used to design the application structure, generate/refine code, troubleshoot, and improve the user interface. The developer should test and understand the generated code before submission.

### 3. Add a database
Supabase PostgreSQL stores tasks and completed Pomodoro sessions.

### 4. Add login
Supabase Auth provides email/password registration and login. Flask stores the authenticated user's ID in the server session.

### 5. Create the frontend
The HTML frontend provides:
- registration
- login
- logout
- timer controls
- task CRUD
- progress statistics
- Pomodoro history

### 6. Use GitHub
Create a public repository, commit regularly, and use meaningful commit messages.

Suggested commits:
- `Initial Flask Pomodoro app`
- `Add Supabase authentication`
- `Add task CRUD and database schema`
- `Add Pomodoro timer and session history`
- `Improve responsive frontend`
- `Add deployment configuration and README`

### 7. Deploy
Deploy the Flask application as a Render Web Service.

### 8. Demo video
Record 3–5 minutes showing:
1. The deployed URL
2. Registration
3. Login
4. Adding a task
5. Starting/pausing/resetting the timer
6. Completing a Pomodoro
7. Refreshing to show saved history
8. Toggling and deleting a task
9. Briefly explaining the code structure and Supabase database

### 9. README
This README documents the app, technologies, setup instructions, deployment, and demo checklist.

## AI disclosure

AI tools were used as development assistance for planning, code generation, debugging, and documentation. The final application was reviewed and tested by the student.
