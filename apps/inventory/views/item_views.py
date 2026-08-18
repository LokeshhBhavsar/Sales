from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.serializers.item_serializer import ItemSerializer
from apps.inventory.services.item_service import ItemService


class ItemListCreateView(APIView):

    def get(self, request):

        queryset = ItemService.list(
            company_id=request.query_params.get("company"),
            plant_id=request.query_params.get("plant"),
            category_id=request.query_params.get("category"),
            item_type=request.query_params.get("item_type"),
            is_active=request.query_params.get("is_active")
        )

        serializer = ItemSerializer(
            queryset,
            many=True
        )

        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })

    def post(self, request):

        serializer = ItemSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        item = ItemService.create(
            serializer.validated_data
        )

        return Response(
            {
                "success": True,
                "message": "Item created successfully.",
                "data": ItemSerializer(item).data
            },
            status=status.HTTP_201_CREATED
        )


class ItemDetailView(APIView):

    def get(self, request, item_id):

        item = ItemService.get_by_id(
            item_id
        )

        return Response({
            "success": True,
            "data": ItemSerializer(item).data
        })

    def put(self, request, item_id):

        item = ItemService.get_by_id(
            item_id
        )

        serializer = ItemSerializer(
            item,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        item = ItemService.update(
            item,
            serializer.validated_data
        )

        return Response({
            "success": True,
            "message": "Item updated successfully.",
            "data": ItemSerializer(item).data
        })

    def patch(self, request, item_id):

        item = ItemService.get_by_id(
            item_id
        )

        serializer = ItemSerializer(
            item,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        item = ItemService.update(
            item,
            serializer.validated_data
        )

        return Response({
            "success": True,
            "message": "Item updated successfully.",
            "data": ItemSerializer(item).data
        })

    def delete(self, request, item_id):

        item = ItemService.get_by_id(
            item_id
        )

        ItemService.deactivate(item)

        return Response({
            "success": True,
            "message": "Item deactivated successfully."
        })