from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'student'

def redirect_to_unified_login(request):
    return redirect('accounts:login')

urlpatterns = [
    path('login/', redirect_to_unified_login, name='login'),  # Redirect old login URL
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('attendance/<int:course_id>/', views.attendance_detail, name='attendance_detail'),
    path('profile/', views.student_profile, name='profile'),  # <-- Added profile URL
    path('profile/update/', views.student_profile_update, name='profile_update'),
]
