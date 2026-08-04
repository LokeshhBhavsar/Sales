from rest_framework.permissions import BasePermission

from apps.accounts.models.user_role import UserRole


class IsSuperAdmin(BasePermission):
    """
    Only Super Admin can access.
    """

    message = "Only Super Admin can perform this action."

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        print("\n========== SUPER ADMIN CHECK ==========")
        print("User ID:", request.user.id)
        print("Email:", request.user.email)

        roles = UserRole.objects.filter(
            user_id=request.user.id
        ).values(
            "role__name",
            "role__code"
        )

        print("Roles:", list(roles))

        is_super_admin = UserRole.objects.filter(
            user_id=request.user.id,
            role__code__iexact="SUPER_ADMIN"
        ).exists()

        print("Is Super Admin:", is_super_admin)
        print("=======================================\n")

        return is_super_admin


class IsSuperAdminOrCompanyAdmin(BasePermission):

    message = "Permission denied."

    def has_object_permission(self, request, view, obj):

        if not request.user.is_authenticated:
            return False

        if UserRole.objects.filter(
            user_id=request.user.id,
            role__code__iexact="SUPER_ADMIN"
        ).exists():
            return True

        if UserRole.objects.filter(
            user_id=request.user.id,
            role__code__iexact="COMPANY_ADMIN"
        ).exists():

            return request.user.company_id == obj.id

        return False