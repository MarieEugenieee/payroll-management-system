from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy



# uploaded file path
from accounts.utils import user_directory_path


# Create your models here.
class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_employee(self, email, password, **extra_fields):
        extra_fields.setdefault('is_employee', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, password, **extra_fields)

    def get_queryset(self):
            """
            Return the queryset excluding deleted users by default.
            """
            return super().get_queryset().filter(is_deleted=False)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    is_employee = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        gettext_lazy('staff_status'), default=False,
        help_text=gettext_lazy('designates whether the user can login to this site'),
    )

    is_active = models.BooleanField(
        gettext_lazy('active'), default=True,
        help_text=gettext_lazy('designates whether the user can loin to this site'),
    )

    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email


# profile models gender choices
GENDER_OPT = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=264, blank=True)
    last_name = models.CharField(max_length=15, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_OPT, default='male')
    photo = models.ImageField(upload_to=user_directory_path, null=True, default='default/user.jpg')
    date_of_join = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.first_name+"'s profile"


class PresentAddress(models.Model):
    address_of = models.OneToOneField(User, on_delete=models.CASCADE, related_name='present_address')
    present_country = models.CharField(max_length=50)
    present_street = models.CharField(max_length=50)
    present_brgy = models.CharField(max_length=50)
    present_city = models.CharField(max_length=50)
    present_province = models.CharField(max_length=50)
    present_post_code = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.address_of}'s Present Address"


class PermanentAddress(models.Model):
    address_of = models.OneToOneField(User, on_delete=models.CASCADE, related_name='permanent_address')
    permanent_country = models.CharField(max_length=50)
    permanent_street = models.CharField(max_length=50)
    permanent_brgy = models.CharField(max_length=50)
    permanent_city = models.CharField(max_length=50)
    permanent_province = models.CharField(max_length=50)
    permanent_post_code = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.address_of}'s Permanent Address"
