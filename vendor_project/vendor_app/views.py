from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from rest_framework import status
from rest_framework.authentication import TokenAuthentication  # Add TokenAuthentication
from rest_framework.permissions import IsAuthenticated  # Add IsAuthenticated
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer, VendorPerformanceSerializer

class BaseCreateView(APIView):
    """
    Base class for creating and listing instances.

    Subclasses need to define `serializer_class` and `model_class`.
    """
    serializer_class = None
    model_class = None

    def post(self, request):
        """
        Create a new instance.

        Returns:
            Response: HTTP response with serialized instance data or errors.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        List all instances.

        Returns:
            Response: HTTP response with serialized instances data.
        """
        instances = self.model_class.objects.all()
        serializer = self.serializer_class(instances, many=True)
        return Response(serializer.data)

class VendorListView(BaseCreateView):
    """
    View for creating and listing Vendor instances.
    """
    serializer_class = VendorSerializer
    model_class = Vendor

class PurchaseOrderListView(BaseCreateView):
    """
    View for creating and listing PurchaseOrder instances.
    Supports filtering by vendor_id using query parameters.
    """
    serializer_class = PurchaseOrderSerializer
    model_class = PurchaseOrder

    def get(self, request):
        """
        List all PurchaseOrder instances or filter by vendor_id.

        Returns:
            Response: HTTP response with serialized instances data.
        """
        vendor_id = request.query_params.get('vendor_id')
        if vendor_id:
            instances = self.model_class.objects.filter(vendor__id=vendor_id)
        else:
            instances = self.model_class.objects.all()

        serializer = self.serializer_class(instances, many=True)
        return Response(serializer.data)

class HistoricalPerformanceListView(BaseCreateView):
    """
    View for creating and listing HistoricalPerformance instances.
    """
    serializer_class = HistoricalPerformanceSerializer
    model_class = HistoricalPerformance

class VendorDetailView(APIView):
    """
    View for retrieving, updating, and deleting Vendor instances.
    """
    serializer_class = VendorSerializer
    model_class = Vendor

    def get(self, request, vendor_id):
        """
        Retrieve a specific Vendor instance.

        Returns:
            Response: HTTP response with serialized instance data or 404 if not found.
        """
        instance = get_object_or_404(self.model_class, id=vendor_id)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def put(self, request, vendor_id):
        """
        Update a specific Vendor instance.

        Returns:
            Response: HTTP response with serialized instance data or errors.
        """
        instance = get_object_or_404(self.model_class, id=vendor_id)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, vendor_id):
        """
        Delete a specific Vendor instance.

        Returns:
            Response: HTTP response with 204 status.
        """
        instance = get_object_or_404(self.model_class, id=vendor_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PurchaseOrderDetailView(APIView):
    """
    View for retrieving, updating, and deleting PurchaseOrder instances.
    """
    serializer_class = PurchaseOrderSerializer
    model_class = PurchaseOrder

    def get(self, request, po_id):
        """
        Retrieve a specific PurchaseOrder instance.

        Returns:
            Response: HTTP response with serialized instance data or 404 if not found.
        """
        instance = get_object_or_404(self.model_class, id=po_id)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def delete(self, request, po_id):
        """
        Delete a specific PurchaseOrder instance.

        Returns:
            Response: HTTP response with 204 status.
        """
        instance = get_object_or_404(self.model_class, id=po_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, po_id):
        """
        Update a specific PurchaseOrder instance.

        Returns:
            Response: HTTP response with serialized instance data or errors.
        """
        instance = get_object_or_404(self.model_class, id=po_id)
        serializer = self.serializer_class(instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VendorPerformanceView(APIView):
    """
    View for retrieving Vendor performance metrics.
    """
    serializer_class = VendorPerformanceSerializer
    authentication_classes = [TokenAuthentication]  # Add TokenAuthentication
    permission_classes = [IsAuthenticated]  # Add IsAuthenticated

    def get(self, request, vendor_id):
        """
        Retrieve performance metrics for a specific Vendor.

        Returns:
            Response: HTTP response with serialized performance metrics.
        """
        vendor = get_object_or_404(Vendor, id=vendor_id)

        # Calculate the performance metrics
        on_time_delivery_rate = vendor.calculate_on_time_delivery_rate()
        quality_rating_avg = vendor.calculate_quality_rating_avg()
        average_response_time = vendor.calculate_average_response_time()
        fulfillment_rate = vendor.calculate_fulfillment_rate()

        data = {
            'on_time_delivery_rate': on_time_delivery_rate,
            'quality_rating_avg': quality_rating_avg,
            'average_response_time': average_response_time,
            'fulfillment_rate': fulfillment_rate,
        }

        serializer = self.serializer_class(data)
        return Response(serializer.data)

class UpdateAcknowledgmentView(APIView):
    """
    View for retrieving acknowledgment date of a PurchaseOrder.
    """
    authentication_classes = [TokenAuthentication]  # Add TokenAuthentication
    permission_classes = [IsAuthenticated]  # Add IsAuthenticated

    def get(self, request, po_id):
        """
        Retrieve acknowledgment date for a specific PurchaseOrder.

        Returns:
            Response: HTTP response with acknowledgment date or 400 if not available.
        """
        purchase_order = get_object_or_404(PurchaseOrder, id=po_id)
        acknowledgment_date = purchase_order.acknowledgment_date

        if acknowledgment_date is None:
            return Response({'detail': 'Acknowledgment date is not available.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'acknowledgment_date': acknowledgment_date}, status=status.HTTP_200_OK)
