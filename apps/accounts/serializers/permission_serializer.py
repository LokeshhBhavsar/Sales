from rest_framework import serializers

from apps.accounts.models.permission import Permission


class PermissionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = [
            "company",
            "plant",
            "department",
            "scope",
            "module",
            "action",
            "code",
            "description",
        ]

    def validate(self, attrs):

        company = attrs.get("company")
        plant = attrs.get("plant")
        department = attrs.get("department")
        scope = attrs.get("scope")

        module = attrs.get("module").strip().lower()
        action = attrs.get("action").strip().lower()
        code = attrs.get("code")

        attrs["module"] = module
        attrs["action"] = action

        if code:
            attrs["code"] = code.strip().lower()
        else:
            attrs["code"] = f"{module}.{action}"

        if not company:
            raise serializers.ValidationError({
                "company": "Company is required."
            })

        if scope == "company":

            attrs["plant"] = None
            attrs["department"] = None

        elif scope == "plant":

            if not plant:
                raise serializers.ValidationError({
                    "plant": "Plant is required."
                })

            if plant.company_id != company.id:
                raise serializers.ValidationError({
                    "plant": "Plant does not belong to selected company."
                })

            attrs["department"] = None

        elif scope == "department":

            if not plant:
                raise serializers.ValidationError({
                    "plant": "Plant is required."
                })

            if not department:
                raise serializers.ValidationError({
                    "department": "Department is required."
                })

            if plant.company_id != company.id:
                raise serializers.ValidationError({
                    "plant": "Plant does not belong to selected company."
                })

            if department.plant_id != plant.id:
                raise serializers.ValidationError({
                    "department": "Department does not belong to selected plant."
                })

        if Permission.objects.filter(
            company=company,
            plant=attrs.get("plant"),
            department=attrs.get("department"),
            module=module,
            action=action,
        ).exists():

            raise serializers.ValidationError({
                "permission": "Permission already exists."
            })

        return attrs


class PermissionSerializer(serializers.ModelSerializer):

    company_id = serializers.UUIDField(
        source="company.id",
        read_only=True
    )

    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    plant_id = serializers.UUIDField(
        source="plant.id",
        read_only=True
    )

    plant_name = serializers.CharField(
        source="plant.name",
        read_only=True
    )

    department_id = serializers.UUIDField(
        source="department.id",
        read_only=True
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    class Meta:

        model = Permission

        fields = [
            "id",

            "company_id",
            "company_name",

            "plant_id",
            "plant_name",

            "department_id",
            "department_name",

            "scope",

            "module",
            "action",
            "code",
            "description",

            "created_at",
        ]