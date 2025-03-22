"""
Module: store.views

Contains Django views for managing items, profiles,
and deliveries in the store application.

Classes handle product listing, creation, updating,
deletion, and delivery management.
The module integrates with Django's authentication
and querying functionalities.
"""

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

def dashboard(request):
    
    return render(request, "store/dashboard.html", get_common_context(module_name="achat"))

def stock(request):
    return render(request, "store/stock.html", get_common_context(module_name="stock"))

def fournisseurs_clients(request):
    return render(request, "store/fournisseurs_clients.html", get_common_context(module_name="fournisseurs_clients"))

def personnels(request):
    return render(request, "store/personnels.html", get_common_context(module_name="personnels"))

def facturation(request):
    return render(request, "store/facturation.html", get_common_context(module_name="facturation"))

def fabrication(request):
    nomenclatures = Nomenclature.objects.all()
    selected_product = request.GET.get("product_filter")

    # Filtrer les nomenclatures si un produit est sélectionné
    if selected_product:
        nomenclatures = nomenclatures.filter(product__name=selected_product)

    # Récupérer les statistiques de fabrication
    total_fabrications = Fabrication.objects.count()
    total_quantity_produced = Fabrication.objects.aggregate(Sum("quantity"))["quantity__sum"] or 0

    if request.method == "POST":
        # Si le formulaire de nomenclature est soumis
        if "product_name" in request.POST:
            product_name = request.POST.get("product_name")
            components = request.POST.getlist("component[]")
            quantities = request.POST.getlist("quantity[]")

            # Récupérer ou créer le produit fini
            product, created = Item.objects.get_or_create(name=product_name)

            # Enregistrer chaque élément dans la base de données
            for component_name, quantity in zip(components, quantities):
                component, created = Item.objects.get_or_create(name=component_name)
                Nomenclature.objects.create(
                    product=product,
                    component=component,
                    quantity=quantity
                )

            messages.success(request, f"Nomenclature enregistrée pour {product_name}.")
            return redirect("fabrication")

        # Si le formulaire de lancement de fabrication est soumis
        elif "product_to_manufacture" in request.POST:
            product_to_manufacture = request.POST.get("product_to_manufacture")
            quantity_to_produce = int(request.POST.get("quantity"))

            # Récupérer le produit fini
            try:
                product = Item.objects.get(name=product_to_manufacture)
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

    # Contexte pour masquer la sidebar et passer les données
    context = {
        "hide_sidebar": True,
        "nomenclatures": nomenclatures,
        "products": products,
        "selected_product": selected_product,
        "total_fabrications": total_fabrications,
        "total_quantity_produced": total_quantity_produced
    }
    return render(request, "store/fabrication.html", context)
class ProductListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.

    Attributes:
    - model: The model associated with the view.
    - table_class: The table class used for rendering.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    - paginate_by: Number of items per page for pagination.
    """

    model = Item
    table_class = ItemTable
    template_name = "store/productslist.html"
    context_object_name = "items"
    paginate_by = 10
    SingleTableView.table_pagination = False


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


class ProductUpdateView(LoginRequiredMixin,  UpdateView):
    """
    View class to update product information.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - fields: The fields to be updated.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Item
    template_name = "store/productupdate.html"
    form_class = ItemForm
    ssuccess_url = reverse_lazy("productslist")

    def test_func(self):
        # Autoriser tous les utilisateurs authentifiés à mettre à jour
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
