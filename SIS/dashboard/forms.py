from django import forms
from accounts.models import CustomUser
from core.models import Department, Student, Course, Subject, ClassGroup, Lecturer

# ---------- ADMIN PROFILE FORM ----------
class AdminProfileForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
        })
    )
    class Meta:
        model = CustomUser
        fields = ['full_name', 'short_name', 'email', 'department', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your full name',
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your short name (e.g. Ali)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 bg-gray-100 cursor-not-allowed',
                'readonly': 'readonly',
                'placeholder': 'Your email address',
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 bg-white/10 rounded border border-white/20 text-white',
                'accept': 'image/*',
            }),
        }