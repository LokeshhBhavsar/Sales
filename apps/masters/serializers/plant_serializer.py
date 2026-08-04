from rest_framework import serializers

from apps.masters.models.company import Company
from apps.masters.models.plant import Plant


class PlantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Plant.
    """

    company = serializers.UUIDField(write_only=True)

    class Meta:
        model = Plant
        fields = [
            "company",
            "name",
            "location",
        ]

    def validate_company(self, value):

        try:
            company = Company.objects.get(id=value)

        except Company.DoesNotExist:
            raise serializers.ValidationError(
                "Company does not exist."
            )

        return company

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Plant name is required."
            )

        return value

    def validate(self, attrs):

        company = attrs["company"]
        name = attrs["name"]

        if Plant.objects.filter(
            company=company,
            name__iexact=name
        ).exists():

            raise serializers.ValidationError(
                {
                    "name": "Plant already exists for this company."
                }
            )

        return attrs


class PlantListSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:
        model = Plant
        fields = [
            "id",
            "company_name",
            "name",
            "location",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PlantDetailSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:
        model = Plant
        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "location",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PlantUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plant
        fields = [
            "name",
            "location",
            "is_active",
        ]

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Plant name is required."
            )

        if Plant.objects.filter(
            company=self.instance.company,
            name__iexact=value
        ).exclude(
            id=self.instance.id
        ).exists():

            raise serializers.ValidationError(
                "Plant already exists."
            )

        return value