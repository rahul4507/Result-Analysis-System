from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from user.manager import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Role(models.TextChoices):
        STUDENT = 'S', _('Student')
        TEACHER = 'T', _('Teacher')
        HOD = 'H', _('HOD')
        SUPERUSER = 'SU', _('Superuser')

    role = models.CharField(max_length=2, choices=Role.choices, default=Role.STUDENT)

    def __str__(self):
        return self.email


class Semester(models.Model):
    year = models.DateField()
    semester = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Batch: {self.year}, Sem: {self.semester}'


class Course(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=8, null=True, blank=True)
    credits = models.IntegerField(default=0)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='course_sem')
    is_active = models.BooleanField(default=True)
    is_optional = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Course: {self.name}'


class OptionalCourse(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='optional_course_sem')
    course = models.ManyToManyField(Course)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Sem: {self.semester}, courses: {self.course}'


class Class(models.Model):
    class Division(models.TextChoices):
        Division_A = 'A', _('Division A')
        Division_B = 'B', _('Division B')
        Division_C = 'C', _('Division C')
        Division_D = 'D', _('Division D')
        Division_E = 'E', _('Division E')
        Division_F = 'F', _('Division F')
        Division_G = 'G', _('Division G')
        Division_H = 'H', _('Division H')

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='class_sem')
    division = models.CharField(max_length=1, choices=Division.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.semester}, Division: {self.division}'


class Exam(models.Model):
    name = models.CharField(max_length=8, null=True, blank=True)
    total_marks = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
