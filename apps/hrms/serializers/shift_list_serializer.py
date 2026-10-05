from rest_framework import serializers

from apps.hrms.models.shift import Shift


class ShiftListSerializer(
    serializers.ModelSerializer
):

    # =========================================================
    # RESPONSE FIELD MAPPING
    # =========================================================

    shift_id = serializers.UUIDField(
        source="id",
        read_only=True
    )

    shift_code = serializers.CharField(
        source="code",
        read_only=True
    )

    shift_start_time = serializers.TimeField(
        source="start_time",
        read_only=True
    )

    shift_end_time = serializers.TimeField(
        source="end_time",
        read_only=True
    )

    shift_name = serializers.CharField(
        source="name",
        read_only=True
    )

    shift_company_id = serializers.UUIDField(
        source="company_id",
        read_only=True
    )

    shift_plant_id = serializers.UUIDField(
        source="plant_id",
        read_only=True
    )

    grace_time = serializers.IntegerField(
        source="grace_minutes",
        read_only=True
    )

    shift_assign_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:

        model = Shift

        fields = [

            # -------------------------------------------------
            # Shift identification
            # -------------------------------------------------

            "shift_id",
            "shift_code",
            "shift_name",

            # -------------------------------------------------
            # Shift timing
            # -------------------------------------------------

            "shift_start_time",
            "shift_end_time",

            # -------------------------------------------------
            # Shift type
            # -------------------------------------------------

            "shift_type",

            # -------------------------------------------------
            # Organization
            # -------------------------------------------------

            "shift_company_id",
            "shift_plant_id",

            # -------------------------------------------------
            # Shift settings
            # -------------------------------------------------

            "grace_time",

            # -------------------------------------------------
            # Status
            # -------------------------------------------------

            "is_active",
            "is_deleted",

            # -------------------------------------------------
            # Audit
            # -------------------------------------------------

            "created_at",
            "updated_at",
            "created_by",
            "updated_by",

            # -------------------------------------------------
            # Assignment count
            # -------------------------------------------------

            "shift_assign_count",
        ]

        read_only_fields = fields