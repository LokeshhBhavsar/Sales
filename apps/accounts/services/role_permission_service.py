# from django.db import transaction

# from rest_framework.exceptions import ValidationError

# from apps.accounts.models.role_permission import RolePermission


# class RolePermissionService:

#     @staticmethod
#     @transaction.atomic
#     def assign_permission(validated_data):

#         role = validated_data["role"]
#         permission = validated_data["permission"]

#         if RolePermission.objects.filter(
#             role=role,
#             permission=permission
#         ).exists():

#             raise ValidationError({
#                 "permission": "Permission already assigned."
#             })

#         return RolePermission.objects.create(
#             role=role,
#             permission=permission
#         )

#     @staticmethod
#     def get_role_permissions(role_id):

#         return RolePermission.objects.select_related(
#             "role",
#             "permission",
#             "permission__company",
#             "permission__plant",
#             "permission__department"
#         ).filter(
#             role_id=role_id
#         ).order_by(
#             "permission__module",
#             "permission__action"
#         )

#     @staticmethod
#     @transaction.atomic
#     def remove_permission(role, permission):

#         deleted, _ = RolePermission.objects.filter(
#             role=role,
#             permission=permission
#         ).delete()

#         if deleted == 0:
#             raise ValidationError({
#                 "permission":
#                 "Permission is not assigned."
#             })

#         return True



from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.accounts.models.role_permission import RolePermission


class RolePermissionService:

    @staticmethod
    @transaction.atomic
    def assign_permission(validated_data):

        role = validated_data["role"]

        permission = validated_data["permission"]

        if RolePermission.objects.filter(
            role=role,
            permission=permission
        ).exists():

            raise ValidationError({
                "permission":
                    "Permission already assigned to this role."
            })

        return RolePermission.objects.create(
            role=role,
            permission=permission
        )

    @staticmethod
    @transaction.atomic
    def remove_permission(
        role,
        permission
    ):

        deleted, _ = (
            RolePermission.objects
            .filter(
                role=role,
                permission=permission
            )
            .delete()
        )

        if deleted == 0:

            raise ValidationError({
                "permission":
                    "Permission is not assigned to this role."
            })

        return True