from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View

from hod.models import HOD
from hod.process_data import update_student_data, register_students
from student.models import StudentEnrollment, Student
from teacher.models import Teacher
from user.models import Class, Course, Semester, Exam, CustomUser
from user.permission import hod_required


@hod_required
def dashboard(request):
    classes = Class.objects.all()
    if request.method == 'POST' and 'studentGradeFile' in request.POST:
        class_id = request.POST.get('classId')
        student_grade_file = request.FILES.get('studentGradeFile')
        class_ins = Class.objects.get(pk=class_id)
        update_student_data(class_ins, student_grade_file)
        student_enroll = StudentEnrollment.objects.filter(class_id=class_id)
        context = {
            'student_enroll': student_enroll,
            'selected_class_id': class_id,
            'classes': classes
        }
        return render(request, 'hod/dashboard.html', context=context)
    else:
        context = {
            'classes': classes
        }
        return render(request, 'hod/dashboard.html', context=context)


@hod_required
def view_results(request):
    classes = Class.objects.all()
    context = {
        'classes': classes,
    }
    if request.method == 'POST':
        class_id = int(request.POST.get('classID'))
        students = Student.objects.all()
        student_results = []
        enrolled_class = Class.objects.get(id=int(class_id))
        for student in students:
            enrollments = student.student_enrollment.filter(class_id=class_id)
            fail_count = enrollments.filter(grade__in=['0', 'FF']).count()
            total_enrollments = enrollments.count()

            if total_enrollments > 0:
                if fail_count == 0:
                    student_data_result = (student, "Pass")
                else:
                    student_data_result = (student, "Fail")
                student_results.append(student_data_result)
        passing_students = [
            student for student, result in student_results if result == "Pass"
        ]
        passing_students_count = len(passing_students)
        students_per_page = 20
        paginator = Paginator(student_results, students_per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
            'classes': classes,
            'en_class': enrolled_class,
            'passing_students': passing_students_count
        }
        return render(request, 'hod/view_results.html', context=context)
    else:
        return render(request, 'hod/view_results.html', context=context)


@hod_required
def batch_result(request):
    classes = Class.objects.all()
    students = Student.objects.all()
    student_batch_results = []
    context = {
        'classes': classes,
    }
    if request.method == 'POST':
        class_id = int(request.POST.get('classID'))
        class_inc = Class.objects.get(pk=class_id)
        enrolled_batch = Class.objects.get(id=int(class_id))
        for student in students:
            enrollments = student.student_enrollment.filter(class_id__semester__year=class_inc.semester.year)
            fail_count = enrollments.filter(grade__in=['0', 'FF', 'XX']).count()
            total_enrollments = enrollments.count()

            if total_enrollments > 0:
                if fail_count == 0:
                    student_data_result = (student, "Pass")
                else:
                    student_data_result = (student, "Fail")
                student_batch_results.append(student_data_result)
        passing_students = [
            student for student, result in student_batch_results if result == "Pass"
        ]
        passing_students_count = len(passing_students)
        context = {
            'classes': classes,
            'batch_result': student_batch_results,
            'enrolled_batch': enrolled_batch,
            'passing_students': passing_students,
            'passing_students_count': passing_students_count
        }
        return render(request, 'hod/batch_result.html', context)
    else:
        return render(request, 'hod/batch_result.html', context=context)


class HodLoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('hod:hod_dashboard')
        return render(request, 'hod/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            try:
                HOD.objects.get(user=user)
            except HOD.DoesNotExist:
                return render(request, 'hod/login.html', {'error': 'Please login with hod account.'})
            else:
                login(request, user)
                return redirect('hod:hod_dashboard')
        else:
            return render(request, 'hod/login.html', {'error': 'Invalid login credentials. Please try again.'})


@method_decorator(hod_required, name='dispatch')
class HodLogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('hod:hod_login')


@hod_required
def manage_courses(request):
    courses = Course.objects.all()
    return render(request, 'hod/manage_courses.html', context={'courses': courses})


@hod_required
def create_course(request):
    context = {'class': Class.objects.all()}
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        credit = request.POST.get('credits')
        semester_id = request.POST.get('semester')
        is_optional = request.POST.get('is_optional', 'off')
        if is_optional == 'on':
            set_optional = True
        else:
            set_optional = False
        semester = get_object_or_404(Semester, pk=semester_id)
        course = Course(name=name, code=code, credits=credit, semester=semester,
                        is_active=True, is_optional=set_optional)
        course.save()

        return redirect('hod:manage_courses')
    else:
        return render(request, 'hod/course/create_course.html', context=context)


@hod_required
def update_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    classes = Class.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        credits = request.POST.get('credits')
        semester_id = request.POST.get('semester')
        is_optional = request.POST.get('is_optional', 'off')
        if is_optional == 'on':
            set_optional = True
        else:
            set_optional = False

        semester = get_object_or_404(Semester, pk=semester_id)
        course.name = name
        course.code = code
        course.credits = credits
        course.semester = semester
        course.is_optional = set_optional
        course.save()

        return redirect('hod:manage_courses')
    else:
        return render(request, 'hod/course/update_course.html', {'course': course, 'classes': classes})


@hod_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        course.delete()
        return redirect('hod:manage_courses')
    else:
        return render(request, 'hod/course/delete_course.html', {'course': course})


@hod_required
def manage_exams(request):
    exams = Exam.objects.all()
    return render(request, 'hod/manage_exams.html', context={'exams': exams})


@hod_required
def create_exam(request):
    exams = Exam.objects.all()
    context = {
        'exams': exams
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        total_marks = request.POST.get('total_marks')
        exam = Exam.objects.create(name=name, total_marks=total_marks)
        exam.save()
        return redirect('hod:manage_exams')

    else:
        return render(request, 'hod/Exam/create_exam.html', context=context)


@hod_required
def delete_exam(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    if request.method == 'POST':
        exam.delete()
        return redirect('hod:manage_exams')
    else:
        return render(request, 'hod/Exam/delete.html', {'exam': exam})


@hod_required
def update_exam(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    if request.method == 'POST':
        exam.name = request.POST.get('name')
        exam.total_marks = request.POST.get('total_marks')
        exam.save()
        return redirect('hod:manage_exams')
    return render(request, 'hod/Exam/update_exam.html', {'exam': exam})


@hod_required
def manage_students(request):
    students = Student.objects.all()
    context = {
        'students': students
    }
    if request.method == 'POST':
        student_data = request.FILES.get('student-data')
        register_students(student_data)
    return render(request, 'hod/manage_students.html', context=context)


@hod_required
def create_student(request):
    global validate
    students = Student.objects.all()
    context = {
        'validate': 1,
        'students': students
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        dob = request.POST.get('dob')
        prn = request.POST.get('prn')
        contact_no = request.POST.get('contact_no')
        address = request.POST.get('address')
        email = request.POST.get('email')
        password = 'Student@123'
        try:
            # Check if a user with the same email already exists
            user = CustomUser.objects.get(email=email)
            if (user):
                validate = 0
        except CustomUser.DoesNotExist:
            # Create a new user if no user with the same email exists
            user = CustomUser.objects.create(
                role='S',
                email=email,
                password=make_password(password)
            )
        try:
            student = Student.objects.get(prn=prn)
            if (student):
                validate = 0
        except Student.DoesNotExist:
            # Create a new student if no student with the same prn exists
            student = Student(
                prn=prn,
                name=name,
                address=address,
                dob=dob,
                contact_no=contact_no,
                user=user,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            student.save()
        if validate:
            context = {
                'students': students
            }
            return render(request, 'hod/manage_students.html', context=context)
        else:
            context = {
                'validate': validate,
                'students': students
            }
            return render(request, 'hod/student/create_student.html', context=context)

    else:
        # Render the form to create a new Student
        return render(request, 'hod/student/create_student.html', context=context)


@hod_required
def update_student(request, student_id):
    student = Student.objects.get(id=student_id)
    prn_occupied = False

    if request.method == 'POST':
        new_prn = request.POST.get('prn')

        if Student.objects.filter(prn=new_prn).exclude(id=student_id).exists():
            prn_occupied = True
        else:
            student.name = request.POST.get('name')
            student.PRN = new_prn
            student.dob = request.POST.get('dob')
            student.address = request.POST.get('address')
            student.contact_no = request.POST.get('contact_no')
            student.save()
            return redirect('hod:manage_students')

    context = {'student': student, 'prn_occupied': prn_occupied}
    return render(request, 'hod/student/update_student.html', context)


@hod_required
def delete_student(request, student_id):
    student = Student.objects.get(id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('hod:manage_students')
    else:
        return render(request, 'hod/student/delete_student.html', {'student': student})


@hod_required
def manage_teachers(request):
    teachers = Teacher.objects.all()
    context = {
        'teachers': teachers
    }
    return render(request, 'hod/manage_teachers.html', context=context)


@hod_required
def create_teacher(request):
    return render(request, 'hod/teacher/create_teacher.html')


@hod_required
def update_teacher(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id)
    name_occupied = False

    if request.method == 'POST':
        new_name = request.POST.get('name')

        if Teacher.objects.filter(name=new_name).exclude(id=teacher_id).exists():
            name_occupied = True
        else:
            teacher.name = new_name
            teacher.address = request.POST.get('address')
            teacher.contact_no = request.POST.get('contact_no')
            teacher.save()
            return redirect('hod:manage_teachers')

    context = {'teacher': teacher, 'name_occupied': name_occupied}
    return render(request, 'hod/teacher/update_teacher.html', context=context)


@hod_required
def delete_teacher(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id)
    if request.method == 'POST':
        teacher.delete()
        return redirect('hod:manage_teachers')
    else:
        return render(request, 'hod/teacher/delete_teacher.html', {'teacher': teacher})


@hod_required
def manage_classes(request):
    classes = Class.objects.all()
    context = {
        'classes': classes
    }
    return render(request, 'hod/manage_classes.html', context=context)


@hod_required
def create_class(request):
    # classes = Class.objects.all().distinct()
    # distinct_semesters = Semester.objects.values_list('semester', flat=True).distinct()
    # distinct_years = Semester.objects.values_list('year__year', flat=True).distinct()
    semesters = Semester.objects.all()
    context = {
        'semesters': semesters,
    }

    if request.method == 'POST':
        semester = request.POST.get('semester')
        division = request.POST.get('division')

        # Check if a similar entry already exists
        class_exists = Class.objects.filter(semester_id=semester, division=division).exists()

        if not class_exists:
            class_this = Class.objects.create(semester_id=semester, division=division)
            class_this.save()
            return redirect('hod:manage_classes')
        else:
            # Set a flag to indicate duplicate entry
            context['duplicate_entry'] = True

    return render(request, 'hod/class/create_class.html', context=context)


@hod_required
def update_class(request, class_id):
    classes = Class.objects.get(id=class_id)
    semesters = Semester.objects.all()
    context = {
        'classes': classes,
        'semesters': semesters
    }
    if request.method == 'POST':
        division = request.POST.get('division')
        sem = request.POST.get('semester')

        # Check if the updated values already exist in another class
        class_exists = Class.objects.exclude(id=class_id).filter(semester_id=sem, division=division).exists()
        semester = Semester.objects.get(id=sem)
        if not class_exists:
            classes.semester = semester
            classes.division = division
            classes.save()
            return redirect('hod:manage_classes')
        else:
            # Set a flag to indicate duplicate entry
            context['duplicate_entry'] = True

    return render(request, 'hod/class/update_class.html', context=context)


@hod_required
def delete_class(request, class_id):
    classes = Class.objects.get(id=class_id)
    if request.method == 'POST':
        classes.delete()
        return redirect('hod:manage_classes')
    else:
        return render(request, 'hod/class/delete_class.html', {'classes': classes})
