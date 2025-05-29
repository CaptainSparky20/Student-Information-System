from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views

app_name = 'lecturer'  # Namespace for URL reversing

def redirect_to_unified_login(request):
    return redirect('accounts:login')

urlpatterns = [
    # Redirect legacy login URL to unified login page
    path('login/', redirect_to_unified_login, name='login'),

    # Lecturer dashboard and profile management
    path('dashboard/', views.lecturer_dashboard, name='dashboard'),
    path('profile/', views.lecturer_profile, name='profile'),  # View profile
    path('profile/update/', views.lecturer_profile_update, name='profile_update'),  # Update profile

    # Logout handled by Django auth, redirecting to unified login
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),

    # Interactive features
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('add-grade/', views.add_grade, name='add_grade'),
    path('send-message/', views.send_message, name='send_message'),

    # Student-specific features
    path('students/<int:student_id>/achievements/', views.student_achievements, name='student_achievements'),
    path('students/<int:student_id>/disciplinary-actions/', views.student_disciplinary_actions, name='student_disciplinary_actions'),
    path('students/<int:student_id>/full-details/', views.student_full_details, name='student_full_details'),
    path('students/<int:student_id>/update-activity/', views.update_student_activity, name='update_student_activity'),

    # Optional calendar feature
    # path('calendar/', views.lecturer_calendar, name='calendar'),
]
