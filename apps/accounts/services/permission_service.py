from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.accounts.models.permission import Permission


class PermissionService:

    @staticmethod
    @transaction.atomic
    def create_permission(validated_data):
        """
        Create Permission
        """

        module = validated_data["module"].strip().lower()
        action = validated_data["action"].strip().lower()

        code = validated_data.get("code")

        if code:
            code = code.strip().lower()
        else:
            code = f"{module}.{action}"

        if Permission.objects.filter(
            code=code
        ).exists():

            raise ValidationError({
                "code": "Permission already exists."
            })

        permission = Permission.objects.create(
            module=module,
            action=action,
            code=code,
            description=validated_data.get("description"),
        )

        return permission