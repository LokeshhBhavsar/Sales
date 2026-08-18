from rest_framework import serializers

from apps.inventory.models.batch import Batch
from apps.inventory.models.item import Item
from apps.inventory.models.storage_location import StorageLocation
from apps.inventory.models.warehouse import Warehouse

from apps.masters.models.company import Company
from apps.masters.models.plant import Plant


# ============================================================
# RECEIVE STOCK
# ============================================================

class ReceiveStockSerializer(serializers.Serializer):

    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all()
    )

    plant = serializers.PrimaryKeyRelatedField(
        queryset=Plant.objects.all()
    )

    item = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all()
    )

    warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )

    storage_location = serializers.PrimaryKeyRelatedField(
        queryset=StorageLocation.objects.all()
    )

    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(),
        required=False,
        allow_null=True
    )

    quantity = serializers.DecimalField(
        max_digits=18,
        decimal_places=3,
        min_value=0.001
    )

    reference_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )


# ============================================================
# ISSUE STOCK
# ============================================================

class IssueStockSerializer(serializers.Serializer):

    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all()
    )

    plant = serializers.PrimaryKeyRelatedField(
        queryset=Plant.objects.all()
    )

    item = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all()
    )

    warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )

    storage_location = serializers.PrimaryKeyRelatedField(
        queryset=StorageLocation.objects.all()
    )

    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(),
        required=False,
        allow_null=True
    )

    quantity = serializers.DecimalField(
        max_digits=18,
        decimal_places=3,
        min_value=0.001
    )

    reference_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )


# ============================================================
# TRANSFER STOCK
# ============================================================

class TransferStockSerializer(serializers.Serializer):

    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all()
    )

    plant = serializers.PrimaryKeyRelatedField(
        queryset=Plant.objects.all()
    )

    item = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all()
    )

    from_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )

    from_location = serializers.PrimaryKeyRelatedField(
        queryset=StorageLocation.objects.all()
    )

    to_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )

    to_location = serializers.PrimaryKeyRelatedField(
        queryset=StorageLocation.objects.all()
    )

    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(),
        required=False,
        allow_null=True
    )

    quantity = serializers.DecimalField(
        max_digits=18,
        decimal_places=3,
        min_value=0.001
    )

    reference_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )


# ============================================================
# STOCK ADJUSTMENT
# ============================================================

class AdjustmentSerializer(serializers.Serializer):

    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all()
    )

    plant = serializers.PrimaryKeyRelatedField(
        queryset=Plant.objects.all()
    )

    item = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all()
    )

    warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )

    storage_location = serializers.PrimaryKeyRelatedField(
        queryset=StorageLocation.objects.all()
    )

    batch = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.all(),
        required=False,
        allow_null=True
    )

    quantity = serializers.DecimalField(
        max_digits=18,
        decimal_places=3,
        min_value=0.001
    )

    reference_number = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )