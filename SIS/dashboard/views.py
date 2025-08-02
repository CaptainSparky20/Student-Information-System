from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import CustomUser
from core.models import Course, Lecturer, Student, Enrollment, Attendance, Grade, DisciplinaryAction
from notifications.models import Notification
from django.utils import timezone
from datetime import date

# ========== Unified Dashboard ==========

@login_required
def unified_dashboard(request):
    user = request.user
    context = {}
    
    if user.role == CustomUser.Role.ADMIN:
        # Admin dashboard stats
        context.update({
            'total_lecturers': CustomUser.objects.filter(role=CustomUser.Role.LECTURER).count(),
            'total_students': CustomUser.objects.filter(role=CustomUser.Role.STUDENT).count(),
            'total_courses': Course.objects.count(),
            'total_users': CustomUser.objects.count(),
        })
    elif user.role == CustomUser.Role.LECTURER:
        # Lecturer dashboard context
        try:
            lecturer = Lecturer.objects.get(user=user)
        except Lecturer.DoesNotExist:
            return redirect('accounts:login')  # Or show an error page
        
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
        notifications = Notification.objects.filter(lecturer=user, is_read=False)
        notifications_unread_count = notifications.count()

        context.update({
            'courses_data': courses_data,
            'notifications': notifications,
            'notifications_unread_count': notifications_unread_count,
            'total_students': total_students,
            'average_attendance': average_attendance,
            'todays_attendance_count': todays_attendance_count,
        })
    elif user.role == CustomUser.Role.STUDENT:
        # Student dashboard context
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

        # Get disciplinary actions for the student
        if student:
            disciplinary_actions = DisciplinaryAction.objects.filter(student=student).order_by('-date')
        else:
            disciplinary_actions = []

        context.update({
            'courses_data': courses_data,
            'disciplinary_actions': disciplinary_actions,
        })

    else:
        return redirect('accounts:login')

    context["profile_url_name"] = "dashboard:profile"
    return render(request, "dashboard/dashboard.html", context)

# ========== Unified Profile View ==========

@login_required
def profile_view(request):
    user = request.user
    context = {
        "profile_url_name": "dashboard:profile",
    }
    # You can add more context here if needed per role
    return render(request, "dashboard/profile.html", context)

# ========== Unified Profile Update View ==========

@login_required
def profile_update(request):
    user = request.user
    # Select the correct form for each user type
    if user.role == CustomUser.Role.ADMIN:
        from .forms import AdminProfileForm
        form_class = AdminProfileForm
    elif user.role == CustomUser.Role.LECTURER:
        from .forms import LecturerProfileUpdateForm
        form_class = LecturerProfileUpdateForm
    else:
        from .forms import StudentProfileUpdateForm
        form_class = StudentProfileUpdateForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('dashboard:profile_update')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = form_class(instance=user)
    context = {
        "profile_url_name": "dashboard:profile",
        "form": form,
    }
    return render(request, "dashboard/profile_update.html", context)
