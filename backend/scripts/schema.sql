-- Supabase Schema for Smart Caregiver Workload Balancer
-- Run this in Supabase SQL Editor

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Team members table
create table team_members (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    avatar_initials text not null,
    timezone text not null default 'UTC',
    email text unique,
    password_hash text,
    role text not null check (role in ('manager', 'member')) default 'member',
    team_id uuid,  -- references team id for multi-team support
    join_code text unique,  -- for members to join team
    created_at timestamptz default now()
);

-- Teams table (for multi-team support)
create table teams (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    manager_id uuid references team_members(id) on delete set null,
    join_code text unique not null,
    created_at timestamptz default now()
);

-- Tasks table
create table tasks (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    assignee_id uuid references team_members(id) on delete set null,
    priority text not null check (priority in ('low', 'medium', 'high')),
    status text not null check (status in ('todo', 'in_progress', 'done')) default 'todo',
    estimated_hours numeric(4,1) not null default 1.0,
    due_date date,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Risk signals table (daily snapshots per member)
create table risk_signals (
    id uuid primary key default uuid_generate_v4(),
    member_id uuid references team_members(id) on delete cascade,
    date date not null,
    tasks_today int not null default 0,
    overdue_tasks int not null default 0,
    late_night_activity_flag boolean not null default false,
    avg_response_latency_mins numeric(6,1) not null default 0,
    consecutive_overloaded_days int not null default 0,
    self_checkin_score int check (self_checkin_score between 1 and 5),
    created_at timestamptz default now(),
    unique (member_id, date)
);

-- Risk scores table (daily computed scores)
create table risk_scores (
    id uuid primary key default uuid_generate_v4(),
    member_id uuid references team_members(id) on delete cascade,
    date date not null,
    score int not null check (score between 0 and 100),
    top_drivers text[] not null default '{}',
    created_at timestamptz default now(),
    unique (member_id, date)
);

-- Proposed reassignments table (human-in-the-loop)
create table proposed_reassignments (
    id uuid primary key default uuid_generate_v4(),
    task_id uuid references tasks(id) on delete cascade,
    from_member_id uuid references team_members(id) on delete cascade,
    to_member_id uuid references team_members(id) on delete cascade,
    reason text not null,
    status text not null check (status in ('pending', 'accepted', 'dismissed')) default 'pending',
    created_at timestamptz default now(),
    resolved_at timestamptz
);

-- Indexes for common queries
create index idx_risk_signals_member_date on risk_signals(member_id, date desc);
create index idx_risk_scores_member_date on risk_scores(member_id, date desc);
create index idx_tasks_assignee_status on tasks(assignee_id, status);
create index idx_proposed_reassignments_status on proposed_reassignments(status);

-- Row Level Security (optional - enable if needed)
-- alter table team_members enable row level security;
-- alter table tasks enable row level security;
-- alter table risk_signals enable row level security;
-- alter table risk_scores enable row level security;
-- alter table proposed_reassignments enable row level security;