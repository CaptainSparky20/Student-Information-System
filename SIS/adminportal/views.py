from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import role_required
from accounts.models import CustomUser
from .forms import (
    AdminProfileForm, LecturerCreationForm,
    StudentUpdateForm, StudentProfileUpdateForm,
    AssignLecturersForm, CourseForm, DepartmentForm
)
from core.models import Department, Course, Lecturer, Student, Enrollment
import csv
from django.http import HttpResponse


# ----- DASHBOARD -----
@role_required(CustomUser.Role.ADMIN)
def admin_dashboard(request):
    # Stats
    total_lecturers = CustomUser.objects.filter(role=CustomUser.Role.LECTURER).count()
    total_students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT).count()
    total_courses = Course.objects.count()
    total_users = CustomUser.objects.count()
    context = {
        'total_lecturers': total_lecturers,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_users': total_users,
    }
    return render(request, 'adminportal/admin_dashboard.html', context)

# ----- ADMIN PROFILE -----
@role_required(CustomUser.Role.ADMIN)
def admin_profile(request):
    # Display admin details (profile page)
    return render(request, 'adminportal/profile.html', {'user': request.user})

@role_required(CustomUser.Role.ADMIN)
def admin_profile_update(request):
    # Update admin details (profile edit page)
    admin_user = request.user
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, request.FILES, instance=admin_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.", extra_tags='admin_profile')
            return redirect('adminportal:profile_update')
        else:
            messages.error(request, "Please correct the errors below.", extra_tags='admin_profile')
    else:
        form = AdminProfileForm(instance=admin_user)
    return render(request, 'adminportal/admin_profile_update.html', {'form': form})

# ----- LECTURERS -----

def lecturer_list(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department')
    lecturers = Lecturer.objects.select_related('user__department').prefetch_related('courses')

    if query:
        lecturers = lecturers.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
    if department_id:
        lecturers = lecturers.filter(user__department_id=department_id)
    departments = Department.objects.all()
    return render(request, 'adminportal/lecturer_list.html', {
        'lecturers': lecturers,
        'departments': departments,
    })


@role_required(CustomUser.Role.ADMIN)
def add_lecturer(request):
    if request.method == 'POST':
        form = LecturerCreationForm(request.POST, request.FILES)
        if form.is_valid():
            lecturer = form.save(commit=False)
            lecturer.role = CustomUser.Role.LECTURER
            lecturer.save()
            form.save_m2m()
            messages.success(request, "Lecturer added successfully.", extra_tags='lecturer')
            return redirect('adminportal:lecturer_list')
        else:
            messages.error(request, "Please correct the errors in the lecturer form.", extra_tags='lecturer')
    else:
        form = LecturerCreationForm()
    return render(request, 'adminportal/add_lecturer.html', {
        'lecturer_form': form,
        'departments': Department.objects.all(),
        'courses': Course.objects.all(),
    })

# ----- EXPORT LECTURERS -----

def export_lecturers(request):
    # Use user__department, NOT department
    lecturers = Lecturer.objects.select_related('user__department').prefetch_related('courses')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lecturers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Department', 'Courses'])
    for lecturer in lecturers:
        user = lecturer.user
        name = user.get_full_name()
        email = user.email
        phone = user.phone_number or "-"
        department = user.department.name if user.department else "-"
        courses = ', '.join([course.name for course in lecturer.courses.all()])
        writer.writerow([name, email, phone, department, courses])

    return response
# ----- STUDENTS -----
@role_required(CustomUser.Role.ADMIN)
def student_list(request):
    query = request.GET.get('q', '')
    course_id = request.GET.get('course')
    department_id = request.GET.get('department')
    students = CustomUser.objects.filter(role=CustomUser.Role.STUDENT)
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    if department_id:
        students = students.filter(department_id=department_id)
    if course_id:
        students = students.filter(student__enrollment__course_id=course_id).distinct()
    return render(request, 'adminportal/student_list.html', {
        'students': students,
        'courses': Course.objects.all(),
        'departments': Department.objects.all(),
    })

@role_required(CustomUser.Role.ADMIN)
def add_student(request):
    departments = Department.objects.all()
    courses = Course.objects.all()
    if request.method == 'POST':
        # Collect fields
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        registration_number = request.POST.get('registration_number')
        department_id = request.POST.get('department')
        course_id = request.POST.get('course')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        profile_picture = request.FILES.get('profile_picture')
        # Validate
        if not all([first_name, last_name, email, password, registration_number, department_id, course_id]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'adminportal/add_student.html', {
                'departments': departments, 'courses': courses
            })
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "A user with this email already exists.")
            return render(request, 'adminportal/add_student.html', {
                'departments': departments, 'courses': courses
            })
        student_user = CustomUser.objects.create_user(
            email=email, password=password,
            first_name=first_name, last_name=last_name,
            role=CustomUser.Role.STUDENT, department_id=department_id,
        )
        student_profile = Student.objects.get(user=student_user)
        student_profile.registration_number = registration_number
        student_profile.phone_number = phone_number
        student_profile.address = address
        student_profile.date_of_birth = date_of_birth
        if profile_picture:
            student_profile.profile_picture.save(profile_picture.name, profile_picture)
        student_profile.save()
        Enrollment.objects.create(student=student_profile, course_id=course_id)
        messages.success(request, f"Student {student_user.get_full_name()} added and enrolled successfully.")
        return redirect('adminportal:student_list')
    return render(request, 'adminportal/add_student.html', {
        'departments': departments, 'courses': courses
    })

@role_required(CustomUser.Role.ADMIN)
def student_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk, role=CustomUser.Role.STUDENT)
    student_profile = user.student
    enrollments = student_profile.enrollment_set.select_related('course')
    return render(request, 'adminportal/student_detail.html', {
        'user': user,
        'student_profile': student_profile,
        'enrollments': enrollments,
    })

@role_required(CustomUser.Role.ADMIN)
def student_edit(request, pk):
    user = get_object_or_404(CustomUser, pk=pk, role=CustomUser.Role.STUDENT)
    student_profile = user.student
    if request.method == 'POST':
        user_form = StudentUpdateForm(request.POST, instance=user)
        profile_form = StudentProfileUpdateForm(request.POST, request.FILES, instance=student_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Student information updated successfully.")
            return redirect('adminportal:student_detail', pk=pk)
    else:
        user_form = StudentUpdateForm(instance=user)
        profile_form = StudentProfileUpdateForm(instance=student_profile)
    return render(request, 'adminportal/student_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
    })

# ----- STAFF -----
@role_required(CustomUser.Role.ADMIN)
def staff_list(request):
    staff_users = CustomUser.objects.filter(role=CustomUser.Role.STAFF).order_by('last_name', 'first_name')
    return render(request, 'adminportal/staff_list.html', {'staff_users': staff_users})

@role_required(CustomUser.Role.ADMIN)
def add_staff(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.role = CustomUser.Role.STAFF
            staff.save()
            messages.success(request, "Staff added successfully.", extra_tags='staff')
            return redirect('adminportal:staff_list')
        else:
            messages.error(request, "Please correct the errors in the staff form.", extra_tags='staff')
    else:
        form = CustomUserCreationForm()
    return render(request, 'adminportal/add_staff.html', {'staff_form': form})

# ----- COURSE MANAGEMENT -----
@role_required(CustomUser.Role.ADMIN)
def course_list(request):
    courses = Course.objects.all().order_by('name')
    return render(request, 'adminportal/course_list.html', {'courses': courses})

@role_required(CustomUser.Role.ADMIN)
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully.")
            return redirect('adminportal:course_list')
    else:
        form = CourseForm()
    return render(request, 'adminportal/add_course.html', {'form': form})

@role_required(CustomUser.Role.ADMIN)
def assign_lecturer_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = AssignLecturersForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Lecturers assigned to course successfully.")
            return redirect('adminportal:course_list')
    else:
        form = AssignLecturersForm(instance=course)
    return render(request, 'adminportal/assign_lecturer_course.html', {
        'course': course,
        'form': form
    })
# ----- EDIT COURSE -----
@role_required(CustomUser.Role.ADMIN)
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect('adminportal:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'adminportal/edit_course.html', {'form': form, 'course': course})

# ----- EXPORT COURSES -----
@role_required(CustomUser.Role.ADMIN)
def export_courses(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="courses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Code', 'Lecturers', 'Classroom'])

    for course in Course.objects.all():
        lecturers = ', '.join(str(l) for l in course.lecturers.all())
        writer.writerow([course.name, course.code, lecturers, course.classroom])

    return response

# ----- DEPARTMENT MANAGEMENT -----
@role_required(CustomUser.Role.ADMIN)
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'adminportal/department_list.html', {'departments': departments})

@role_required(CustomUser.Role.ADMIN)
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department added successfully.")
            return redirect('adminportal:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'adminportal/add_department.html', {'form': form})
