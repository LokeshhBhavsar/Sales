
import uuid

from django.db import models

from apps.hrms.models.attendance_import import AttendanceImport
from apps.hrms.models.employee import Employee


class AttendanceImportRow(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False
        )

    attendance_import = models.ForeignKey(
        AttendanceImport,
        on_delete=models.CASCADE,
        related_name="rows"
    )

    row_number = models.PositiveIntegerField()

    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_import_rows"
    )

    employee_code = models.CharField(
        max_length=100,
        blank=True
    )

    attendance_date = models.DateField(
        null=True,
        blank=True
    )

    check_in = models.DateTimeField(
        null=True,
        blank=True
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    error_message = models.TextField(
        blank=True
    )

    class Meta:
        db_table = "hrms_attendance_import_rows"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "attendance_import",
                    "row_number"
                ],
                name="unique_attendance_import_row"
            )
        ]

    def __str__(self):
        return (
            f"{self.attendance_import.file_name} - "
            f"Row {self.row_number}"
        )

