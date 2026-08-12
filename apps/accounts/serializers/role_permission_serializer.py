# from rest_framework import serializers

# from apps.accounts.models.role import Role
# from apps.accounts.models.permission import Permission
# from apps.accounts.models.role_permission import RolePermission


# class RolePermissionAssignSerializer(serializers.Serializer):

#     role_id = serializers.UUIDField()
#     permission_id = serializers.UUIDField()

#     def validate(self, attrs):

#         try:
#             role = Role.objects.get(
#                 id=attrs["role_id"],
#                 is_active=True
#             )
#         except Role.DoesNotExist:
#             raise serializers.ValidationError({
#                 "role_id": "Role not found."
#             })

#         try:
#             permission = Permission.objects.get(
#                 id=attrs["permission_id"]
#             )
#         except Permission.DoesNotExist:
#             raise serializers.ValidationError({
#                 "permission_id": "Permission not found."
#             })

#         # -----------------------------------
#         # Same Company
#         # -----------------------------------

#         if role.company_id != permission.company_id:

#             raise serializers.ValidationError({
#                 "company":
#                 "Role and Permission belong to different companies."
#             })

#         # -----------------------------------
#         # Plant Validation
#         # -----------------------------------

#         if permission.scope == "plant":

#             if role.plant_id != permission.plant_id:

#                 raise serializers.ValidationError({
#                     "plant":
#                     "Role and Permission belong to different plants."
#                 })

#         # -----------------------------------
#         # Department Validation
#         # -----------------------------------

#         if permission.scope == "department":

#             if role.department_id != permission.department_id:

#                 raise serializers.ValidationError({
#                     "department":
#                     "Role and Permission belong to different departments."
#                 })

#         if RolePermission.objects.filter(
#             role=role,
#             permission=permission
#         ).exists():

#             raise serializers.ValidationError({
#                 "permission":
#                 "Permission already assigned."
#             })

#         attrs["role"] = role
#         attrs["permission"] = permission

#         return attrs

# class RolePermissionSerializer(serializers.ModelSerializer):

#     role_id = serializers.UUIDField(
#         source="role.id",
#         read_only=True
#     )

#     role_name = serializers.CharField(
#         source="role.name",
#         read_only=True
#     )

#     company = serializers.CharField(
#         source="permission.company.name",
#         read_only=True
#     )

#     plant = serializers.CharField(
#         source="permission.plant.name",
#         read_only=True
#     )

#     department = serializers.CharField(
#         source="permission.department.name",
#         read_only=True
#     )

#     scope = serializers.CharField(
#         source="permission.scope",
#         read_only=True
#     )

#     module = serializers.CharField(
#         source="permission.module",
#         read_only=True
#     )

#     action = serializers.CharField(
#         source="permission.action",
#         read_only=True
#     )

#     permission = serializers.CharField(
#         source="permission.code",
#         read_only=True
#     )

#     class Meta:
#         model = RolePermission
#         fields = [
#             "id",
#             "role_id",
#             "role_name",
#             "company",
#             "plant",
#             "department",
#             "scope",
#             "module",
#             "action",
#             "permission",
#             "created_at",
#         ]




from rest_framework import serializers

from apps.accounts.models.role import Role
from apps.accounts.models.permission import Permission
from apps.accounts.models.role_permission import RolePermission


class RolePermissionAssignSerializer(
    serializers.Serializer
):

    role_id = serializers.UUIDField()

    permission_id = serializers.UUIDField()

    def validate(self, attrs):

        role_id = attrs["role_id"]

        permission_id = attrs["permission_id"]

        try:

            role = Role.objects.get(
                id=role_id,
                is_active=True
            )

        except Role.DoesNotExist:

            raise serializers.ValidationError({
                "role_id":
                    "Role not found."
            })

        try:

            permission = Permission.objects.get(
                id=permission_id
            )

        except Permission.DoesNotExist:

            raise serializers.ValidationError({
                "permission_id":
                    "Permission not found."
            })

        # ---------------------------------------------
        # Company validation
        # ---------------------------------------------

        if role.company_id != permission.company_id:

            raise serializers.ValidationError({
                "permission":
                    "Permission does not belong to role company."
            })

        # ---------------------------------------------
        # Plant role validation
        # ---------------------------------------------

        if role.scope == "plant":

            if permission.scope== "plant":

                if role.plant_id != permission.plant_id:

                    raise serializers.ValidationError({
                        "permission":
                            "Permission does not belong to role plant."
                    })

            elif permission.scope == "department":

                if role.plant_id != permission.plant_id:

                    raise serializers.ValidationError({
                        "permission":
                            "Permission does not belong to role plant."
                    })

        # ---------------------------------------------
        # Department role validation
        # ---------------------------------------------

        if role.scope == "department":

            if permission.scope == "plant":

                if role.plant_id != permission.plant_id:

                    raise serializers.ValidationError({
                        "permission":
                            "Permission does not belong to role plant."
                    })

            if permission.scope == "department":

                if (
                    role.plant_id != permission.plant_id
                    or
                    role.department_id != permission.department_id
                ):

                    raise serializers.ValidationError({
                        "permission":
                            "Permission does not belong to role department."
                    })

        # ---------------------------------------------
        # Duplicate
        # ---------------------------------------------

        if RolePermission.objects.filter(
            role=role,
            permission=permission
        ).exists():

            raise serializers.ValidationError({
                "permission":
                    "Permission already assigned to this role."
            })

        attrs["role"] = role

        attrs["permission"] = permission

        return attrs


class RolePermissionSerializer(
    serializers.ModelSerializer
):

    role_name = serializers.CharField(
        source="role.name",
        read_only=True
    )

    role_code = serializers.CharField(
        source="role.code",
        read_only=True
    )

    permission_code = serializers.CharField(
        source="permission.code",
        read_only=True
    )

    class Meta:

        model = RolePermission

        fields = [
            "id",

            "role_name",
            "role_code",

            "permission_code",

            "created_at",
        ]