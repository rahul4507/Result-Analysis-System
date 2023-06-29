from django.contrib import admin

from .models import Student, StudentEnrollment, StudentResult

admin.site.register(Student)
admin.site.register(StudentEnrollment)
admin.site.register(StudentResult)
