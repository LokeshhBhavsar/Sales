from datetime import datetime, timedelta
from django.db import models, transaction
from django.utils import timezone
from django.utils import timezone

from apps.hrms.models.employee import Employee
from apps.hrms.models.attendance import Attendance
from apps.hrms.models.attendance_log import AttendanceLog
from apps.hrms.models.employee_shift import EmployeeShift


class AttendanceService:

    @staticmethod
    def get_employee_shift(employee, attendance_date):

        return (
            EmployeeShift.objects
            .filter(
                employee=employee,
                effective_from__lte=attendance_date,
                is_active=True,
            )
            .filter(
                models.Q(effective_to__isnull=True)
                | models.Q(
                    effective_to__gte=attendance_date
                )
            )
            .select_related("shift")
            .order_by("-effective_from")
            .first()
        )

    @staticmethod
    @transaction.atomic
    def create_or_update_attendance(
        employee,
        attendance_date,
        check_in=None,
        check_out=None,
        source="system",
        remarks=""
    ):

        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            attendance_date=attendance_date,
            defaults={
                "company": employee.company,
                "plant": employee.plant,
                "source": source,
                "status": "absent",
            }
        )

        if check_in:

            if (
                attendance.check_in is None
                or check_in < attendance.check_in
            ):
                attendance.check_in = check_in

        if check_out:

            if (
                attendance.check_out is None
                or check_out > attendance.check_out
            ):
                attendance.check_out = check_out

        attendance.source = source

        if remarks:
            attendance.remarks = remarks

        AttendanceService.calculate_attendance(
            attendance
        )

        attendance.save()

        return attendance

    @staticmethod
    def calculate_attendance(attendance):

        if not attendance.check_in:

            attendance.status = "absent"
            attendance.total_work_minutes = 0

            return attendance

        if not attendance.check_out:

            attendance.status = "present"
            attendance.total_work_minutes = 0

            return attendance

        total_seconds = (
            attendance.check_out -
            attendance.check_in
        ).total_seconds()

        total_minutes = max(
            int(total_seconds / 60),
            0
        )

        attendance.total_work_minutes = total_minutes

        # Get employee shift
        shift_assignment = (
            EmployeeShift.objects
            .filter(
                employee=attendance.employee,
                effective_from__lte=attendance.attendance_date,
                is_active=True,
            )
            .filter(
                models.Q(effective_to__isnull=True)
                | models.Q(
                    effective_to__gte=
                    attendance.attendance_date
                )
            )
            .select_related("shift")
            .order_by("-effective_from")
            .first()
        )

        if not shift_assignment:

            attendance.status = "present"

            return attendance

        shift = shift_assignment.shift

        # ------------------------------------------
        # Calculate late
        # ------------------------------------------

        shift_start = datetime.combine(
            attendance.attendance_date,
            shift.start_time
        )

        shift_start = timezone.make_aware(
            shift_start
        )

        grace_time = shift_start + timedelta(
            minutes=shift.grace_minutes
        )

        if attendance.check_in > grace_time:

            attendance.late_minutes = int(
                (
                    attendance.check_in -
                    grace_time
                ).total_seconds() / 60
            )

        else:

            attendance.late_minutes = 0

        # ------------------------------------------
        # Calculate early leave
        # ------------------------------------------

        shift_end_date = attendance.attendance_date

        if shift.is_overnight:

            shift_end_date += timedelta(days=1)

        shift_end = datetime.combine(
            shift_end_date,
            shift.end_time
        )

        shift_end = timezone.make_aware(
            shift_end
        )

        if attendance.check_out < shift_end:

            attendance.early_leave_minutes = int(
                (
                    shift_end -
                    attendance.check_out
                ).total_seconds() / 60
            )

        else:

            attendance.early_leave_minutes = 0

        # ------------------------------------------
        # Overtime
        # ------------------------------------------

        overtime_after = shift.overtime_after_minutes

        if total_minutes > overtime_after:

            attendance.overtime_minutes = (
                total_minutes -
                overtime_after
            )

        else:

            attendance.overtime_minutes = 0

        # ------------------------------------------
        # Status
        # ------------------------------------------

        if total_minutes < shift.minimum_work_minutes / 2:

            attendance.status = "half_day"

        else:

            attendance.status = "present"

        return attendance

    @staticmethod
    @transaction.atomic
    def add_punch(
        employee,
        punch_time,
        punch_type,
        source="biometric",
        device_id=""
    ):

        attendance_date = punch_time.date()

        attendance, _ = Attendance.objects.get_or_create(
            employee=employee,
            attendance_date=attendance_date,
            defaults={
                "company": employee.company,
                "plant": employee.plant,
                "status": "absent",
                "source": source,
            }
        )

        AttendanceLog.objects.create(
            employee=employee,
            attendance=attendance,
            punch_type=punch_type,
            punch_time=punch_time,
            source=source,
            device_id=device_id,
        )

        if punch_type == "check_in":

            if (
                attendance.check_in is None
                or punch_time < attendance.check_in
            ):
                attendance.check_in = punch_time

        elif punch_type == "check_out":

            if (
                attendance.check_out is None
                or punch_time > attendance.check_out
            ):
                attendance.check_out = punch_time

        attendance.source = source

        AttendanceService.calculate_attendance(
            attendance
        )

        attendance.save()

        return attendance