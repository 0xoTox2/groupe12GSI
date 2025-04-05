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
def check_stock_level(sender, instance, **kwargs):
    if instance.quantity < instance.stock_min and not instance.alert_sent:
        # Envoyer email
        send_mail(
            f'Alerte Stock: {instance.name}',
            f'Niveau critique: {instance.quantity} unités restantes',
            'admin@optistock.com',
            ['manager@optistock.com'],
        )
        instance.alert_sent = True
        instance.save()