from rest_framework import serializers

from apps.hrms.models.attendance import Attendance
from apps.hrms.models.attendance_log import AttendanceLog


class AttendanceLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceLog

        fields = [
            "id",
            "employee",
            "attendance",
            "punch_type",
            "punch_time",
            "source",
            "latitude",
            "longitude",
            "device_id",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class AttendanceSerializer(serializers.ModelSerializer):

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True
    )

    employee_name = serializers.SerializerMethodField()

    logs = AttendanceLogSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Attendance

        fields = [
            "id",
            "company",
            "plant",
            "employee",
            "employee_code",
            "employee_name",
            "attendance_date",
            "status",
            "InTime",
            "OutTime",
            "total_work_minutes",
            "break_minutes",
            "late_minutes",
            "early_leave_minutes",
            "overtime_minutes",
            "source",
            "remarks",
            "logs",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "total_work_minutes",
            "break_minutes",
            "late_minutes",
            "early_leave_minutes",
            "overtime_minutes",
            "created_at",
            "updated_at",
        ]

    def get_employee_name(self, obj):

        return (
            f"{obj.employee.first_name} "
            f"{obj.employee.last_name}"
        ).strip()