from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication."""

    def _create_user(self, email, password=None, **extra_fields):
        """Handles the common logic for user creation."""
        if not email:
            raise ValueError(_("The Email field is required"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)


ROLE_ACCOUNTANT = 'accountant'
ROLE_SPECIALIST = 'specialist'
ROLE_DIRECTOR = 'director'
ROLE_CHAIRMAN = 'chairman'


class User(AbstractUser):
    ROLE_CHOICES = (
        (ROLE_SPECIALIST, 'Специалист'),
        (ROLE_DIRECTOR, 'Генеральный директор'),
        (ROLE_CHAIRMAN, 'Председатель'),
        (ROLE_ACCOUNTANT, 'Бухгалтер'),
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия'
    )
    patronymic = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Отчество'
    )
    email = models.EmailField(
        _("email address"),
        validators=[EmailValidator(_("Enter a valid email address."))],
        unique=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        verbose_name='Роль'
    )

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
