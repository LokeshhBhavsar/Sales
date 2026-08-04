from rest_framework import serializers

from apps.accounts.models.role import Role
from apps.accounts.models.permission import Permission
from apps.accounts.models.role_permission import RolePermission


class RolePermissionAssignSerializer(serializers.Serializer):
    """
    Assign Permission to Role
    """

    role_id = serializers.UUIDField()
    permission_id = serializers.UUIDField()

    def validate(self, attrs):

        role_id = attrs.get("role_id")
        permission_id = attrs.get("permission_id")

        try:
            role = Role.objects.get(
                id=role_id,
                is_active=True
            )
        except Role.DoesNotExist:
            raise serializers.ValidationError({
                "role_id": "Role not found."
            })

        try:
            permission = Permission.objects.get(
                id=permission_id
            )
        except Permission.DoesNotExist:
            raise serializers.ValidationError({
                "permission_id": "Permission not found."
            })

        if RolePermission.objects.filter(
            role=role,
            permission=permission
        ).exists():

            raise serializers.ValidationError({
                "permission": "Permission already assigned to this role."
            })

        attrs["role"] = role
        attrs["permission"] = permission

        return attrs


    
class RolePermissionSerializer(serializers.ModelSerializer):

    role = serializers.CharField(
        source="role.name",
        read_only=True
    )

    permission = serializers.CharField(
        source="permission.code",
        read_only=True
    )

    class Meta:
        model = RolePermission
        fields = [
            "id",
            "role",
            "permission",
            "created_at",
        ]