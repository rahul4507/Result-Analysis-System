from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, When, Case
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View

from user.models import CustomUser, Course
from user.permission import student_required
from .models import Student, StudentEnrollment, StudentResult
import plotly.graph_objects as go
from plotly.offline import plot


class StudentLoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('student:student_dashboard')
        return render(request, 'student/login.html')

    def post(self, request):
        prn = request.POST.get('prn')
        password = request.POST.get('password')
        try:
            student = Student.objects.get(prn=prn)
        except Student.DoesNotExist:
            return render(request, 'student/login.html', {'error': 'Invalid PRN. Please login with a Student account.'})

        user = student.user
        if user.check_password(password):
            login(request, user)
            return redirect('student:student_dashboard')
        else:
            return render(request, 'student/login.html', {'error': 'Invalid login credentials. Please try again.'})


@method_decorator(student_required, name='dispatch')
class StudentLogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('student:student_login')


@student_required
def student_dashboard(request):
    student_enroll = StudentEnrollment.objects.filter(student_id__user=request.user)
    return render(request, 'student/dashboard.html', context={'student_enroll': student_enroll})


@student_required
def student_courses(request):
    student = Student.objects.get(user=request.user)
    student_enroll = StudentEnrollment.objects.filter(student_id=student.id)
    context = {
        'student_enroll': student_enroll,
        'student': student
    }
    return render(request, 'student/student_courses.html', context=context)


@student_required
def student_course_detail(request, course_id):
    student = Student.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id)
    student_result = StudentResult.objects.filter(student_id=student, course_id=course)

    exams = [result.exam_id.name for result in student_result]
    obtained_marks = [result.obtained_marks for result in student_result]
    tags = [result.TAG for result in student_result]

    # Define color mapping based on tag values
    color_map = {
        'FAST': '#28a745',  # Green
        'MODERATE': '#ffc107',  # Yellow
        'WEAK': '#dc3545'  # Red
    }

    # Create the bar chart
    data = [
        go.Bar(
            x=exams,
            y=obtained_marks,
            name='Obtained Marks',
            marker=dict(color=[color_map[tag] for tag in tags]),
            hovertext=tags,
            hoverinfo='text'
        )
    ]

    layout = go.Layout(
        title='Performance in Course',
        xaxis=dict(title='Exam'),
        yaxis=dict(title='Marks'),
        hovermode='closest'
    )

    fig = go.Figure(data=data, layout=layout)

    performance_chart = plot(fig, output_type='div')

    context = {
        'student_result': student_result,
        'student': student,
        'performance_chart': performance_chart
    }
    return render(request, 'student/course_details.html', context=context)


@student_required
def overall_performance(request, course_id):
    try:
        student = Student.objects.get(user=request.user)
        student = StudentEnrollment.objects.get(student_id=student.id, course_id=course_id)
        student_tag = StudentResult.objects.filter(student_id=student.id, course_id=course_id).values(
            'TAG').annotate(
            tag_count=Count('TAG')).order_by('-tag_count').annotate(
            tag_order=Case(*[When(TAG=tag, then=pos) for pos, tag in enumerate(['FAST', 'MODERATE', 'WEAK'])],
                           default=len(['FAST', 'MODERATE', 'WEAK']))).first()

        if student_tag is not None:
            student.performance = student_tag.get('TAG')
            student.save()
    except ObjectDoesNotExist:
        # Handle the case when StudentEnrollment does not exist
        student = None

    context = {
        'student': student,
    }
    return render(request, 'student/overall_performance.html', context)
