import pandas as pd
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from student.models import Student, StudentEnrollment
from user.models import Course, CustomUser


def update_student_data(class_ins, student_grade_file):
    semester = class_ins.semester
    df = pd.read_csv(student_grade_file)
    df = df.fillna(0)
    # TODO: Remove PRN_NO and NAME from courses_list
    # TODO: Create courses Course
    courses_list = list(df.columns)
    course_list = courses_list[4:]
    for course in course_list:
        try:
            # Try to get the course with the same name
            existing_course = Course.objects.get(name=course)
        except Course.DoesNotExist:
            # Create a new course if no course with the same name exists
            new_course = Course(
                name=course,
                semester=semester,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            new_course.save()
    # Student Creation from the file
    for idx, row in df.iterrows():
        email = row['EMAIL_ID']
        password = 'Student@123'

        try:
            # Check if a user with the same email already exists
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Create a new user if no user with the same email exists
            user = CustomUser.objects.create(
                role='S',
                email=email,
                password=make_password(password)
            )

        prn = row['PRN_NO']
        name = row['FIRST_NAME']

        # Try to get the student with the same prn if it already exists
        try:
            student = Student.objects.get(prn=prn)
        except Student.DoesNotExist:
            # Create a new student if no student with the same prn exists
            student = Student(
                prn=prn,
                name=name,
                user=user,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            student.save()
        else:
            # Update the existing student's information
            student.name = name
            student.user = user
            student.updated_at = timezone.now()
            student.save()

    # Creating the Enrollments
    for idx, row in df.iterrows():
        prn = row['PRN_NO']
        student = Student.objects.get(prn=prn)

        for course in course_list:
            # Get the grade for the current course in the row
            grade = row[course]
            course_obj = Course.objects.get(name=course)
            # Create the student enrollment
            enrollment, created = StudentEnrollment.objects.get_or_create(
                student_id=student,
                course_id=course_obj,
                class_id=class_ins,
                defaults={
                    'grade': grade,
                    'created_at': timezone.now(),
                    'updated_at': timezone.now()
                }
            )

            if not created:
                # Update the existing enrollment grade if it already exists
                enrollment.grade = grade
                enrollment.updated_at = timezone.now()
                enrollment.save()


def register_students(student_data_file):
    df = pd.read_csv(student_data_file)
    df = df.fillna(0)
    for idx, row in df.iterrows():
        email = row['EMAIL_ID']
        password = 'Student@123'
        try:
            # Check if a user with the same email already exists
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Create a new user if no user with the same email exists
            user = CustomUser.objects.create(
                role='S',
                email=email,
                password=make_password(password)
            )
        prn = row['PRN']
        name = row['NAME']
        # Try to get the student with the same prn if it already exists
        try:
            student = Student.objects.get(prn=prn)
        except Student.DoesNotExist:
            # Create a new student if no student with the same prn exists
            student = Student(
                prn=prn,
                name=name,
                user=user,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            student.save()
        else:
            # Update the existing student's information
            student.name = name
            student.user = user
            student.updated_at = timezone.now()
            student.save()
