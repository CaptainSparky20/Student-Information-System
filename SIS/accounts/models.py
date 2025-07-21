from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from core.models import Department
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        LECTURER = 'LECTURER', 'Lecturer'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    department = models.ForeignKey(
    Department,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='users'
)

    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Added profile_picture field
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, blank=True, null=True)



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.email

# Proxy model for Lecturers
class LecturerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=CustomUser.Role.LECTURER)

class Lecturer(CustomUser):
    objects = LecturerManager()

    class Meta:
        proxy = True
        verbose_name = 'Lecturer'
        verbose_name_plural = 'Lecturers'

# Proxy model for Students
class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=CustomUser.Role.STUDENT)

class Student(CustomUser):
    objects = StudentManager()

    class Meta:
        proxy = True
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


