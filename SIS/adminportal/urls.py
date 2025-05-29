from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'adminportal'

def redirect_to_unified_login(request):
    return redirect('accounts:login')

urlpatterns = [
    # Redirect old login URL to unified login
    path('login/', redirect_to_unified_login, name='login'),

    # Admin main dashboard showing admin profile and links
    path('dashboard/', views.admin_dashboard, name='dashboard'),

    # Admin profile update page
    path('profile/update/', views.admin_profile_update, name='profile_update'),

    # Lecturer management pages
    path('lecturers/', views.lecturer_list, name='lecturer_list'),
    path('lecturers/add/', views.add_lecturer, name='add_lecturer'),

    # Student management pages
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
]
