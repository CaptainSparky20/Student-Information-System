# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import UnifiedLoginForm
from .models import CustomUser

def unified_login(request):
    if request.method == 'POST':
        form = UnifiedLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_active:
                login(request, user)
                # Redirect based on role
                if user.role == CustomUser.Role.STUDENT:
                    return redirect('student:dashboard')
                elif user.role == CustomUser.Role.LECTURER:
                    return redirect('lecturer:dashboard')
                elif user.role == CustomUser.Role.ADMIN:
                    return redirect('adminportal:dashboard')  # Adjust namespace if different
                else:
                    messages.error(request, 'User role not recognized.')
                    return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UnifiedLoginForm()
    return render(request, 'accounts/login.html', {'form': form})
