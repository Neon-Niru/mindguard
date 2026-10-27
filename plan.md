# MindGuard AI - System Architecture

# 5-Layer Architecture

MindGuard AI follows a **5-layer architecture** to ensure modularity, scalability, maintainability, and secure communication between the user interface, backend services, AI engine, and database.

The five layers, in data-flow order, are:

1. User Interface — the student-facing frontend
2. Backend — authentication, application logic, request routing
3. AI Wellness Interviewer — conversational data collection
4. Burnout Engine — deterministic scoring of interview data
5. Database — persistent storage, independent of all other layers

# ============================================
# LEVEL 1 — USER INTERFACE (UI)
# ============================================

## Objective

Build a modern, calming and professional Student Wellness platform.

The interface must feel welcoming and premium without becoming visually overwhelming.

Do NOT copy the previous Bolt implementation.
Use it only as visual inspiration.

---

## Design Language

The entire application must follow one consistent design system.

Theme:
- Dark Mode by default

Primary Accent:
- Blue → Purple Gradient

Style:
- Glassmorphism
- Frosted glass cards
- Soft glowing borders
- Large rounded corners
- Smooth transitions
- Floating decorative icons
- Subtle animations

The design should feel

- Calm
- Clean
- Modern
- Student Friendly
- Professional

Avoid

- Cyberpunk aesthetics
- Neon overload
- Flashy animations
- Bright red warning screens
- Cluttered layouts

---

# Navigation

Create a fixed navigation bar.

Navigation Items

- Home
- Features
- How It Works
- About
- Contact

Right Side

- Login
- Get Started

---

# Landing Page

The landing page should introduce MindGuard AI.

Sections

1. Hero Section

Contains

- Large headline
- Short description
- Get Started button
- Dashboard preview illustration
- Floating animated wellness icons

2. Features Section

Display ONLY four feature cards.

Feature Cards

Dashboard

AI Wellness Companion

Recovery Planner

Progress Tracker

Each card should contain

- Icon
- Title
- Short description

3. How It Works

Illustrate

Student

↓

AI Conversation

↓

Burnout Assessment

↓

Recovery Plan

↓

Daily Progress

↓

Long-Term Wellness

4. About

Brief explanation of the project.

5. Contact

Simple footer.

---

# Authentication

Create

- Login Page
- Register Page
- Forgot Password

Keep the UI minimal.

---

# Dashboard

Purpose

Show the user's latest wellness information.

Display

- Latest Wellness Score
- Burnout Risk
- Mood
- Sleep
- Stress
- Productivity
- Today's Planner Progress
- Recovery Goals
- Previous Check-in Comparison
- Quick Actions

The dashboard should ONLY show the latest assessment.

Do NOT display historical graphs here.

---

# AI Wellness Chat

Purpose

Provide a counselor-like conversation.

Interface

- Chat History
- Message Input
- Send Button
- New Conversation Button

After each completed conversation

Automatically display

- Wellness Report
- Burnout Score
- Mood Summary
- Stress Summary
- Sleep Summary
- Recovery Suggestions

The report should appear naturally inside the conversation.

---

# Recovery Planner

Purpose

Combine

- User Tasks

AND

- Recovery Goals

into one planner.

Each task should include

- Title
- Category
- Priority
- Date
- Time
- Completion Checkbox

Display

Large Daily Progress Bar

Percentage Completed

The progress bar should increase as tasks are completed.

---

# Progress Page

Purpose

Display long-term wellness trends.

Show

Weekly Wellness Score

Burnout Trend

Mood Trend

Sleep Trend

Stress Trend

Planner Completion

Recovery Goal Completion

Unlike Dashboard,
this page displays historical information.

---

# Settings

Include

- Profile
- Password
- Notifications
- Theme
- AI Configuration
- Privacy
- Logout

Keep everything simple.

---

# UI Rules

Every page MUST

 Use glassmorphism

 Have rounded cards

 Use blue-purple accents

 Maintain consistent spacing

 Be responsive

 Animate smoothly

 Feel calming

Do NOT create pages with inconsistent styles.

# ============================================
# LEVEL 2 — BACKEND
# ============================================

## Objective

Build a modular backend that serves as the central controller of MindGuard AI.

The backend is responsible for authenticating users, processing frontend requests, validating data, communicating with the AI Wellness Interviewer and Burnout Engine, interacting with the MySQL database, and returning structured JSON responses.

The backend MUST NOT contain UI code or perform AI reasoning or burnout calculations.

---

# Technologies

Programming Language

- Python

Recommended Framework

- Flask

Communication

- REST API

Data Format

- JSON

Database Connection

- MySQL

---

# Responsibilities

The backend acts as the communication bridge between every major component of the application.

Frontend

↓

Backend

↓

AI Wellness Interviewer (when required)

↓

Burnout Engine (when required)

↓

MySQL Database

↓

Backend

↓

Frontend

Every request from the frontend must pass through the backend before reaching the AI modules or the database.

Ownership Rule:

- The Backend is the only component allowed to create, modify, or delete database records.
- Neither the AI Wellness Interviewer nor the Burnout Engine communicates directly with MySQL.

---

# Backend Modules

The backend should be divided into the following independent modules.

---

## Authentication & User Management Module

Purpose

Manage user identity, authentication, authorization, and secure access throughout the application.

Responsibilities

- Register new users
- Login existing users
- Logout users
- Hash and verify passwords
- Validate credentials
- Create and manage user sessions
- Retrieve authenticated user's unique `user_id`
- Associate all stored information with the authenticated user
- Prevent unauthorized access
- Prevent users from accessing another user's information
- Handle forgot-password requests by generating a time-limited reset token
- Verify reset tokens and allow the user to set a new password

Input

- Name
- Email
- Password
- Reset Token (forgot-password flow only)

Output

- Authentication Status
- User Session
- User ID
- Password Reset Token
- Error Messages

Rules

- Email is only used during authentication.
- All application data must be linked using `user_id`.
- Never use email as a foreign key.
- Reset tokens must expire after a short, fixed window and be single-use.

---

## Dashboard Module

Purpose

Prepare the latest wellness information displayed on the Dashboard.

Responsibilities

Retrieve

- Latest Wellness Score
- Latest Burnout Score
- Latest Burnout Risk
- Latest Sleep Summary
- Latest Mood Summary
- Latest Stress Summary
- Latest Productivity Summary
- Current Recovery Goals
- Today's Planner Progress
- Previous Check-in Comparison

Rules

- Only retrieve information belonging to the authenticated user.
- Display only the latest assessment.
- Include one previous assessment for comparison.
- Do NOT retrieve complete historical records.

---

## Planner Module

Purpose

Manage the student's daily planner and recovery activities.

Responsibilities

- Create Tasks
- Edit Tasks
- Delete Tasks
- Mark Tasks Complete
- Import Recovery Goals generated by the Burnout Engine
- Calculate Daily Progress Percentage
- Synchronize planner data

Task Categories

- Study
- Assignment
- Exam
- Recovery
- Exercise
- Personal
- Other

Output

- Daily Task List
- Completion Percentage
- Remaining Tasks

Rules

- All planner data belongs to the authenticated user.
- AI-generated recovery goals should behave exactly like normal planner tasks.

---

## Progress Module

Purpose

Provide historical wellness information for long-term tracking.

Responsibilities

Retrieve

- Weekly Wellness Scores
- Burnout History
- Mood History
- Sleep History
- Stress History
- Productivity Trend
- Planner Completion History
- Recovery Goal Completion

Return

Chart-ready JSON data.

Rules

- Only retrieve stored information.
- Never calculate new scores.
- Never perform AI analysis.

---

## Settings Module

Purpose

Manage user preferences.

Responsibilities

- Update Profile
- Change Password
- Update Theme
- Notification Preferences
- Privacy Preferences
- Logout

Future Support

- Export User Data
- Delete Account

Rules

- Settings belong only to the authenticated user.

---

## Recovery Goal Manager

Purpose

Receive recovery goals generated after burnout analysis and synchronize them with the Planner.

Responsibilities

- Save Recovery Goals
- Convert Recovery Goals into Planner Tasks, storing the source `goal_id` on the created task
- Prevent Duplicate Goals
- Track Goal Completion by updating Recovery Goals.completed whenever the linked Planner Task (matched via `goal_id`) is marked complete
- Archive Completed or Expired Goals

Rules

- Recovery goals should automatically appear in the Planner while remaining editable by the user.
- Every goal-derived Planner Task must carry the originating `goal_id` so completion can sync back to the Recovery Goals table.
- Recovery Focus Areas identify why burnout is elevated; Recovery Goals define what actions the student should take. These are distinct concepts and should not be treated as duplicates.
- Completion sync is one-way: a completed Planner Task updates the linked Recovery Goal; Recovery Goals do not mutate Planner Tasks in return.
- Planner Tasks remain editable after synchronization.

---

## API Controller

Purpose

Receive all frontend requests, validate them, and route them to the correct backend module.

Responsibilities

- Authenticate Requests
- Validate Input
- Route Requests
- Handle Errors
- Return JSON Responses
- Manage HTTP Status Codes

Example Endpoints

Authentication

POST /register

POST /login

POST /logout

POST /forgot-password

POST /reset-password

Dashboard

GET /dashboard

Planner

GET /planner

POST /planner/task

PUT /planner/task

DELETE /planner/task

Progress

GET /progress

Settings

GET /settings

PUT /settings

AI

POST /chat

POST /interview

POST /burnout-report

---

# Backend Workflow

Frontend

↓

Authenticate User

↓

Retrieve Authenticated user_id

↓

Validate Request

↓

Route Request

↓

If AI Interview Required

↓

Send Request to AI Wellness Interviewer

↓

Receive Structured JSON

↓

Send JSON to Burnout Engine

↓

Receive Burnout Report

↓

Create Recovery Goals

↓

Create Planner Tasks

↓

Store Assessment in MySQL

↓

Return JSON Response

↓

Frontend Updates Interface

---

# Communication Rules

Frontend

↓

Backend

↓

AI Wellness Interviewer (only when required)

↓

Burnout Engine (only when required)

↓

MySQL Database

↓

Backend

↓

Frontend

The frontend must NEVER communicate directly with

- MySQL
- AI Wellness Interviewer
- Burnout Engine

All communication must pass through the backend.

---

# Security Rules

Always

  Authenticate every protected request.

  Validate all incoming data.

  Retrieve the authenticated user's `user_id`.

  Store all records using `user_id`.

  Hash passwords before storage.

  Return structured JSON.

  Handle errors gracefully.

  Keep modules independent.

  Log important backend events.

  Protect API keys and secrets.

Never

  Store plaintext passwords.

  Mix frontend code with backend logic.

  Perform AI reasoning.

  Calculate burnout scores.

  Allow direct database access from the frontend.

  Allow users to access another user's data.

  Hardcode sensitive information.

---

# Expected Output

The Backend should function as the central controller of MindGuard AI.

It authenticates users, manages application logic, communicates with the AI Wellness Interviewer, forwards structured data to the Burnout Engine, securely stores and retrieves information from the MySQL database, and returns clean, secure, and structured JSON responses to the frontend.

The backend should remain completely independent of the User Interface, AI reasoning, Burnout calculations, and database implementation details.

# ============================================
# LEVEL 3 — AI WELLNESS INTERVIEWER
# ============================================

## Objective

Develop an AI-powered wellness interviewer that behaves like a calm, empathetic school counselor.

Its only responsibility is to conduct natural conversations with students and collect accurate wellness information.

The AI should make students feel comfortable sharing their experiences while transforming the conversation into structured data for the Burnout Engine.

The AI is **NOT** responsible for assessment, scoring, diagnosis, or decision-making.

---

# Primary Role

The AI acts as

- Student Wellness Interviewer
- School Counselor
- Active Listener
- Friendly Conversation Partner

The AI does NOT act as

- Therapist
- Doctor
- Psychologist
- Burnout Calculator
- Mental Health Expert

---

# Purpose

The purpose of the AI is to replace long and boring questionnaires with natural conversations.

Instead of asking students to fill out dozens of forms, the AI should gradually collect the same information through supportive dialogue.

The student should feel like they are talking to a caring counselor rather than answering a survey.

---

# Responsibilities

The AI should

 Welcome the student warmly.

 Build trust before asking personal questions.

 Ask one question at a time.

 Adapt future questions based on previous responses.

 Ask follow-up questions when answers are unclear.

 Encourage honest responses.

 Cover every required assessment category naturally.

 Convert the conversation into structured JSON.

 Send the structured data to the Burnout Engine.

The AI should NEVER

 Calculate burnout.

 Predict burnout risk.

 Generate wellness scores.

 Diagnose mental health conditions.

 Invent missing information.

 Skip required categories.

---

# Conversation Flow

Every interview should generally follow this flow.

Greeting

↓

Friendly Conversation

↓

Daily Check-in

↓

Gradually Explore Wellness Topics

↓

Clarify Missing Information

↓

Confirm Information

↓

Generate Structured Data

↓

Send Data to Burnout Engine

↓

End Conversation

---

# Required Topics

The AI should naturally gather information about

- Academic Load
- Sleep
- Emotional Exhaustion
- Motivation
- Concentration
- Physical Wellbeing
- Stress
- Anxiety
- Mood
- Social Support
- Lifestyle
- Time Management
- Recent Life Events
- Digital Habits
- Burnout Symptoms

The AI should never ask these topics as a checklist.

Instead, blend them into a natural conversation.

---

# Interview Style

The AI should

- Ask open-ended questions.
- Listen carefully.
- Respond naturally.
- Avoid sounding scripted.
- Be patient.
- Give students time to answer.

Examples

Instead of

"Rate your stress from 1–5."

Prefer

"How have your studies been feeling lately?"

Instead of

"How many hours do you sleep?"

Prefer

"What does a typical night's sleep look like for you?"

---

# Follow-Up Behaviour

If an answer is vague

Example

"I'm tired."

The AI should ask

"What do you think has been making you feel tired recently?"

instead of assuming the reason.

The AI should continue asking follow-up questions until enough information has been collected.

---

# Structured Output

When the interview is complete,

convert the conversation into structured JSON.

Example

{
  "academic_load": {...},
  "sleep": {...},
  "motivation": {...},
  "stress": {...},
  "mood": {...},
  "lifestyle": {...},
  "burnout_symptoms": {...}
}

The JSON should contain only factual information gathered during the conversation.

Never estimate missing values.

---

# Personality

The AI should always be

- Calm
- Friendly
- Supportive
- Respectful
- Professional
- Encouraging
- Curious
- Patient

Avoid

- Robotic responses
- Long lectures
- Judging the student
- Rushing the conversation
- Excessive emojis
- Overly formal language

---

# Safety Rules

The AI must never

- Diagnose depression.
- Diagnose anxiety.
- Recommend medication.
- Claim to replace professional counselors.
- Promise medical confidentiality.
- Pressure students into answering.

If a student expresses serious emotional distress,

the AI should remain supportive and gently encourage speaking with a trusted adult, parent, teacher, school counselor, or mental health professional.

---

# Memory

During a conversation

The AI should remember previous responses to avoid asking duplicate questions.

Across multiple check-ins

The AI may reference previous conversations to make the interaction feel more personal.
Only previously stored information retrieved by the Backend may be referenced.

Example

"Last time you mentioned that exams were causing stress. Has that improved this week?"

The AI should never alter previous responses.

---

# General Rules

Always

 Be conversational.

 Ask naturally.

 Build trust.

 Collect complete information.

 Generate structured JSON only.

Never

Calculate scores.

 Interpret results.

 Explain burnout severity.

 Recommend treatment.

 Replace the Burnout Engine.

---

# Expected Outcome

The AI Wellness Interviewer should function as a digital school counselor that makes students feel heard while collecting accurate and structured wellness information.

Its sole purpose is to transform natural conversations into reliable data for the Burnout Engine, allowing the assessment process to remain human-centered while keeping all scoring and analysis separate.

# ============================================
# LEVEL 4 — BURNOUT ENGINE
# ============================================

## Objective

Develop a deterministic, rule-based burnout assessment engine that converts structured wellness data into a standardized burnout report.

The Burnout Engine MUST NOT use AI to calculate burnout.

Instead, it should use predefined rules, weighted scoring, and validated psychological dimensions to produce consistent and explainable results.

This ensures that burnout assessment remains transparent, repeatable, and resistant to AI hallucinations.

---

# Purpose

The Burnout Engine acts as the analytical core of MindGuard AI.

It receives structured wellness data collected by the AI Wellness Interviewer and transforms it into meaningful burnout metrics.

The engine is completely independent of the AI conversation.

---

# Input Source

The engine only accepts validated JSON generated by the AI Wellness Interviewer.

Example

{
    "sleep_hours": "",
    "stress_level": "",
    "motivation": "",
    "academic_load": "",
    "emotional_exhaustion": "",
    ...
}

The engine must never communicate directly with the user.

---

# Assessment Categories

The engine should evaluate the following categories.

## Basic Information

- Age
- Grade
- Stream
- School Hours
- Tuition Hours

---

## Academic Load

- Study Hours
- Homework Load
- Assignments
- Projects
- Upcoming Exams
- Subject Difficulty
- Academic Expectations
- Attendance

---

## Sleep

- Average Sleep Hours
- Sleep Quality
- Time Taken to Sleep
- Sleep Consistency
- Feeling Rested

---

## Emotional Exhaustion

- Feeling Mentally Drained
- Feeling Emotionally Exhausted
- Feeling Overwhelmed
- Too Tired To Study

---

## Motivation

- Interest In Studies
- Motivation Level
- Procrastination
- Difficulty Starting Work

---

## Cognitive Symptoms

- Concentration
- Brain Fog
- Memory
- Focus

---

## Physical Symptoms

- Fatigue
- Headaches
- Eye Strain
- Body Pain
- Appetite Changes

---

## Stress

- Overall Stress
- Exam Pressure
- Family Pressure
- Teacher Pressure
- Financial Pressure

---

## Anxiety Indicators

- Overthinking
- Worrying
- Fear Of Failure
- Restlessness

---

## Mood

- Happiness
- Mood Swings
- Irritability
- Enjoyment Of Hobbies

---

## Productivity

- Task Completion Rate
- Focus During Study Sessions
- Procrastination Frequency
- Ability To Meet Deadlines

---

## Social Support

- Friends
- Family Support
- Teacher Support
- Loneliness

---

## Lifestyle

- Exercise
- Water Intake
- Meals
- Outdoor Activity
- Screen Time

---

## Time Management

- Planning
- Last Minute Studying
- Breaks
- Free Time

---

## Recent Life Events

- Family Issues
- Bullying
- Health Problems
- Major Failures
- Financial Problems

---

## Personality Traits

- Perfectionism
- Fear Of Failure
- People Pleasing
- High Expectations

---

## Digital Behaviour

- Social Media
- Gaming
- Phone Usage
- Late Night Scrolling

---

## Burnout Symptoms

- Emotional Detachment
- Cynicism
- Feeling Empty
- Reduced Accomplishment
- Giving Up Easily

---

# Rating Scale

Each response should be normalized using a five-point Likert Scale.

Never

Rarely

Sometimes

Often

Always

Convert internally to

0

25

50

75

100

---

# Scoring Method

The Burnout Engine should

1. Receive structured data

↓

2. Normalize all responses

↓

3. Group responses by category

↓

4. Apply category weights

↓

5. Apply protective factors

↓

6. Calculate weighted average

↓

7. Clamp score between 0 and 100

↓

8. Generate burnout report

---

# Weighting System

Use research-informed weighting based on established burnout dimensions.

Initial weighting

| Category | Weight |
|-----------|--------|
| Emotional Exhaustion | 25% |
| Academic Load | 15% |
| Sleep | 15% |
| Burnout Symptoms | 15% |
| Motivation | 8% |
| Cognitive Symptoms | 6% |
| Stress | 5% |
| Anxiety | 3% |
| Mood | 3% |
| Productivity | 3% |
| Time Management | 3% |
| Recent Life Events | 2% |
| Personality Traits | 2% |
| Digital Behaviour | 2% |
| Lifestyle | 2% |
| Social Support | -2% |
| Exercise | -1% |

The weights are normalized during calculation to produce a deterministic burnout score between 0 and 100. These values should remain configurable so future research can adjust them.

---

# Research Basis

The engine should be inspired by validated psychological constructs rather than arbitrary scoring.

Reference dimensions include

- Maslach Burnout Inventory – Student Survey (MBI-SS)
- Oldenburg Burnout Inventory – Student Version (OLBI-S)

Do not copy copyrighted questionnaires directly.

Instead, derive assessment dimensions such as

- Emotional Exhaustion
- Cynicism / Detachment
- Academic Efficacy
- Lifestyle Factors
- Academic Pressure

---

# Output

The engine should generate

- Burnout Score (0–100)
- Risk Level
- Wellness Score (calculated as 100 − Burnout Score)
- Sleep Score
- Stress Score
- Motivation Score
- Academic Load Score
- Emotional Exhaustion Score
- Cognitive Score
- Lifestyle Score
- Mental Energy Score
- Mood Score
- Productivity Score
- Primary Burnout Contributors
- Recovery Focus Areas
- Category Summaries (stored as JSON), generated from the numeric scores — plain factual text, not interpretation or diagnosis

Example

Burnout Score

74 / 100

Risk Level

High

Primary Contributors

- Poor Sleep
- Emotional Exhaustion
- Academic Pressure

Recovery Focus Areas

- Sleep
- Academic Pressure
- Emotional Exhaustion

---

# Rules

Always

  Produce deterministic results.

  Generate the same score for identical inputs.

  Keep calculations transparent.

  Return structured JSON.

  Explain major contributing factors.

  Generate short, factual per-category narrative summaries directly from numeric scores (no interpretation, no diagnosis) using deterministic templates.

Never

  Use AI to calculate scores.

  Invent missing information.

  Diagnose mental illnesses.

  Modify stored user responses.

  Store results directly in the database.

  Retrieve historical records for scoring.

  Modify planner tasks.

---

# Expected Outcome

The Burnout Engine should function as an independent analytical component that transforms structured wellness data into an explainable, research-informed burnout assessment. It should produce consistent, repeatable results while remaining separate from the conversational AI, ensuring that the assessment is transparent, evidence-based, and resistant to AI hallucinations.

# ============================================
# LEVEL 5 — DATABASE
# ============================================

## Objective

Develop a secure and well-structured MySQL database that serves as the permanent storage layer of MindGuard AI.

The database is responsible for storing all user information, burnout assessment results, planner tasks, recovery goals, interview sessions, and application settings.

The database must NOT perform calculations, AI processing, burnout analysis, or business logic.

Its only responsibility is to securely store and retrieve data requested by the Backend.

---

# Technologies

Database

- MySQL

Communication

- Backend API Only

Data Format

- Relational Tables
- JSON (for API communication)

---

# Responsibilities

The database should

  Store user account information

  Store authentication credentials securely

  Store every completed burnout assessment

  Store burnout scores and category scores

  Store recovery goals

  Store planner tasks

  Store interview sessions

  Store user settings

The database should NEVER

  Perform burnout calculations

  Generate reports

  Communicate directly with the frontend

  Communicate directly with the AI modules

  Execute business logic

---

# Database Architecture

The database consists of multiple interconnected tables.

Every table should be connected using the user's unique `user_id`.

The email address is only used for login and authentication.

All application data should reference the authenticated user's `user_id`.

---

# Database Tables

---

## Users

Purpose

Store user account information.

Fields

- user_id (Primary Key)
- full_name
- email
- password_hash
- account_created
- last_login
- reset_token (nullable)
- reset_token_expires_at (nullable)

Responsibilities

- Store login credentials
- Identify every user uniquely
- Link all other application data
- Store the active password-reset token and its expiry, if any

---

## Burnout Assessments

Purpose

Store every burnout report generated by the Burnout Engine.

Each completed AI interview creates one new assessment record.

Fields

- assessment_id
- user_id
- session_id (Foreign Key → Interview Sessions.session_id)
- assessment_date

Overall Results

- burnout_score
- wellness_score
- risk_level
- engine_version

Category Scores

- sleep_score
- stress_score
- motivation_score
- academic_load_score
- emotional_exhaustion_score
- cognitive_score
- lifestyle_score
- mental_energy_score
- mood_score
- productivity_score

Analysis

- primary_contributors
- recovery_focus_areas
- category_summaries (JSON)

Responsibilities

- Store every assessment permanently
- Never overwrite previous assessments
- Create a complete history for progress tracking
- Link back to the Interview Sessions record that produced it via `session_id`
- Serve as the single source of truth for all historical wellness progress data

---

## Interview Sessions

Purpose

Store previous AI interview conversations.

Fields

- session_id
- user_id
- interview_date
- conversation_history
- interview_status

Responsibilities

- Save completed interviews
- Allow future review if needed

Note: Storing the full conversation as a single column is acceptable for this 
project scope. If future features require searching/filtering individual messages, 
this table should be normalized into ChatSessions + ChatMessages.
---

## Planner Tasks

Purpose

Store all planner activities.

Fields

- task_id
- user_id
- title
- description
- category
- task_source
- goal_id (Foreign Key → Recovery Goals.goal_id, nullable — set only for goal-derived tasks)
- due_date
- completed
- completion_date
- created_at
- updated_at

Task Sources

- USER
- ENGINE

Responsibilities

- Store user-created tasks
- Store AI-generated recovery goals as planner tasks, recording the source `goal_id`
- Track completion status
- When a goal-derived task (non-null `goal_id`) is marked complete, propagate that status to the linked Recovery Goals row

---

## Recovery Goals

Purpose

Store immutable recovery recommendations generated by each burnout assessment.

Unlike Planner Tasks (which are editable and may be deleted), Recovery Goals 
preserve the exact recommendations the Burnout Engine produced, creating a 
permanent audit trail. Students may choose not to implement these, and they 
may delete corresponding Planner Tasks, but the original assessment 
recommendations always remain unchanged.

Fields

- goal_id
- assessment_id
- user_id
- goal
- completed
- created_at
- updated_at

Responsibilities

- Preserve recovery recommendations
- Connect goals to the assessment that generated them
- Synchronize with the Planner

---

## Progress Data Source

Purpose

Use Burnout Assessments as the single source of truth for historical wellness information.

Responsibilities

- Provide historical data for Progress Graphs, Weekly Trends, Burnout Trends, and Wellness Trends
- Retrieve assessment records directly from Burnout Assessments
- Avoid duplicating assessment history in a second table

Rules

- The Progress page should read historical assessment records from Burnout Assessments ordered by assessment_date.
- No separate Progress History table should be created.

---

## User Settings

Purpose

Store user preferences.

Fields

- setting_id
- user_id
- theme
- notification_preference
- privacy_settings
- updated_at

Responsibilities

Store application preferences for each user.

---

# Database Relationships

Users

↓

├── Burnout Assessments

├── Interview Sessions

├── Planner Tasks

├── Recovery Goals

└── User Settings

Each table should reference the Users table using `user_id`.

The Burnout Assessments table should also connect to

- Recovery Goals

using `assessment_id`.

Additional cross-table links:

- Burnout Assessments connects to Interview Sessions using `session_id`, so a report can be traced back to the conversation that generated it.
- Planner Tasks connects to Recovery Goals using `goal_id`, so completing a goal-derived task can update the matching recovery goal.
- The Progress page reads historical assessment data directly from Burnout Assessments, making it the single source of truth.

---

# Data Storage Workflow

User

↓

Frontend

↓

Backend

↓

AI Wellness Interviewer

↓

Burnout Engine

↓

Structured Burnout Report

↓

Backend

↓

MySQL Database

The Backend stores

- Burnout Scores
- Category Scores
- Risk Level
- Recovery Focus Areas
- Recovery Goals
- Planner Tasks

The database only stores the received information.

It must never modify or recalculate the Burnout Engine's output.

---

# Progress Tracking

Every completed burnout assessment must generate a new database record.

Historical assessment records should never be overwritten.

The Progress page should retrieve stored assessment records directly from the database to display

- Weekly Progress

- Burnout Trends

- Wellness Trends

- Historical Category Scores

This ensures that students can monitor their improvement over time.

---

# Data Integrity Rules

Always

  Use Primary Keys.

  Use Foreign Keys.

  Store every assessment separately.

  Preserve historical records.

  Keep data normalized.

  Maintain relationships between tables.

  Timestamp important events.

Never

  Delete previous assessments automatically.

  Overwrite historical reports.

  Duplicate user records.

  Store temporary frontend data.

---

# Security Rules

Always

  Hash passwords before storage.

  Restrict database access to the Backend only.

  Validate incoming data before storage.

  Use parameterized SQL queries.

  Protect user privacy.

Never

  Store plaintext passwords.

  Store API keys.

  Expose database credentials.

  Allow direct frontend access.

---

# Expected Outcome

The MySQL database should function as the secure data layer of MindGuard AI.

It should permanently store user accounts, interview sessions, burnout assessment reports, planner tasks, recovery goals, and user settings.

Every completed burnout assessment should be preserved as a historical record so that the Progress module can accurately visualize changes in the student's wellbeing over time.

The database should remain completely independent of the User Interface, Backend logic, AI Wellness Interviewer, and Burnout Engine, serving only as a secure, reliable, and scalable storage system.