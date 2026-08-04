from rest_framework import serializers

from apps.masters.models.company import Company


class CompanyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a company.
    """

    class Meta:
        model = Company
        fields = [
            "name",
            "code",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Company name is required."
            )

        return value

    def validate_code(self, value):
        if value:
            value = value.strip().upper()

        return value


class CompanyListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing companies.
    """

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "code",
            "is_active",
            "created_at",
            "updated_at",
        ]


class CompanyDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for company details.
    """

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "code",
            "is_active",
            "created_at",
            "updated_at",
        ]


class CompanyUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a company.
    """

    class Meta:
        model = Company
        fields = [
            "name",
            "code",
            "is_active",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Company name is required."
            )

        return value

    def validate_code(self, value):

      if value:
        value = value.strip().upper()

        if Company.objects.filter(
            code__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "Company code already exists."
            )

        return value