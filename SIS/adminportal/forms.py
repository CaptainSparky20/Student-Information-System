from django import forms
from accounts.models import CustomUser
from django import forms
from accounts.models import CustomUser
from core.models import Department

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'department']
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
            'department': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Enter your department',
            }),
        }

class LecturerCreationForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        empty_label="Select Department"
    )
    date_joined = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'department', 'profile_picture', 'date_joined']


    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'department']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Enter first name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Enter last name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Enter email address',
            }),
            'department': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-600',
                'placeholder': 'Enter department',
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
