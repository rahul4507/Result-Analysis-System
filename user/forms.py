# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from user.models import CustomUser, Student, Course
#
#
# class StudentRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False)
#
#     class Meta:
#         model = CustomUser
#         fields = ('email', 'password1', 'password2')
#
#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if CustomUser.objects.filter(email=email).exists():
#             raise forms.ValidationError('This email is already in use')
#         return email
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.username = user.email
#         user.is_active = True
#         if commit:
#             user.save()
#
#         student = Student(user=user, course=self.cleaned_data.get('course'))
#         student.save()
#         return user
