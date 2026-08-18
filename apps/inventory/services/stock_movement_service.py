from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.db.models import Q

from apps.inventory.models.stock_movement import StockMovement


class StockMovementService:

    @staticmethod
    def get_by_id(movement_id):

        try:

            return (
                StockMovement.objects
                .select_related(
                    "company",
                    "plant",
                    "item",
                    "batch",
                    "from_warehouse",
                    "from_location",
                    "to_warehouse",
                    "to_location"
                )
                .get(id=movement_id)
            )

        except StockMovement.DoesNotExist:

            raise ValidationError(
                "Stock movement not found."
            )

    @staticmethod
    def list(
        *,
        company_id=None,
        plant_id=None,
        item_id=None,
        batch_id=None,
        movement_type=None,
        warehouse_id=None
    ):

        queryset = (
            StockMovement.objects
            .select_related(
                "company",
                "plant",
                "item",
                "batch",
                "from_warehouse",
                "from_location",
                "to_warehouse",
                "to_location"
            )
        )

        if company_id:
            queryset = queryset.filter(
                company_id=company_id
            )

        if plant_id:
            queryset = queryset.filter(
                plant_id=plant_id
            )

        if item_id:
            queryset = queryset.filter(
                item_id=item_id
            )

        if batch_id:
            queryset = queryset.filter(
                batch_id=batch_id
            )

        if movement_type:
            queryset = queryset.filter(
                movement_type=movement_type
            )

        if warehouse_id:

            queryset = queryset.filter(
                from_warehouse_id=warehouse_id
            ) | queryset.filter(
                to_warehouse_id=warehouse_id
            )

        return queryset.order_by(
            "-created_at"
        )

    @staticmethod
    def get_item_history(
        *,
        item_id,
        plant_id=None
    ):

        queryset = (
            StockMovement.objects
            .select_related(
                "item",
                "batch",
                "from_warehouse",
                "from_location",
                "to_warehouse",
                "to_location"
            )
            .filter(
                item_id=item_id
            )
        )

        if plant_id:
            queryset = queryset.filter(
                plant_id=plant_id
            )

        return queryset.order_by(
            "-created_at"
        )

    @staticmethod
    def get_batch_history(batch_id):

        return (
            StockMovement.objects
            .select_related(
                "item",
                "batch",
                "from_warehouse",
                "from_location",
                "to_warehouse",
                "to_location"
            )
            .filter(
                batch_id=batch_id
            )
            .order_by(
                "-created_at"
            )
        )