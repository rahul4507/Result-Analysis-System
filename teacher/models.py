from django.db import models

from user.models import CustomUser, Course, Class


class Teacher(models.Model):
    name = models.CharField(max_length=32)
    address = models.TextField(blank=True, null=True)
    contact_no = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Teacher: {self.user}'


class TeacherEnrollment(models.Model):
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_enrollment')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='teacher_course_enrollment')
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='teacher_class_enrollment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'TeacherEnroll: {self.teacher_id}'
