from django.db import transaction

from apps.accounts.models.role import Role


class RoleService:
    """
    Service layer for Role operations.
    """

    @staticmethod
    @transaction.atomic
    def create_role(validated_data):
        """
        Create a new role.
        """
        return Role.objects.create(
            **validated_data
        )

    @staticmethod
    def get_roles():
        """
        Get all active roles.
        """
        return (
            Role.objects.select_related(
                "company",
                "plant",
                "department"
            )
            .filter(is_active=True)
            .order_by("name")
        )

    @staticmethod
    def get_role(role_id):
        """
        Get role by id.
        """
        return Role.objects.select_related(
            "company",
            "plant",
            "department"
        ).get(
            id=role_id
        )

    @staticmethod
    @transaction.atomic
    def update_role(role, validated_data):
        """
        Update role.
        """
        for field, value in validated_data.items():
            setattr(role, field, value)

        role.save()

        return role

    @staticmethod
    @transaction.atomic
    def delete_role(role):
        """
        Delete role.
        """
        role.delete()