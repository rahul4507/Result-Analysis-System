from django.urls import path

from .views import (
    StudentLoginView, StudentLogoutView,
    student_dashboard, student_courses, student_course_detail, overall_performance
)

app_name = 'student'
urlpatterns = [
    path('login/', StudentLoginView.as_view(), name='student_login'),
    path('logout/', StudentLogoutView.as_view(), name='student_logout'),
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('overall-performance/<int:course_id>/', overall_performance, name='overall_performance'),
    path('dashboard/student-courses/', student_courses, name='student_courses'),
    path('dashboard/student-courses/<int:course_id>/', student_course_detail, name='student_course_detail'),
]
