from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from core.models import Lecturer, Course, Enrollment, Grade, Attendance, Student, StudentAchievement, DisciplinaryAction
from accounts.models import CustomUser
from accounts.decorators import role_required
from accounts.forms import LecturerProfileUpdateForm
from notifications.models import Notification
from .forms import StudentAssignmentForm, AttendanceForm, GradeForm, MessageForm

@role_required(CustomUser.Role.LECTURER)
def lecturer_dashboard(request):
    try:
        lecturer = Lecturer.objects.get(user=request.user)
    except Lecturer.DoesNotExist:
        raise Http404("Lecturer profile not found.")

    courses = Course.objects.filter(lecturer=lecturer)

    courses_data = []
    attendance_values = []
    total_students = 0

    for course in courses:
        enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
        students_info = []
        for enrollment in enrollments:
            grades = Grade.objects.filter(enrollment=enrollment)
            attendance_records = Attendance.objects.filter(enrollment=enrollment)
            total_attendance = attendance_records.count()
            present_attendance = attendance_records.filter(status='present').count()
            attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0

            students_info.append({
                'student': enrollment.student,
                'email': enrollment.student.user.email,  # FIXED: Use .user.email
                'full_name': enrollment.student.user.get_full_name(),  # Optional: Pass full name
                'date_enrolled': enrollment.date_enrolled,
                'grades': grades,
                'attendance_percentage': round(attendance_percentage, 2),
                'enrollment': enrollment,
            })

            attendance_values.append(attendance_percentage)

        total_students += len(students_info)

        courses_data.append({
            'course': course,
            'students_info': students_info,
        })

    average_attendance = round(sum(attendance_values) / len(attendance_values), 2) if attendance_values else 0

    notifications = Notification.objects.filter(lecturer=request.user, is_read=False)
    notifications_unread_count = notifications.count()

    context = {
        'courses_data': courses_data,
        'form': StudentAssignmentForm(),
        'attendance_form': AttendanceForm(),
        'grade_form': GradeForm(),
        'message_form': MessageForm(),
        'notifications': notifications,
        'notifications_unread_count': notifications_unread_count,
        'total_students': total_students,
        'average_attendance': average_attendance,
    }
    return render(request, 'lecturer/dashboard.html', context)

@role_required(CustomUser.Role.LECTURER)
def mark_attendance(request):
    if request.method == 'POST':
        attendance_form = AttendanceForm(request.POST)
        if attendance_form.is_valid():
            enrollment = attendance_form.cleaned_data['enrollment']
            date = attendance_form.cleaned_data['date']
            present = attendance_form.cleaned_data['present']
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=date,
                defaults={'present': present}
            )
            messages.success(request, f"Attendance updated for {enrollment.student.user.get_full_name()} on {date}.")
        else:
            messages.error(request, "Please correct the errors in the attendance form.")
    return redirect('lecturer:dashboard')

@role_required(CustomUser.Role.LECTURER)
def add_grade(request):
    if request.method == 'POST':
        grade_form = GradeForm(request.POST)
        if grade_form.is_valid():
            enrollment = grade_form.cleaned_data['enrollment']
            subject_name = grade_form.cleaned_data['subject_name']
            grade_value = grade_form.cleaned_data['grade']
            Grade.objects.update_or_create(
                enrollment=enrollment,
                subject_name=subject_name,
                defaults={'grade': grade_value}
            )
            messages.success(request, f"Grade updated for {enrollment.student.user.get_full_name()} ({subject_name}).")
        else:
            messages.error(request, "Please correct the errors in the grade form.")
    return redirect('lecturer:dashboard')

@role_required(CustomUser.Role.LECTURER)
def send_message(request):
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            student_email = message_form.cleaned_data['student_email']
            message_text = message_form.cleaned_data['message']
            try:
                student_user = CustomUser.objects.get(email=student_email, role=CustomUser.Role.STUDENT)
            except CustomUser.DoesNotExist:
                messages.error(request, "Student not found.")
            else:
                Notification.objects.create(
                    lecturer=request.user,
                    message=f"Message sent to {student_user.get_full_name()}: {message_text}"
                )
                messages.success(request, "Message sent successfully.")
        else:
            messages.error(request, "Please correct the errors in the message form.")
    return redirect('lecturer:dashboard')

@role_required(CustomUser.Role.LECTURER)
def lecturer_profile(request):
    user = request.user
    return render(request, 'lecturer/profile.html', {'user': user})

@role_required(CustomUser.Role.LECTURER)
def lecturer_profile_update(request):
    user = request.user
    if request.method == 'POST':
        form = LecturerProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('lecturer:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LecturerProfileUpdateForm(instance=user)

    return render(request, 'lecturer/profile_update.html', {'form': form})

@role_required(CustomUser.Role.LECTURER)
def student_achievements(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    achievements = StudentAchievement.objects.filter(student=student).order_by('-date_awarded')
    context = {
        'student': student,
        'achievements': achievements,
    }
    return render(request, 'lecturer/student_achievements.html', context)

@role_required(CustomUser.Role.LECTURER)
def student_disciplinary_actions(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    disciplinary_actions = DisciplinaryAction.objects.filter(student=student).order_by('-date')
    context = {
        'student': student,
        'disciplinary_actions': disciplinary_actions,
    }
    return render(request, 'lecturer/student_disciplinary_actions.html', context)

@role_required(CustomUser.Role.LECTURER)
def student_full_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    context = {
        'student': student,
    }
    return render(request, 'lecturer/student_full_details.html', context)

@role_required(CustomUser.Role.LECTURER)
def update_student_activity(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.latest_activity = timezone.now()
    student.save(update_fields=['latest_activity'])
    messages.success(request, f"Updated latest activity for {student.user.get_full_name()}.")
    return redirect('lecturer:student_full_details', student_id=student.id)
