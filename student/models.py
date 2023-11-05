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
    grade = models.CharField(max_length=5, blank=True, null=True)
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
        global z, x, y
        df = pd.read_csv(result_data_file)
        df = df.fillna(0)
        enrolled_students = StudentEnrollment.objects.filter(course_id=course_id, class_id=class_id)
        for idx, row in df.iterrows():
            for ens in enrolled_students:
                obtained_marks = row['MARKS'] if ens.student_id.prn == row['PRN'] else 0
                result, created = StudentResult.objects.get_or_create(
                    exam_id=Exam.objects.get(pk=exam_id),
                    student_id=ens.student_id,
                    course_id=course_id,
                    class_id=class_id,
                    defaults={'obtained_marks': obtained_marks},
                )
                if not created:
                    updated_obtained_marks = row['MARKS'] if ens.student_id.prn == row['PRN'] else result.obtained_marks
                    result.obtained_marks = updated_obtained_marks
                result.save()
        mse = Exam.objects.get(name='MSE')
        ese = Exam.objects.get(name='ESE')
        ia = Exam.objects.get(name='IA')
        t = Exam.objects.get(name='TOTAL')
        if mse and ese and ia:
            mse_data = StudentResult.objects.filter(exam_id=mse.id, course_id=course_id,
                                                    class_id=class_id)
            ese_data = StudentResult.objects.filter(exam_id=ese.id, course_id=course_id,
                                                    class_id=class_id)
            ia_data = StudentResult.objects.filter(exam_id=ia.id, course_id=course_id,
                                                   class_id=class_id)
            # Assuming you have imported the necessary models and variables

            for ens in enrolled_students:
                # Initialize variables
                x = 0
                y = 0
                z = 0

                # Find the corresponding marks from mse_data
                for i in mse_data:
                    if ens.student_id.prn == i.student_id.prn:
                        x = i.obtained_marks
                        break

                # Find the corresponding marks from ese_data
                for j in ese_data:
                    if ens.student_id.prn == j.student_id.prn:
                        y = j.obtained_marks
                        break

                # Find the corresponding marks from ia_data
                for k in ia_data:
                    if ens.student_id.prn == k.student_id.prn:
                        z = k.obtained_marks
                        break

                # Calculate the total obtained marks
                total = int(round(z + (7 * (x + y)) / 10))

                # Update or create the StudentResult instance
                student_result, created = StudentResult.objects.update_or_create(
                    exam_id=t,
                    course_id=course_id,
                    student_id=ens.student_id,
                    class_id=class_id,
                    defaults={'obtained_marks': total}
                )

            # Call the updateTAG method to update the TAGs

    @classmethod
    def updateTAG(cls, exam_id, course_id, class_id, slow_cutoff, moderate_cutoff):
        student_results = StudentResult.objects.filter(course_id=course_id, class_id=class_id, exam_id=exam_id)
        exam = Exam.objects.get(pk=exam_id)
        total_marks = exam.total_marks
        slow = (total_marks * int(slow_cutoff)) / 100
        moderate = (total_marks * int(moderate_cutoff)) / 100
        for res in student_results:
            if res.obtained_marks < slow:
                tag = "WEAK"
            elif res.obtained_marks > moderate:
                tag = "FAST"
            else:
                tag = "MODERATE"
            result, created = StudentResult.objects.get_or_create(
                exam_id=Exam.objects.get(pk=exam_id),
                student_id=res.student_id,
                course_id=course_id,
                class_id=class_id,
                defaults={'TAG': tag},
            )
            if not created:
                result.TAG = tag
            result.save()
