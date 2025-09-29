from django.db import models


class RoleChoices(models.TextChoices):
    OWNER = "OWNER",
    ADMIN = "ADMIN",
    MEMBER = "MEMBER",
    GUEST = "GUEST",
