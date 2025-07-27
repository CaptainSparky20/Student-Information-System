from django.contrib import admin
from .models import Lecturer, Student, Course, Enrollment, Grade, Attendance, StudentAchievement, DisciplinaryAction

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture_display')
    readonly_fields = ('profile_picture_display',)

    def profile_picture_display(self, obj):
        if obj.profile_picture:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.profile_picture.url)
        return "-"
    profile_picture_display.short_description = 'Profile Picture'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture_display', 'latest_activity')
    readonly_fields = ('profile_picture_display',)

    def profile_picture_display(self, obj):
        if obj.profile_picture:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.profile_picture.url)
        return "-"
    profile_picture_display.short_description = 'Profile Picture'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_lecturers')  # add more field names as needed, e.g. 'code', 'description'


    def get_lecturers(self, obj):
        return ", ".join([str(lecturer) for lecturer in obj.lecturers.all()])
    get_lecturers.short_description = "Lecturers"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date_enrolled')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'subject_name', 'grade')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'date', 'status')

@admin.register(StudentAchievement)
class StudentAchievementAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'date_awarded')
    list_filter = ('date_awarded',)

@admin.register(DisciplinaryAction)
class DisciplinaryActionAdmin(admin.ModelAdmin):
    list_display = ('student', 'action', 'date')
    list_filter = ('date',)


from django.contrib import admin
from .models import Department

admin.site.register(Department)
