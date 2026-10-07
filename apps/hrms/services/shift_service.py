import re

from django.db import transaction
from django.db.models import Count, F, Q
from django.utils import timezone

from apps.hrms.models.shift import Shift
from apps.masters.models.plant import Plant

class DuplicateShiftError(ValueError):

    def __init__(
        self,
        message,
        shift=None
    ):
        super().__init__(message)

        self.shift = shift

class ShiftService:

    # =========================================================
    # GET FIRST WORD
    # =========================================================

    @staticmethod
    def _get_first_word(value):

        if not value:

            raise ValueError(
                "Company name or plant name is required "
                "to generate shift code."
            )

        # Extract the first alphanumeric word.
        #
        # Example:
        #
        # "DM Technologies"
        #       ↓
        # "DM"
        #
        # "kolkata kl Plant"
        #       ↓
        # "kolkata"

        words = re.findall(
            r"[A-Za-z0-9]+",
            value.strip()
        )

        if not words:

            raise ValueError(
                "Unable to generate shift code from "
                "company or plant name."
            )

        return words[0].upper()

    # =========================================================
    # GENERATE SHIFT CODE
    # =========================================================

    @staticmethod
    def _generate_shift_code(
        company,
        plant
    ):

        # -----------------------------------------------------
        # COMPANY FIRST WORD
        # -----------------------------------------------------

        company_word = (
            ShiftService._get_first_word(
                company.name
            )
        )

        # -----------------------------------------------------
        # PLANT FIRST WORD
        # -----------------------------------------------------

        plant_word = (
            ShiftService._get_first_word(
                plant.name
            )
        )

        # -----------------------------------------------------
        # CODE PREFIX
        # -----------------------------------------------------

        prefix = (
            f"{company_word}-"
            f"{plant_word}"
        )

        # -----------------------------------------------------
        # FIND NEXT AVAILABLE NUMBER
        # -----------------------------------------------------
        #
        # Example:
        #
        # DM-KOLKATA-SH001
        # DM-KOLKATA-SH002
        # DM-KOLKATA-SH003
        #
        # If SH002 already exists, it will not be reused.
        #
        # The next available number will be generated.
        # -----------------------------------------------------

        existing_codes = (
            Shift.objects
            .filter(
                plant=plant,
                code__startswith=f"{prefix}-SH"
            )
            .values_list(
                "code",
                flat=True
            )
        )

        existing_numbers = set()

        pattern = re.compile(
            rf"^{re.escape(prefix)}-SH(\d+)$",
            re.IGNORECASE
        )

        for existing_code in existing_codes:

            match = pattern.match(
                existing_code
            )

            if match:

                existing_numbers.add(
                    int(match.group(1))
                )

        # -----------------------------------------------------
        # GENERATE NEXT NUMBER
        # -----------------------------------------------------

        sequence = 1

        while sequence in existing_numbers:

            sequence += 1

        return (
            f"{prefix}-SH{sequence:03d}"
        )

    # =========================================================
    # CREATE SHIFT
    # =========================================================

    @staticmethod
    @transaction.atomic
    def create_shift(
        validated_data,
        user
    ):

        # -----------------------------------------------------
        # GET COMPANY AND PLANT
        # -----------------------------------------------------

        company = validated_data.get(
            "company"
        )

        plant = validated_data.get(
            "plant"
        )

        if not company:

            raise ValueError(
                "Company is required."
            )

        if not plant:

            raise ValueError(
                "Plant is required."
            )
                # -----------------------------------------------------
        # VALIDATE AUDIT USER
        # -----------------------------------------------------

        if not user or not getattr(
            user,
            "is_authenticated",
            False
        ):

            raise ValueError(
                "Authenticated user is required to create a shift."
            )

        # -----------------------------------------------------
        # VALIDATE ACTIVE COMPANY
        # -----------------------------------------------------

        if not company.is_active:

            raise ValueError(
                "The selected company is inactive."
            )

        # -----------------------------------------------------
        # VALIDATE ACTIVE PLANT
        # -----------------------------------------------------

        if not plant.is_active:

            raise ValueError(
                "The selected plant is inactive."
            )

        # -----------------------------------------------------
        # NORMALIZE VALUES
        # -----------------------------------------------------

        name = str(
            validated_data.get(
                "name",
                ""
            )
        ).strip()

        shift_type = str(
            validated_data.get(
                "shift_type",
                ""
            )
        ).strip().lower()

        start_time = validated_data.get(
            "start_time"
        )

        end_time = validated_data.get(
            "end_time"
        )

        # -----------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -----------------------------------------------------

        if not name:

            raise ValueError(
                "Shift name is required."
            )

        if shift_type not in {
            "basic",
            "contract"
        }:

            raise ValueError(
                "Invalid shift_type. "
                "Allowed values are basic and contract."
            )

        if start_time is None:

            raise ValueError(
                "start_time is required."
            )

        if end_time is None:

            raise ValueError(
                "end_time is required."
            )

        validated_data["name"] = name
        validated_data["shift_type"] = shift_type

        # -----------------------------------------------------
        # DUPLICATE CHECK 1
        #
        # SAME:
        # company + plant + name + shift_type
        # -----------------------------------------------------

        existing_shift = (
            Shift.objects
            .filter(
                company=company,
                plant=plant,
                name__iexact=name,
                shift_type=shift_type,
                is_deleted=False,
            )
            .first()
        )

        if existing_shift:

            raise DuplicateShiftError(
                "A shift with the same name and "
                "shift type already exists for "
                "this company and plant.",
                shift=existing_shift
            )

        # -----------------------------------------------------
        # DUPLICATE CHECK 2
        #
        # SAME:
        # company + plant + start_time + end_time
        # -----------------------------------------------------

        existing_shift = (
            Shift.objects
            .filter(
                company=company,
                plant=plant,
                start_time=start_time,
                end_time=end_time,
                is_deleted=False,
            )
            .first()
        )

        if existing_shift:

            raise DuplicateShiftError(
                "A shift with the same start time "
                "and end time already exists for "
                "this company and plant.",
                shift=existing_shift
            )
        # -----------------------------------------------------
        # LOCK PLANT ROW
        # -----------------------------------------------------
        #
        # This prevents two requests for the same plant
        # from generating the same SH number at the same time.
        # -----------------------------------------------------

        plant = (
            Plant.objects
            .select_for_update()
            .select_related("company")
            .get(
                pk=plant.pk
            )
        )

        # -----------------------------------------------------
        # COMPANY / PLANT SAFETY CHECK
        # -----------------------------------------------------

        if plant.company_id != company.id:

            raise ValueError(
                "The selected plant does not belong "
                "to the selected company."
            )

        # -----------------------------------------------------
        # GENERATE SHIFT CODE
        # -----------------------------------------------------

        shift_code = (
            ShiftService._generate_shift_code(
                company=company,
                plant=plant
            )
        )

        # -----------------------------------------------------
        # CREATE SHIFT
        # -----------------------------------------------------

        shift = Shift.objects.create(
            **validated_data,

            # Backend generated
            code=shift_code,

            # Audit fields
            created_by=user,
            updated_by=user,

            # Soft delete
            is_deleted=False
        )

        return shift

    # =========================================================
    # GET SHIFTS
    # =========================================================

    @staticmethod
    def get_shifts(
        company_id=None,
        plant_id=None,
        shift_type=None
    ):

        queryset = (
            Shift.objects

            .select_related(
                "company",
                "plant",
                "created_by",
                "updated_by",
            )

            .annotate(
                shift_assign_count=Count(
                    "employee_assignments",
                    filter=Q(
                        employee_assignments__is_active=True
                    )
                ),
                assigned_user_count=Count(
                    "employee_assignments__employee__user__id",
                    filter=(
                        Q(employee_assignments__is_active=True)
                        & Q(employee_assignments__effective_from__lte=timezone.localdate())
                        & (
                            Q(employee_assignments__effective_to__isnull=True)
                            | Q(employee_assignments__effective_to__gte=timezone.localdate())
                        )
                        & Q(employee_assignments__employee__status="active")
                        & Q(employee_assignments__employee__user__isnull=False)
                        & Q(employee_assignments__employee__user__is_active=True)
                        & Q(employee_assignments__employee__user__is_deleted=False)
                        & Q(employee_assignments__employee__company_id=F("company_id"))
                        & Q(employee_assignments__employee__plant_id=F("plant_id"))
                        & (
                            Q(
                                employee_assignments__employee__user__scope="company",
                                employee_assignments__employee__user__company_id=F("company_id"),
                            )
                            | Q(
                                employee_assignments__employee__user__scope__in=(
                                    "plant",
                                    "department",
                                ),
                                employee_assignments__employee__user__company_id=F("company_id"),
                                employee_assignments__employee__user__plant_id=F("plant_id"),
                            )
                        )
                    ),
                    distinct=True,
                ),
            )

            .filter(
                is_deleted=False
            )
        )

        # -----------------------------------------------------
        # COMPANY FILTER
        # -----------------------------------------------------

        if company_id:

            queryset = queryset.filter(
                company_id=company_id
            )

        # -----------------------------------------------------
        # PLANT FILTER
        # -----------------------------------------------------

        if plant_id:

            queryset = queryset.filter(
                plant_id=plant_id
            )

        # -----------------------------------------------------
        # SHIFT TYPE FILTER
        # -----------------------------------------------------

        if shift_type:

            queryset = queryset.filter(
                shift_type=shift_type
            )

        # -----------------------------------------------------
        # ORDERING
        # -----------------------------------------------------

        return queryset.order_by(
            "name"
        )
