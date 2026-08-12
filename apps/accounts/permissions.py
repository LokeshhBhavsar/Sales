# from rest_framework.permissions import BasePermission

# from apps.accounts.models.user_role import UserRole


# class IsSuperAdmin(BasePermission):

#     message = "Only Super Admin can perform this action."

#     def has_permission(self, request, view):

#         if not request.user.is_authenticated:
#             return False

#         return UserRole.objects.filter(
#             user=request.user,
#             role__code__iexact="SUPER_ADMIN"
#         ).exists()




from rest_framework.permissions import BasePermission

from apps.accounts.models.user_role import UserRole


class IsSuperAdmin(BasePermission):

    message = "Only Super Admin can perform this action."

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return (
            request.user.is_superuser
            or
            UserRole.objects.filter(
                user=request.user,
                role__code__iexact="SUPER_ADMIN",
                role__is_active=True
            ).exists()
        )


class IsPlantAdmin(BasePermission):

    message = (
        "Only Plant Head or Plant HR can perform this action."
    )

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return UserRole.objects.filter(
            user=request.user,
            role__code__in=[
                "PLANT_HEAD",
                "PLANT_HR"
            ],
            role__level="plant",
            role__is_active=True
        ).exists()


class IsDepartmentHead(BasePermission):

    message = "Only Department Head can perform this action."

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return UserRole.objects.filter(
            user=request.user,
            role__code="DEPARTMENT_HEAD",
            role__level="department",
            role__is_active=True
        ).exists()