from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from accounts.choices import RoleChoices


class MemberManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if not extra["is_staff"] or not extra["is_superuser"]:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True")
        return self.create_user(email, password, **extra)


class Member(AbstractBaseUser, PermissionsMixin):
    # Authentication
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)

    # Profile
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    role = models.CharField(max_length=10, choices=RoleChoices.choices, default=RoleChoices.MEMBER)
    organization = models.ForeignKey(
        "orgs.Organization",
        on_delete=models.SET_NULL,
        null=True, blank=True, related_name="members"
    )

    timezone = models.CharField(max_length=64, default="UTC")
    language = models.CharField(max_length=10, default="en")
    preferences = models.JSONField(default=dict, blank=True)  # e.g. {"task_view": "kanban"}
    notification_settings = models.JSONField(default=dict, blank=True)
    # {"task_assigned": {"email": True, "push": True},
    #  "comment": {"email": True, "push": False},
    #  "mention": {"email": True, "push": True},
    #  "due_reminder": {"email": True, "push": True}}

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(null=True, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    projects_limit = models.PositiveIntegerField(null=True, blank=True)
    storage_quota_mb = models.PositiveIntegerField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = MemberManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        fn = f"{self.first_name} {self.last_name}".strip()
        return fn or self.email