
from django.shortcuts import render
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from myshop import settings
import stripe
stripe.api_key = settings.STRIPE_API_KEY


PRODUCTS_STRIPE_PRICING_ID = {
    'product_regular': 'price_1HdwzdDczYfn2Ku8qrXbD6b4',
    'product_pro': 'price_1Hdx00DczYfn2Ku8AdAjeWp8',
    'product_platinum': 'price_1Hdx1SDczYfn2Ku8pCVNQifP',
}


@login_required
@csrf_exempt
def create_stripe_checkout_session(request, product_name):

    try:

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer=request.user.customerprofile.stripe_customer_id,
            client_reference_id=request.user.id,
            metadata={'product_name': product_name, },
            line_items=[
                {'price': PRODUCTS_STRIPE_PRICING_ID[product_name], 'quantity': 1, },
            ],
            mode='payment',
            success_url='http://localhost:8000/success_payment.html',
            cancel_url='http://localhost:8000/cancelled_payment.html',
        )

        return JsonResponse({'id': checkout_session.id})

    except Exception as e:
        print(e)
        raise SuspiciousOperation(e)

@require_POST
@csrf_exempt
def stripe_webhook_paid_endpoint(request):

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    # Try to validate and create a local instance of the event
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_SIGNING_SECRET)
    except ValueError as e:
        # Invalid payload
        return SuspiciousOperation(e)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return SuspiciousOperation(e)

  # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        checkout_session = event['data']['object']
        # Make sure is already paid and not delayed
        if checkout_session.payment_status == "paid":
            _handle_successful_payment(checkout_session)

    # Passed signature verification
    return HttpResponse(status=200)

def _handle_successful_payment(checkout_session):
    # Define what to do after the user has successfully paid
    pass

