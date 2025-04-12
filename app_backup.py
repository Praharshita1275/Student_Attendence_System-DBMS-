# app.py - Main application file

import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.secret_key = "your_secret_key"
DB_PATH = "attendance_system.db"

# Database initialization function
def init_db():
    # Check if database file exists
    db_exists = os.path.exists(DB_PATH)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if not db_exists:
        # Read schema from schema.sql file
        with open('schema.sql', 'r') as schema_file:
            schema_script = schema_file.read()
        
        # Execute the schema script
        cursor.executescript(schema_script)
        conn.commit()
        print("Database initialized successfully!")
    
    conn.close()

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Routes for student management
@app.route('/students')
def list_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM Students').fetchall()
    conn.close()
    return render_template('students/list.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        enrollment_date = request.form['enrollment_date']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO Students (first_name, last_name, email, phone, enrollment_date) VALUES (?, ?, ?, ?, ?)',
                    (first_name, last_name, email, phone, enrollment_date))
        conn.commit()
        conn.close()
        
        flash('Student added successfully!')
        return redirect(url_for('list_students'))
    
    return render_template('students/add.html')

# Routes for course management
@app.route('/courses')
def list_courses():
    conn = get_db_connection()
    courses = conn.execute('''
        SELECT c.*, i.first_name || ' ' || i.last_name as instructor_name 
        FROM Courses c
        JOIN Instructors i ON c.instructor_id = i.instructor_id
    ''').fetchall()
    conn.close()
    return render_template('courses/list.html', courses=courses)

# Routes for attendance management
@app.route('/attendance')
def attendance_menu():
    return render_template('attendance/menu.html')

@app.route('/attendance/take', methods=['GET', 'POST'])
def take_attendance():
    conn = get_db_connection()
    
    if request.method == 'POST':
        try:
            course_id = request.form['course_id']
            date = request.form['date']
            instructor_id = request.form['instructor_id']
            
            # Validate date format
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.')
                return redirect(url_for('take_attendance'))
            
            # Get all students enrolled in the course
            students = conn.execute('''
                SELECT s.*, e.enrollment_id
                FROM Students s
                JOIN Enrollments e ON s.student_id = e.student_id
                WHERE e.course_id = ? AND e.status = 'Active'
                ORDER BY s.last_name, s.first_name
            ''', (course_id,)).fetchall()
            
            # Process attendance for each student
            for student in students:
                status_key = f'status_{student["student_id"]}'
                remarks_key = f'remarks_{student["student_id"]}'
                
                if status_key in request.form:
                    status = request.form[status_key]
                    remarks = request.form.get(remarks_key, '')
                    
                    # Validate status
                    if status not in ['Present', 'Absent', 'Late', 'Excused']:
                        flash(f'Invalid status for student {student["first_name"]} {student["last_name"]}')
                        continue
                    
                    # Check if record already exists
                    existing = conn.execute('''
                        SELECT record_id FROM Attendance_Records
                        WHERE student_id = ? AND course_id = ? AND date = ?
                    ''', (student["student_id"], course_id, date)).fetchone()
                    
                    if existing:
                        # Update existing record
                        conn.execute('''
                            UPDATE Attendance_Records
                            SET status = ?, remarks = ?, recorded_by = ?, recorded_at = CURRENT_TIMESTAMP
                            WHERE record_id = ?
                        ''', (status, remarks, instructor_id, existing['record_id']))
                    else:
                        # Insert new record
                        conn.execute('''
                            INSERT INTO Attendance_Records (student_id, course_id, date, status, remarks, recorded_by)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (student["student_id"], course_id, date, status, remarks, instructor_id))
            
            conn.commit()
            flash('Attendance recorded successfully!')
            return redirect(url_for('attendance_menu'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error recording attendance: {str(e)}')
            return redirect(url_for('take_attendance'))
    
    # GET request handling
    courses = conn.execute('SELECT * FROM Courses').fetchall()
    instructors = conn.execute('SELECT * FROM Instructors').fetchall()
    
    conn.close()
    return render_template('attendance/take.html', courses=courses, instructors=instructors, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/attendance/stats', methods=['GET'])
def attendance_stats():
    """Generate attendance statistics for courses or students"""
    conn = get_db_connection()
    stats_type = request.args.get('type', 'course')
    
    if stats_type == 'course':
        # Course attendance statistics
        stats = conn.execute('''
            SELECT c.course_id, c.course_code, c.course_name,
                   COUNT(DISTINCT a.student_id) as total_students,
                   SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count,
                   ROUND(100.0 * SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) / 
                         COUNT(*), 2) as attendance_percentage
            FROM Attendance_Records a
            JOIN Courses c ON a.course_id = c.course_id
            GROUP BY c.course_id
            ORDER BY attendance_percentage DESC
        ''').fetchall()
    else:
        # Student attendance statistics
        stats = conn.execute('''
            SELECT s.student_id, s.first_name, s.last_name,
                   COUNT(DISTINCT a.course_id) as total_courses,
                   SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count,
                   ROUND(100.0 * SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) / 
                         COUNT(*), 2) as attendance_percentage
            FROM Attendance_Records a
            JOIN Students s ON a.student_id = s.student_id
            GROUP BY s.student_id
            ORDER BY attendance_percentage DESC
        ''').fetchall()
    
    conn.close()
    return render_template('attendance/stats.html', stats=stats, stats_type=stats_type)

@app.route('/attendance/export', methods=['GET'])
def export_attendance():
    """Export attendance data in CSV or PDF format"""
    format_type = request.args.get('format', 'csv')
    stats_type = request.args.get('type', 'course')
    
    conn = get_db_connection()
    
    if stats_type == 'course':
        data = conn.execute('''
            SELECT c.course_code, c.course_name, 
                   a.date, a.status, COUNT(*) as count
            FROM Attendance_Records a
            JOIN Courses c ON a.course_id = c.course_id
            GROUP BY c.course_id, a.date, a.status
            ORDER BY c.course_code, a.date
        ''').fetchall()
    else:
        data = conn.execute('''
            SELECT s.student_id, s.first_name, s.last_name,
                   c.course_code, a.date, a.status
            FROM Attendance_Records a
            JOIN Students s ON a.student_id = s.student_id
            JOIN Courses c ON a.course_id = c.course_id
            ORDER BY s.last_name, s.first_name, a.date
        ''').fetchall()
    
    conn.close()

    if format_type == 'pdf':
        # Create PDF export
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        
        # PDF content generation
        p.drawString(100, 800, "Attendance Report")
        p.drawString(100, 780, f"Report Type: {stats_type.title()} Statistics")
        y_position = 760
        
        for row in data:
            if stats_type == 'course':
                text = f"{row['course_code']} - {row['course_name']}: {row['date']} - {row['status']} ({row['count']})"
            else:
                text = f"{row['first_name']} {row['last_name']}: {row['course_code']} - {row['date']} - {row['status']}"
            
            p.drawString(100, y_position, text)
            y_position -= 20
            if y_position < 50:  # Add new page if running out of space
                p.showPage()
                y_position = 800
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_{stats_type}.pdf'
        return response
    else:
        # Create CSV export
        output = BytesIO()
        if stats_type == 'course':
            df = pd.DataFrame(data, columns=['course_code', 'course_name', 'date', 'status', 'count'])
        else:
            df = pd.DataFrame(data, columns=['student_id', 'first_name', 'last_name', 'course_code', 'date', 'status'])
        
        df.to_csv(output, index=False)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_{stats_type}.csv'
        return response

@app.route('/attendance/report', methods=['GET', 'POST'])
def attendance_report():
    if request.method == 'POST':
        conn = get_db_connection()
        
        report_type = request.form['report_type']
        
        if report_type == 'student':
            student_id = request.form['student_id']
            attendance_data = conn.execute('''
                SELECT a.*, c.course_code, c.course_name, s.first_name || ' ' || s.last_name as student_name
                FROM Attendance_Records a
                JOIN Courses c ON a.course_id = c.course_id
                JOIN Students s ON a.student_id = s.student_id
                WHERE a.student_id = ?
                ORDER BY a.date DESC
            ''', (student_id,)).fetchall()
            
            student = conn.execute('SELECT * FROM Students WHERE student_id = ?', (student_id,)).fetchone()
            conn.close()
            
            return render_template('attendance/student_report.html', attendance_data=attendance_data, student=student)
        
        elif report_type == 'course':
            course_id = request.form['course_id']
            date = request.form.get('date', None)
            
            query = '''
                SELECT a.*, s.first_name || ' ' || s.last_name as student_name
                FROM Attendance_Records a
                JOIN Students s ON a.student_id = s.student_id
                WHERE a.course_id = ?
            '''
            params = [course_id]
            
            if date:
                query += ' AND a.date = ?'
                params.append(date)
            
            query += ' ORDER BY a.date DESC, s.last_name, s.first_name'
            
            attendance_data = conn.execute(query, params).fetchall()
            course = conn.execute('SELECT * FROM Courses WHERE course_id = ?', (course_id,)).fetchone()
            
            conn.close()
            return render_template('attendance/course_report.html', attendance_data=attendance_data, course=course, selected_date=date)
        
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM Students').fetchall()
    courses = conn.execute('SELECT * FROM Courses').fetchall()
    conn.close()
    
    return render_template('attendance/report_form.html', students=students, courses=courses)

# Initialize the database when the app starts
@app.before_first_request
def before_first_request():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)