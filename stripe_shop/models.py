from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from myshop import settings
import stripe
stripe.api_key = settings.STRIPE_API_KEY

class CustomerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    stripe_customer_id = models.CharField(max_length=120)

    # Add additional fields you want to add to the customer profile


@receiver(post_save, sender=User)
def _on_update_user(sender, instance, created, **kwargs):

    if created:  # If a new user is created

        # Create Stripe user
        customer = stripe.Customer.create(
            email=instance.email,
            name=instance.get_full_name(),
            metadata={
                'user_id': instance.pk,
                'username': instance.username
            },
            description='Created from Django',
        )

        # Create profile
        profile = CustomerProfile.objects.create(user=instance, stripe_customer_id=customer.id)
        profile.save()
