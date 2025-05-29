# core/forms.py
from django import forms
from .models import StudentAchievement, DisciplinaryAction

class StudentAchievementForm(forms.ModelForm):
    class Meta:
        model = StudentAchievement
        fields = ['title', 'description', 'date_awarded']

class DisciplinaryActionForm(forms.ModelForm):
    class Meta:
        model = DisciplinaryAction
        fields = ['action', 'description', 'date']
