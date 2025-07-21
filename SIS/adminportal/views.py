from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import CustomUser
from .forms import AdminProfileForm, LecturerCreationForm
from core.models import Department

@role_required(CustomUser.Role.ADMIN)
def admin_dashboard(request):
    admin_user = request.user

    profile_form = AdminProfileForm(instance=admin_user)

    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = AdminProfileForm(request.POST, instance=admin_user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully.", extra_tags='admin_profile')
            return redirect('adminportal:dashboard')
        else:
            messages.error(request, "Please correct the errors in your profile form.", extra_tags='admin_profile')

    context = {
        'admin_user': admin_user,
        'profile_form': profile_form,
    }
    return render(request, 'adminportal/admin_dashboard.html', context)

@role_required(CustomUser.Role.ADMIN)
def admin_profile(request):
    """Renders the admin's profile page with their details."""
    return render(request, 'adminportal/profile.html', {'user': request.user})

@role_required(CustomUser.Role.ADMIN)
def admin_profile_update(request):
    admin_user = request.user

    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=admin_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.", extra_tags='admin_profile')
            return redirect('adminportal:profile_update')
        else:
            messages.error(request, "Please correct the errors below.", extra_tags='admin_profile')
    else:
        form = AdminProfileForm(instance=admin_user)

    return render(request, 'adminportal/admin_profile_update.html', {'form': form})

@role_required(CustomUser.Role.ADMIN)
def lecturer_list(request):
    lecturers = CustomUser.objects.filter(role=CustomUser.Role.LECTURER).order_by('last_name', 'first_name')
    return render(request, 'adminportal/lecturer_list.html', {'lecturers': lecturers})

@role_required(CustomUser.Role.ADMIN)
def add_lecturer(request):
    if request.method == 'POST':
        form = LecturerCreationForm(request.POST, request.FILES)
        if form.is_valid():
            lecturer = form.save(commit=False)
            lecturer.role = CustomUser.Role.LECTURER
            lecturer.save()
            messages.success(request, "Lecturer added successfully.", extra_tags='lecturer')
            return redirect('adminportal:lecturer_list')
        else:
            messages.error(request, "Please correct the errors in the lecturer form.", extra_tags='lecturer')
    else:
        form = LecturerCreationForm()

    return render(request, 'adminportal/add_lecturer.html', {'lecturer_form': form})


@role_required(CustomUser.Role.ADMIN)
def student_list(request):
    students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT).order_by('last_name', 'first_name')
    return render(request, 'adminportal/student_list.html', {'students': students})

@role_required(CustomUser.Role.ADMIN)
def add_student(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([first_name, last_name, email, password]):
            messages.error(request, "Please fill in all fields.", extra_tags='student')
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.", extra_tags='student')
        else:
            user = CustomUser.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=CustomUser.Role.STUDENT
            )
            messages.success(request, f"Student {user.get_full_name()} added successfully.", extra_tags='student')
            return redirect('adminportal:student_list')

    return render(request, 'adminportal/add_student.html')

@role_required(CustomUser.Role.ADMIN)
def add_lecturer(request):
    if request.method == 'POST':
        form = LecturerCreationForm(request.POST, request.FILES)
        if form.is_valid():
            lecturer = form.save(commit=False)
            lecturer.role = CustomUser.Role.LECTURER
            lecturer.save()
            messages.success(request, "Lecturer added successfully.", extra_tags='lecturer')
            return redirect('adminportal:lecturer_list')
        else:
            messages.error(request, "Please correct the errors in the lecturer form.", extra_tags='lecturer')
    else:
        form = LecturerCreationForm()

    return render(request, 'adminportal/add_lecturer.html', {'lecturer_form': form})

@role_required(CustomUser.Role.ADMIN)
def add_lecturer(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        # ... (your form processing here)
        pass
    return render(request, 'adminportal/add_lecturer.html', {
        'departments': departments,
        # add other context vars if needed
    })