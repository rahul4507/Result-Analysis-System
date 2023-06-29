from django import forms
from django.contrib.auth import password_validation
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _

from .models import *

admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Class)
admin.site.register(Exam)


class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'role')


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            'Raw passwords are not stored, so there is no way to see '
            'this user\'s password, but you can change the password '
            'using <a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        model = CustomUser
        fields = (
            'email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'role', 'groups',
            'user_permissions',)


class CustomUserAdmin(UserAdmin):
    """
    The User admin interface.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'role', 'is_active', 'is_staff', 'is_superuser',)
    list_filter = ('is_staff', 'is_superuser', 'role', 'is_active', 'groups',)
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Authorization'), {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions', 'role')}
         ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
