from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from datetime import timedelta
from accounts.decorators import head_required, admin_required
from heads.models import HouseholdHead
from families.models import Family
from .models import Plan, Subscription, Payment
from .forms import CardPaymentForm, UPIPaymentForm, NetBankingForm


def pricing(request):
    plans = Plan.objects.all().order_by('sort_order')
    current_sub = None
    if request.session.get('user_type') == 'head':
        try:
            head = HouseholdHead.objects.get(head_id=request.session['head_id'])
            current_sub = Subscription.objects.filter(family=head.family).first()
        except HouseholdHead.DoesNotExist:
            pass
    return render(request, 'subscriptions/pricing.html', {
        'plans': plans,
        'current_sub': current_sub,
    })


@head_required
def checkout(request, plan_slug, cycle):
    plan = get_object_or_404(Plan, slug=plan_slug)
    cycle = cycle if cycle in ('monthly', 'yearly') else 'monthly'
    head = HouseholdHead.objects.get(head_id=request.session['head_id'])

    if plan.slug == 'free':
        # Free plan — directly subscribe
        sub, _ = Subscription.objects.update_or_create(
            family=head.family,
            defaults={
                'plan': plan,
                'billing_cycle': cycle,
                'status': 'active',
                'started_at': timezone.now(),
                'expires_at': None,
            },
        )
        messages.success(request, '✅ You are on the Free plan!')
        return redirect('subscription_manage')

    amount = plan.price_yearly if cycle == 'yearly' else plan.price_monthly
    return render(request, 'subscriptions/checkout.html', {
        'plan': plan, 'cycle': cycle, 'amount': amount,
        'head': head,
    })


@head_required
def process_payment(request, plan_slug, cycle):
    if request.method != 'POST':
        return redirect('subscription_pricing')
    plan = get_object_or_404(Plan, slug=plan_slug)
    cycle = cycle if cycle in ('monthly', 'yearly') else 'monthly'
    head = HouseholdHead.objects.get(head_id=request.session['head_id'])
    amount = plan.price_yearly if cycle == 'yearly' else plan.price_monthly
    method = request.POST.get('payment_method', 'card')

    # Validate the relevant form
    payer_name = ''
    last_four = ''
    upi_id = ''
    bank_name = ''
    form_errors = None

    if method == 'card':
        form = CardPaymentForm(request.POST)
        if not form.is_valid():
            form_errors = form.errors
        else:
            payer_name = form.cleaned_data['payer_name']
            last_four = form.cleaned_data['card_number'][-4:]
    elif method == 'upi':
        form = UPIPaymentForm(request.POST)
        if not form.is_valid():
            form_errors = form.errors
        else:
            payer_name = form.cleaned_data['payer_name']
            upi_id = form.cleaned_data['upi_id']
    elif method == 'netbanking':
        form = NetBankingForm(request.POST)
        if not form.is_valid():
            form_errors = form.errors
        else:
            payer_name = form.cleaned_data['payer_name']
            bank_name = form.cleaned_data['bank']
    else:
        form_errors = 'Invalid payment method.'

    if form_errors:
        messages.error(request, 'Please check your payment details.')
        return render(request, 'subscriptions/checkout.html', {
            'plan': plan, 'cycle': cycle, 'amount': amount, 'head': head,
            'errors': form_errors, 'payment_method': method,
        })

    # Find or create subscription
    sub, _ = Subscription.objects.get_or_create(
        family=head.family,
        defaults={'plan': plan, 'billing_cycle': cycle, 'status': 'active',
                  'started_at': timezone.now()},
    )
    sub.plan = plan
    sub.billing_cycle = cycle
    sub.status = 'active'
    if not sub.started_at:
        sub.started_at = timezone.now()
    sub.extend(cycle)  # also saves

    # Create payment record
    payment = Payment.objects.create(
        subscription=sub, plan=plan, billing_cycle=cycle,
        amount=amount, currency='INR', payment_method=method,
        status='success',
        transaction_id=Payment.generate_transaction_id(),
        invoice_number=Payment.generate_invoice_number(),
        payer_name=payer_name, last_four=last_four,
        upi_id=upi_id, bank_name=bank_name,
        notes='Demo payment for BCA project — no real transaction.',
    )

    return redirect('subscription_payment_success', payment_id=payment.payment_id)


@head_required
def payment_success(request, payment_id):
    head = HouseholdHead.objects.get(head_id=request.session['head_id'])
    payment = get_object_or_404(Payment, pk=payment_id, subscription__family=head.family)
    return render(request, 'subscriptions/payment_success.html', {
        'payment': payment, 'subscription': payment.subscription,
    })


@head_required
def manage_subscription(request):
    head = HouseholdHead.objects.get(head_id=request.session['head_id'])
    sub = Subscription.objects.filter(family=head.family).first()
    if not sub:
        # Auto-assign Free plan
        free_plan = Plan.objects.filter(slug='free').first()
        if free_plan:
            sub = Subscription.objects.create(
                family=head.family, plan=free_plan, status='active',
                billing_cycle='monthly', started_at=timezone.now(),
            )
    payments = Payment.objects.filter(subscription__family=head.family).order_by('-created_at')[:10]

    # Usage metrics
    from dependents.models import FamilyDependent
    from chores.models import Chore
    from goals.models import SavingsGoal
    usage = {
        'dependents': FamilyDependent.objects.filter(family=head.family).count(),
        'active_chores': Chore.objects.filter(family=head.family, status__in=['active', 'pending_approval']).count(),
        'goals': SavingsGoal.objects.filter(dependent__family=head.family, is_completed=False).count(),
    }
    return render(request, 'subscriptions/manage.html', {
        'subscription': sub, 'payments': payments, 'usage': usage,
    })


@head_required
def cancel_subscription(request):
    if request.method == 'POST':
        head = HouseholdHead.objects.get(head_id=request.session['head_id'])
        sub = Subscription.objects.filter(family=head.family).first()
        if sub and sub.plan.slug != 'free':
            sub.auto_renew = False
            sub.status = 'cancelled'
            sub.cancelled_at = timezone.now()
            sub.save()
            messages.success(request, 'Auto-renewal cancelled. You can use the plan until it expires.')
        else:
            messages.info(request, 'Free plan cannot be cancelled.')
    return redirect('subscription_manage')


@head_required
def payment_history(request):
    head = HouseholdHead.objects.get(head_id=request.session['head_id'])
    payments = Payment.objects.filter(subscription__family=head.family).order_by('-created_at')
    return render(request, 'subscriptions/history.html', {'payments': payments})


@head_required
def invoice(request, payment_id):
    head = HouseholdHead.objects.get(head_id=request.session['head_id'])
    payment = get_object_or_404(Payment, pk=payment_id, subscription__family=head.family)
    return render(request, 'subscriptions/invoice.html', {'payment': payment})


# ----- ADMIN -----

@admin_required
def admin_subscriptions(request):
    subs = Subscription.objects.select_related('family', 'plan').order_by('-started_at')
    by_plan = list(Subscription.objects.values('plan__name').annotate(cnt=Count('subscription_id')))
    return render(request, 'admin/subscriptions.html', {'subs': subs, 'by_plan': by_plan})


@admin_required
def admin_payments(request):
    payments = Payment.objects.select_related('subscription__family', 'plan').order_by('-created_at')
    total_revenue = Payment.objects.filter(status='success').aggregate(s=Sum('amount'))['s'] or 0
    success_count = Payment.objects.filter(status='success').count()
    failed_count = Payment.objects.filter(status='failed').count()

    # Monthly revenue chart
    from django.utils import timezone
    today = timezone.now()
    months = []
    revenue_per_month = []
    for i in range(11, -1, -1):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%b'))
        revenue_per_month.append(Payment.objects.filter(
            status='success', created_at__year=d.year, created_at__month=d.month,
        ).aggregate(s=Sum('amount'))['s'] or 0)

    return render(request, 'admin/payments.html', {
        'payments': payments,
        'total_revenue': total_revenue,
        'success_count': success_count,
        'failed_count': failed_count,
        'months': months,
        'revenue_per_month': revenue_per_month,
    })
