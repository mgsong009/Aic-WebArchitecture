CREATE DATABASE IF NOT EXISTS aic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aic_db;

CREATE TABLE users (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id_str   VARCHAR(64)  NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role          ENUM('student','teacher') NOT NULL,
    name          VARCHAR(128) NOT NULL,
    email         VARCHAR(256),
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role)
) ENGINE=InnoDB;

CREATE TABLE classes (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    class_code  VARCHAR(32)  NOT NULL UNIQUE,
    class_name  VARCHAR(256) NOT NULL,
    teacher_id  INT UNSIGNED NOT NULL,
    semester    VARCHAR(32),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE class_enrollments (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    class_id    INT UNSIGNED NOT NULL,
    student_id  INT UNSIGNED NOT NULL,
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id)   REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id)   ON DELETE CASCADE,
    UNIQUE KEY uq_enrollment (class_id, student_id)
) ENGINE=InnoDB;

CREATE TABLE assignments (
    id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    class_id     INT UNSIGNED NOT NULL,
    title        VARCHAR(512) NOT NULL,
    description  TEXT,
    course_code  VARCHAR(32),
    due_date     DATETIME,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    INDEX idx_class (class_id)
) ENGINE=InnoDB;

CREATE TABLE submissions (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    assignment_id   INT UNSIGNED NOT NULL,
    student_id      INT UNSIGNED NOT NULL,
    chatgpt_before  MEDIUMTEXT NOT NULL,
    user_prompt     MEDIUMTEXT NOT NULL,
    essay           MEDIUMTEXT NOT NULL,
    submitted_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id)    REFERENCES users(id)       ON DELETE CASCADE,
    UNIQUE KEY uq_submission (assignment_id, student_id),
    INDEX idx_student (student_id)
) ENGINE=InnoDB;

CREATE TABLE metrics (
    id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    submission_id         INT UNSIGNED NOT NULL UNIQUE,
    pi_score              TINYINT UNSIGNED,
    ui_score              TINYINT UNSIGNED,
    oi_score              TINYINT UNSIGNED,
    aic_score             TINYINT UNSIGNED,
    topic_score           TINYINT UNSIGNED,
    weight_pi             FLOAT,
    weight_ui             FLOAT,
    weight_oi             FLOAT,
    pi_depth_tokens       INT,
    pi_depth_norm         FLOAT,
    pi_critical_ratio     FLOAT,
    pi_avg_sent_len       FLOAT,
    pi_ttr                FLOAT,
    pi_complexity         FLOAT,
    ui_cos_similarity     FLOAT,
    ui_distance           FLOAT,
    ui_newinfo_ratio      FLOAT,
    oi_topic_score_raw    FLOAT,
    embedding_backend     VARCHAR(16),
    computed_at           DATETIME,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE analysis_jobs (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    job_uuid        CHAR(36) NOT NULL UNIQUE,
    submission_id   INT UNSIGNED NOT NULL,
    status          ENUM('pending','running','done','failed') DEFAULT 'pending',
    error_message   TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at      DATETIME,
    completed_at    DATETIME,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    INDEX idx_status (status)
) ENGINE=InnoDB;

CREATE TABLE teacher_feedback (
    id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    assignment_id   INT UNSIGNED NOT NULL,
    student_id      INT UNSIGNED NOT NULL,
    teacher_id      INT UNSIGNED NOT NULL,
    content         TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id)    REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id)    REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uq_feedback (assignment_id, student_id)
) ENGINE=InnoDB;

-- Seed data
-- Demo password for all users: password123 (bcrypt hash)
INSERT INTO users (user_id_str, password_hash, role, name, email) VALUES
('teacher_kim', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'teacher', 'Teacher Kim', 'teacher@aic.edu'),
('student_001', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 001', 's001@aic.edu'),
('student_002', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 002', 's002@aic.edu'),
('student_003', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 003', 's003@aic.edu'),
('student_004', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 004', 's004@aic.edu'),
('student_005', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 005', 's005@aic.edu'),
('student_006', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 006', 's006@aic.edu'),
('student_007', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 007', 's007@aic.edu'),
('student_008', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 008', 's008@aic.edu'),
('student_009', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 009', 's009@aic.edu'),
('student_010', '$2b$12$NwyXPzy1aFg3Zl4Z7zDLRe95xCTC2o7W1Iy4tAXZeor2oJcr36TpW', 'student', 'Student 010', 's010@aic.edu');

INSERT INTO classes (class_code, class_name, teacher_id, semester) VALUES
('CS101', 'Introduction to Computing and AI', 1, '2025-Spring');

INSERT INTO class_enrollments (class_id, student_id) VALUES
(1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
(1, 7), (1, 8), (1, 9), (1, 10), (1, 11);

INSERT INTO assignments (class_id, title, description, course_code, due_date) VALUES
(1, 'AI Ethics and Responsibility', 'Analyze key ethical issues in generative AI.', 'CS101', '2025-02-15 23:59:00'),
(1, 'Digital Transformation and Society', 'Explain social impacts of digital transformation.', 'CS101', '2025-02-28 23:59:00'),
(1, 'Algorithmic Bias Analysis', 'Describe causes of algorithmic bias and mitigation.', 'CS101', '2025-03-14 23:59:00'),
(1, 'Future of Open Source', 'Discuss sustainability and governance in open source.', 'CS101', '2025-03-21 23:59:00'),
(1, 'AI Creativity and IP', 'Evaluate authorship and ownership in AI-generated works.', 'CS101', '2025-04-04 23:59:00');

INSERT INTO submissions (assignment_id, student_id, chatgpt_before, user_prompt, essay, submitted_at) VALUES
(1, 2, 'AI ethics is a complex field...', 'What are the main ethical issues of AI?', 'The ethics of artificial intelligence encompasses fairness, accountability, and transparency. AI systems must be designed with care to avoid reinforcing societal biases. Moreover, transparency in decision-making is critical for public trust.', '2025-02-14 10:00:00'),
(2, 2, 'Digital transformation reshapes industries...', 'How does digital technology change society?', 'Digital transformation fundamentally alters how we work, communicate, and access services. However, the digital divide remains a critical challenge that policymakers must address proactively.', '2025-02-27 11:00:00'),
(3, 2, 'Algorithmic bias occurs when...', 'Why do algorithms become biased and how can we fix it?', 'Algorithmic bias stems from training data that reflects historical inequalities. Critically evaluating datasets and implementing fairness metrics are essential steps toward equitable AI systems.', '2025-03-13 09:30:00'),
(4, 2, 'Open source software has grown significantly...', 'What is the future of open source and why does it matter?', 'Open source software forms the backbone of the modern internet. Its collaborative nature enables rapid innovation, although sustainability depends on community governance and corporate sponsorship models.', '2025-03-20 14:00:00'),
(5, 2, 'Generative AI raises profound questions...', 'How should we think about AI creativity and intellectual property?', 'Generative AI challenges conventional notions of authorship and creativity. Although AI can produce compelling content, the question of ownership and ethical use requires nuanced legal and ethical frameworks that balance innovation with protection.', '2025-04-03 16:00:00');

INSERT INTO metrics (submission_id, pi_score, ui_score, oi_score, aic_score, topic_score, weight_pi, weight_ui, weight_oi, pi_depth_tokens, pi_depth_norm, pi_critical_ratio, pi_avg_sent_len, pi_ttr, pi_complexity, ui_cos_similarity, ui_distance, ui_newinfo_ratio, oi_topic_score_raw, embedding_backend, computed_at) VALUES
(1, 52, 58, 51, 54, 70, 0.333, 0.333, 0.333, 8, 0.45, 0.08, 0.52, 0.68, 0.51, 0.62, 0.38, 0.55, 0.70, 'sbert', '2025-02-14 10:05:00'),
(2, 55, 60, 58, 58, 72, 0.333, 0.333, 0.333, 10, 0.52, 0.10, 0.54, 0.70, 0.55, 0.58, 0.42, 0.58, 0.72, 'sbert', '2025-02-27 11:05:00'),
(3, 63, 62, 60, 62, 75, 0.333, 0.333, 0.333, 12, 0.60, 0.12, 0.58, 0.72, 0.60, 0.55, 0.45, 0.60, 0.75, 'sbert', '2025-03-13 09:35:00'),
(4, 68, 65, 68, 67, 78, 0.333, 0.333, 0.333, 14, 0.65, 0.13, 0.60, 0.74, 0.63, 0.52, 0.48, 0.63, 0.78, 'sbert', '2025-03-20 14:05:00'),
(5, 72, 68, 75, 72, 83, 0.38, 0.31, 0.31, 18, 0.72, 0.15, 0.64, 0.76, 0.68, 0.48, 0.52, 0.67, 0.83, 'sbert', '2025-04-03 16:05:00');

INSERT INTO submissions (assignment_id, student_id, chatgpt_before, user_prompt, essay, submitted_at) VALUES
(5, 3, 'Generative AI is transforming creative industries...', 'Tell me about generative AI', 'Generative AI is transforming creative industries by enabling new forms of content creation. It can produce text, images, and music with remarkable quality.', '2025-04-03 20:00:00');

INSERT INTO metrics (submission_id, pi_score, ui_score, oi_score, aic_score, topic_score, weight_pi, weight_ui, weight_oi, pi_depth_tokens, pi_depth_norm, pi_critical_ratio, pi_avg_sent_len, pi_ttr, pi_complexity, ui_cos_similarity, ui_distance, ui_newinfo_ratio, oi_topic_score_raw, embedding_backend, computed_at) VALUES
(6, 35, 40, 42, 39, 65, 0.333, 0.333, 0.333, 5, 0.25, 0.03, 0.40, 0.55, 0.35, 0.78, 0.22, 0.30, 0.65, 'sbert', '2025-04-03 20:05:00');

INSERT INTO teacher_feedback (assignment_id, student_id, teacher_id, content) VALUES
(3, 2, 1, 'UI score is still moderate. Please revise AI draft with more of your own analysis.'),
(4, 2, 1, 'OI improved. Keep adding your own perspective and examples.'),
(5, 2, 1, 'Great PI and OI. Improve UI further by revising AI-generated phrasing.');

