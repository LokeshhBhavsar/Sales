import re

from django.db import transaction
from django.db.models import Count, Q

from apps.hrms.models.shift import Shift
from apps.masters.models.plant import Plant


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
                )
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