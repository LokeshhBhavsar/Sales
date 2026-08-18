from rest_framework import serializers

from apps.inventory.models.item import Item


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item

        fields = [
            "id",
            "company",
            "plant",
            "category",
            "uom",
            "code",
            "name",
            "item_type",
            "description",
            "minimum_stock",
            "maximum_stock",
            "is_batch_required",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        category = attrs.get("category")
        uom = attrs.get("uom")
        plant = attrs.get("plant")

        if category and plant:
            if category.plant_id != plant.id:
                raise serializers.ValidationError(
                    "Category does not belong to the selected plant."
                )

        if uom and plant:
            if uom.plant_id != plant.id:
                raise serializers.ValidationError(
                    "UOM does not belong to the selected plant."
                )

        minimum = attrs.get("minimum_stock")
        maximum = attrs.get("maximum_stock")

        if minimum is not None and maximum is not None:
            if maximum < minimum:
                raise serializers.ValidationError(
                    "Maximum stock cannot be less than minimum stock."
                )

        return attrs    