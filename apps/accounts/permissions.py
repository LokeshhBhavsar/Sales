from rest_framework.permissions import BasePermission

from apps.accounts.models.user_role import UserRole


class IsSuperAdmin(BasePermission):

    message = "Only Super Admin can perform this action."

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return UserRole.objects.filter(
            user=request.user,
            role__code__iexact="SUPER_ADMIN"
        ).exists()