
from django.urls import path
from .views import (
    VendorPerformanceView,
    UpdateAcknowledgmentView,
    PurchaseOrderListView,
    HistoricalPerformanceListView,
    BaseCreateView,
    VendorDetailView,
    VendorListView,
    PurchaseOrderDetailView,
)

app_name = 'vendor_app'

urlpatterns = [
    path('api/vendors/', VendorListView.as_view(), name='vendor-list'),
    path('api/vendors/<int:vendor_id>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('api/vendors/<int:vendor_id>/performance/', VendorPerformanceView.as_view(), name='vendor-performance'),

    path('api/purchase_orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('api/purchase_orders/<int:po_id>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),
    path('api/purchase_orders/<int:po_id>/acknowledge/', UpdateAcknowledgmentView.as_view(), name='update-acknowledgment'),

    path('api/historical_performances/', HistoricalPerformanceListView.as_view(), name='historical-performance-list'),

    path('api/vendors/create', BaseCreateView.as_view(), name='create-vendor'),
]
