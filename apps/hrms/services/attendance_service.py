# from datetime import datetime, timedelta
# from django.db import models, transaction
# from django.utils import timezone
# from django.utils import timezone

# from apps.hrms.models.employee import Employee
# from apps.hrms.models.attendance import Attendance
# from apps.hrms.models.attendance_log import AttendanceLog
# from apps.hrms.models.employee_shift import EmployeeShift


# class AttendanceService:

#     @staticmethod
#     def get_employee_shift(employee, attendance_date):

#         return (
#             EmployeeShift.objects
#             .filter(
#                 employee=employee,
#                 effective_from__lte=attendance_date,
#                 is_active=True,
#             )
#             .filter(
#                 models.Q(effective_to__isnull=True)
#                 | models.Q(
#                     effective_to__gte=attendance_date
#                 )
#             )
#             .select_related("shift")
#             .order_by("-effective_from")
#             .first()
#         )

#     @staticmethod
#     @transaction.atomic
#     def create_or_update_attendance(
#         employee,
#         attendance_date,
#         in_time=None,
#         out_time=None,
#         source="system",
#         remarks=""
#     ):

#         attendance, created = Attendance.objects.get_or_create(
#             employee=employee,
#             attendance_date=attendance_date,
#             defaults={
#                 "company": employee.company,
#                 "plant": employee.plant,
#                 "source": source,
#                 "status": "absent",
#             }
#         )

#         if in_time:

#             if (
#                 attendance.in_time is None
#                 or in_time < attendance.in_time
#             ):
#                 attendance.in_time = in_time

#         if out_time:

#             if (
#                 attendance.out_time is None
#                 or out_time > attendance.out_time
#             ):
#                 attendance.out_time = out_time

#         attendance.source = source

#         if remarks:
#             attendance.remarks = remarks

#         AttendanceService.calculate_attendance(
#             attendance
#         )

#         attendance.save()

#         return attendance

#     @staticmethod
#     def calculate_attendance(attendance):

#         if not attendance.in_time:

#             attendance.status = "absent"
#             attendance.total_work_minutes = 0

#             return attendance

#         if not attendance.out_time:

#             attendance.status = "present"
#             attendance.total_work_minutes = 0

#             return attendance

#         total_seconds = (
#             attendance.out_time -
#             attendance.in_time
#         ).total_seconds()

#         total_minutes = max(
#             int(total_seconds / 60),
#             0
#         )

#         attendance.total_work_minutes = total_minutes

#         # Get employee shift
#         shift_assignment = (
#             EmployeeShift.objects
#             .filter(
#                 employee=attendance.employee,
#                 effective_from__lte=attendance.attendance_date,
#                 is_active=True,
#             )
#             .filter(
#                 models.Q(effective_to__isnull=True)
#                 | models.Q(
#                     effective_to__gte=
#                     attendance.attendance_date
#                 )
#             )
#             .select_related("shift")
#             .order_by("-effective_from")
#             .first()
#         )

#         if not shift_assignment:

#             attendance.status = "present"

#             return attendance

#         shift = shift_assignment.shift

#         # ------------------------------------------
#         # Calculate late
#         # ------------------------------------------

#         shift_start = datetime.combine(
#             attendance.attendance_date,
#             shift.start_time
#         )

#         shift_start = timezone.make_aware(
#             shift_start
#         )

#         grace_time = shift_start + timedelta(
#             minutes=shift.grace_minutes
#         )

#         if attendance.in_time > grace_time:

#             attendance.late_minutes = int(
#                 (
#                     attendance.in_time -
#                     grace_time
#                 ).total_seconds() / 60
#             )

#         else:

#             attendance.late_minutes = 0

#         # ------------------------------------------
#         # Calculate early leave
#         # ------------------------------------------

#         shift_end_date = attendance.attendance_date

#         if shift.is_overnight:

#             shift_end_date += timedelta(days=1)

#         shift_end = datetime.combine(
#             shift_end_date,
#             shift.end_time
#         )

#         shift_end = timezone.make_aware(
#             shift_end
#         )

#         if attendance.out_time < shift_end:

#             attendance.early_leave_minutes = int(
#                 (
#                     shift_end -
#                     attendance.out_time
#                 ).total_seconds() / 60
#             )

#         else:

#             attendance.early_leave_minutes = 0

#         # ------------------------------------------
#         # Overtime
#         # ------------------------------------------

#         overtime_after = shift.overtime_after_minutes

#         if total_minutes > overtime_after:

#             attendance.overtime_minutes = (
#                 total_minutes -
#                 overtime_after
#             )

#         else:

#             attendance.overtime_minutes = 0

#         # ------------------------------------------
#         # Status
#         # ------------------------------------------

#         if total_minutes < shift.minimum_work_minutes / 2:

#             attendance.status = "half_day"

#         else:

#             attendance.status = "present"

#         return attendance

#     @staticmethod
#     @transaction.atomic
#     def add_punch(
#         employee,
#         punch_time,
#         punch_type,
#         source="biometric",
#         device_id=""
#     ):

#         attendance_date = punch_time.date()

#         attendance, _ = Attendance.objects.get_or_create(
#             employee=employee,
#             attendance_date=attendance_date,
#             defaults={
#                 "company": employee.company,
#                 "plant": employee.plant,
#                 "status": "absent",
#                 "source": source,
#             }
#         )

#         AttendanceLog.objects.create(
#             employee=employee,
#             attendance=attendance,
#             punch_type=punch_type,
#             punch_time=punch_time,
#             source=source,
#             device_id=device_id,
#         )

#         if punch_type == "in_time":

#             if (
#                 attendance.in_time is None
#                 or punch_time < attendance.in_time
#             ):
#                 attendance.in_time = punch_time

#         elif punch_type == "out_time":

#             if (
#                 attendance.out_time is None
#                 or punch_time > attendance.out_time
#             ):
#                 attendance.out_time = punch_time

#         attendance.source = source

#         AttendanceService.calculate_attendance(
#             attendance
#         )

#         attendance.save()

#         return attendance

from datetime import datetime, timedelta

from django.db import models, transaction
from django.utils import timezone

from apps.hrms.models.employee import Employee
from apps.hrms.models.attendance import Attendance
from apps.hrms.models.attendance_log import AttendanceLog
from apps.hrms.models.employee_shift import EmployeeShift


class AttendanceService:

    # ============================================================
    # GET EMPLOYEE SHIFT
    # ============================================================

    @staticmethod
    def get_employee_shift(
        employee,
        attendance_date
    ):

        return (
            EmployeeShift.objects
            .filter(
                employee=employee,
                effective_from__lte=attendance_date,
                is_active=True,
            )
            .filter(
                models.Q(
                    effective_to__isnull=True
                )
                |
                models.Q(
                    effective_to__gte=attendance_date
                )
            )
            .select_related("shift")
            .order_by("-effective_from")
            .first()
        )

    # ============================================================
    # CREATE OR UPDATE ATTENDANCE
    # ============================================================

    @staticmethod
    @transaction.atomic
    def create_or_update_attendance(
        employee,
        attendance_date,
        in_time=None,
        out_time=None,
        source="system",
        remarks=""
    ):

        # --------------------------------------------------------
        # Find existing attendance or create new record
        # --------------------------------------------------------

        attendance, created = (
            Attendance.objects.get_or_create(
                employee=employee,
                attendance_date=attendance_date,
                defaults={
                    "company": employee.company,
                    "plant": employee.plant,
                    "source": source,
                    "status": "absent",
                }
            )
        )

        # --------------------------------------------------------
        # Update in_time
        #
        # Keep the earliest in_time if multiple records exist.
        # --------------------------------------------------------

        if in_time:

            if (
                attendance.in_time is None
                or in_time < attendance.in_time
            ):

                attendance.in_time = in_time

        # --------------------------------------------------------
        # Update out_time
        #
        # Keep the latest out_time if multiple records exist.
        # --------------------------------------------------------

        if out_time:

            if (
                attendance.out_time is None
                or out_time > attendance.out_time
            ):

                attendance.out_time = out_time

        # --------------------------------------------------------
        # Update source
        # --------------------------------------------------------

        attendance.source = source

        # --------------------------------------------------------
        # Update remarks if provided
        # --------------------------------------------------------

        if remarks:

            attendance.remarks = remarks

        # --------------------------------------------------------
        # Calculate attendance
        # --------------------------------------------------------

        AttendanceService.calculate_attendance(
            attendance
        )

        # --------------------------------------------------------
        # Save attendance
        # --------------------------------------------------------

        attendance.save()

        return attendance

    # ============================================================
    # CALCULATE ATTENDANCE
    # ============================================================

    @staticmethod
    def calculate_attendance(attendance):

        # --------------------------------------------------------
        # No in_time
        # --------------------------------------------------------

        if not attendance.in_time:

            attendance.status = "absent"

            attendance.total_work_minutes = 0

            return attendance

        # --------------------------------------------------------
        # in_time exists but out_time doesn't exist
        # --------------------------------------------------------

        if not attendance.out_time:

            attendance.status = "present"

            attendance.total_work_minutes = 0

            return attendance

        # --------------------------------------------------------
        # Calculate total working time
        # --------------------------------------------------------

        total_seconds = (
            attendance.out_time
            - attendance.in_time
        ).total_seconds()

        total_minutes = max(
            int(total_seconds / 60),
            0
        )

        attendance.total_work_minutes = (
            total_minutes
        )

        # ========================================================
        # GET EMPLOYEE SHIFT
        # ========================================================

        shift_assignment = (
            EmployeeShift.objects
            .filter(
                employee=attendance.employee,
                effective_from__lte=attendance.attendance_date,
                is_active=True,
            )
            .filter(
                models.Q(
                    effective_to__isnull=True
                )
                |
                models.Q(
                    effective_to__gte=
                    attendance.attendance_date
                )
            )
            .select_related("shift")
            .order_by("-effective_from")
            .first()
        )

        # --------------------------------------------------------
        # No shift assigned
        # --------------------------------------------------------

        if not shift_assignment:

            attendance.status = "present"

            return attendance

        shift = shift_assignment.shift

        # ========================================================
        # CALCULATE LATE MINUTES
        # ========================================================

        shift_start = datetime.combine(
            attendance.attendance_date,
            shift.start_time
        )

        shift_start = timezone.make_aware(
            shift_start
        )

        grace_time = (
            shift_start
            + timedelta(
                minutes=shift.grace_minutes
            )
        )

        if attendance.in_time > grace_time:

            attendance.late_minutes = int(
                (
                    attendance.in_time
                    - grace_time
                ).total_seconds() / 60
            )

        else:

            attendance.late_minutes = 0

        # ========================================================
        # CALCULATE EARLY LEAVE
        # ========================================================

        shift_end_date = (
            attendance.attendance_date
        )

        if shift.is_overnight:

            shift_end_date += timedelta(
                days=1
            )

        shift_end = datetime.combine(
            shift_end_date,
            shift.end_time
        )

        shift_end = timezone.make_aware(
            shift_end
        )

        if attendance.out_time < shift_end:

            attendance.early_leave_minutes = int(
                (
                    shift_end
                    - attendance.out_time
                ).total_seconds() / 60
            )

        else:

            attendance.early_leave_minutes = 0

        # ========================================================
        # CALCULATE OVERTIME
        # ========================================================

        overtime_after = (
            shift.overtime_after_minutes
        )

        if total_minutes > overtime_after:

            attendance.overtime_minutes = (
                total_minutes
                - overtime_after
            )

        else:

            attendance.overtime_minutes = 0

        # ========================================================
        # CALCULATE STATUS
        # ========================================================

        if (
            total_minutes
            < shift.minimum_work_minutes / 2
        ):

            attendance.status = "half_day"

        else:

            attendance.status = "present"

        return attendance

    # ============================================================
    # ADD BIOMETRIC PUNCH
    # ============================================================

    @staticmethod
    @transaction.atomic
    def add_punch(
        employee,
        punch_time,
        punch_type,
        source="biometric",
        device_id=""
    ):

        attendance_date = (
            punch_time.date()
        )

        # --------------------------------------------------------
        # Find or create attendance
        # --------------------------------------------------------

        attendance, _ = (
            Attendance.objects.get_or_create(
                employee=employee,
                attendance_date=attendance_date,
                defaults={
                    "company": employee.company,
                    "plant": employee.plant,
                    "status": "absent",
                    "source": source,
                }
            )
        )

        # --------------------------------------------------------
        # Create attendance log
        # --------------------------------------------------------

        AttendanceLog.objects.create(
            employee=employee,
            attendance=attendance,
            punch_type=punch_type,
            punch_time=punch_time,
            source=source,
            device_id=device_id,
        )

        # ========================================================
        # IN TIME PUNCH
        # ========================================================

        if punch_type == "in_time":

            if (
                attendance.in_time is None
                or punch_time < attendance.in_time
            ):

                attendance.in_time = punch_time

        # ========================================================
        # OUT TIME PUNCH
        # ========================================================

        elif punch_type == "out_time":

            if (
                attendance.out_time is None
                or punch_time > attendance.out_time
            ):

                attendance.out_time = punch_time

        # --------------------------------------------------------
        # Update source
        # --------------------------------------------------------

        attendance.source = source

        # --------------------------------------------------------
        # Calculate attendance
        # --------------------------------------------------------

        AttendanceService.calculate_attendance(
            attendance
        )

        # --------------------------------------------------------
        # Save attendance
        # --------------------------------------------------------

        attendance.save()

        return attendance