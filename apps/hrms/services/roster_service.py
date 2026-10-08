from datetime import timedelta
from uuid import UUID

from django.db import transaction
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.hrms.models.employee import Employee
from apps.hrms.models.roster import Roster, RosterAssignment
from apps.hrms.models.shift import Shift


def _actor_name(user):
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return full_name or user.email or str(user.pk)


class RosterService:
    @staticmethod
    def active_rosters():
        return Roster.objects.filter(is_deleted=False).annotate(
            total_employees=Count("assignments__employee_id", filter=Q(assignments__is_deleted=False), distinct=True)
        ).select_related("company", "plant", "department").order_by("-created_at")

    @staticmethod
    def _request_date(value, field):
        try:
            return serializers.DateField().run_validation(value)
        except ValidationError as exc:
            raise ValidationError({field: exc.detail})

    @staticmethod
    def _uuid(value, field):
        try:
            return UUID(str(value))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError({field: "Enter a valid UUID."})

    @staticmethod
    @transaction.atomic
    def generate_assignments(roster, payload, user):
        employee_ids = payload.get("employee_ids")
        if not isinstance(employee_ids, list) or not employee_ids:
            raise ValidationError({"employee_ids": "Provide a non-empty list of employee UUIDs."})
        parsed_employee_ids = [RosterService._uuid(value, "employee_ids") for value in employee_ids]
        if len(set(parsed_employee_ids)) != len(parsed_employee_ids):
            raise ValidationError({"employee_ids": "Duplicate employee IDs are not allowed."})

        start_date = RosterService._request_date(payload.get("start_date"), "start_date")
        end_date = RosterService._request_date(payload.get("end_date"), "end_date")
        if start_date > end_date:
            raise ValidationError({"end_date": "end_date must be on or after start_date."})
        if start_date < roster.start_date or end_date > roster.end_date:
            raise ValidationError({"start_date": "Request dates must be inside the roster date range."})

        requested_shift_type = payload.get("shift_type")
        if requested_shift_type is not None:
            requested_shift_type = str(requested_shift_type).strip().lower()
            allowed_types = {choice[0] for choice in Shift.SHIFT_TYPE_CHOICES}
            if requested_shift_type not in allowed_types:
                raise ValidationError({"shift_type": f"Use one of: {', '.join(sorted(allowed_types))}."})

        employees = list(Employee.objects.filter(
            id__in=parsed_employee_ids,
            company_id=roster.company_id,
            plant_id=roster.plant_id,
        ).select_related("department"))
        employee_by_id = {employee.id: employee for employee in employees}
        missing = [str(item) for item in parsed_employee_ids if item not in employee_by_id]
        if missing:
            raise ValidationError({"employee_ids": f"Employees not found in this roster's company and plant: {', '.join(missing)}."})
        if roster.department_id:
            wrong_department = [str(item) for item in parsed_employee_ids if employee_by_id[item].department_id != roster.department_id]
            if wrong_department:
                raise ValidationError({"employee_ids": "Every employee must belong to the roster department."})

        schedule = payload.get("schedule")
        if not isinstance(schedule, list) or not schedule:
            raise ValidationError({"schedule": "Provide a non-empty schedule."})
        parsed_schedule = []
        allowed_day_types = {choice[0] for choice in RosterAssignment.DAY_TYPE_CHOICES}
        for index, item in enumerate(schedule):
            if not isinstance(item, dict):
                raise ValidationError({"schedule": f"Schedule item {index + 1} must be an object."})
            item_start = RosterService._request_date(item.get("start_date"), f"schedule.{index}.start_date")
            item_end = RosterService._request_date(item.get("end_date"), f"schedule.{index}.end_date")
            if item_start > item_end or item_start < start_date or item_end > end_date:
                raise ValidationError({"schedule": f"Schedule item {index + 1} has dates outside the request range."})
            day_type = str(item.get("day_type", "WORKING_DAY")).strip().upper()
            if day_type not in allowed_day_types:
                raise ValidationError({"schedule": f"Invalid day_type in schedule item {index + 1}."})

            shift = None
            raw_shift_id = item.get("shift_id")
            if day_type == "WORKING_DAY":
                if raw_shift_id in (None, ""):
                    raise ValidationError({"schedule": f"shift_id is required for working schedule item {index + 1}."})
                shift_id = RosterService._uuid(raw_shift_id, f"schedule.{index}.shift_id")
                shift = Shift.objects.filter(id=shift_id, is_deleted=False, is_active=True).first()
                if not shift:
                    raise ValidationError({"schedule": f"Shift in schedule item {index + 1} was not found or is inactive."})
                if shift.company_id != roster.company_id or shift.plant_id != roster.plant_id:
                    raise ValidationError({"schedule": f"Shift in schedule item {index + 1} is outside the roster company and plant."})
                if not requested_shift_type:
                    raise ValidationError({"shift_type": "shift_type is required when assigning working days."})
                if shift.shift_type.lower() != requested_shift_type:
                    raise ValidationError({"schedule": f"Shift in schedule item {index + 1} does not match shift_type."})
            elif raw_shift_id not in (None, ""):
                raise ValidationError({"schedule": f"shift_id must be null for non-working schedule item {index + 1}."})
            elif "day_type" not in item:
                raise ValidationError({"schedule": f"day_type is required for non-working schedule item {index + 1}."})

            parsed_schedule.append((item_start, item_end, shift, day_type))

        parsed_schedule.sort(key=lambda row: row[0])
        next_date = start_date
        for item_start, item_end, _shift, _day_type in parsed_schedule:
            if item_start < next_date:
                raise ValidationError({"schedule": "Schedule ranges must not overlap."})
            if item_start > next_date:
                raise ValidationError({"schedule": "Schedule ranges must cover every date without gaps."})
            next_date = item_end + timedelta(days=1)
        if next_date != end_date + timedelta(days=1):
            raise ValidationError({"schedule": "Schedule ranges must cover every date without gaps."})

        dates = []
        for item_start, item_end, shift, day_type in parsed_schedule:
            current = item_start
            while current <= item_end:
                dates.append((current, shift, day_type))
                current += timedelta(days=1)

        if RosterAssignment.objects.filter(roster=roster, employee_id__in=parsed_employee_ids, assignment_date__range=(start_date, end_date), is_deleted=False).exists():
            raise ValidationError({"assignments": "One or more employees already have active assignments in this roster and date range."})

        actor = _actor_name(user)
        assignment_rows = [
            RosterAssignment(
                roster=roster,
                employee=employee_by_id[employee_id],
                assignment_date=assignment_date,
                shift=shift,
                day_type=day_type,
                created_by_name=actor,
                updated_by_name=actor,
            )
            for employee_id in parsed_employee_ids
            for assignment_date, shift, day_type in dates
        ]
        RosterAssignment.objects.bulk_create(assignment_rows)
        return len(assignment_rows)

    @staticmethod
    def assignment_grid(roster):
        assignments = roster.assignments.filter(is_deleted=False).select_related("employee", "shift").order_by("assignment_date", "employee__employee_code")
        return {
            "roster": {
                "id": str(roster.id), "name": roster.name,
                "company": {"id": str(roster.company_id), "name": roster.company.name},
                "plant": {"id": str(roster.plant_id), "name": roster.plant.name},
                "department": ({"id": str(roster.department_id), "name": roster.department.name} if roster.department_id else None),
                "start_date": roster.start_date, "end_date": roster.end_date, "status": roster.status,
            },
            "assignments": [
                {
                    "id": str(item.id),
                    "employee": {"id": str(item.employee_id), "employee_code": item.employee.employee_code, "name": f"{item.employee.first_name} {item.employee.last_name}".strip()},
                    "assignment_date": item.assignment_date,
                    "day_type": item.day_type,
                    "shift_id": str(item.shift_id) if item.shift_id else None,
                    "shift_name": item.shift.name if item.shift_id else None,
                    "shift_code": item.shift.code if item.shift_id else None,
                    "shift_time": f"{item.shift.start_time.strftime('%H:%M')} - {item.shift.end_time.strftime('%H:%M')}" if item.shift_id else None,
                    "shift_type": item.shift.shift_type if item.shift_id else None,
                    "shift": ({
                        "id": str(item.shift_id), "name": item.shift.name, "code": item.shift.code,
                        "time": f"{item.shift.start_time.strftime('%H:%M')} - {item.shift.end_time.strftime('%H:%M')}",
                        "type": item.shift.shift_type,
                    } if item.shift_id else None),
                }
                for item in assignments
            ],
        }
