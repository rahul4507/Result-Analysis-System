import plotly.graph_objs as go
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Case, When
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from student.models import StudentResult, StudentEnrollment
from teacher.models import Teacher, TeacherEnrollment
from user.models import Exam
from user.permission import teacher_required


class TeacherLoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('teacher:teacher_dashboard')
        return render(request, 'teacher/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            try:
                Teacher.objects.get(user=user)
            except Teacher.DoesNotExist:
                return render(request, 'teacher/login.html', {'error': 'Please login with Teacher account.'})
            else:
                login(request, user)
                return redirect('teacher:teacher_dashboard')
        else:
            return render(request, 'teacher/login.html', {'error': 'Invalid login credentials. Please try again.'})


@method_decorator(teacher_required, name='dispatch')
class TeacherLogoutView(View):

    def get(self, request):
        logout(request)
        return redirect('teacher:teacher_login')


@teacher_required
def teacher_courses(request):
    teacher_enroll = TeacherEnrollment.objects.filter(teacher_id__user=request.user)
    return render(request, 'teacher/courses.html', context={'teacher_enroll': teacher_enroll})


@teacher_required
def teacher_dashboard(request):
    teacher_enroll = TeacherEnrollment.objects.filter(teacher_id__user=request.user)
    return render(request, 'teacher/dashboard.html', context={'teacher_enroll': teacher_enroll})


@teacher_required
def teacher_course_detail(request, pk):
    teacher_enroll = TeacherEnrollment.objects.get(pk=pk)
    exams = Exam.objects.all()
    if request.method == 'POST':
        exam_id = request.POST.get('examId')
        result_data_file = request.FILES.get('studentResultFile')
        StudentResult.update(exam_id, teacher_enroll.course_id, teacher_enroll.class_id, result_data_file)
        StudentResult.updateTAG(exam_id, teacher_enroll.course_id, teacher_enroll.class_id)
    return render(request, 'teacher/course_detail.html',
                  context={'teacher_enroll': teacher_enroll, 'exams': exams})


@teacher_required
def student_performance(request, pk):
    teacher_enroll = TeacherEnrollment.objects.get(pk=pk)
    exams = Exam.objects.all()
    if request.method == 'POST':
        exam_id = request.POST.get('examId')
        exam = Exam.objects.get(pk=exam_id)
        res_data = StudentResult.objects.filter(exam_id=exam, course_id=teacher_enroll.course_id,
                                                class_id=teacher_enroll.class_id)
        # Count the occurrences of each tag value
        tag_counts = {
            'WEAK': 0,
            'FAST': 0,
            'MODERATE': 0
        }

        for result in res_data:
            if result.TAG == 'WEAK':
                tag_counts['WEAK'] += 1
            elif result.TAG == 'FAST':
                tag_counts['FAST'] += 1
            elif result.TAG == 'MODERATE':
                tag_counts['MODERATE'] += 1

        # BAR chart
        labels = list(tag_counts.keys())
        values = list(tag_counts.values())
        colors = ['red', 'green', 'blue']

        category_order = ['FAST', 'MODERATE', 'WEAK']

        fig = go.Figure(data=[go.Bar(x=labels, y=values, marker=dict(color=colors))])
        fig.update_layout(
            title='Tag Distribution',
            xaxis_title='Performance',
            yaxis_title='Students',
            xaxis=dict(type='category', categoryorder='array', categoryarray=category_order)
        )

        return render(request, 'teacher/course_performance.html',
                      context={'teacher_enroll': teacher_enroll, 'exams': exams, 'res_data': res_data,
                               'Performance_Distribution': fig.to_html()})
    return render(request, 'teacher/course_performance.html',
                  context={'teacher_enroll': teacher_enroll, 'exams': exams, 'res_data': []})


@teacher_required
def performance_analysis(request, pk):
    teacher_enroll = get_object_or_404(TeacherEnrollment, pk=pk)
    exams = Exam.objects.all()
    res_data1 = []
    res_data2 = []
    transition_count1 = {
        'WEAK_to_FAST': [],
        'MODERATE_to_FAST': [],
        'FAST_to_FAST': [],
        'WEAK_to_MODERATE': [],
        'MODERATE_to_MODERATE': [],
        'WEAK_to_WEAK': [],
        'MODERATE_to_WEAK': [],
        'FAST_to_WEAK': [],
        'FAST_to_MODERATE': []
    }
    transition_count2 = {
        'WEAK_to_FAST': [],
        'MODERATE_to_FAST': [],
        'FAST_to_FAST': [],
        'WEAK_to_MODERATE': [],
        'MODERATE_to_MODERATE': [],
        'WEAK_to_WEAK': [],
        'MODERATE_to_WEAK': [],
        'FAST_to_WEAK': [],
        'FAST_to_MODERATE': []
    }
    validate = 0
    if request.method == 'POST':
        exam_id1 = request.POST.get('examId1')
        exam_id2 = request.POST.get('examId2')

        exam1 = get_object_or_404(Exam, pk=exam_id1)
        res_data1 = StudentResult.objects.filter(exam_id=exam1, course_id=teacher_enroll.course_id,
                                                 class_id=teacher_enroll.class_id)

        exam2 = get_object_or_404(Exam, pk=exam_id2)
        res_data2 = StudentResult.objects.filter(exam_id=exam2, course_id=teacher_enroll.course_id,
                                                 class_id=teacher_enroll.class_id)
        if res_data1 and res_data2:
            validate = 1
            for i in res_data1:
                for j in res_data2:
                    if (i.TAG == "WEAK" and j.TAG == "FAST") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['WEAK_to_FAST'].append(i)
                        transition_count2['WEAK_to_FAST'].append(j)
                    elif (i.TAG == "WEAK" and j.TAG == "MODERATE") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['WEAK_to_MODERATE'].append(i)
                        transition_count2['WEAK_to_MODERATE'].append(j)
                    elif (i.TAG == "WEAK" and j.TAG == "WEAK") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['WEAK_to_WEAK'].append(i)
                        transition_count2['WEAK_to_WEAK'].append(j)

                    elif (i.TAG == "MODERATE" and j.TAG == "FAST") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['MODERATE_to_FAST'].append(i)
                        transition_count2['MODERATE_to_FAST'].append(j)

                    elif (i.TAG == "MODERATE" and j.TAG == "WEAK") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['MODERATE_to_WEAK'].append(i)
                        transition_count2['MODERATE_to_WEAK'].append(j)

                    elif (i.TAG == "MODERATE" and j.TAG == "MODERATE") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['MODERATE_to_MODERATE'].append(i)
                        transition_count2['MODERATE_to_MODERATE'].append(j)

                    elif (i.TAG == "FAST" and j.TAG == "WEAK") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['FAST_to_WEAK'].append(i)
                        transition_count2['FAST_to_WEAK'].append(j)

                    elif (i.TAG == "FAST" and j.TAG == "MODERATE") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['FAST_to_MODERATE'].append(i)
                        transition_count2['FAST_to_MODERATE'].append(j)

                    elif (i.TAG == "FAST" and j.TAG == "FAST") and (i.student_id.prn == j.student_id.prn):
                        transition_count1['FAST_to_FAST'].append(i)
                        transition_count2['FAST_to_FAST'].append(j)

        else:
            validate = 0
        if validate:
            labels1 = ['FAST_to_FAST', 'MODERATE_to_FAST', 'WEAK_to_FAST', 'FAST_to_MODERATE', 'MODERATE_to_MODERATE',
                       'WEAK_to_MODERATE', 'FAST_to_WEAK', 'MODERATE_to_WEAK', 'WEAK_to_WEAK']
            values1 = [len(transition_count1['FAST_to_FAST']), len(transition_count1['MODERATE_to_FAST']),
                       len(transition_count1['WEAK_to_FAST']), len(transition_count1['FAST_to_MODERATE']),
                       len(transition_count1['MODERATE_to_MODERATE']),
                       len(transition_count1['WEAK_to_MODERATE']), len(transition_count1['FAST_to_WEAK']),
                       len(transition_count1['MODERATE_to_WEAK']),
                       len(transition_count1['WEAK_to_WEAK'])]
            colors1 = ['green', 'red', 'blue', 'yellow', 'pink', 'indigo', 'orange', 'gray', 'brown']

            fig1 = go.Figure(data=[go.Bar(x=labels1, y=values1, marker=dict(color=colors1))])
            fig1.update_layout(title='Performance', xaxis_title='Transition Types', yaxis_title='Count')
            progression = (len(transition_count1['WEAK_to_FAST']) + len(transition_count1['WEAK_to_MODERATE']) + len(
                transition_count1['MODERATE_to_FAST']))
            stable = (len(transition_count1['WEAK_to_WEAK']) + len(transition_count1['FAST_to_FAST']) + len(
                transition_count1['MODERATE_to_MODERATE']))
            degradation = (len(transition_count1['FAST_to_WEAK']) + len(transition_count1['FAST_to_MODERATE']) + len(
                transition_count1['MODERATE_to_WEAK']))

            # plot The second graph
            labels2 = ['Progressive_Students', 'Stable_Students', 'Degrading_Students']
            values2 = [progression, stable, degradation]
            colors2 = ['green', 'blue', 'red']

            fig2 = go.Figure(data=[go.Bar(x=labels2, y=values2, marker=dict(color=colors2))])
            fig2.update_layout(title='Performance', xaxis_title='Transition Types', yaxis_title='Count')
            context = {
                'teacher_enroll': teacher_enroll,
                'exams': exams,
                'transition_data1': transition_count1,
                'transition_data2': transition_count1,
                'W_TO_F1': transition_count1['WEAK_to_FAST'],
                'W_TO_F2': transition_count2['WEAK_to_FAST'],
                'F_TO_F1': transition_count1['FAST_to_FAST'],
                'F_TO_F2': transition_count2['FAST_to_FAST'],
                'M_TO_F1': transition_count1['MODERATE_to_FAST'],
                'M_TO_F2': transition_count2['MODERATE_to_FAST'],
                'W_TO_M1': transition_count1['WEAK_to_MODERATE'],
                'W_TO_M2': transition_count2['WEAK_to_MODERATE'],
                'F_TO_M1': transition_count1['FAST_to_MODERATE'],
                'F_TO_M2': transition_count2['FAST_to_MODERATE'],
                'M_TO_M1': transition_count1['MODERATE_to_MODERATE'],
                'M_TO_M2': transition_count2['MODERATE_to_MODERATE'],
                'W_TO_W1': transition_count1['WEAK_to_WEAK'],
                'W_TO_W2': transition_count2['WEAK_to_WEAK'],
                'F_TO_W1': transition_count1['FAST_to_WEAK'],
                'F_TO_W2': transition_count2['FAST_to_WEAK'],
                'M_TO_W1': transition_count1['MODERATE_to_WEAK'],
                'M_TO_W2': transition_count2['MODERATE_to_WEAK'],

                'res_data1': res_data1,
                'res_data2': res_data2,
                'validate': validate,
                'Transition': fig1.to_html(),
                'Types': fig2.to_html()
            }
            return render(request, 'teacher/performance_analysis.html', context)

    context = {
        'teacher_enroll': teacher_enroll,
        'exams': exams,
        'transition_data': transition_count1,
        'W_TO_F': transition_count1['WEAK_to_FAST'],
        'res_data1': [],
        'res_data2': [],
        'validate': validate,
    }
    return render(request, 'teacher/performance_analysis.html', context)


@teacher_required
def overall_performance(request, pk):
    teacher_enroll = TeacherEnrollment.objects.get(pk=pk)
    exam = Exam.objects.get(name='Total')
    res_data = StudentResult.objects.filter(exam_id=exam, course_id=teacher_enroll.course_id,
                                            class_id=teacher_enroll.class_id)

    if res_data:
        # Count the occurrences of each tag value
        tag_counts = {
            'WEAK': 0,
            'FAST': 0,
            'MODERATE': 0
        }

        for result in res_data:
            if result.TAG == 'WEAK':
                tag_counts['WEAK'] += 1
            elif result.TAG == 'FAST':
                tag_counts['FAST'] += 1
            elif result.TAG == 'MODERATE':
                tag_counts['MODERATE'] += 1

        # BAR chart
        labels = list(tag_counts.keys())
        values = list(tag_counts.values())
        colors = ['red', 'green', 'blue']

        category_order = ['FAST', 'MODERATE', 'WEAK']

        fig = go.Figure(data=[go.Bar(x=labels, y=values, marker=dict(color=colors))])
        fig.update_layout(
            title='Tag Distribution',
            xaxis_title='Performance',
            yaxis_title='Students',
            xaxis=dict(type='category', categoryorder='array', categoryarray=category_order)
        )

        return render(request, 'teacher/overall_performance.html',
                      context={'teacher_enroll': teacher_enroll, 'exams': exam, 'res_data': res_data,
                               'Performance_Distribution': fig.to_html()})
    else:
        return render(request, 'teacher/overall_performance.html',
                      context={'teacher_enroll': teacher_enroll, 'exams': exam, 'res_data': []})
