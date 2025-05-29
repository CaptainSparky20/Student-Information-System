from django.contrib import admin
from accounts.models import Lecturer, Student

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'department']
    search_fields = ['email', 'first_name', 'last_name', 'department']
    ordering = ['last_name', 'first_name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['last_name', 'first_name']
