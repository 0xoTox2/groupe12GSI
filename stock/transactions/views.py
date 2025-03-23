# Standard library imports
import json
import logging

# Django core imports
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.db import transaction

# Class-based views
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

# Authentication and permissions
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Third-party packages
from openpyxl import Workbook

# Local app imports
from store.models import Item
from accounts.models import Customer
from .models import Sale, Purchase, SaleDetail
from .forms import PurchaseForm


logger = logging.getLogger(__name__)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def export_sales_to_excel(request):
    # Create a workbook and select the active worksheet.
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Sales'

    # Define the column headers
    columns = [
        'ID', 'Date', 'Customer', 'Sub Total',
        'Grand Total', 'Tax Amount', 'Tax Percentage',
        'Amount Paid', 'Amount Change'
    ]
    worksheet.append(columns)

    # Fetch sales data
    sales = Sale.objects.all()

    for sale in sales:
        # Convert timezone-aware datetime to naive datetime
        if sale.date_added.tzinfo is not None:
            date_added = sale.date_added.replace(tzinfo=None)
        else:
            date_added = sale.date_added

        worksheet.append([
            sale.id,
            date_added,
            sale.customer.phone,
            sale.sub_total,
            sale.grand_total,
            sale.tax_amount,
            sale.tax_percentage,
            sale.amount_paid,
            sale.amount_change
        ])

    # Set up the response to send the file
    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    )
    response['Content-Disposition'] = 'attachment; filename=sales.xlsx'
    workbook.save(response)

    return response


def export_purchases_to_excel(request):
    # Create a workbook and select the active worksheet.
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Purchases'

    # Define the column headers
    columns = [
        'ID', 'Item', 'Description', 'Vendor', 'Order Date',
        'Delivery Date', 'Quantity', 'Delivery Status',
        'Price per item (Ksh)', 'Total Value'
    ]
    worksheet.append(columns)

    # Fetch purchases data
    purchases = Purchase.objects.all()

    for purchase in purchases:
        # Convert timezone-aware datetime to naive datetime
        delivery_tzinfo = purchase.delivery_date.tzinfo
        order_tzinfo = purchase.order_date.tzinfo

        if delivery_tzinfo or order_tzinfo is not None:
            delivery_date = purchase.delivery_date.replace(tzinfo=None)
            order_date = purchase.order_date.replace(tzinfo=None)
        else:
            delivery_date = purchase.delivery_date
            order_date = purchase.order_date
        worksheet.append([
            purchase.id,
            purchase.item.name,
            purchase.description,
            purchase.vendor.name,
            order_date,
            delivery_date,
            purchase.quantity,
            purchase.get_delivery_status_display(),
            purchase.price,
            purchase.total_value
        ])

    # Set up the response to send the file
    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    )
    response['Content-Disposition'] = 'attachment; filename=purchases.xlsx'
    workbook.save(response)

    return response


class SaleListView(LoginRequiredMixin, ListView):
    """
    View to list all sales with pagination.
    """

    model = Sale
    template_name = "transactions/sales_list.html"
    context_object_name = "sales"
    paginate_by = 10
    ordering = ['date_added']


class SaleDetailView(LoginRequiredMixin, DetailView):
    """
    View to display details of a specific sale.
    """

    model = Sale
    template_name = "transactions/saledetail.html"


def SaleCreateView(request):
    context = {
        "active_icon": "sales",
        "customers": [c.to_select2() for c in Customer.objects.all()]
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            try:
                # Load the JSON data from the request body
                data = json.loads(request.body)
                logger.info(f"Received data: {data}")

                # Validate required fields
                required_fields = [
                    'customer', 'sub_total', 'grand_total',
                    'amount_paid', 'amount_change', 'items'
                ]
                for field in required_fields:
                    if field not in data:
                        raise ValueError(f"Missing required field: {field}")

                # Create sale attributes
                sale_attributes = {
                    "customer": Customer.objects.get(id=int(data['customer'])),
                    "sub_total": float(data["sub_total"]),
                    "grand_total": float(data["grand_total"]),
                    "tax_amount": float(data.get("tax_amount", 0.0)),
                    "tax_percentage": float(data.get("tax_percentage", 0.0)),
                    "amount_paid": float(data["amount_paid"]),
                    "amount_change": float(data["amount_change"]),
                }

                # Use a transaction to ensure atomicity
                with transaction.atomic():
                    # Create the sale
                    new_sale = Sale.objects.create(**sale_attributes)
                    logger.info(f"Sale created: {new_sale}")

                    # Create sale details and update item quantities
                    items = data["items"]
                    if not isinstance(items, list):
                        raise ValueError("Items should be a list")

                    for item in items:
                        if not all(
                            k in item for k in [
                                "id", "price", "quantity", "total_item"
                            ]
                        ):
                            raise ValueError("Item is missing required fields")

                        item_instance = Item.objects.get(id=int(item["id"]))
                        if item_instance.quantity < int(item["quantity"]):
                            raise ValueError(f"Not enough stock for item: {item_instance.name}")

                        detail_attributes = {
                            "sale": new_sale,
                            "item": item_instance,
                            "price": float(item["price"]),
                            "quantity": int(item["quantity"]),
                            "total_detail": float(item["total_item"])
                        }
                        SaleDetail.objects.create(**detail_attributes)
                        logger.info(f"Sale detail created: {detail_attributes}")

                        # Reduce item quantity
                        item_instance.quantity -= int(item["quantity"])
                        item_instance.save()

                return JsonResponse(
                    {
                        'status': 'success',
                        'message': 'Sale created successfully!',
                        'redirect': '/transactions/sales/'
                    }
                )

            except json.JSONDecodeError:
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Invalid JSON format in request body!'
                    }, status=400)
            except Customer.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Customer does not exist!'
                    }, status=400)
            except Item.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Item does not exist!'
                    }, status=400)
            except ValueError as ve:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Value error: {str(ve)}'
                    }, status=400)
            except TypeError as te:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Type error: {str(te)}'
                    }, status=400)
            except Exception as e:
                logger.error(f"Exception during sale creation: {e}")
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': (
                            f'There was an error during the creation: {str(e)}'
                        )
                    }, status=500)

    return render(request, "transactions/sale_create.html", context=context)


class SaleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete a sale.
    """

    model = Sale
    template_name = "transactions/saledelete.html"

    def get_success_url(self):
        """
        Redirect to the sales list after successful deletion.
        """
        return reverse("saleslist")

    def test_func(self):
        """
        Allow deletion only for superusers.
        """
        return self.request.user.is_superuser


class PurchaseListView(LoginRequiredMixin, ListView):
    """
    View to list all purchases with pagination.
    """

    model = Purchase
    template_name = "transactions/purchases_list.html"
    context_object_name = "purchases"
    paginate_by = 10


class PurchaseDetailView(LoginRequiredMixin, DetailView):
    """
    View to display details of a specific purchase.
    """

    model = Purchase
    template_name = "transactions/purchasedetail.html"


from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import CreateView
from .forms import PurchaseForm

from django.urls import reverse
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Purchase
from .forms import PurchaseForm

class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = "transactions/purchases_form.html"

    def get_initial(self):
        """
        Récupère la quantité passée dans l'URL et la pré-remplit dans le formulaire.
        """
        initial = super().get_initial()
        quantity = self.request.GET.get('quantity')  # Récupère la quantité depuis l'URL
        if quantity:
            initial['quantity'] = int(float(quantity))  # Convertit en entier
        return initial

    def form_valid(self, form):
        """
        Calcule total_value avant d'enregistrer l'objet.
        """
        # Récupère l'instance de l'achat sans l'enregistrer dans la base de données
        purchase = form.save(commit=False)

        # Calcule total_value en fonction du prix et de la quantité
        purchase.total_value = purchase.price * purchase.quantity

        # Enregistre l'objet dans la base de données
        purchase.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirige vers la liste des achats après la création.
        """
        return reverse("purchaseslist")


class PurchaseUpdateView(LoginRequiredMixin, UpdateView):
    """
    View to update an existing purchase.
    """

    model = Purchase
    form_class = PurchaseForm
    template_name = "transactions/purchases_form.html"

    def get_success_url(self):
        """
        Redirect to the purchases list after successful form submission.
        """
        return reverse("purchaseslist")


class PurchaseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete a purchase.
    """

    model = Purchase
    template_name = "transactions/purchasedelete.html"

    def get_success_url(self):
        """
        Redirect to the purchases list after successful deletion.
        """
        return reverse("purchaseslist")

    def test_func(self):
        """
        Allow deletion only for superusers.
        """
        return self.request.user.is_superuser

from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import PolicySelectionForm


from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import PolicySelectionForm

def select_policy(request):
    if request.method == 'POST':
        form = PolicySelectionForm(request.POST)
        if form.is_valid():
            policy = form.cleaned_data['policy']
            if policy == 'fixed':
                return redirect(reverse('fixed-replenishment'))
            elif policy == 'point':
                return redirect(reverse('point-replenishment'))
            elif policy == 'replenishment':  # Ajoutez cette condition
                return redirect(reverse('replenishment'))
    else:
        form = PolicySelectionForm()
    
    return render(request, 'transactions/select_policy.html', {'form': form})

from django.shortcuts import render
from .forms import FixedReplenishmentForm, PointReplenishmentForm, ReplenishmentForm
from .models import Purchase, Item
from .policies import ReapprovisionnementPointCommande ,ReapprovisionnementFixe



def fixed_replenishment(request):
    if request.method == 'POST':
        form = FixedReplenishmentForm(request.POST)
        if form.is_valid():
            # Récupérer les données du formulaire
            delai_livraison = form.cleaned_data['delai_livraison']
            consommation_annuelle = form.cleaned_data['consommation_annuelle']
            prix_achat_unitaire = form.cleaned_data['prix_achat_unitaire']
            taux_possession = form.cleaned_data['taux_possession']
            cout_lancement = form.cleaned_data['cout_lancement']

            # Créer l'objet ReapprovisionnementFixe
            stock_fixe = ReapprovisionnementFixe(
                delai_livraison=delai_livraison,
                consommation_annuelle=consommation_annuelle,
                prix_achat_unitaire=prix_achat_unitaire,
                taux_possession=taux_possession,
                cout_lancement=cout_lancement
            )

            # Calculer les résultats
            qec = stock_fixe.calculer_qec()
            periode = stock_fixe.calculer_periode_reapprovisionnement()
            cout_lancement = stock_fixe.calculer_cout_lancement()
            cout_possession = stock_fixe.calculer_cout_possession()
            cout_total = stock_fixe.calculer_cout_total_stock()

            # Afficher les résultats
            return render(request, 'transactions/fixed_replenishment_results.html', {
                'qec': qec,
                'periode': periode,
                'cout_lancement': cout_lancement,
                'cout_possession': cout_possession,
                'cout_total': cout_total,
            })
    else:
        form = FixedReplenishmentForm()
    
    return render(request, 'transactions/fixed_replenishment.html', {'form': form})

def point_replenishment(request):
    if request.method == 'POST':
        form = PointReplenishmentForm(request.POST)
        if form.is_valid():
            # Récupérer les données du formulaire
            stock_actuel = form.cleaned_data['stock_actuel']
            delai_livraison = form.cleaned_data['delai_livraison']
            taille_lot = form.cleaned_data['taille_lot']
            consommation_annuelle = form.cleaned_data['consommation_annuelle']
            prix_achat_unitaire = form.cleaned_data['prix_achat_unitaire']
            taux_possession = form.cleaned_data['taux_possession']
            cout_lancement = form.cleaned_data['cout_lancement']
            stock_securite = form.cleaned_data['stock_securite']

            # Créer l'objet ReapprovisionnementPointCommande
            stock_point_commande = ReapprovisionnementPointCommande(
                stock_actuel=stock_actuel,
                delai_livraison=delai_livraison,
                taille_lot=taille_lot,
                consommation_annuelle=consommation_annuelle,
                prix_achat_unitaire=prix_achat_unitaire,
                taux_possession=taux_possession,
                cout_lancement=cout_lancement,
                stock_securite=stock_securite
            )

            # Calculer les résultats
            qec = stock_point_commande.calculer_qec()
            quantite_ajustee = stock_point_commande.ajuster_quantite_lot(qec)
            point_commande = stock_point_commande.calculer_point_commande()
            cout_lancement = stock_point_commande.calculer_cout_lancement()
            cout_possession = stock_point_commande.calculer_cout_possession()
            cout_total = stock_point_commande.calculer_cout_total_stock()

            # Afficher les résultats
            return render(request, 'transactions/point_replenishment_results.html', {
                'qec': qec,
                'quantite_ajustee': quantite_ajustee,
                'point_commande': point_commande,
                'cout_lancement': cout_lancement,
                'cout_possession': cout_possession,
                'cout_total': cout_total,
            })
    else:
        form = PointReplenishmentForm()
    
    return render(request, 'transactions/point_replenishment.html', {'form': form})

import math
def replenishment(request):
    if request.method == 'POST':
        form = ReplenishmentForm(request.POST)
        if form.is_valid():
            # Récupérer les données du formulaire
            demande_moyenne = form.cleaned_data['demande_moyenne']
            periode_reapprovisionnement = form.cleaned_data['periode_reapprovisionnement']
            delai_livraison = form.cleaned_data['delai_livraison']
            stock_securite = form.cleaned_data['stock_securite']
            stock_actuel = form.cleaned_data['stock_actuel']
            taille_lot = form.cleaned_data['taille_lot']

            # Calculer le niveau cible (NC)
            niveau_cible = demande_moyenne * periode_reapprovisionnement + demande_moyenne * delai_livraison + stock_securite

            # Calculer la quantité à commander (Qc)
            qc = demande_moyenne * (periode_reapprovisionnement + delai_livraison) + stock_securite - stock_actuel
            if qc < 0:
                qc = 0
            qc_ajuste = math.ceil(qc / taille_lot) * taille_lot

            # Calculer le nombre de commandes dans une année (N)
            nombre_commandes_annuelles = 365 / periode_reapprovisionnement

            # Afficher les résultats
            return render(request, 'transactions/replenishment_results.html', {
                'niveau_cible': niveau_cible,
                'quantite_commander': qc_ajuste,
                'nombre_commandes_annuelles': nombre_commandes_annuelles,
            })
    else:
        form = ReplenishmentForm()
    
    return render(request, 'transactions/replenishment.html', {'form': form})



from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import WagnerWhitinForm

def wagner_whitin(demande, cout_commande, cout_possession):
    n = len(demande)
    cout_min = [float('inf')] * (n + 1)
    cout_min[0] = 0
    periode_commande = [0] * (n + 1)

    for j in range(1, n + 1):
        for i in range(1, j + 1):
            cout_stock = sum((k - i) * demande[k - 1] * cout_possession for k in range(i + 1, j + 1))
            cout_total = cout_min[i - 1] + cout_commande + cout_stock
            if cout_total < cout_min[j]:
                cout_min[j] = cout_total
                periode_commande[j] = i

    plan_commande = []
    j = n
    while j > 0:
        i = periode_commande[j]
        plan_commande.append((i, j))
        j = i - 1

    plan_commande.reverse()
    return plan_commande, cout_min[n]

def wagner_whitin_view(request):
    if request.method == 'POST':
        form = WagnerWhitinForm(request.POST)
        if form.is_valid():
            demande = form.cleaned_data['demande']
            cout_commande = form.cleaned_data['cout_commande']
            cout_possession = form.cleaned_data['cout_possession']

            # Convertir la demande en liste de nombres
            demande_list = [float(d) for d in demande.split(',')]

            # Appeler l'algorithme de Wagner-Whitin
            plan_commande, cout_total = wagner_whitin(demande_list, cout_commande, cout_possession)

            # Préparer les résultats pour l'affichage
            results = []
            for debut, fin in plan_commande:
                quantite = sum(demande_list[debut-1:fin])
                results.append({
                    'periode': f"{debut} à {fin}",
                    'quantite': quantite
                })

            return render(request, 'transactions/wagner_whitin_results.html', {
                'results': results,
                'cout_total': cout_total
            })
    else:
        form = WagnerWhitinForm()

    return render(request, 'transactions/wagner_whitin.html', {'form': form})