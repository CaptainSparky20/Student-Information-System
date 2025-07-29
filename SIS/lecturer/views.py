# Standard library imports
import csv
from datetime import date, datetime, timedelta

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.contrib.auth.decorators import login_required

# App/model imports
from core.models import (
    Lecturer, Course, Enrollment, Attendance,
    Student, StudentAchievement, DisciplinaryAction
)
from accounts.models import CustomUser
from accounts.decorators import role_required
from accounts.forms import LecturerProfileUpdateForm
from notifications.models import Notification
from .forms import AttendanceForm, MessageForm


@role_required(CustomUser.Role.LECTURER)
def lecturer_dashboard(request):
    try:
        lecturer = Lecturer.objects.get(user=request.user)
    except Lecturer.DoesNotExist:
        raise Http404("Lecturer profile not found.")

    courses = Course.objects.filter(lecturers=lecturer)

    courses_data = []
    attendance_values = []
    total_students = 0

    # --- Count today's attendance ---
    today = date.today()
    todays_attendance_count = Attendance.objects.filter(
        enrollment__course__in=courses,
        date=today
    ).count()

    for course in courses:
        enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
        students_info = []

        for enrollment in enrollments:
            attendance_records = Attendance.objects.filter(enrollment=enrollment)
            total_attendance = attendance_records.count()
            present_attendance = attendance_records.filter(status='present').count()
            attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0

            students_info.append({
                'student': enrollment.student,
                'email': enrollment.student.user.email,
                'full_name': enrollment.student.user.get_full_name(),
                'date_enrolled': enrollment.date_enrolled,
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
        'notifications': notifications,
        'notifications_unread_count': notifications_unread_count,
        'total_students': total_students,
        'average_attendance': average_attendance,
        'todays_attendance_count': todays_attendance_count,  # <-- THIS enables your dashboard card!
    }
    return render(request, 'lecturer/dashboard.html', context)

@role_required(CustomUser.Role.LECTURER)
def mark_attendance(request):
    # Not used for bulk anymore, keep for compatibility or remove if not needed.
    if request.method == 'POST':
        attendance_form = AttendanceForm(request.POST)
        if attendance_form.is_valid():
            enrollment = attendance_form.cleaned_data['enrollment']
            date_value = attendance_form.cleaned_data['date']
            status = attendance_form.cleaned_data['status']
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=date_value,
                defaults={'status': status}
            )
            messages.success(request, f"Attendance updated for {enrollment.student.user.get_full_name()} on {date_value}.")
        else:
            messages.error(request, "Please correct the errors in the attendance form.")
    return redirect('lecturer:dashboard')

@role_required(CustomUser.Role.LECTURER)
def mark_individual_attendance(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            date_value = form.cleaned_data['date']
            status = form.cleaned_data['status']
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                date=date_value,
                defaults={'status': status}
            )
            messages.success(request, f"Attendance recorded for {enrollment.student.user.get_full_name()} on {date_value}.")
            return redirect('lecturer:attendance_list')
    else:
        form = AttendanceForm(initial={'enrollment': enrollment})

    return render(request, 'lecturer/mark_attendance.html', {
        'form': form,
        'enrollment': enrollment
    })

@role_required(CustomUser.Role.LECTURER)
def attendance_list(request):
    lecturer = get_object_or_404(Lecturer, user=request.user)
    courses = Course.objects.filter(lecturers=lecturer)
    enrollments = Enrollment.objects.filter(course__in=courses).select_related('student__user', 'course')
    today = date.today()
    selected_date = request.POST.get('date') or request.GET.get('date') or today.isoformat()

    # Parse selected date safely
    try:
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except Exception:
        selected_date_obj = today

    # Attach attendance status for the selected date
    att_map = {att.enrollment_id: att for att in Attendance.objects.filter(
        enrollment__in=enrollments, date=selected_date_obj
    )}
    for enroll in enrollments:
        att = att_map.get(enroll.id)
        enroll.attendance_selected_date = att.status if att else None

    if request.method == "POST":
        # Individual mark
        single_enrollment_id = request.POST.get('single_enrollment_id')
        single_status = request.POST.get('single_status')
        if single_enrollment_id:
            try:
                enrollment = enrollments.get(id=single_enrollment_id)
                if single_status in ['present', 'absent']:
                    Attendance.objects.update_or_create(
                        enrollment=enrollment,
                        date=selected_date_obj,
                        defaults={'status': single_status}
                    )
                    messages.success(request, f"Attendance for {enrollment.student.user.get_full_name()} on {selected_date_obj} set as {single_status.capitalize()}.")
                else:
                    messages.error(request, "Please select Present/Absent before marking.")
            except Enrollment.DoesNotExist:
                messages.error(request, "Enrollment not found.")
            return redirect('lecturer:attendance_list')

        # Bulk submission
        updated = 0
        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.id}')
            if status in ['present', 'absent']:
                Attendance.objects.update_or_create(
                    enrollment=enrollment,
                    date=selected_date_obj,
                    defaults={'status': status}
                )
                updated += 1
        if updated:
            messages.success(request, f"Bulk attendance recorded for {updated} students for {selected_date_obj}.")
        else:
            messages.warning(request, "No attendance was marked.")
        return redirect('lecturer:attendance_list')

    context = {
        'enrollments': enrollments,
        'today': today.isoformat(),
        'selected_date': selected_date_obj.isoformat(),
    }
    return render(request, 'lecturer/attendance_list.html', context)

from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.db.models import Q

@role_required(CustomUser.Role.LECTURER)
def attendance_history(request):
    lecturer = get_object_or_404(Lecturer, user=request.user)
    courses = Course.objects.filter(lecturers=lecturer)
    attendance_list = None
    selected_course = None
    selected_date = date.today()

    if request.method == "POST":
        course_id = request.POST.get('course')
        date_str = request.POST.get('date')
        monthly = request.POST.get('monthly')
        if date_str:
            from django.utils.dateparse import parse_date
            selected_date = parse_date(date_str) or date.today()
        if course_id:
            try:
                selected_course = Course.objects.get(id=course_id)
                if monthly:
                    # Get all attendance for that month
                    month_start = selected_date.replace(day=1)
                    if selected_date.month == 12:
                        next_month = selected_date.replace(year=selected_date.year+1, month=1, day=1)
                    else:
                        next_month = selected_date.replace(month=selected_date.month+1, day=1)
                    month_end = next_month - timedelta(days=1)
                    attendance_list = Attendance.objects.filter(
                        enrollment__course=selected_course,
                        date__range=[month_start, month_end]
                    ).select_related('student__user', 'enrollment__student__user')
                else:
                    attendance_list = Attendance.objects.filter(
                        enrollment__course=selected_course,
                        date=selected_date
                    ).select_related('student__user', 'enrollment__student__user')
            except Course.DoesNotExist:
                selected_course = None

    from lecturer.forms import AttendanceHistoryFilterForm
    filter_form = AttendanceHistoryFilterForm(initial={
        'course': selected_course.id if selected_course else '',
        'date': selected_date,
    })

    context = {
        'attendance_list': attendance_list,
        'form': filter_form,
        'selected_course': selected_course,
        'selected_date': selected_date,
    }
    return render(request, 'lecturer/attendance_history.html', context)

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
    return render(request, 'lecturer/profile.html', {'user': request.user})

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
    return render(request, 'lecturer/student_achievements.html', {
        'student': student,
        'achievements': achievements,
    })

@role_required(CustomUser.Role.LECTURER)
def student_disciplinary_actions(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    disciplinary_actions = DisciplinaryAction.objects.filter(student=student).order_by('-date')
    return render(request, 'lecturer/student_disciplinary_actions.html', {
        'student': student,
        'disciplinary_actions': disciplinary_actions,
    })

@role_required(CustomUser.Role.LECTURER)
def student_full_details(request, student_id):
    # student_id is the user's id
    student = get_object_or_404(Student, user__id=student_id)
    return render(request, 'lecturer/student_full_details.html', {
        'student': student,
    })


@role_required(CustomUser.Role.LECTURER)
def update_student_activity(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.latest_activity = timezone.now()
    student.save(update_fields=['latest_activity'])
    messages.success(request, f"Updated latest activity for {student.user.get_full_name()}.")
    return redirect('lecturer:student_full_details', student_id=student.id)


class AttendanceHistoryFilterForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.none(), label="Course")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date")

    def __init__(self, *args, **kwargs):
        lecturer = kwargs.pop('lecturer')
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(lecturers=lecturer)

@role_required(CustomUser.Role.LECTURER)
def attendance_history(request):
    lecturer = get_object_or_404(Lecturer, user=request.user)
    courses = Course.objects.filter(lecturers=lecturer)
    attendance_list = None
    selected_course = None
    selected_date = None

    if request.method == 'POST':
        form = AttendanceHistoryFilterForm(request.POST, lecturer=lecturer)
        if form.is_valid():
            selected_course = form.cleaned_data['course']
            selected_date = form.cleaned_data['date']
            enrollments = Enrollment.objects.filter(course=selected_course).select_related('student__user')
            attendance_records = Attendance.objects.filter(
                enrollment__in=enrollments, date=selected_date
            ).select_related('enrollment__student__user')

            # Build a dict: enrollment_id -> attendance obj (for fast lookup)
            attendance_map = {a.enrollment_id: a for a in attendance_records}

            attendance_list = []
            for enrollment in enrollments:
                att = attendance_map.get(enrollment.id)
                attendance_list.append({
                    'student': enrollment.student,
                    'status': att.status if att else 'not marked',
                })
    else:
        form = AttendanceHistoryFilterForm(lecturer=lecturer)

    context = {
        'form': form,
        'attendance_list': attendance_list,
        'selected_course': selected_course,
        'selected_date': selected_date,
    }
    return render(request, 'lecturer/attendance_history.html', context)

@role_required(CustomUser.Role.LECTURER)
def course_student_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    students = [enrollment.student for enrollment in enrollments]
    return render(request, 'student_list.html', {'course': course, 'students': students})


@role_required(CustomUser.Role.LECTURER)
def course_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id, lecturer__user=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    today = date.today()

    # Bulk attendance for this course
    if request.method == "POST":
        updated = 0
        for enrollment in enrollments:
            status = request.POST.get(f'status_{enrollment.id}')
            if status in ['present', 'absent']:
                Attendance.objects.update_or_create(
                    enrollment=enrollment,
                    date=today,
                    defaults={'status': status}
                )
                updated += 1
        if updated:
            messages.success(request, f"Attendance recorded for {updated} students in {course.name}.")
        else:
            messages.warning(request, "No attendance was marked.")
        return redirect('lecturer:course_attendance', course_id=course.id)

    return render(request, 'lecturer/course_attendance.html', {
        'course': course,
        'enrollments': enrollments,
        'today': today,
    })

@role_required(CustomUser.Role.LECTURER)
def course_attendance_history(request, course_id):
    course = get_object_or_404(Course, id=course_id, lecturer__user=request.user)
    enrollments = Enrollment.objects.filter(course=course)
    attendance_by_date = {}

    for att in Attendance.objects.filter(enrollment__in=enrollments).select_related('enrollment__student__user').order_by('-date'):
        day = att.date
        if day not in attendance_by_date:
            attendance_by_date[day] = []
        attendance_by_date[day].append(att)

    return render(request, 'lecturer/course_attendance_history.html', {
        'course': course,
        'attendance_by_date': attendance_by_date,
    })

def student_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    students = [enrollment.student.user for enrollment in enrollments]
    return render(request, 'lecturer/student_list.html', {'students': students, 'course': course})

def student_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    students = sorted(
        [enrollment.student.user for enrollment in enrollments],
        key=lambda u: u.get_full_name().lower()
    )
    return render(request, 'lecturer/student_list.html', {'students': students, 'course': course})



def export_attendance(request):
    # Get course and date from GET parameters
    course_id = request.GET.get('course')
    date_str = request.GET.get('date')

    # Security: Only allow for logged-in lecturers with this course
    try:
        lecturer = Lecturer.objects.get(user=request.user)
    except Lecturer.DoesNotExist:
        return HttpResponse("Not authorized", status=403)

    course = Course.objects.filter(id=course_id, lecturers=lecturer).first()
    if not course:
        return HttpResponse("Course not found or access denied", status=404)

    # Convert date string from dd-mm-yyyy to date object
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
    except (ValueError, TypeError):
        return HttpResponse("Invalid date format. Use dd-mm-yyyy.", status=400)

    # Gather attendance records for the date
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')
    attendance_records = Attendance.objects.filter(
        enrollment__in=enrollments, date=date_obj
    ).select_related('enrollment__student__user')

    # Prepare response
    response = HttpResponse(content_type='text/csv')
    filename = f"attendance_{course.code}_{date_obj.strftime('%d-%m-%Y')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Email', 'Status'])

    # Build a dict: enrollment_id -> attendance
    attendance_map = {a.enrollment_id: a for a in attendance_records}

    for enrollment in enrollments:
        student = enrollment.student.user
        att = attendance_map.get(enrollment.id)
        status = att.status if att else 'not marked'
        writer.writerow([
            student.get_full_name(),
            student.email,
            status.capitalize()
        ])

    return response