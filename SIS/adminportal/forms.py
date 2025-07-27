from django import forms
from accounts.models import CustomUser
from core.models import Department, Student, Course, Lecturer

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
        fields = ['first_name', 'last_name', 'email', 'department', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your last name',
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


# ---------- LECTURER CREATION FORM ----------
class LecturerCreationForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        empty_label="Select Department",
        widget=forms.Select(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
        })
    )
    date_joined = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'department', 'profile_picture', 'date_joined']


# ---------- STUDENT UPDATE FORM ----------
class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'department']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }


# ---------- STUDENT PROFILE FORM ----------
class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['phone_number', 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }


# ---------- ASSIGN LECTURERS TO COURSE FORM (ManyToMany) ----------
class AssignLecturersForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['lecturers']
        widgets = {
            'lecturers': forms.SelectMultiple(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
            })
        }


# ---------- ADD/EDIT COURSE FORM ----------
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'lecturers', 'classroom']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
                'placeholder': 'Course name',
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
                'placeholder': 'Course code',
            }),
            'lecturers': forms.SelectMultiple(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
            }),
            'classroom': forms.TextInput(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
                'placeholder': 'Classroom',
            }),
        }


# ---------- ADD/EDIT DEPARTMENT FORM ----------
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
                'placeholder': 'Department name',
            }),
        }
