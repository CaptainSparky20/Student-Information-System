# core/forms.py
from django import forms
from .models import (
    StudentAchievement, DisciplinaryAction, Attendance, Enrollment, Student, Parent
)

class StudentAchievementForm(forms.ModelForm):
    class Meta:
        model = StudentAchievement
        fields = ['title', 'description', 'date_awarded']

class DisciplinaryActionForm(forms.ModelForm):
    class Meta:
        model = DisciplinaryAction
        fields = ['action', 'description', 'date']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'session', 'description']
        widgets = {
            'session': forms.Select(choices=Attendance.SESSION_CHOICES),
            'status': forms.Select(choices=Attendance.STATUS_CHOICES),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add notes, e.g., left early'}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'subject', 'class_group']

# --- Student Profile Edit Form with Malaysian Naming Convention ---
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            # The naming fields (get from linked user model!)
            'date_of_birth',
            'address',
            'phone_number',
            'profile_picture',
            'class_group',
            'emergency_name',
            'emergency_relation',
            'emergency_phone',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'profile_picture': forms.FileInput(),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

# --- Parent/Emergency Info Form ---
class ParentForm(forms.ModelForm):
    roles = forms.CharField(
        required=False,
        label="Relationship(s) to Student",
        help_text="Comma-separated if more than one (e.g. 'mother, guardian')."
    )

    class Meta:
        model = Parent
        fields = [
            'user',             # Usually set programmatically in views, can be hidden
            'profile_picture',
            'phone_number',
            'address',
            'occupation',
            'roles',            # Now allows multiple roles as comma-separated string
        ]
        widgets = {
            'profile_picture': forms.FileInput(),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
