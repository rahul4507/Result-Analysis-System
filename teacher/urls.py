from django.urls import path

from .views import (
    teacher_dashboard,
    TeacherLoginView, TeacherLogoutView,
    teacher_courses, teacher_course_detail, student_performance,
    performance_analysis, overall_performance, student_download_results, student_download_results_overall,
    performance_analysis_download
)

app_name = 'teacher'
urlpatterns = [
    path('login/', TeacherLoginView.as_view(), name='teacher_login'),
    path('logout/', TeacherLogoutView.as_view(), name='teacher_logout'),
    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('courses/', teacher_courses, name='teacher_courses'),
    path('courses/<int:pk>', teacher_course_detail, name='teacher_course_detail'),
    path('course-performance/<int:pk>', student_performance, name='student_performance'),
    path('course-performance/download-results/<int:pk>', student_download_results, name='download_results'),
    path('course-performance-analysis/<int:pk>', performance_analysis, name='performance_Analysis'),
    path('course-performance-analysis/download/<int:pk>', performance_analysis_download, name='performance_analysis_download'),
    path('overall-course-performance/<int:pk>', overall_performance, name='overall_Performance'),
    path('overall-course-performance/download_results_overall/<int:pk>', student_download_results_overall,
         name='download_results_overall'),
]
