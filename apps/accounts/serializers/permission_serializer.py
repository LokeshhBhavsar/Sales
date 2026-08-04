from rest_framework import serializers

from apps.accounts.models.permission import Permission


class PermissionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for Creating Permission
    """

    class Meta:
        model = Permission
        fields = [
            "module",
            "action",
            "code",
            "description",
        ]

    def validate_module(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Module is required."
            )

        return value

    def validate_action(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Action is required."
            )

        return value

    def validate_code(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Permission code is required."
            )

        return value

    def validate(self, attrs):

        module = attrs.get("module")
        action = attrs.get("action")
        code = attrs.get("code")

        # ----------------------------
        # Auto Generate Code
        # ----------------------------

        if not code:
            attrs["code"] = f"{module}.{action}"

        # ----------------------------
        # Duplicate Code
        # ----------------------------

        if Permission.objects.filter(
            code=attrs["code"]
        ).exists():

            raise serializers.ValidationError(
                {
                    "code": "Permission already exists."
                }
            )

        return attrs