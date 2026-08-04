from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.accounts.models.role_permission import RolePermission


class RolePermissionService:

    @staticmethod
    @transaction.atomic
    def assign_permission(validated_data):
        """
        Assign Permission to Role
        """

        role = validated_data["role"]
        permission = validated_data["permission"]

        if RolePermission.objects.filter(
            role=role,
            permission=permission
        ).exists():

            raise ValidationError({
                "permission": "Permission already assigned to this role."
            })

        role_permission = RolePermission.objects.create(
            role=role,
            permission=permission
        )

        return role_permission

    @staticmethod
    @transaction.atomic
    def remove_permission(role, permission):
        """
        Remove Permission from Role
        """

        deleted, _ = RolePermission.objects.filter(
            role=role,
            permission=permission
        ).delete()

        if deleted == 0:
            raise ValidationError({
                "permission": "Permission is not assigned to this role."
            })

        return True