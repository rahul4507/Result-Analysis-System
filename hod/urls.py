from django.urls import path

from .views import (dashboard, HodLoginView, HodLogoutView,
                    manage_courses, manage_exams, manage_students, manage_teachers, create_course, update_course,
                    delete_course, create_exam, update_exam, delete_exam, create_student, update_student,
                    delete_student, manage_classes, create_class, delete_class, update_class, create_teacher,
                    update_teacher, delete_teacher, view_results, batch_result)

app_name = 'hod'
urlpatterns = [
    path('dashboard/', dashboard, name='hod_dashboard'),
    path('dashboard/view-results/', view_results, name='view_results'),
    path('dashboard/batch-result', batch_result, name='batch_result'),
    path('login/', HodLoginView.as_view(), name='hod_login'),
    path('logout/', HodLogoutView.as_view(), name='hod_logout'),
    path('manage-courses/', manage_courses, name='manage_courses'),
    path('manage-exams/', manage_exams, name='manage_exams'),
    path('manage-students/', manage_students, name='manage_students'),
    path('manage-teachers/', manage_teachers, name='manage_teachers'),
    path('manage-classes/', manage_classes, name='manage_classes'),
    path('manage-courses/create-course', create_course, name='create_course'),
    path('manage-courses/update-course/<int:course_id>/', update_course, name='update_course'),
    path('manage-courses/delete-course/<int:course_id>/', delete_course, name='delete_course'),
    path('manage-exams/create-exam', create_exam, name='create_exam'),
    path('manage-exams/update-exam/<int:exam_id>/', update_exam, name='update_exam'),
    path('manage-exams/delete-exam/<int:exam_id>/', delete_exam, name='delete_exam'),
    path('manage-students/create-student', create_student, name='create_student'),
    path('manage-students/update-student/<int:student_id>/', update_student, name='update_student'),
    path('manage-students/delete-student/<int:student_id>/', delete_student, name='delete_student'),
    path('manage-classes/create-class', create_class, name='create_class'),
    path('manage-classes/update-class/<int:class_id>/', update_class, name='update_class'),
    path('manage-classes/delete-class/<int:class_id>/', delete_class, name='delete_class'),
    path('manage-teachers/create-teacher/', create_teacher, name='create_teacher'),
    path('manage-teachers/update-teacher/<int:teacher_id>/', update_teacher, name='update_teacher'),
    path('manage-teachers/delete-teacher/<int:teacher_id>/', delete_teacher, name='delete_teacher'),
]
