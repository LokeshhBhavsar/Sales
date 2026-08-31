from datetime import datetime

from django.db.models import Q

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

        if employee:
            queryset = queryset.filter(
                employee_id=employee
            )

        if employee_code:
            queryset = queryset.filter(
                employee__employee_code=employee_code
            )

        if company:
            queryset = queryset.filter(
                company_id=company
            )

        if plant:
            queryset = queryset.filter(
                plant_id=plant
            )

        if attendance_date:
            queryset = queryset.filter(
                attendance_date=attendance_date
            )

        if start_date:
            queryset = queryset.filter(
                attendance_date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                attendance_date__lte=end_date
            )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter
            )

        if source:
            queryset = queryset.filter(
                source=source
            )

        return queryset

    @action(
        detail=False,
        methods=["post"],
        url_path="check-in"
    )
    def check_in(self, request):

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
            punch_type="check_in",
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

    @action(
        detail=False,
        methods=["post"],
        url_path="check-out"
    )
    def check_out(self, request):

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
            punch_type="check_out",
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