from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from user.models import CustomUser


def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != CustomUser.Role.STUDENT:
            return render(request, '403.html')
        return view_func(request, *args, **kwargs)

    return login_required(login_url='student:student_login')(wrapper)


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != CustomUser.Role.TEACHER:
            return render(request, '403.html')
        return view_func(request, *args, **kwargs)

    return login_required(login_url='teacher:teacher_login')(wrapper)


def hod_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != CustomUser.Role.HOD:
            return render(request, '403.html')
        return view_func(request, *args, **kwargs)

    return login_required(login_url='hod:hod_login')(wrapper)
