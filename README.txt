# Result Analysis System - Django Models and Data Updates

This repository contains Django models for a Result Analysis System, including models for Teachers, Students, Enrollments, Results, and data update methods.

## Features

### Teacher Model
- Represents teachers with their name, address, contact number, and associated user account.

### Teacher Enrollment Model
- Represents the enrollment of a teacher into a specific course and class.

### Student Model
- Represents students with their PRN (Permanent Registration Number), name, date of birth, address, contact numbers, and associated user account.

### Student Enrollment Model
- Represents the enrollment of a student into a specific course and class. Stores additional information like roll number, grade, and performance.

### Student Result Model
- Represents the results of students in various exams. Stores the obtained marks, a calculated TAG (indicating performance), and allows data updates.

## Data Updates
- The `StudentResult` model includes methods to update student results and TAGs based on input data files. The provided CSV file is processed to update student results and calculate TAGs.

## Setup

1. **Clone the Repository:**
   - Clone this repository to your local machine using the command:
     ```
     git clone <repository_url>
     ```
   
2. **Install Dependencies:**
   - Make sure you have Django and pandas installed. If not, install them using:
     ```
     pip install Django pandas
     ```

3. **Migrate the Database:**
   - Navigate to the project directory where you have your Django settings and models.
   - Run the following commands to create the necessary database tables:
     ```
     python manage.py makemigrations
     python manage.py migrate
     ```

4. **Add Models to Your App:**
   - Copy and paste the provided model classes into your Django app's `models.py` file.

5. **Superuser Creation:**
   - Create a superuser to access the Django Admin interface using:
     ```
     python manage.py createsuperuser
     ```

6. **Run the Development Server:**
   - Start the Django development server to interact with your models and perform CRUD operations through the Django Admin interface:
     ```
     python manage.py runserver
     ```
   - Access the Django Admin interface at `http://localhost:8000/admin/`.

7. **Run Data Updates (Optional):**
   - Edit the data file path in the code.
   - Run the provided data update methods using:
     ```
     python manage.py shell
     ```
     Then run the following commands within the shell:
     ```python
     from your_app.models import StudentResult
     StudentResult.update(exam_id, course_id, class_id, 'path_to_your_data_file.csv')
     ```

## Notes

- These models provide a foundation for managing teachers, students, enrollments, and results in a university management system.

- Use the provided data update methods carefully, ensuring that the input data is structured correctly.

- Make sure to follow Django best practices for security, data validation, and project structuring.

- Feel free to customize the code further to meet your specific requirements.
