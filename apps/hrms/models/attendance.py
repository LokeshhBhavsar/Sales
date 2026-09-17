
import uuid

from django.db import models

from apps.hrms.models.employee import Employee
from apps.masters.models.company import Company
from apps.masters.models.plant import Plant


class Attendance(models.Model):

    STATUS_CHOICES = (
        ("present", "Present"),
        ("absent", "Absent"),
        ("half_day", "Half Day"),
        ("leave", "Leave"),
        ("holiday", "Holiday"),
        ("weekly_off", "Weekly Off"),
        ("work_from_home", "Work From Home"),
    )

    SOURCE_CHOICES = (
        ("biometric", "Biometric"),
        ("excel", "Excel"),
        ("manual", "Manual"),
        ("regularization", "Regularization"),
        ("system", "System"),
    )

    id = models.UUIDField(
            primary_key=True,
            default=uuid.uuid4,
            editable=False
        )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    attendance_date = models.DateField()

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="absent"
    )

    InTime = models.DateTimeField(
        null=True,
        blank=True
    )

    OutTime = models.DateTimeField(
        null=True,
        blank=True
    )

    total_work_minutes = models.PositiveIntegerField(
        default=0
    )

    break_minutes = models.PositiveIntegerField(
        default=0
    )

    late_minutes = models.PositiveIntegerField(
        default=0
    )

    early_leave_minutes = models.PositiveIntegerField(
        default=0
    )

    overtime_minutes = models.PositiveIntegerField(
        default=0
    )

    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default="system"
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "hrms_attendance"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "attendance_date"
                ],
                name="unique_employee_attendance_date"
            )
        ]

        indexes = [
            models.Index(
                fields=["employee", "attendance_date"]
            ),
            models.Index(
                fields=["company", "attendance_date"]
            ),
            models.Index(
                fields=["plant", "attendance_date"]
            ),
            models.Index(
                fields=["status"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_code} - "
            f"{self.attendance_date}"
        )

