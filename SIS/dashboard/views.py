from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import CustomUser
from core.models import Department, Course, Lecturer, Student, Enrollment, Attendance, Grade
from notifications.models import Notification
from django.utils import timezone
from datetime import date


# ================== Unified Dashboard View ==================
@login_required
def unified_dashboard(request):
    user = request.user
    # ... existing context code
    if user.role == "ADMIN":
        profile_url_name = "dashboard:profile"
    elif user.role == "LECTURER":
        profile_url_name = "dashboard:profile"
    else:
        profile_url_name = "dashboard:profile"
    context = {
        # ...all your dashboard context...
        "profile_url_name": profile_url_name,
    }
    return render(request, "dashboard/dashboard.html", context)

    # ================= ADMIN DASHBOARD ===================
    if user.role == CustomUser.Role.ADMIN:
        total_lecturers = CustomUser.objects.filter(role=CustomUser.Role.LECTURER).count()
        total_students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT).count()
        total_courses = Course.objects.count()
        total_users = CustomUser.objects.count()
        context = {
            'total_lecturers': total_lecturers,
            'total_students': total_students,
            'total_courses': total_courses,
            'total_users': total_users,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)

    # ================= LECTURER DASHBOARD ===================
    elif user.role == CustomUser.Role.LECTURER:
        try:
            lecturer = Lecturer.objects.get(user=user)
        except Lecturer.DoesNotExist:
            return redirect('accounts:login')
        courses = Course.objects.filter(lecturers=lecturer)
        courses_data = []
        attendance_values = []
        total_students = 0
        today = date.today()

        todays_attendance_count = Attendance.objects.filter(
            enrollment__course__in=courses,
            date=today
        ).values('enrollment__student').distinct().count()

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
        notifications = Notification.objects.filter(lecturer=user, is_read=False) if 'Notification' in globals() else []
        notifications_unread_count = notifications.count() if notifications else 0

        context = {
            'courses_data': courses_data,
            'notifications': notifications,
            'notifications_unread_count': notifications_unread_count,
            'total_students': total_students,
            'average_attendance': average_attendance,
            'todays_attendance_count': todays_attendance_count,
        }
        return render(request, 'dashboard/lecturer_dashboard.html', context)

    # ================= STUDENT DASHBOARD ===================
    elif user.role == CustomUser.Role.STUDENT:
        try:
            student = Student.objects.get(user=user)
            student.latest_activity = timezone.now()
            student.save(update_fields=['latest_activity'])
        except Student.DoesNotExist:
            student = None

        enrollments = Enrollment.objects.filter(student__user=user).select_related('course')
        courses_data = []

        for enrollment in enrollments:
            course = enrollment.course
            grades = Grade.objects.filter(enrollment=enrollment)
            attendance_records = Attendance.objects.filter(enrollment=enrollment)

            total_attendance = attendance_records.count()
            present_attendance = attendance_records.filter(status='present').count()
            attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0

            courses_data.append({
                'course': course,
                'grades': grades,
                'attendance_percentage': round(attendance_percentage, 2),
            })

        disciplinary_actions = DisciplinaryAction.objects.filter(student=student).order_by('-date') if student else []

        context = {
            'courses_data': courses_data,
            'disciplinary_actions': disciplinary_actions,
        }
        return render(request, 'dashboard/student_dashboard.html', context)

    # ================ Unknown role =====================
    return redirect('accounts:login')

# ================== Profile View and Update ==================
@login_required
def profile_view(request):
    # Build context (user, etc.) as needed for your profile page
    user = request.user
    context = {
        "profile_url_name": "dashboard:profile",  # You can adjust as needed
    }
    return render(request, "dashboard/profile.html", context)

@login_required
def profile_update(request):
    # Implement your profile update logic here
    user = request.user
    context = {
        "profile_url_name": "dashboard:profile",
    }
    return render(request, "dashboard/profile_update.html", context)
