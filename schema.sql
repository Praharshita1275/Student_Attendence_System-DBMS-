-- Database Schema for Student Attendance Tracking System

-- Students Table
CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    enrollment_date DATE NOT NULL
);

-- Instructors Table
CREATE TABLE Instructors (
    instructor_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    department VARCHAR(50) NOT NULL
);

-- Courses Table
CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY,
    course_code VARCHAR(10) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    instructor_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id)
);

-- Enrollments Table
CREATE TABLE Enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL, -- Active, Dropped, Completed
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    UNIQUE(student_id, course_id)
);

-- Attendance Records Table
CREATE TABLE Attendance_Records (
    record_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL, -- Present, Absent, Late, Excused
    remarks TEXT,
    recorded_by INTEGER NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (recorded_by) REFERENCES Instructors(instructor_id),
    UNIQUE(student_id, course_id, date)
);

-- Sample Data Insertion
-- Insert Instructors
INSERT INTO Instructors (instructor_id, first_name, last_name, email, phone, department) VALUES
(1, 'John', 'Smith', 'john.smith@university.edu', '555-1234', 'Computer Science'),
(2, 'Jane', 'Doe', 'jane.doe@university.edu', '555-5678', 'Mathematics'),
(3, 'Michael', 'Johnson', 'michael.johnson@university.edu', '555-9012', 'Physics');

-- Insert Students
INSERT INTO Students (student_id, first_name, last_name, email, phone, enrollment_date) VALUES
(1, 'Alice', 'Johnson', 'alice.j@student.edu', '555-1111', '2023-08-15'),
(2, 'Bob', 'Williams', 'bob.w@student.edu', '555-2222', '2023-08-15'),
(3, 'Charlie', 'Brown', 'charlie.b@student.edu', '555-3333', '2023-08-15'),
(4, 'Diana', 'Garcia', 'diana.g@student.edu', '555-4444', '2023-08-15'),
(5, 'Edward', 'Miller', 'edward.m@student.edu', '555-5555', '2023-08-15');

-- Insert Courses
INSERT INTO Courses (course_id, course_code, course_name, instructor_id, semester, start_date, end_date) VALUES
(1, 'CS101', 'Introduction to Programming', 1, 'Fall 2023', '2023-09-01', '2023-12-15'),
(2, 'MATH201', 'Calculus II', 2, 'Fall 2023', '2023-09-01', '2023-12-15'),
(3, 'PHYS101', 'Physics I', 3, 'Fall 2023', '2023-09-01', '2023-12-15');

-- Insert Enrollments
INSERT INTO Enrollments (enrollment_id, student_id, course_id, enrollment_date, status) VALUES
(1, 1, 1, '2023-08-20', 'Active'),
(2, 1, 2, '2023-08-20', 'Active'),
(3, 2, 1, '2023-08-21', 'Active'),
(4, 2, 3, '2023-08-21', 'Active'),
(5, 3, 2, '2023-08-19', 'Active'),
(6, 3, 3, '2023-08-19', 'Active'),
(7, 4, 1, '2023-08-22', 'Active'),
(8, 4, 2, '2023-08-22', 'Active'),
(9, 5, 2, '2023-08-23', 'Active'),
(10, 5, 3, '2023-08-23', 'Active');

-- Insert some attendance records
INSERT INTO Attendance_Records (record_id, student_id, course_id, date, status, remarks, recorded_by) VALUES
(1, 1, 1, '2023-09-05', 'Present', NULL, 1),
(2, 2, 1, '2023-09-05', 'Present', NULL, 1),
(3, 4, 1, '2023-09-05', 'Absent', 'Sick', 1),
(4, 1, 2, '2023-09-05', 'Present', NULL, 2),
(5, 3, 2, '2023-09-05', 'Late', 'Arrived 15 minutes late', 2),
(6, 4, 2, '2023-09-05', 'Present', NULL, 2),
(7, 5, 2, '2023-09-05', 'Present', NULL, 2);