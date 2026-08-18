from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.serializers.category_serializer import CategorySerializer
from apps.inventory.services.category_service import CategoryService


class CategoryListCreateView(APIView):

    def get(self, request):

        queryset = CategoryService.list(
            company_id=request.query_params.get("company"),
            plant_id=request.query_params.get("plant"),
            is_active=request.query_params.get("is_active")
        )

        serializer = CategorySerializer(
            queryset,
            many=True
        )

        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })

    def post(self, request):

        serializer = CategorySerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        category = CategoryService.create(
            serializer.validated_data
        )

        return Response(
            {
                "success": True,
                "message": "Category created successfully.",
                "data": CategorySerializer(category).data
            },
            status=status.HTTP_201_CREATED
        )


class CategoryDetailView(APIView):

    def get(self, request, category_id):

        category = CategoryService.get_by_id(
            category_id
        )

        return Response({
            "success": True,
            "data": CategorySerializer(category).data
        })

    def put(self, request, category_id):

        category = CategoryService.get_by_id(
            category_id
        )

        serializer = CategorySerializer(
            category,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        category = CategoryService.update(
            category,
            serializer.validated_data
        )

        return Response({
            "success": True,
            "message": "Category updated successfully.",
            "data": CategorySerializer(category).data
        })

    def patch(self, request, category_id):

        category = CategoryService.get_by_id(
            category_id
        )

        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        category = CategoryService.update(
            category,
            serializer.validated_data
        )

        return Response({
            "success": True,
            "message": "Category updated successfully.",
            "data": CategorySerializer(category).data
        })

    def delete(self, request, category_id):

        category = CategoryService.get_by_id(
            category_id
        )

        CategoryService.deactivate(category)

        return Response({
            "success": True,
            "message": "Category deactivated successfully."
        })