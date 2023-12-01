"""
Serializers for Django Models and Data Transformations

This module contains serializers for Django models, data transformations, and utility functions.

Classes:
- VendorSerializer: Serializer for the Vendor model, providing validation for the vendor_code field.

- PurchaseOrderSerializer: Serializer for the PurchaseOrder model, including logic for creating and updating purchase orders and managing associated vendors.

- HistoricalPerformanceSerializer: Serializer for the HistoricalPerformance model, including logic for creating historical performance records.

- UpdateAcknowledgmentSerializer: Serializer for updating acknowledgment dates in purchase orders.

- VendorPerformanceSerializer: Serializer for vendor performance metrics.

Usage:
- Import these serializers into your Django project.
- Use the serializers to transform Django model instances into JSON and vice versa.
- Apply these serializers in views or other parts of your Django application to handle data input and output.

Note: This code assumes the existence of a Django project and models (Vendor, PurchaseOrder, HistoricalPerformance) with appropriate configurations.
"""
from .models import HistoricalPerformance, PurchaseOrder, Vendor
from rest_framework import serializers
from django.db import transaction


class VendorSerializer(serializers.ModelSerializer):
    """
        Serializer for the Vendor model.

        Fields:
        - id: Vendor identifier.
        - name: Vendor name.
        - contact_details: Vendor contact details.
        - address: Vendor address.
        - vendor_code: Unique vendor code.
        - on_time_delivery_rate: Vendor's on-time delivery rate.
        - quality_rating_avg: Vendor's average quality rating.
        - average_response_time: Vendor's average response time.
        - fulfillment_rate: Vendor's fulfillment rate.
        """
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_details', 'address', 'vendor_code', 'on_time_delivery_rate',
                  'quality_rating_avg', 'average_response_time', 'fulfillment_rate']

    def validate_vendor_code(self, value):
        instance = self.instance
        if instance and instance.vendor_code == value:
            return value  # No change, so it's okay

        existing_vendor = Vendor.objects.filter(vendor_code=value).first()
        if existing_vendor:
            raise serializers.ValidationError({'vendor_code': 'Vendor with this vendor code already exists.'})
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
        Serializer for the PurchaseOrder model.

        Fields:
        - id: Purchase order identifier.
        - po_number: Purchase order number.
        - vendor_code: Vendor code for associating the purchase order with a vendor.
        - order_date: Date of the purchase order.
        - delivery_date: Expected delivery date.
        - items: JSON representation of items in the purchase order.
        - quantity: Quantity of items.
        - status: Status of the purchase order (pending, completed, delivered, cancelled).
        - quality_rating: Quality rating assigned to the purchase order.
        - issue_date: Date when the purchase order was issued.
        - acknowledgment_date: Date when the purchase order was acknowledged.

        Methods:
        - create: Create a new purchase order instance.
        - update: Update an existing purchase order instance.
        - _get_or_create_vendor: Get or create a vendor instance associated with the purchase order.
        """

    vendor_code = serializers.CharField(write_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'vendor_code', 'order_date', 'delivery_date', 'items', 'quantity', 'status',
                  'quality_rating', 'issue_date', 'acknowledgment_date']

    def create(self, validated_data):
        vendor_code = validated_data.pop('vendor_code')
        vendor_instance = self._get_or_create_vendor(vendor_code)

        with transaction.atomic():
            validated_data['vendor'] = vendor_instance
            purchase_order_instance = PurchaseOrder.objects.create(**validated_data)

        return purchase_order_instance

    def update(self, instance, validated_data):
        vendor_data = validated_data.pop('vendor', None)

        if vendor_data:
            instance.vendor = self._get_or_create_vendor(vendor_data['vendor_code'])

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def _get_or_create_vendor(self, vendor_code):
        with transaction.atomic():
            vendor_instance, _ = Vendor.objects.get_or_create(vendor_code=vendor_code)
            return vendor_instance
class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    """
        Serializer for the HistoricalPerformance model.

        Fields:
        - id: Historical performance record identifier.
        - vendor: VendorSerializer instance representing the associated vendor.
        - date: Date for which the historical performance metrics are recorded.
        - on_time_delivery_rate: Historical on-time delivery rate.
        - quality_rating_avg: Historical average quality rating.
        - average_response_time: Historical average response time.
        - fulfillment_rate: Historical fulfillment rate.

        Methods:
        - create: Create a new historical performance record instance.
        """
    vendor = VendorSerializer()

    class Meta:
        model = HistoricalPerformance
        fields = ['id', 'vendor', 'date', 'on_time_delivery_rate', 'quality_rating_avg',
                  'average_response_time', 'fulfillment_rate']

    def create(self, validated_data):
        vendor_data = validated_data.pop('vendor')
        vendor_instance, _ = Vendor.objects.get_or_create(**vendor_data)

        historical_performance_instance = HistoricalPerformance.objects.create(vendor=vendor_instance, **validated_data)

        return historical_performance_instance

class UpdateAcknowledgmentSerializer(serializers.Serializer):
    """
        Serializer for updating acknowledgment dates in purchase orders.

        Fields:
        - acknowledgment_date: New acknowledgment date for the purchase order.
        """
    acknowledgment_date = serializers.DateTimeField()

class VendorPerformanceSerializer(serializers.Serializer):
    """
        Serializer for vendor performance metrics.

        Fields:s
        - on_time_delivery_rate: Vendor's on-time delivery rate.
        - quality_rating_avg: Vendor's average quality rating.
        - average_response_time: Vendor's average response time.
        - fulfillment_rate: Vendor's fulfillment rate.
        """
    on_time_delivery_rate = serializers.FloatField()
    quality_rating_avg = serializers.FloatField()
    average_response_time = serializers.FloatField()
    fulfillment_rate = serializers.FloatField()
