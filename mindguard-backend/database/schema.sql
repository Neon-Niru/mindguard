CREATE TABLE students (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name VARCHAR(100),

    email VARCHAR(150),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE interview_sessions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id INTEGER,

    status VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(student_id)
    REFERENCES students(id)

);



CREATE TABLE collected_data (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    session_id INTEGER,

    facts JSON,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(session_id)
    REFERENCES interview_sessions(id)

);



CREATE TABLE burnout_reports (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    session_id INTEGER,

    report JSON,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(session_id)
    REFERENCES interview_sessions(id)

);