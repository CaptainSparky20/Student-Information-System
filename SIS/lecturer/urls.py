from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views

app_name = 'lecturer'

def redirect_to_unified_login(request):
    return redirect('accounts:login')

urlpatterns = [
    path('login/', redirect_to_unified_login, name='login'),

    # Dashboard and profile
    path('dashboard/', views.lecturer_dashboard, name='dashboard'),
    path('profile/', views.lecturer_profile, name='profile'),
    path('profile/update/', views.lecturer_profile_update, name='profile_update'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),

    # Attendance (all courses)
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/mark/<int:enrollment_id>/', views.mark_individual_attendance, name='mark_individual_attendance'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),

    # Course-specific actions
    path('courses/<int:course_id>/students/', views.student_list, name='student_list'),  # Use only ONE view!
    path('courses/<int:course_id>/attendance/', views.course_attendance, name='course_attendance'),
    path('courses/<int:course_id>/attendance/history/', views.course_attendance_history, name='course_attendance_history'),

    # Messaging (optional)
    path('send-message/', views.send_message, name='send_message'),

    # Student-specific features
    path('students/<int:student_id>/achievements/', views.student_achievements, name='student_achievements'),
    path('students/<int:student_id>/disciplinary-actions/', views.student_disciplinary_actions, name='student_disciplinary_actions'),
    path('students/<int:student_id>/full-details/', views.student_full_details, name='student_full_details'),
    path('students/<int:student_id>/update-activity/', views.update_student_activity, name='update_student_activity'),
    path('students/<int:student_id>/full-details/', views.student_full_details, name='student_full_details'),

]
