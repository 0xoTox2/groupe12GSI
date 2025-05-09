# Django core imports
from django.urls import path
from .views import fabrication
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard, module,stock,facturation,personnels,fournisseurs_clients
# Local app imports
from . import views
from .views import finished_products_list , fabrication_history
from .views import FinishedProductCreateView, raw_materials_list
from .views import (
    FinishedProductUpdateView,
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ItemSearchListView,
    DeliveryListView,
    DeliveryDetailView,
    DeliveryCreateView,
    DeliveryUpdateView,
    DeliveryDeleteView,
    get_items_ajax_view,
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    ClientOrderListView,
    ClientOrderCreateView, 
    ClientOrderDetailView ,
    LaunchFabricationView,
    MarkAsReadyView,
    DeliverOrderView,
    confirm_fabrication
    
)

# URL patterns
urlpatterns = [
    path('finished-product/update/<slug:slug>/', FinishedProductUpdateView.as_view(), name='finished-product-update'),
    path('module/',module, name='module'),
     path(
        'new-finished-product/',
        FinishedProductCreateView.as_view(),
        name='finished-product-create'
    ),
   
    # Dashboard
    path('dashboard/',dashboard, name='dashboard'),
    path('stock/',stock, name='stock'),
    path('facturation/',facturation, name='facturation'),
    path('personnels/',personnels, name='personnels'),
    path('fournisseurs_clients/',fournisseurs_clients, name='fournisseurs_clients'),
    path('client-orders/<int:pk>/launch/', LaunchFabricationView.as_view(), name='launch-fabrication'),
    path('client-orders/<int:pk>/ready/', MarkAsReadyView.as_view(), name='mark-as-ready'),
    path('client-orders/<int:pk>/deliver/', DeliverOrderView.as_view(), name='deliver-order'),
    path('orders/<int:pk>/delete/', views.ClientOrderDeleteView.as_view(), name='client-order-delete'),
    path('fabrication/confirm/<int:fabrication_id>/', confirm_fabrication, name='confirm-fabrication'),
    # Product URLs
    path(
        'products/',
        ProductListView.as_view(),
        name='productslist'
    ),
    path(
        'product/<slug:slug>/',
        ProductDetailView.as_view(),
        name='product-detail'
    ),
    path(
        'new-product/',
        ProductCreateView.as_view(),
        name='product-create'
    ),
    path(
        'product/<slug:slug>/update/',
        ProductUpdateView.as_view(),
        name='product-update'
    ),
    path(
        'product/<slug:slug>/delete/',
        ProductDeleteView.as_view(),
        name='product-delete'
    ),

    # Item search
    path(
        'search/',
        ItemSearchListView.as_view(),
        name='item_search_list_view'
    ),

    # Delivery URLs
    path(
        'deliveries/',
        DeliveryListView.as_view(),
        name='deliveries'
    ),
    path(
        'delivery/<slug:slug>/',
        DeliveryDetailView.as_view(),
        name='delivery-detail'
    ),
    path(
        'new-delivery/',
        DeliveryCreateView.as_view(),
        name='delivery-create'
    ),
    path(
        'delivery/<int:pk>/update/',
        DeliveryUpdateView.as_view(),
        name='delivery-update'
    ),
    path(
        'delivery/<int:pk>/delete/',
        DeliveryDeleteView.as_view(),
        name='delivery-delete'
    ),

    # AJAX view
    path(
        'get-items/',
        get_items_ajax_view,
        name='get_items'
    ),

    # Category URLs
    path(
        'categories/',
        CategoryListView.as_view(),
        name='category-list'
    ),
    path(
        'categories/<int:pk>/',
        CategoryDetailView.as_view(),
        name='category-detail'
    ),
    path(
        'categories/create/',
        CategoryCreateView.as_view(),
        name='category-create'
    ),
    path(
        'categories/<int:pk>/update/',
        CategoryUpdateView.as_view(),
        name='category-update'
    ),
    path(
        'categories/<int:pk>/delete/',
        CategoryDeleteView.as_view(),
        name='category-delete'
    ),
    # Autres routes existantes...
    path('finished-products/', finished_products_list, name='finished_products_list'),
    path('raw-materials/', raw_materials_list, name='raw_materials_list'),
    path('fabrication-history/', fabrication_history, name='fabrication_history'),
    path('fabrication/', fabrication, name='fabrication'),

    path('client-orders/', ClientOrderListView.as_view(), name='client-orders-list'),
    path('client-orders/new/', ClientOrderCreateView.as_view(), name='client-order-create'),
    path('client-orders/<int:pk>/', ClientOrderDetailView.as_view(), name='client-order-detail'),
    
]


# Static media files configuration for development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
