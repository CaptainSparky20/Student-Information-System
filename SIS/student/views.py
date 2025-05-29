from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import CustomUser
from accounts.forms import StudentProfileUpdateForm
from core.models import Enrollment, Grade, Attendance, Course, Student
from django.utils.dateparse import parse_date
from django.utils import timezone

@role_required(CustomUser.Role.STUDENT)
def student_dashboard(request):
    """
    Student dashboard showing enrolled courses, grades, and attendance summary.
    Also updates latest activity timestamp.
    """
    # Update latest activity
    try:
        student = Student.objects.get(user=request.user)
        student.latest_activity = timezone.now()
        student.save(update_fields=['latest_activity'])
    except Student.DoesNotExist:
        pass

    enrollments = Enrollment.objects.filter(student__user=request.user).select_related('course')

    courses_data = []
    for enrollment in enrollments:
        course = enrollment.course
        grades = Grade.objects.filter(enrollment=enrollment)
        attendance_records = Attendance.objects.filter(enrollment=enrollment)
        total_attendance = attendance_records.count()
        present_attendance = attendance_records.filter(status='present').count()  # Updated for status field
        attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0

        courses_data.append({
            'course': course,
            'grades': grades,
            'attendance_percentage': round(attendance_percentage, 2),
        })

    context = {
        'courses_data': courses_data,
    }
    return render(request, 'student/dashboard.html', context)


@role_required(CustomUser.Role.STUDENT)
def attendance_detail(request, course_id):
    """
    Show detailed attendance records for a specific course,
    with optional date filtering and attendance summary.
    """
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student__user=request.user, course=course)

    attendance_qs = Attendance.objects.filter(enrollment=enrollment).order_by('date')

    # Date range filter from GET parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    if start_date:
        attendance_qs = attendance_qs.filter(date__gte=start_date)
    if end_date:
        attendance_qs = attendance_qs.filter(date__lte=end_date)

    total_classes = attendance_qs.count()
    attended_classes = attendance_qs.filter(status='present').count()  # Updated for status field
    absences = attendance_qs.filter(status='absent').count()
    attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0

    context = {
        'course': course,
        'attendance_records': attendance_qs,
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'absences': absences,
        'attendance_percentage': round(attendance_percentage, 2),
    }
    return render(request, 'student/attendance_detail.html', context)


@login_required
@role_required(CustomUser.Role.STUDENT)
def student_profile(request):
    """
    Display the student profile page.
    Also updates latest activity timestamp.
    """
    try:
        student = Student.objects.get(user=request.user)
        student.latest_activity = timezone.now()
        student.save(update_fields=['latest_activity'])
    except Student.DoesNotExist:
        pass

    user = request.user
    return render(request, 'student/profile.html', {'user': user})


@login_required
@role_required(CustomUser.Role.STUDENT)
def student_profile_update(request):
    """
    Allow students to update their profile information including profile picture.
    """
    user = request.user

    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, request.FILES, instance=user)  # Accept files
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('student:profile_update')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentProfileUpdateForm(instance=user)

    return render(request, 'student/profile_update.html', {'form': form})
