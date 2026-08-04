from rest_framework import serializers

from apps.masters.models.department import Department
from apps.masters.models.plant import Plant


class DepartmentCreateSerializer(serializers.ModelSerializer):

    plant = serializers.UUIDField(write_only=True)

    class Meta:
        model = Department
        fields = [
            "plant",
            "name",
        ]

    def validate_plant(self, value):

        try:
            return Plant.objects.get(id=value)

        except Plant.DoesNotExist:
            raise serializers.ValidationError(
                "Plant does not exist."
            )

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Department name is required."
            )

        return value

    def validate(self, attrs):

        if Department.objects.filter(
            plant=attrs["plant"],
            name__iexact=attrs["name"]
        ).exists():

            raise serializers.ValidationError(
                {
                    "name": "Department already exists for this plant."
                }
            )

        return attrs


class DepartmentListSerializer(serializers.ModelSerializer):

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True
    )

    company_name = serializers.CharField(
        source="plant.company.name",
        read_only=True
    )

    class Meta:
        model = Department
        fields = [
            "id",
            "company_name",
            "plant_name",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]


class DepartmentDetailSerializer(serializers.ModelSerializer):

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True
    )

    company_name = serializers.CharField(
        source="plant.company.name",
        read_only=True
    )

    class Meta:
        model = Department
        fields = [
            "id",
            "plant",
            "plant_name",
            "company_name",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]


class DepartmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = [
            "name",
            "is_active",
        ]

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Department name is required."
            )

        if Department.objects.filter(
            plant=self.instance.plant,
            name__iexact=value
        ).exclude(
            id=self.instance.id
        ).exists():

            raise serializers.ValidationError(
                "Department already exists."
            )

        return value