from datetime import datetime, date, timedelta

from django.db.models import Q
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.hrms.models.attendance import Attendance
from apps.hrms.models.employee import Employee
from apps.hrms.models.attendance_log import AttendanceLog

from apps.hrms.serializers.attendance import (
    AttendanceSerializer,
    AttendanceLogSerializer,
)

from apps.hrms.services.attendance_service import (
    AttendanceService,
)


class AttendanceViewSet(viewsets.ModelViewSet):

    queryset = (
        Attendance.objects
        .select_related(
            "employee",
            "company",
            "plant",
        )
        .prefetch_related("logs")
        .order_by("-attendance_date")
    )

    serializer_class = AttendanceSerializer

    def get_queryset(self):

        queryset = super().get_queryset()

        # =====================================================
        # EXISTING FILTERS
        # =====================================================

        employee = self.request.query_params.get(
            "employee"
        )

        employee_code = self.request.query_params.get(
            "employee_code"
        )

        company = self.request.query_params.get(
            "company"
        )

        plant = self.request.query_params.get(
            "plant"
        )

        attendance_date = self.request.query_params.get(
            "date"
        )

        start_date = self.request.query_params.get(
            "start_date"
        )

        end_date = self.request.query_params.get(
            "end_date"
        )

        status_filter = self.request.query_params.get(
            "status"
        )

        source = self.request.query_params.get(
            "source"
        )

        # =====================================================
        # NEW FILTERS
        # =====================================================

        department = self.request.query_params.get(
            "department"
        )

        week = self.request.query_params.get(
            "week"
        )

        month = self.request.query_params.get(
            "month"
        )

        year = self.request.query_params.get(
            "year"
        )

        # =====================================================
        # EMPLOYEE FILTER
        # =====================================================

        if employee:
            queryset = queryset.filter(
                employee_id=employee
            )

        # =====================================================
        # EMPLOYEE CODE FILTER
        # =====================================================

        if employee_code:
            queryset = queryset.filter(
                employee__employee_code=employee_code
            )

        # =====================================================
        # COMPANY FILTER
        # =====================================================

        if company:
            queryset = queryset.filter(
                company_id=company
            )

        # =====================================================
        # PLANT FILTER
        # =====================================================

        if plant:
            queryset = queryset.filter(
                plant_id=plant
            )

        # =====================================================
        # DEPARTMENT FILTER
        # =====================================================

        if department:
            queryset = queryset.filter(
                employee__department_id=department
            )

        # =====================================================
        # EXACT DATE FILTER
        # Example:
        # ?date=2026-09-17
        # =====================================================

        if attendance_date:
            queryset = queryset.filter(
                attendance_date=attendance_date
            )

        # =====================================================
        # WEEK FILTER
        # Example:
        # ?week=2026-W38
        #
        # ISO week:
        # Monday -> Sunday
        # =====================================================

        if week:

            try:

                week_year, week_number = week.split("-W")

                week_year = int(week_year)
                week_number = int(week_number)

                first_day_of_week = date.fromisocalendar(
                    week_year,
                    week_number,
                    1
                )

                last_day_of_week = first_day_of_week + timedelta(
                    days=6
                )

                queryset = queryset.filter(
                    attendance_date__range=[
                        first_day_of_week,
                        last_day_of_week
                    ]
                )

            except (ValueError, TypeError):

                queryset = queryset.none()

        # =====================================================
        # MONTH FILTER
        #
        # Example:
        # ?month=9&year=2026
        #
        # Returns:
        # 2026-09-01 -> 2026-09-30
        # =====================================================

        if month:

            try:

                month_number = int(month)

                if year:
                    year_number = int(year)
                else:
                    year_number = date.today().year

                if month_number < 1 or month_number > 12:
                    return queryset.none()

                first_day_of_month = date(
                    year_number,
                    month_number,
                    1
                )

                if month_number == 12:

                    first_day_of_next_month = date(
                        year_number + 1,
                        1,
                        1
                    )

                else:

                    first_day_of_next_month = date(
                        year_number,
                        month_number + 1,
                        1
                    )

                last_day_of_month = (
                    first_day_of_next_month -
                    timedelta(days=1)
                )

                queryset = queryset.filter(
                    attendance_date__range=[
                        first_day_of_month,
                        last_day_of_month
                    ]
                )

            except (ValueError, TypeError):

                queryset = queryset.none()

        # =====================================================
        # YEAR FILTER
        #
        # Example:
        # ?year=2026
        #
        # Returns:
        # 2026-01-01 -> 2026-12-31
        # =====================================================

        if year and not month:

            try:

                year_number = int(year)

                first_day_of_year = date(
                    year_number,
                    1,
                    1
                )

                last_day_of_year = date(
                    year_number,
                    12,
                    31
                )

                queryset = queryset.filter(
                    attendance_date__range=[
                        first_day_of_year,
                        last_day_of_year
                    ]
                )

            except (ValueError, TypeError):

                queryset = queryset.none()

        # =====================================================
        # CUSTOM DATE RANGE
        #
        # Example:
        # ?start_date=2026-09-01&end_date=2026-09-15
        # =====================================================

        if start_date:
            queryset = queryset.filter(
                attendance_date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                attendance_date__lte=end_date
            )

        # =====================================================
        # STATUS FILTER
        # =====================================================

        if status_filter:
            queryset = queryset.filter(
                status=status_filter
            )

        # =====================================================
        # SOURCE FILTER
        # =====================================================

        if source:
            queryset = queryset.filter(
                source=source
            )

        return queryset

    # =========================================================
    # CHECK-IN API
    # =========================================================

    @action(
        detail=False,
        methods=["post"],
        url_path="check-in"
    )
    def in_time(self, request):

        employee_id = request.data.get(
            "employee"
        )

        if not employee_id:

            return Response(
                {
                    "success": False,
                    "message": "Employee is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            employee = Employee.objects.get(
                id=employee_id,
                status="active"
            )

        except Employee.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Active employee not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        now = datetime.now().astimezone()

        attendance = AttendanceService.add_punch(
            employee=employee,
            punch_time=now,
            punch_type="in_time",
            source="manual"
        )

        return Response(
            {
                "success": True,
                "message": "Check-in recorded successfully.",
                "data": AttendanceSerializer(
                    attendance
                ).data
            },
            status=status.HTTP_201_CREATED
        )

    # =========================================================
    # CHECK-OUT API
    # =========================================================

    @action(
        detail=False,
        methods=["post"],
        url_path="check-out"
    )
    def out_time(self, request):

        employee_id = request.data.get(
            "employee"
        )

        if not employee_id:

            return Response(
                {
                    "success": False,
                    "message": "Employee is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            employee = Employee.objects.get(
                id=employee_id,
                status="active"
            )

        except Employee.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Active employee not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        now = datetime.now().astimezone()

        attendance = AttendanceService.add_punch(
            employee=employee,
            punch_time=now,
            punch_type="out_time",
            source="manual"
        )

        return Response(
            {
                "success": True,
                "message": "Check-out recorded successfully.",
                "data": AttendanceSerializer(
                    attendance
                ).data
            }
        )

    # =========================================================
    # EXISTING SUMMARY API
    # =========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="summary"
    )
    def summary(self, request):

        queryset = self.get_queryset()

        data = {
            "total": queryset.count(),

            "present": queryset.filter(
                status="present"
            ).count(),

            "absent": queryset.filter(
                status="absent"
            ).count(),

            "half_day": queryset.filter(
                status="half_day"
            ).count(),

            "leave": queryset.filter(
                status="leave"
            ).count(),

            "holiday": queryset.filter(
                status="holiday"
            ).count(),

            "weekly_off": queryset.filter(
                status="weekly_off"
            ).count(),

            "work_from_home": queryset.filter(
                status="work_from_home"
            ).count(),

            "total_overtime_minutes": sum(
                queryset.values_list(
                    "overtime_minutes",
                    flat=True
                )
            ),
        }

        return Response(
            {
                "success": True,
                "data": data
            }
        )

    # =========================================================
    # NEW DAILY ATTENDANCE SUMMARY API
    #
    # GET:
    # /api/hrms/attendance/today-summary/
    #
    # Returns today's:
    # Total
    # Present
    # Absent
    # Half Day
    # Leave
    # Overtime
    # =========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="today-summary"
    )
    def today_summary(self, request):

        # Get current date according to
        # Django application timezone
        today = timezone.localdate()

        # Get only today's attendance records
        queryset = Attendance.objects.filter(
            attendance_date=today
        )

        # -----------------------------------------------------
        # TOTAL
        # -----------------------------------------------------

        total = queryset.count()

        # -----------------------------------------------------
        # PRESENT
        # -----------------------------------------------------

        present = queryset.filter(
            status="present"
        ).count()

        # -----------------------------------------------------
        # ABSENT
        # -----------------------------------------------------

        absent = queryset.filter(
            status="absent"
        ).count()

        # -----------------------------------------------------
        # HALF DAY
        #
        # Half day is counted from the status already
        # calculated and saved by AttendanceService/import.
        # -----------------------------------------------------

        half_day = queryset.filter(
            status="half_day"
        ).count()

        # -----------------------------------------------------
        # LEAVE
        # -----------------------------------------------------

        leave = queryset.filter(
            status="leave"
        ).count()

        # -----------------------------------------------------
        # OVERTIME
        #
        # Count employees/attendance records having
        # overtime greater than 0 minutes.
        # -----------------------------------------------------

        overtime = queryset.filter(
            overtime_minutes__gt=0
        ).count()

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return Response(
            {
                "success": True,
                "date": today,
                "data": {
                    "total": total,
                    "present": present,
                    "absent": absent,
                    "half_day": half_day,
                    "leave": leave,
                    "overtime": overtime,
                }
            },
            status=status.HTTP_200_OK
        )


class AttendanceLogViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = (
        AttendanceLog.objects
        .select_related(
            "employee",
            "attendance"
        )
        .order_by("-punch_time")
    )

    serializer_class = AttendanceLogSerializer

    def get_queryset(self):

        queryset = super().get_queryset()

        employee = self.request.query_params.get(
            "employee"
        )

        source = self.request.query_params.get(
            "source"
        )

        punch_type = self.request.query_params.get(
            "punch_type"
        )

        if employee:
            queryset = queryset.filter(
                employee_id=employee
            )

        if source:
            queryset = queryset.filter(
                source=source
            )

        if punch_type:
            queryset = queryset.filter(
                punch_type=punch_type
            )

        return queryset