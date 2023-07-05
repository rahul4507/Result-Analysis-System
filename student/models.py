import pandas as pd
from django.db import models

from user.models import CustomUser, Class, Course, Exam


class Student(models.Model):
    prn = models.IntegerField(unique=True)
    name = models.CharField(max_length=32)
    dob = models.DateTimeField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_no = models.IntegerField(blank=True, null=True)
    parent_contact_no = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Student: {self.user} PRN: {self.prn}'


class StudentEnrollment(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_enrollment')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_course_enrollment')
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='student_class_enrollment')
    roll_no = models.IntegerField(blank=True, null=True)
    grade = models.CharField(max_length=5,blank=True,null=True)
    performance = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.student_id} {self.course_id} {self.class_id}'


class StudentResult(models.Model):
    exam_id = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='student_exam')
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_result')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_course_result')
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='student_class_result')
    TAG = models.CharField(max_length=10, null=True)
    obtained_marks = models.FloatField()

    def __str__(self):
        return f'{self.student_id} {self.course_id} {self.class_id} -{self.exam_id} -{self.obtained_marks} -{self.TAG}'

    @classmethod
    def update(cls, exam_id, course_id, class_id, result_data_file):
       
     df = pd.read_csv(result_data_file)
     df = df.fillna(0)
     for idx, row in df.iterrows():
        enrolled_students = StudentEnrollment.objects.filter(course_id=course_id, class_id=class_id)
        for ens in enrolled_students:
            if ens.student_id.prn == row['PRN']:
                obtained_marks = row['MARKS']
                # Update the obtained marks for the student
                StudentResult.objects.update_or_create(
                    exam_id=Exam.objects.get(pk=exam_id),
                    student_id=ens.student_id,
                    course_id=course_id,
                    class_id=class_id,
                    defaults={'obtained_marks': obtained_marks},
                )
                # Update the tag for the student
                ens.student_id.tag = row['TAG']
                ens.student_id.save()

    @classmethod
    def updateTAG(cls, exam_id, course_id, class_id):
     student_results = StudentResult.objects.filter(course_id=course_id, class_id=class_id, exam_id=exam_id)
     min_marks = 100
     max_marks = 0
     for res in student_results:
        if min_marks > res.obtained_marks:
            min_marks = res.obtained_marks
        if max_marks < res.obtained_marks:
            max_marks = res.obtained_marks
     mid = (min_marks + max_marks) / 2
     factor = (max_marks - min_marks) / 100
     norm = 17.5 * factor
     for res in student_results:
        if res.obtained_marks < mid - norm:
            tag = "WEAK"
        elif res.obtained_marks > mid + norm:
            tag = "FAST"
        else:
            tag = "MODERATE"
        result, created = StudentResult.objects.update_or_create(
            exam_id=Exam.objects.get(pk=exam_id),
            student_id=res.student_id,
            course_id=course_id,
            class_id=class_id,
            defaults={'TAG': tag},
        )
        if not created:
            result.TAG = tag
            result.save()
