from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import UserCreationForm

from user.models import CustomUser
from .models import Student


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    prn = forms.IntegerField(required=True)
    name = forms.CharField(max_length=32, required=True)
    dob = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    contact_no = forms.IntegerField(required=False)
    parent_contact_no = forms.IntegerField(required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.is_active = True
        if commit:
            user.save()
        student = Student(
            user=user,
            prn=self.cleaned_data.get('prn'),
            name=self.cleaned_data.get('name'),
            dob=self.cleaned_data.get('dob'),
            address=self.cleaned_data.get('address'),
            contact_no=self.cleaned_data.get('contact_no'),
            parent_contact_no=self.cleaned_data.get('parent_contact_no')
        )
        student.save()
        return user
