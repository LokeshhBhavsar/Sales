from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from apps.accounts.models.permission import Permission
from apps.accounts.models import UserRole, user

class PermissionService:

    @staticmethod
    @transaction.atomic
    def create_permission(validated_data):

        permission = Permission.objects.create(

            company=validated_data["company"],

            plant=validated_data.get("plant"),

            department=validated_data.get("department"),

            scope=validated_data["scope"],

            module=validated_data["module"],

            action=validated_data["action"],

            code=validated_data["code"],

            description=validated_data.get("description"),

        )

        return permission

    @staticmethod
    def get_permissions_for_user(user):

      is_super_admin = UserRole.objects.filter(
        user=user,
        role__code="SUPER_ADMIN"
    ).exists()

      if is_super_admin:

       return Permission.objects.select_related(
            "company",
            "plant",
            "department"
        ).order_by(
            "module",
            "action"
        )

      queryset = Permission.objects.select_related(
            "company",
            "plant",
            "department"
        ).filter(
            company=user.company
        )

      if user.department:
            queryset = queryset.filter(
                Q(scope="company") |
                Q(scope="plant", plant=user.plant) |
                Q(
                    scope="department",
                    plant=user.plant,
                    department=user.department
                )
            )
      elif user.plant:
            queryset = queryset.filter(
                Q(scope="company") |
                Q(scope="plant", plant=user.plant) |
                Q(scope="department", plant=user.plant)
            )

      return queryset.order_by(
            "module",
            "action"
        )