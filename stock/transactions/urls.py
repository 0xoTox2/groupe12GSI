# Django core imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local app imports
from .views import (
    
    PurchaseListView,
    PurchaseDetailView,
    PurchaseCreateView,
    PurchaseUpdateView,
    PurchaseDeleteView,
    wagner_whitin_view_2,
    select_policy, 
    fixed_replenishment, 
    point_replenishment,
    replenishment,
    wagner_whitin_view,
    degressive_replenishment, 
    degressive_replenishment_results,
    degressive_remise_replenishment, 
    degressive_remise_replenishment_results,
    SaleListView,
    SaleDetailView,
    SaleCreateView,
    SaleDeleteView,

    export_sales_to_excel,
    export_purchases_to_excel
)

# URL patterns
urlpatterns = [
    # Purchase URLs
    path('purchases/', PurchaseListView.as_view(), name='purchaseslist'),
    path('purchase/<slug:slug>/', PurchaseDetailView.as_view(),name='purchase-detail'),
    path('new-purchase/', PurchaseCreateView.as_view(),name='purchase-create' ),
    path('purchase/<int:pk>/update/', PurchaseUpdateView.as_view(),name='purchase-update'),
    path(
         'purchase/<int:pk>/delete/', PurchaseDeleteView.as_view(),
         name='purchase-delete'
     ),
    path('select-policy/', select_policy, name='select-policy'),
    path('fixed-replenishment/', fixed_replenishment, name='fixed-replenishment'),
    path('point-replenishment/', point_replenishment, name='point-replenishment'),
    path('replenishment/', replenishment, name='replenishment'),
    path('wagner-whitin/', wagner_whitin_view, name='wagner-whitin'),
    path('wagner-whitin-2/', wagner_whitin_view_2, name='wagner-whitin-2'),
    path('degressive-replenishment/', degressive_replenishment, name='degressive-replenishment'),
    path('degressive-replenishment/results/', degressive_replenishment_results, name='degressive-replenishment-results'),
    path('degressive-remise-replenishment/', degressive_remise_replenishment, name='degressive-remise-replenishment'),
path('degressive-remise-replenishment/results/', degressive_remise_replenishment_results, name='degressive-remise-replenishment-results'),
    # Sale URLs
    path('sales/', SaleListView.as_view(), name='saleslist'),
    path('sale/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
    path('new-sale/', SaleCreateView, name='sale-create'),
    path('sale/<slug:slug>/delete/', SaleDeleteView.as_view(),name='sale-delete'),

    # Sales and purchases export
    path('sales/export/', export_sales_to_excel, name='sales-export'),
    path('purchases/export/', export_purchases_to_excel,
         name='purchases-export'),
]

# Static media files configuration for development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
