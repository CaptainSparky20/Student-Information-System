from django import forms
from accounts.models import CustomUser
from core.models import Course, Student, Enrollment  # Import Enrollment for forms below

class LecturerLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter your email',
        }),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter your password',
        }),
        label="Password"
    )

class LecturerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'short_name', 'department', 'phone_number', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your full name',
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your short name (e.g. Ali)',
            }),
            'department': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your phone number',
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your address',
                'rows': 3,
            }),
        }

class LecturerCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
            'placeholder': 'Enter password',
        }),
        label='Password'
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'short_name', 'email', 'department']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Enter full name (as per IC)',
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Enter short name (e.g. Ali)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Enter email address',
            }),
            'department': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.LECTURER
        user.is_staff = False  # Adjust if lecturers should have staff access
        user.is_active = True
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class StudentAssignmentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
        }),
        label="Student"
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
        }),
        label="Course"
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Enter department (optional)',
        }),
        label="Department"
    )

class AttendanceForm(forms.Form):
    enrollment = forms.ModelChoiceField(
        queryset=Enrollment.objects.all(),
        widget=forms.HiddenInput()
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600'}),
        label="Date"
    )
    present = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        label="Present"
    )

class GradeForm(forms.Form):
    enrollment = forms.ModelChoiceField(
        queryset=Enrollment.objects.all(),
        widget=forms.HiddenInput()
    )
    subject_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Subject name',
        }),
        label="Subject Name"
    )
    grade = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Grade',
        }),
        label="Grade"
    )

class MessageForm(forms.Form):
    student_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Student email',
        }),
        label="Student Email"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
            'placeholder': 'Type your message here...',
            'rows': 4,
        }),
        label="Message"
    )

class AttendanceHistoryFilterForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(), required=False, label="Course",
        widget=forms.Select(attrs={'class': 'text-white bg-gray-800 rounded p-2'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'text-white bg-gray-800 rounded p-2'}),
        required=False, label="Date"
    )

    def __init__(self, *args, **kwargs):
        courses = kwargs.pop('courses', None)
        super().__init__(*args, **kwargs)
        if courses is not None:
            self.fields['course'].queryset = courses
