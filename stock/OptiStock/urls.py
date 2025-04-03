from django.contrib import admin
from django.urls import path, include
from store.views import home  # Importez la vue home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Page d'accueil
    path('store/', include('store.urls')),
    path('staff/', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('accounts/', include('accounts.urls')),
    path('invoice/', include('invoice.urls')),
    path('bills/', include('bills.urls'))
]
