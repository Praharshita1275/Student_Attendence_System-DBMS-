# Student Attendance Tracking System

A simple database management system for tracking student attendance in academic courses.

## Features

- Student Management: Add and view student information
- Course Management: View course details
- Attendance Management:
  - Record daily attendance (Present, Absent, Late, Excused)
  - Generate attendance reports by student or course
  - Calculate attendance percentages

## Project Structure

```
student-attendance-system/
├── app.py             # Main application file
├── schema.sql         # Database schema
├── requirements.txt   # Python dependencies
├── static/
│   └── css/
│       └── style.css  # CSS styling
└── templates/         # HTML templates
    ├── index.html
    ├── students/
    │   ├── list.html
    │   └── add.html
    ├── courses/
    │   └── list.html
    └── attendance/
        ├── menu.html
        ├── take.html
        ├── report_form.html
        ├── student_report.html
        └── course_report.html
```

## Setup and Installation

1. Create a new folder for your project:
```
mkdir student-attendance-system
cd student-attendance-system
```

2. Create a virtual environment (optional but recommended):
```
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install the required dependencies:
```
pip install -r requirements.txt
```

5. Create the appropriate file structure as shown above and add the source code to each file.

6. Run the application:
```
python app.py
```

7. Open a web browser and navigate to `http://127.0.0.1:5000` to access the application.

## Database Schema

The application uses SQLite as the database engine with the following tables:

- **Students**: Store student information
- **Instructors**: Store instructor information
- **Courses**: Store course details
- **Enrollments**: Track which students are enrolled in which courses
- **Attendance_Records**: Store individual attendance entries

The database is initialized automatically when the application starts.

## Usage

1. Start by adding students (if not using sample data)
2. View available courses
3. Use the Attendance menu to:
   - Take attendance for a course on a specific date
   - Generate attendance reports by student or course

## Note

This is a simple implementation for educational purposes. For production use, consider adding:
- User authentication and roles
- Form validation
- Backup functionality
- More robust error handling