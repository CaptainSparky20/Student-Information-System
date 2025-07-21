from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from core.models import Department

class LecturerCreationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        required=True
    )
    date_joined = forms.DateField(
        label="Date Joined",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        required=True,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-md'})
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'password', 'department', 'phone_number', 
            'address', 'profile_picture', 'date_joined'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Lecturer Email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'placeholder': 'Address', 'rows': 3}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = CustomUser.Role.LECTURER
        if commit:
            user.save()
        return user


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({'placeholder': 'Email address'})

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'role', 'first_name', 'last_name', 'phone_number', 'address', 'department', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'readonly': 'readonly'})

class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

class LecturerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'department', 'profile_picture']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }

class UnifiedLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'w-full mb-4 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'w-full mb-6 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'
        }),
        label="Password"
    )
