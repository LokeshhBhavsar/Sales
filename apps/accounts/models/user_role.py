import uuid

from django.conf import settings
from django.db import models

from .role import Role


class UserRole(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_roles"
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        db_table = "user_roles"

        unique_together = (
            "user",
            "role"
        )