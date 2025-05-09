# Standard library imports
import operator
from functools import reduce

# Django core imports
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum

# Authentication and permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Class-based views
from django.views.generic import (
    DetailView, CreateView, UpdateView, DeleteView, ListView
)
from django.views.generic.edit import FormMixin

# Third-party packages
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin

# Local app imports
from accounts.models import Profile, Vendor
from transactions.models import Sale
from .models import Category, Item, Delivery
from .forms import ItemForm, CategoryForm, DeliveryForm
from .tables import ItemTable

#fabrication 
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, Sum
from .models import Nomenclature, Fabrication, Item

def home(request):
    return render(request, 'store/home.html')

@login_required
def module(request):
    return render(request, 'store/module.html')

def get_common_context(module_name=None):
    profiles = Profile.objects.all()
    items = Item.objects.all()
    total_items = items.aggregate(Sum("quantity")).get("quantity__sum", 0.00)
    
    # Préparation des données pour les graphiques
    category_counts = Category.objects.annotate(item_count=Count("item"))
    categories = [cat.name for cat in category_counts]
    category_counts_values = [cat.item_count for cat in category_counts]

    sale_dates = Sale.objects.values("date_added__date").annotate(total_sales=Sum("grand_total")).order_by("date_added__date")
    sale_dates_labels = [date["date_added__date"].strftime("%Y-%m-%d") for date in sale_dates]
    sale_dates_values = [float(date["total_sales"]) for date in sale_dates]
    
    context = {
        "items": items,
        "profiles": profiles,
        "profiles_count": profiles.count(),
        "items_count": items.count(),
        "total_items": total_items,
        "vendors": Vendor.objects.all(),
        "delivery": Delivery.objects.all(),
        "sales": Sale.objects.all(),
        "categories": categories,
        "category_counts": category_counts,
        "sale_dates_labels": sale_dates_labels,
        "sale_dates_values": sale_dates_values,
    }
    if module_name:
        context["module_name"] = module_name  # Ajout du module_name si fourni

    return context

from .models import Item, Fabrication


def fabrication_history(request):
    # Récupérer toutes les fabrications
    fabrications = Fabrication.objects.all().order_by('-date_created')
    
    # Contexte pour le template
    context = {
        'fabrications': fabrications,
    }
    return render(request, 'store/fabrication_history.html', context)

def raw_materials_list(request):
    # Récupérer toutes les matières premières (is_finished_product=False)
    raw_materials = Item.objects.filter(is_finished_product=False)
    
    # Contexte pour le template
    context = {
        'raw_materials': raw_materials,
    }
    return render(request, 'store/raw_materials_list.html', context)

def finished_products_list(request):
    # Récupérer tous les produits finis
    finished_products = Item.objects.filter(is_finished_product=True)
    
    # Contexte pour le template
    context = {
        'finished_products': finished_products,
    }
 
    return render(request, 'store/finished_products_list.html', context)

from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta

def dashboard(request):
    # 1. Données de base
    profiles = Profile.objects.all()
    items = Item.objects.all()
    total_items = items.aggregate(total=Sum('quantity'))['total'] or 0
    vendors = Vendor.objects.all()
    deliveries = Delivery.objects.all()
    sales = Sale.objects.all()
    
    # 2. Données pour les produits finis et matières premières
    finished_products = Item.objects.filter(is_finished_product=True)
    raw_materials = Item.objects.filter(is_finished_product=False)
    
    total_finished_products = finished_products.aggregate(total=Sum('quantity'))['total'] or 0
    total_raw_materials = raw_materials.aggregate(total=Sum('quantity'))['total'] or 0

    # 3. Fabrication et production
    recent_fabrications = Fabrication.objects.all().order_by('-date_created')[:5]
    total_fabrications = Fabrication.objects.count()
    
    # 4. Commandes clients
    client_orders = ClientOrder.objects.all()
    pending_orders = client_orders.filter(status='pending').count()
    orders_in_production = client_orders.filter(status='processing').count()
    completed_orders = client_orders.filter(status='delivered').count()

    # 5. Alertes et stocks
    low_stock_alerts = Item.objects.filter(quantity__lt=F('stock_min')).select_related('category')
    critical_stock = Item.objects.filter(quantity__lt=5).count()
    
    # 6. Top produits (stock et ventes)
    top_products = Item.objects.order_by('-quantity')[:5]
    
    # Calcul du chiffre d'affaires (30 derniers jours)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_revenue = Sale.objects.filter(
        date_added__gte=thirty_days_ago
    ).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Top produits vendus - Utilisation de la relation saledetail visible dans l'erreur
    top_selling_products = Item.objects.annotate(
        total_sold=Sum('saledetail__quantity')
    ).order_by('-total_sold').exclude(total_sold=None)[:5]

    # 7. Données pour les graphiques
    # Graphique circulaire - Répartition par catégorie
    category_counts = Category.objects.annotate(
        item_count=Count('item'),
        total_quantity=Sum('item__quantity')
    ).exclude(item_count=0)
    
    categories = [cat.name for cat in category_counts]
    category_quantities = [cat.total_quantity for cat in category_counts]

    # Graphique linéaire - Ventes sur 30 jours
    sale_dates = Sale.objects.filter(
        date_added__gte=thirty_days_ago
    ).values('date_added__date').annotate(
        total_sales=Sum('grand_total')
    ).order_by('date_added__date')
    
    sale_dates_labels = [date["date_added__date"].strftime("%d/%m") for date in sale_dates]
    sale_dates_values = [float(date["total_sales"] or 0) for date in sale_dates]

    # Graphique de production - Fabrications par jour (7 derniers jours)
    seven_days_ago = timezone.now() - timedelta(days=7)
    fabrications_by_day = Fabrication.objects.filter(
        date_created__gte=seven_days_ago
    ).values('date_created__date').annotate(
        total=Count('id'),
        quantity_sum=Sum('quantity')
    ).order_by('date_created__date')
    
    fabrication_dates = [fab["date_created__date"].strftime("%d/%m") for fab in fabrications_by_day]
    fabrication_counts = [fab["total"] for fab in fabrications_by_day]
    fabrication_quantities = [fab["quantity_sum"] for fab in fabrications_by_day]

    raw_materials_table = Item.objects.filter(is_finished_product=False).order_by('-quantity')
    finished_products_table = Item.objects.filter(is_finished_product=True).order_by('-quantity')

    # 8. Calcul des tendances (pour les indicateurs %)
    # Calcul simplifié - en pratique vous voudrez comparer avec la période précédente
    sales_trend = 12  # % fictif pour l'exemple
    stock_trend = -5   # % fictif pour l'exemple
    production_trend = 8  # % fictif pour l'exemple
    delivery_trend = 15  # % fictif pour l'exemple

    # Contexte complet
    context = {
        # Données de base
        'profiles_count': profiles.count(),
        'items_count': items.count(),
        'total_items': total_items,
        'delivery_count': deliveries.count(),
        'sales_count': sales.count(),
        
        # Produits finis/matières premières
        'total_finished_products': total_finished_products,
        'total_raw_materials': total_raw_materials,
        
        # Production
        'recent_fabrications': recent_fabrications,
        'total_fabrications': total_fabrications,
        'fabrication_dates': fabrication_dates,
        'fabrication_counts': fabrication_counts,
        'fabrication_quantities': fabrication_quantities,
        
        # Commandes
        'client_orders': client_orders,
        'pending_orders': pending_orders,
        'orders_in_production': orders_in_production,
        'completed_orders': completed_orders,
        
        # Stocks
        'low_stock_alerts': low_stock_alerts,
        'critical_stock': critical_stock,
        'top_products': top_products,
        
        # Ventes
        'total_revenue': total_revenue,
        'top_selling_products': top_selling_products,
        'sale_dates_labels': sale_dates_labels,
        'sale_dates_values': sale_dates_values,
        
        # Catégories
        'categories': categories,
        'category_quantities': category_quantities,
        
        # Tendances
        'sales_trend': sales_trend,
        'stock_trend': stock_trend,
        'production_trend': production_trend,
        'delivery_trend': delivery_trend,
        
        # Pour les graphiques
        'thirty_days_ago': thirty_days_ago,
        'raw_materials_table': raw_materials_table,
        'finished_products_table': finished_products_table,

        # Données pour les graphiques
        'categories': categories,
        'category_quantities': category_quantities,
        'sale_dates_labels': sale_dates_labels,
        'sale_dates_values': sale_dates_values,
        'fabrication_dates': fabrication_dates,
        'fabrication_quantities': fabrication_quantities,
    }
    
    return render(request, "store/dashboard.html", get_common_context(module_name="achat"))

def stock(request):
    return render(request, "store/stock.html", get_common_context(module_name="stock"))

def fournisseurs_clients(request):
    return render(request, "store/fournisseurs_clients.html", get_common_context(module_name="fournisseurs_clients"))

def personnels(request):
    return render(request, "store/personnels.html", get_common_context(module_name="personnels"))

def facturation(request):
    return render(request, "store/facturation.html", get_common_context(module_name="facturation"))

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, Sum
from .models import Nomenclature, Fabrication, Item, Category

from .forms import FinishedProductUpdateForm
from django import forms
class FinishedProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = FinishedProductUpdateForm
    template_name = "store/finished_product_update.html"
    success_url = reverse_lazy("productslist")

    def get_queryset(self):
        # Ne permet la mise à jour que des produits finis
        return super().get_queryset().filter(is_finished_product=True)
    
def finished_products_list(request):
    # Récupérer tous les produits finis avec leurs fabrications préchargées
    finished_products = Item.objects.filter(is_finished_product=True).prefetch_related('fabrications')
    
    # Contexte pour le template
    context = {
        'finished_products': finished_products,
    }
    return render(request, 'store/finished_products_list.html', context)

def fabrication(request):
    # Récupérer toutes les nomenclatures existantes
    nomenclatures = Nomenclature.objects.all()
    selected_product = request.GET.get("product_filter")

    # Filtrer les nomenclatures si un produit est sélectionné
    if selected_product:
        nomenclatures = nomenclatures.filter(product__name=selected_product)

    # Récupérer les matières premières disponibles
    raw_materials = Item.objects.filter(is_finished_product=False)

    # Récupérer les statistiques de fabrication
    total_fabrications = Fabrication.objects.count()
    total_quantity_produced = Fabrication.objects.aggregate(Sum("quantity"))["quantity__sum"] or 0

    if request.method == "POST":
        # Si le formulaire de nomenclature est soumis
        if "product_name" in request.POST:
            product_name = request.POST.get("product_name")
            components = request.POST.getlist("component[]")
            quantities = request.POST.getlist("quantity[]")

            # Récupérer ou créer la catégorie par défaut pour les produits finis
            default_category, created = Category.objects.get_or_create(
                name="Produits finis",
                defaults={'slug': 'produits-finis'}  # Assurez-vous que le slug est unique
            )

            # Récupérer ou créer le produit fini
            product, created = Item.objects.get_or_create(
                name=product_name,
                defaults={
                    'is_finished_product': True,
                    'category': default_category  # Associer la catégorie par défaut
                }
            )

            # Enregistrer chaque élément dans la base de données
            for component_id, quantity in zip(components, quantities):
                component = Item.objects.get(id=component_id)
                Nomenclature.objects.create(
                    product=product,
                    component=component,
                    quantity=int(quantity)  # Convertir la quantité en entier
                )

            messages.success(request, f"Nomenclature enregistrée pour {product_name}.")
            return redirect("fabrication")

        # Si le formulaire de lancement de fabrication est soumis
        elif "product_to_manufacture" in request.POST:
            product_to_manufacture = request.POST.get("product_to_manufacture")
            quantity_to_produce = int(request.POST.get("quantity"))

            # Récupérer le produit fini
            try:
                product = Item.objects.get(name=product_to_manufacture, is_finished_product=True)
            except Item.DoesNotExist:
                messages.error(request, f"{product_to_manufacture} n'existe pas en stock.")
                return redirect("fabrication")

            # Récupérer la nomenclature du produit
            nomenclatures_for_product = Nomenclature.objects.filter(product=product)

            # Vérifier la disponibilité des matières premières
            can_produce = True
            for nomenclature in nomenclatures_for_product:
                component = nomenclature.component
                required_quantity = nomenclature.quantity * quantity_to_produce

                if component.quantity < required_quantity:
                    can_produce = False
                    messages.error(request, f"Stock insuffisant pour {component.name}.")
                    break

            # Si toutes les matières premières sont disponibles, procéder à la fabrication
            if can_produce:
                # Diminuer les quantités des matières premières
                for nomenclature in nomenclatures_for_product:
                    component = nomenclature.component
                    required_quantity = nomenclature.quantity * quantity_to_produce

                    component.quantity = F("quantity") - required_quantity
                    component.save()

                # Augmenter la quantité du produit fini
                product.quantity = F("quantity") + quantity_to_produce
                product.save()

                # Enregistrer le lancement de fabrication
                Fabrication.objects.create(
                    product=product,
                    quantity=quantity_to_produce
                )

                messages.success(request, f"Fabrication de {quantity_to_produce} unités de {product.name} lancée.")
            return redirect("fabrication")

    # Récupérer la liste des produits pour le filtre
    products = Nomenclature.objects.values_list("product__name", flat=True).distinct()

    pending_order_fabrications = Fabrication.objects.filter(
        origin_order__isnull=False, 
        is_confirmed=False).select_related('origin_order', 'product', 'origin_order__customer')
    # Contexte pour masquer la sidebar et passer les données
    total_fabrications = Fabrication.objects.count()
    context = {
        'total_fabrications': total_fabrications,
        "pending_order_fabrications": pending_order_fabrications,
        "hide_sidebar": True,
        "nomenclatures": nomenclatures,
        "products": products,
        "selected_product": selected_product,
        "total_fabrications": total_fabrications,
        "total_quantity_produced": total_quantity_produced,
        "raw_materials": raw_materials  # Ajouter les matières premières disponibles au contexte
    }
    return render(request, "store/fabrication.html", context)
class ProductListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.
    """
    model = Item
    table_class = ItemTable
    template_name = "store/productslist.html"
    context_object_name = "items"
    paginate_by = 10
    SingleTableView.table_pagination = False

    def get_queryset(self):
        # Filtrer les matières premières (is_finished_product=False)
        return Item.objects.filter(is_finished_product=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les produits finis au contexte
        context['finished_items'] = Item.objects.filter(is_finished_product=True)
        return context


class ItemSearchListView(ProductListView):
    """
    View class to search and display a filtered list of items.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(ItemSearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_, (Q(name__icontains=q) for q in query_list)
                )
            )
        return result


class ProductDetailView(LoginRequiredMixin, FormMixin, DetailView):
    """
    View class to display detailed information about a product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    """

    model = Item
    template_name = "store/productdetail.html"

    def get_success_url(self):
        return reverse("product-detail", kwargs={"slug": self.object.slug})

# Dans views.py

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = "store/productcreate.html"
    form_class = ItemForm
    success_url = reverse_lazy("productslist")  # Utilisez reverse_lazy pour éviter les problèmes de chargement

    def form_valid(self, form):
        # Ajoutez des logs pour déboguer
        print("Form is valid, saving product...")
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = "store/productupdate.html"
    form_class = ItemForm
    success_url = reverse_lazy("productslist")  # Correction ici (enlevé le double 's')

    def test_func(self):
        return self.request.user.is_authenticated


class ProductDeleteView(LoginRequiredMixin,  DeleteView):
    """
    View class to delete a product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Item
    template_name = "store/productdelete.html"
    success_url = reverse_lazy("productslist")
    def test_func(self):
        # Autoriser tous les utilisateurs authentifiés à mettre à jour
        return self.request.user.is_authenticated


class DeliveryListView(
    LoginRequiredMixin, ExportMixin, tables.SingleTableView
):
    """
    View class to display a list of deliveries.

    Attributes:
    - model: The model associated with the view.
    - pagination: Number of items per page for pagination.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    """

    model = Delivery
    pagination = 10
    template_name = "store/deliveries.html"
    context_object_name = "deliveries"


class DeliverySearchListView(DeliveryListView):
    """
    View class to search and display a filtered list of deliveries.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(DeliverySearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.
                    and_, (Q(customer_name__icontains=q) for q in query_list)
                )
            )
        return result


class DeliveryDetailView(LoginRequiredMixin, DetailView):
    """
    View class to display detailed information about a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    """

    model = Delivery
    template_name = "store/deliverydetail.html"


class DeliveryCreateView(LoginRequiredMixin, CreateView):
    """
    View class to create a new delivery.

    Attributes:
    - model: The model associated with the view.
    - fields: The fields to be included in the form.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries"


class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
    """
    View class to update delivery information.

    Attributes:
    - model: The model associated with the view.
    - fields: The fields to be updated.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries"


class DeliveryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View class to delete a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Delivery
    template_name = "store/productdelete.html"
    success_url = "/deliveries"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'store/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    login_url = 'login'


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'store/category_detail.html'
    context_object_name = 'category'
    login_url = 'login'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'store/category_form.html'
    form_class = CategoryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'store/category_form.html'
    form_class = CategoryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'store/category_confirm_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category-list')
    login_url = 'login'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@csrf_exempt
@require_POST
@login_required
def get_items_ajax_view(request):
    if is_ajax(request):
        try:
            term = request.POST.get("term", "")
            data = []

            items = Item.objects.filter(name__icontains=term)
            for item in items[:10]:
                data.append(item.to_json())

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Not an AJAX request'}, status=400)



from django.urls import reverse_lazy
from .forms import FinishedProductForm
from .models import Category

class FinishedProductCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour ajouter un produit fini.
    """
    model = Item
    form_class = FinishedProductForm
    template_name = "store/finished_product_create.html"
    success_url = reverse_lazy("productslist")

    def form_valid(self, form):
        # Définir une catégorie par défaut pour les produits finis
        default_category, created = Category.objects.get_or_create(name="Produits finis")
        form.instance.category = default_category  # Associer la catégorie par défaut
        form.instance.is_finished_product = True  # Marquer comme produit fini
        return super().form_valid(form)

from .models import ClientOrder
from .forms import ClientOrderForm
from django.shortcuts import get_object_or_404
class ClientOrderListView(LoginRequiredMixin, ListView):
    model = ClientOrder
    template_name = 'store/client_orders_list.html'
    context_object_name = 'orders'
    ordering = ['-order_date']
    paginate_by = 10

class ClientOrderCreateView(LoginRequiredMixin, CreateView):
    model = ClientOrder
    form_class = ClientOrderForm
    template_name = 'store/client_order_form.html'
    success_url = reverse_lazy('client-orders-list')

    def form_valid(self, form):
        order = form.save(commit=False)
        order.created_by = self.request.user
        order.status = 'pending'
        order.save()
        
        # Vérifier si une fabrication existe déjà pour cette commande
        if not Fabrication.objects.filter(origin_order=order).exists():
            Fabrication.objects.create(
                product=order.product,
                quantity=order.quantity,
                origin_order=order,
                is_confirmed=False
            )
        
        return super().form_valid(form)
class ClientOrderDetailView(LoginRequiredMixin, DetailView):
    model = ClientOrder
    template_name = 'store/client_order_detail.html'
    context_object_name = 'order'

from django.contrib import messages
from django.views import View

class LaunchFabricationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        fabrication = get_object_or_404(Fabrication, origin_order_id=pk)
        order = fabrication.origin_order
        
        # Vérifier si la fabrication est déjà confirmée
        if fabrication.is_confirmed:
            messages.error(request, "Cette fabrication a déjà été confirmée")
            return redirect('client-order-detail', pk=order.pk)
        
        # Vérifier les matières premières
        nomenclatures = Nomenclature.objects.filter(product=fabrication.product)
        can_produce = True
        
        for nomenclature in nomenclatures:
            required = nomenclature.quantity * fabrication.quantity
            if nomenclature.component.quantity < required:
                can_produce = False
                messages.error(request, f"Stock insuffisant pour {nomenclature.component.name}")
                break
        
        if can_produce:
            with transaction.atomic():
                # Diminuer les matières premières
                for nomenclature in nomenclatures:
                    component = nomenclature.component
                    required = nomenclature.quantity * fabrication.quantity
                    component.quantity = F('quantity') - required
                    component.save()
                
                # Augmenter le produit fini
                fabrication.product.quantity = F('quantity') + fabrication.quantity
                fabrication.product.save()
                
                # Mettre à jour le statut et confirmer la fabrication
                fabrication.is_confirmed = True
                fabrication.confirmed_by = request.user
                fabrication.confirmation_date = timezone.now()
                fabrication.save()
                
                order.status = 'processing'
                order.save()
                
                messages.success(request, "Fabrication confirmée et lancée avec succès!")
        return redirect('client-order-detail', pk=order.pk)
        
from transactions.views import create_sale_from_order     
class DeliverOrderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(ClientOrder, pk=pk)
        
        if order.status == 'ready':
            # Vérifier le stock avant livraison
            if order.product.quantity >= order.quantity:
                with transaction.atomic():
                    # Diminuer le stock du produit fini
                    order.product.quantity = F('quantity') - order.quantity
                    order.product.save()
                    
                    # Créer la vente automatique
                    sale = create_sale_from_order(order)
                    
                    order.status = 'delivered'
                    order.save()
                    
                    messages.success(request, 
                        f"Livraison confirmée! Vente #{sale.id} créée automatiquement.")
            else:
                messages.error(request, "Stock insuffisant pour livrer la commande")
        else:
            messages.error(request, "Seules les commandes prêtes peuvent être livrées")
        
        return redirect('client-order-detail', pk=order.pk)
class MarkAsReadyView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(ClientOrder, pk=pk)
        if order.status == 'processing':
            order.status = 'ready'
            order.save()
            messages.success(request, "Commande marquée comme prête pour livraison!")
        else:
            messages.error(request, "Seules les commandes en production peuvent être marquées comme prêtes")
        return redirect('client-order-detail', pk=order.pk)


from django.views.generic import DeleteView
from django.urls import reverse_lazy
from .models import ClientOrder

class ClientOrderDeleteView(DeleteView):
    model = ClientOrder
    template_name = 'store/client_order_delete.html'
    success_url = reverse_lazy('client-orders-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object
        return context
   
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging
from django.utils import timezone
from django.db import transaction
logger = logging.getLogger(__name__)
@csrf_exempt
@require_POST
@login_required
def confirm_fabrication(request, fabrication_id):
    logger.info(f"Confirmation de fabrication - ID: {fabrication_id}")
    
    # Vérification plus permissive des en-têtes
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logger.warning("Requête non-AJAX reçue")
        return JsonResponse({'error': 'Requête non autorisée'}, status=403)

    try:
        fabrication = Fabrication.objects.select_related('product', 'origin_order').get(id=fabrication_id)
        
        if fabrication.is_confirmed:
            return JsonResponse({
                'success': False,
                'message': 'Cette fabrication a déjà été confirmée'
            }, status=400)

        # Vérification des stocks avec verrouillage des lignes
        with transaction.atomic():
            nomenclatures = Nomenclature.objects.filter(
                product=fabrication.product
            ).select_related('component').select_for_update()
            
            stock_updates = []
            for nom in nomenclatures:
                required = nom.quantity * fabrication.quantity
                if nom.component.quantity < required:
                    return JsonResponse({
                        'success': False,
                        'message': f"Stock insuffisant de {nom.component.name}"
                    }, status=400)
                
                # Mise à jour du stock
                nom.component.quantity -= required
                nom.component.save()
                stock_updates.append({
                    'component_id': nom.component.id,
                    'new_quantity': nom.component.quantity
                })

            # Mise à jour du produit fini
            fabrication.product.quantity += fabrication.quantity
            fabrication.product.save()

            # Confirmation de la fabrication
            fabrication.is_confirmed = True
            fabrication.confirmed_by = request.user
            fabrication.confirmation_date = timezone.now()
            fabrication.save()

            if fabrication.origin_order:
                fabrication.origin_order.status = 'processing'
                fabrication.origin_order.save()

        return JsonResponse({
            'success': True,
            'message': "Fabrication confirmée avec succès!",
            'product_id': fabrication.product.id,
            'new_quantity': fabrication.product.quantity,
            'stock_updates': stock_updates,
            'fabrication_count': Fabrication.objects.filter(is_confirmed=True).count()
        })

    except Fabrication.DoesNotExist:
        return JsonResponse({'error': 'Fabrication non trouvée'}, status=404)
    except Exception as e:
        logger.exception("Erreur lors de la confirmation de fabrication")
        return JsonResponse({'error': str(e)}, status=500)