import stripe
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
from django.urls import reverse_lazy
from django.views import generic

from membership.forms import CustomSignupForm
from membership.models import Customer

# stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = "sk_test_51KtS69SGpZ0PrA5CW4oOCKyyZH61k6a3a0puKZ6YT5K841wbCzriRShMDBoejGEw0nyRNn4pUT5TRgtp6bZU0AEd000SdyzzUY"


def index(request):
    return HttpResponse("Welcome to our Membership website")


def home(request):
    return render(request, 'membership/home.html')


# @login_required
# def settings(request):
#     return render(request, 'registration/settings.html')

@login_required
def settings(request):
    membership = False
    cancel_at_period_end = False
    if request.method == 'POST':
        subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        request.user.customer.cancel_at_period_end = True
        cancel_at_period_end = True
        subscription.save()
        request.user.customer.save()
    else:
        try:
            if request.user.customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        except Customer.DoesNotExist:
            membership = False
    return render(request, 'registration/settings.html', {'membership': membership,
                                                          'cancel_at_period_end': cancel_at_period_end})


def join(request):
    return render(request, 'membership/join.html')


def success(request):
    if request.method == 'GET' and 'session_id' in request.GET:
        session = stripe.checkout.Session.retrieve(request.GET['session_id'], )
        customer = Customer()
        customer.user = request.user
        customer.stripeid = session.customer
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.stripe_subscription_id = session.subscription
        customer.save()
    return render(request, 'membership/success.html')


def cancel(request):
    return render(request, 'membership/cancel.html')


@login_required
def checkout(request):
    try:
        if request.user.customer.membership:
            return redirect('settings')
    except Customer.DoesNotExist:
        pass

    if request.method == 'POST':
        pass
    else:
        membership = 'monthly'
        final_dollar = 10
        membership_id = 'price_1KtSI8SGpZ0PrA5CG1uUKtsH'
        if request.method == 'GET' and 'membership' in request.GET:
            if request.GET['membership'] == 'yearly':
                membership = 'yearly'
                membership_id = 'price_1KtSI9SGpZ0PrA5CM6g8iHja'
                final_dollar = 100

        # Create Strip Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=request.user.email,
            line_items=[{
                'price': membership_id,
                'quantity': 1,
            }],
            mode='subscription',
            allow_promotion_codes=True,
            success_url='http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/cancel',
        )

        return render(request, 'membership/checkout.html', {'final_dollar': final_dollar, 'session_id': session.id})


class SignUp(generic.CreateView):
    form_class = CustomSignupForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid


@user_passes_test(lambda u: u.is_superuser)
def updateaccounts(request):
    customers = Customer.objects.all()
    for customer in customers:
        subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)
        if subscription.status != 'active':
            customer.membership = False
        else:
            customer.membership = True
        customer.cancel_at_period_end = subscription.cancel_at_period_end
        customer.save()
    return HttpResponse('completed')


def pause_payments(request):
    stripe.Subscription.modify(request.user.customer.stripe_subscription_id,
                               pause_collection={'behavior': 'mark_uncollectible',
                                                 },
                               )
    return HttpResponse('Successfully Paused')


def resumepayments(request):
    stripe.Subscription.modify(
        request.user.customer.stripe_subscription_id,
        pause_collection='',
    )
    return HttpResponse('Successfully resumed')


def delete(request):
    stripe.Subscription.delete(stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)),
    return HttpResponse("cancelled successfully")
    # return render(request, 'membership/delete.html')

def update(request):
    current_subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)

    # new plan
    stripe.Subscription.modify(
        request.user.customer.stripe_subscription_id,
        cancel_at_period_end=True,
        proration_behavior='create_prorations',
        # the new subscription
        items=[{
            'id': current_subscription['items'].data[0].id,
            # note if you have more than one Plan per Subscription, you'll need to improve this. This assumes one plan per sub.
            'deleted': True,
        }, {
            'plan': 'price_1KtSI8SGpZ0PrA5CG1uUKtsH'
        }]
    )
    return HttpResponse("updated successfully")


# def modify(request):
#     subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
#
#     stripe.Subscription.modify(
#         subscription.id,
#         cancel_at_period_end=False,
#         proration_behavior='create_prorations',
#         # items=[{
#         #     'id': subscription['items']['data'][0].id,
#         #     'price': 'price_CBb6IXqvTLXp3f',
#         # }]
#         line_items=[{
#             'price': 'price_1KtSI8SGpZ0PrA5CG1uUKtsH',
#             'quantity': 1,
#         }]
#     )



# def modify(request):
#     if request.method == 'GET':
#         subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
#
#         stripe.Subscription.modify(
#             subscription.id,
#             cancel_at_period_end=False,
#             proration_behavior='create_prorations',
#             items=[{
#                 'id': subscription['items']['data'][0].id,
#
#                 'price': 'price id',
#
#             }]
#         )
#         return render(request, '')

# def Updatesubscription(request):
#     if request.method == 'GET':
#         subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
#
#         stripe.Subscription.modify(
#             subscription.id,
#             cancel_at_period_end=False,
#             proration_behavior='create_prorations',
#             items=[{
#                 'id': subscription['items']['data'][0].id,
#
#                 'price': 'price_1KtRbmSADo18SiFgqCL9iqxw',
#
#             }]
#         )
#     return render(request, 'membership/home.html')
