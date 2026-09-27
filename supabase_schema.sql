-- FocusFlow database setup for Supabase
-- Run this entire script in Supabase SQL Editor.

create extension if not exists "pgcrypto";

create table if not exists public.tasks (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    title text not null,
    priority text not null default 'Normal'
        check (priority in ('Low', 'Normal', 'High')),
    completed boolean not null default false,
    created_at timestamptz not null default now()
);

create table if not exists public.pomodoro_sessions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    task_id uuid references public.tasks(id) on delete set null,
    duration_minutes integer not null check (duration_minutes between 1 and 120),
    completed_at timestamptz not null default now()
);

create index if not exists tasks_user_id_idx
    on public.tasks(user_id);

create index if not exists pomodoro_sessions_user_id_idx
    on public.pomodoro_sessions(user_id);

-- The Flask server uses the Supabase service-role key server-side.
-- Never put the service-role key in HTML, JavaScript, GitHub, or the browser.
-- For a production client-side integration, use Supabase Auth + RLS.
