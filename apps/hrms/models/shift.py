
import uuid

from django.db import models

from apps.masters.models.company import Company
from apps.masters.models.plant import Plant


class Shift(models.Model):

    SHIFT_TYPE_CHOICES = (
        ("fixed", "Fixed"),
        ("flexible", "Flexible"),
    )

    id = models.UUIDField(
                primary_key=True,
                default=uuid.uuid4,
                editable=False
            )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="hrms_shifts"
    )

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name="hrms_shifts"
    )

    name = models.CharField(
        max_length=100
    )

    code = models.CharField(
        max_length=50
    )

    shift_type = models.CharField(
        max_length=20,
        choices=SHIFT_TYPE_CHOICES,
        default="fixed"
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    grace_minutes = models.PositiveIntegerField(
        default=15
    )

    break_minutes = models.PositiveIntegerField(
        default=60
    )

    minimum_work_minutes = models.PositiveIntegerField(
        default=480
    )

    overtime_after_minutes = models.PositiveIntegerField(
        default=480
    )

    is_overnight = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "hrms_shifts"

        constraints = [
            models.UniqueConstraint(
                fields=["plant", "code"],
                name="unique_shift_code_per_plant"
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

