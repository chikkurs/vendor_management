
"""
Vendor Performance Tracking System

This module defines a Django application for tracking and calculating performance metrics for vendors and their purchase orders.

Classes:
- UniqueVendorCodeField: A custom CharField to ensure uniqueness of the vendor_code in the Vendor model.

- Vendor: A Django model representing information about vendors, including name, contact details, address, and performance metrics such as on-time delivery rate, quality rating average, average response time, and fulfillment rate. It also provides methods to calculate these metrics.

- PurchaseOrder: A Django model representing purchase orders made to vendors, including details such as the purchase order number, vendor, order date, delivery date, items, quantity, status, quality rating, issue date, and acknowledgment date. It includes a method to calculate the response time.

- HistoricalPerformance: A Django model to store historical performance metrics for vendors, including on-time delivery rate, quality rating average, average response time, and fulfillment rate.

Note: This code assumes the existence of a Django project and database setup with appropriate configurations.

Usage:
- Import this module into your Django project.
- Use the Vendor model to manage vendor information and performance metrics.
- Use the PurchaseOrder model to track purchase orders and calculate response times.
- HistoricalPerformance model can be used to store historical performance metrics for vendors.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum, Avg
from django.utils import timezone

class UniqueVendorCodeField(models.CharField):
    def validate(self, value, model_instance):
        """
                Validate that the vendor_code is unique within the model.

                Args:
                - value (str): The vendor_code value to be validated.
                - model_instance: The instance of the model being validated.

                Raises:
                - ValidationError: If a vendor with the same vendor_code already exists in the database.
                """
        super().validate(value, model_instance)

        # Check for uniqueness of vendor_code
        existing_vendor = model_instance.__class__.objects.filter(vendor_code=value).exclude(id=model_instance.id).first()
        if existing_vendor:
            raise ValidationError('A vendor with this vendor code already exists.')

class Vendor(models.Model):
    """
        Model representing information about vendors and their performance metrics.

        Attributes:
        - name (str): The name of the vendor.
        - contact_details (str): The contact details of the vendor.
        - address (str): The address of the vendor.
        - vendor_code (UniqueVendorCodeField): A unique identifier for the vendor.
        - on_time_delivery_rate (float): The on-time delivery rate of the vendor.
        - quality_rating_avg (float): The average quality rating of the vendor.
        - average_response_time (float): The average response time of the vendor.
        - fulfillment_rate (float): The fulfillment rate of the vendor.

        Methods:
        - calculate_metrics(): Update performance metrics based on purchase order data.
        - calculate_fulfillment_rate(): Calculate and update the fulfillment rate.
        - calculate_average_response_time(): Calculate and update the average response time.
        - calculate_quality_rating_avg(): Calculate and update the average quality rating.
        - calculate_on_time_delivery_rate(): Calculate and update the on-time delivery rate.
        """
    name = models.CharField(max_length=255)
    contact_details = models.TextField(max_length=255)
    address = models.TextField(max_length=255)
    vendor_code = UniqueVendorCodeField(max_length=255, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def calculate_metrics(self):
        self.on_time_delivery_rate = self.calculate_on_time_delivery_rate()
        self.quality_rating_avg = self.calculate_quality_rating_avg()
        self.average_response_time = self.calculate_average_response_time()
        self.fulfillment_rate = self.calculate_fulfillment_rate()
        self.save()

    def calculate_fulfillment_rate(self):
        completed_pos = PurchaseOrder.objects.filter(
            vendor=self,
            status='completed'
        ).count()

        total_pos = PurchaseOrder.objects.filter(
            vendor=self
        ).count()

        print("completed_pos:", completed_pos)
        print("total_pos:", total_pos)

        if total_pos > 0:
            fulfillment_rate = (completed_pos / total_pos) * 100  # Multiply by 100 for percentage
            print("fulfillment_rate:", fulfillment_rate)
            return fulfillment_rate
        else:
            print("Returning 0 for fulfillment_rate.")
            return 0

    def calculate_average_response_time(self):
        response_times = []
        acknowledged_pos = PurchaseOrder.objects.filter(
            vendor=self,
            acknowledgment_date__isnull=False
        )

        for po in acknowledged_pos:
            response_times.append(po.calculate_response_time())

        if response_times:
            return sum(response_times) / len(response_times)
        return 0  # Default value if no response times are available

    def calculate_quality_rating_avg(self):
        completed_pos_with_rating = PurchaseOrder.objects.filter(
            vendor=self,
            status='completed',
            quality_rating__isnull=False
        )

        total_ratings = completed_pos_with_rating.aggregate(Avg('quality_rating'))['quality_rating__avg']

        if total_ratings is not None:
            return total_ratings
        return 0  # Default value if no ratings are available

    def calculate_on_time_delivery_rate(self):
        completed_pos = PurchaseOrder.objects.filter(
            vendor=self,
            status='completed'
        ).count()

        total_pos = PurchaseOrder.objects.filter(
            vendor=self
        ).count()

        print("completed_pos:", completed_pos)
        print("total_pos:", total_pos)

        if total_pos > 0:
            on_time_delivery_rate = (completed_pos / total_pos) * 100  # Multiply by 100 for percentage
            print("on_time_delivery_rate:", on_time_delivery_rate)
            return on_time_delivery_rate
        else:
            print("Returning 0 for on_time_delivery_rate.")
            return 0


class PurchaseOrder(models.Model):
    """
     Model representing purchase orders made to vendors.

     Attributes:
     - po_number (str): The purchase order number.
     - vendor (ForeignKey): Reference to the Vendor model.
     - order_date (DateTimeField): The date of the purchase order.
     - delivery_date (DateTimeField): The delivery date of the purchase order.
     - items (JSONField): JSON representation of the items in the purchase order.
     - quantity (int): The quantity of items in the purchase order.
     - status (str): The status of the purchase order (pending, completed, delivered, cancelled).
     - quality_rating (float): The quality rating assigned to the purchase order.
     - issue_date (DateTimeField): The date when the purchase order was issued.
     - acknowledgment_date (DateTimeField): The date when the purchase order was acknowledged.

     Methods:
     - calculate_response_time(): Calculate the response time for the purchase order.
     """
    po_number = models.CharField(unique=True, max_length=255)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders', db_index=True)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'completed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ])
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True, default=None)

    def calculate_response_time(self):
        if self.acknowledgment_date:
            return (self.acknowledgment_date - self.issue_date).total_seconds() / 60  # in minutes
        return 0

class HistoricalPerformance(models.Model):
    """
        Model representing historical performance metrics for vendors.

        Attributes:
        - vendor (ForeignKey): Reference to the Vendor model.
        - date (DateTimeField): The date for which the historical performance metrics are recorded.
        - on_time_delivery_rate (float): The on-time delivery rate for the specified date.
        - quality_rating_avg (float): The average quality rating for the specified date.
        - average_response_time (float): The average response time for the specified date.
        - fulfillment_rate (float): The fulfillment rate for the specified date.
        """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()
