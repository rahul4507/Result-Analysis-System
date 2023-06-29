from django.urls import path

from .views import (
    teacher_dashboard,
    TeacherLoginView, TeacherLogoutView,
    teacher_courses, teacher_course_detail, student_performance,
    performance_analysis, overall_performance
)

app_name = 'teacher'
urlpatterns = [
    path('login/', TeacherLoginView.as_view(), name='teacher_login'),
    path('logout/', TeacherLogoutView.as_view(), name='teacher_logout'),
    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('courses/', teacher_courses, name='teacher_courses'),
    path('courses/<int:pk>', teacher_course_detail, name='teacher_course_detail'),
    path('course-performance/<int:pk>', student_performance, name='student_performance'),
    path('course-performance-analysis/<int:pk>', performance_analysis, name='performance_Analysis'),
    path('overall-course-performance/<int:pk>', overall_performance, name='overall_Performance')
]
