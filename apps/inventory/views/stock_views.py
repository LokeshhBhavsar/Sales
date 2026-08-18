from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.inventory.services.stock_service import StockService
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.inventory.serializers.stock_operation_serializer import (
    ReceiveStockSerializer
)
from apps.inventory.services.stock_service import StockService



class StockListView(APIView):
    """
    GET /api/inventory/stock/

    Returns current inventory stock.
    """

    def get(self, request):
        try:
            stocks = StockService.list_stock(request)

            return Response(
                {
                    "success": True,
                    "message": "Stock retrieved successfully.",
                    "data": stocks,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StockDetailView(APIView):
    """
    GET /api/inventory/stock/<stock_id>/
    """

    def get(self, request, stock_id):
        try:
            stock = StockService.get_stock(stock_id)

            return Response(
                {
                    "success": True,
                    "message": "Stock retrieved successfully.",
                    "data": stock,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_404_NOT_FOUND,
            )




class ReceiveStockView(APIView):

    def post(self, request):

        serializer = ReceiveStockSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            result = StockService.receive_stock(
                **serializer.validated_data
            )

            return Response(
                {
                    "success": True,
                    "message": "Stock received successfully.",
                    "data": {
                        "stock_id": str(
                            result["stock"].id
                        ),
                        "movement_id": str(
                            result["movement"].id
                        ),
                        "previous_quantity": str(
                            result["previous_quantity"]
                        ),
                        "new_quantity": str(
                            result["new_quantity"]
                        )
                    }
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {
                    "success": False,
                    "message": "Failed to receive stock.",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class IssueStockView(APIView):
    """
    POST /api/inventory/stock/issue/

    Issue stock from warehouse.
    """

    def post(self, request):
        try:
            result = StockService.issue_stock(
                data=request.data,
                user=request.user,
            )

            return Response(
                {
                    "success": True,
                    "message": "Stock issued successfully.",
                    "data": result,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to issue stock.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransferStockView(APIView):
    """
    POST /api/inventory/stock/transfer/

    Transfer stock from one location to another.
    """

    def post(self, request):
        try:
            result = StockService.transfer_stock(
                data=request.data,
                user=request.user,
            )

            return Response(
                {
                    "success": True,
                    "message": "Stock transferred successfully.",
                    "data": result,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to transfer stock.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdjustStockView(APIView):
    """
    POST /api/inventory/stock/adjust/

    Adjust stock after physical stock verification.
    """

    def post(self, request):
        try:
            result = StockService.adjust_stock(
                data=request.data,
                user=request.user,
            )

            return Response(
                {
                    "success": True,
                    "message": "Stock adjusted successfully.",
                    "data": result,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to adjust stock.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )