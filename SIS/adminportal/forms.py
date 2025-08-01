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
        fields = ['full_name', 'short_name', 'email', 'phone_number', 'department', 'profile_picture', 'date_joined']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Full Name (as per IC)',
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Short Name (e.g. Ali)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Lecturer email address',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Phone number',
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 bg-white/10 rounded border border-white/20 text-white',
                'accept': 'image/*',
            }),
        }

# ---------- STUDENT UPDATE FORM ----------
class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'short_name', 'email', 'department']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'short_name': forms.TextInput(attrs={'class': 'form-input'}),
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

# ---------- ASSIGN LECTURERS TO CLASSGROUP FORM (ManyToMany) ----------
class AssignLecturersToClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
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
        fields = ['name', 'code', 'department', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
                'placeholder': 'Course name',
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
                'placeholder': 'Course code',
            }),
            'department': forms.Select(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 rounded bg-white/10 text-white border border-white/20',
                'placeholder': 'Course description (optional)',
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

# ---------- ADD STUDENT FORM ----------
class AddStudentForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'Enter full name'
        })
    )
    short_name = forms.CharField(
        max_length=64,
        label="Short Name",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'Enter short name (optional)'
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'student@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'Set a password'
        }),
        label="Password"
    )
    registration_number = forms.CharField(
        max_length=50,
        label="Registration Number",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'Enter registration number'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label="Department",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 focus:ring-2 focus:ring-blue-500 focus:outline-none transition'
        })
    )
    lecturer = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role=CustomUser.Role.LECTURER),
        label="Assign Lecturer",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 focus:ring-2 focus:ring-blue-500 focus:outline-none transition'
        })
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Assign to Course",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 focus:ring-2 focus:ring-blue-500 focus:outline-none transition'
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        label="Profile Picture",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 focus:ring-2 focus:ring-blue-500 focus:outline-none transition'
        })
    )
    phone_number = forms.CharField(
        required=False,
        max_length=20,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'Optional'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'Optional',
            'rows': 3
        }),
        required=False,
        label="Address"
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-3 rounded-lg bg-white/5 text-white border border-white/20 focus:ring-2 focus:ring-blue-500 focus:outline-none transition'
        }),
        required=False,
        label="Date of Birth"
    )
