from django.conf import settings
from django.db import models
from django.utils import timezone

class Lecturer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.email

class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, related_name='courses')
    classroom = models.CharField(max_length=100, blank=True, null=True)  # Classroom location or name

    def __str__(self):
        return f"{self.name} ({self.code})"

class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    relationship_to_student = models.CharField(max_length=50, blank=True, null=True)  # Father, Mother, Guardian, etc.

    def __str__(self):
        return self.user.get_full_name() or self.user.email

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, through='Enrollment')
    parents = models.ManyToManyField(Parent, related_name='children', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # Additional full details fields
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    # Latest activity timestamp
    latest_activity = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.email

    def full_details(self):
        return {
            'name': self.user.get_full_name(),
            'email': self.user.email,
            'dob': self.date_of_birth,
            'address': self.address,
            'phone': self.phone_number,
            'profile_picture_url': self.profile_picture.url if self.profile_picture else None,
        }

    def update_latest_activity(self):
        self.latest_activity = timezone.now()
        self.save(update_fields=['latest_activity'])

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=255)
    grade = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.enrollment.student} - {self.subject_name}: {self.grade}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = ('enrollment', 'date')

    def __str__(self):
        return f"{self.enrollment.student} - {self.date} - {self.status.capitalize()}"

class StudentAchievement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_awarded = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.student}: {self.title}"

class DisciplinaryAction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='disciplinary_actions')
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.student}: {self.action} on {self.date}"
    
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
