from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from store.models import Item
from .models import Purchase


@receiver(post_save, sender=Purchase)
def update_item_quantity(sender, instance, created, **kwargs):
    """
    Signal to update item quantity when a purchase is made.
    """
    if created:
        instance.item.quantity += instance.quantity
        instance.item.save()

@receiver(post_save, sender=Item)
def check_stock(sender, instance, **kwargs):
    real_instance = Item.objects.get(pk=instance.pk)

    if real_instance.quantity < real_instance.stock_min and not real_instance.alert_sent:
        try:
            send_mail(
                f'Alerte Stock: {real_instance.name}',
                f'Niveau critique: {real_instance.quantity} unités restantes',
                'admin@optistock.com',
                ['manager@optistock.com'],
                fail_silently=False,
            )
            Item.objects.filter(pk=instance.pk).update(alert_sent=True)
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Failed to send email alert: {e}")


from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import ClientOrder, Fabrication

@receiver(post_save, sender=ClientOrder)
def create_fabrication_order(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        # Vérifier si le produit est en stock
        if instance.product.quantity >= instance.quantity:
            # Suffisamment de stock - pas besoin de fabrication
            instance.status = 'completed'
            instance.product.quantity -= instance.quantity
            instance.product.save()
        else:
            # Créer un ordre de fabrication pour la quantité manquante
            needed = instance.quantity - instance.product.quantity
            Fabrication.objects.create(
                product=instance.product,
                quantity=needed,
                origin_order=instance  # Ajoutez ce champ à votre modèle Fabrication si besoin
            )
            instance.status = 'processing'
        instance.save()

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Fabrication)
def update_stocks_on_confirmation(sender, instance, created, **kwargs):
   pass