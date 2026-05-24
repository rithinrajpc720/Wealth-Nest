from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta, date
from accounts.decorators import head_required
from accounts.models import Login
from .models import HouseholdHead
from .forms import ChoreForm, BalanceAdjustForm, AllowanceForm, HeadProfileForm, ChangePasswordForm
from chores.models import Chore, ChoreSubmission
from dependents.models import FamilyDependent
from transactions.models import Transaction, AllowanceSchedule
from goals.models import SavingsGoal
from achievements.utils import check_achievements


def _head(request):
    return HouseholdHead.objects.get(head_id=request.session['head_id'])


@head_required
def dashboard(request):
    head = _head(request)
    family = head.family
    dependents = FamilyDependent.objects.filter(family=family)

    pending_approvals = Chore.objects.filter(family=family, status='pending_approval').count()
    chores_active = Chore.objects.filter(family=family, status='active').count()
    total_rewarded = Transaction.objects.filter(
        dependent__family=family, transaction_type='reward'
    ).aggregate(s=Sum('amount'))['s'] or 0
    family_savings = SavingsGoal.objects.filter(dependent__family=family).aggregate(s=Sum('current_amount'))['s'] or 0

    today = timezone.now()
    month_expenses = Transaction.objects.filter(
        dependent__family=family, transaction_type='expense',
        created_at__year=today.year, created_at__month=today.month
    ).aggregate(s=Sum('amount'))['s'] or 0
    month_rewards = Transaction.objects.filter(
        dependent__family=family, transaction_type='reward',
        created_at__year=today.year, created_at__month=today.month
    ).aggregate(s=Sum('amount'))['s'] or 0

    # Charts
    months = []
    savings_trend = []
    chores_completion = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%b'))
        savings_trend.append(Transaction.objects.filter(
            dependent__family=family, transaction_type='savings',
            created_at__year=d.year, created_at__month=d.month
        ).aggregate(s=Sum('amount'))['s'] or 0)
        chores_completion.append(Chore.objects.filter(
            family=family, status='approved',
            updated_at__year=d.year, updated_at__month=d.month
        ).count())

    expense_categories = list(Transaction.objects.filter(
        dependent__family=family, transaction_type='expense'
    ).values('category').annotate(total=Sum('amount')).order_by('-total')[:6])

    member_balances = []
    for d in dependents:
        recent = Transaction.objects.filter(dependent=d).order_by('-created_at').first()
        member_balances.append({
            'dep': d,
            'recent': recent,
        })

    ctx = {
        'family': family,
        'head': head,
        'total_dependents': dependents.count(),
        'pending_approvals': pending_approvals,
        'chores_active': chores_active,
        'total_rewarded': total_rewarded,
        'family_savings': family_savings,
        'month_expenses': month_expenses,
        'month_rewards': month_rewards,
        'months': months,
        'savings_trend': savings_trend,
        'chores_completion': chores_completion,
        'expense_categories': expense_categories,
        'member_balances': member_balances,
    }
    return render(request, 'head/dashboard.html', ctx)


@head_required
def chore_manager(request):
    head = _head(request)
    filter_status = request.GET.get('status', 'all')
    qs = Chore.objects.filter(family=head.family)
    if filter_status != 'all':
        qs = qs.filter(status=filter_status)
    qs = qs.order_by('-created_at')
    return render(request, 'head/chores.html', {
        'chores': qs, 'filter_status': filter_status,
    })


@head_required
def chore_create(request):
    head = _head(request)
    form = ChoreForm(request.POST or None)
    form.fields['assigned_to'].queryset = FamilyDependent.objects.filter(family=head.family)
    if request.method == 'POST' and form.is_valid():
        chore = form.save(commit=False)
        chore.family = head.family
        chore.assigned_by = head
        chore.save()
        messages.success(request, f'Chore "{chore.chore_name}" assigned!')
        return redirect('head_chores')
    return render(request, 'head/chore_form.html', {'form': form, 'mode': 'Create'})


@head_required
def chore_edit(request, pk):
    head = _head(request)
    chore = get_object_or_404(Chore, pk=pk, family=head.family)
    form = ChoreForm(request.POST or None, instance=chore)
    form.fields['assigned_to'].queryset = FamilyDependent.objects.filter(family=head.family)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Chore updated.')
        return redirect('head_chores')
    return render(request, 'head/chore_form.html', {'form': form, 'mode': 'Edit', 'chore': chore})


@head_required
def chore_delete(request, pk):
    head = _head(request)
    chore = get_object_or_404(Chore, pk=pk, family=head.family)
    chore.delete()
    messages.success(request, 'Chore deleted.')
    return redirect('head_chores')


@head_required
def chore_archive(request, pk):
    head = _head(request)
    chore = get_object_or_404(Chore, pk=pk, family=head.family)
    chore.status = 'archived'
    chore.save()
    messages.success(request, 'Chore archived.')
    return redirect('head_chores')


@head_required
def accounts(request):
    head = _head(request)
    dependents = FamilyDependent.objects.filter(family=head.family)
    cards = []
    for d in dependents:
        sched = AllowanceSchedule.objects.filter(dependent=d).first()
        cards.append({'dep': d, 'sched': sched})
    return render(request, 'head/accounts.html', {'cards': cards, 'family': head.family})


@head_required
def balance_adjust(request, dep_id):
    head = _head(request)
    dep = get_object_or_404(FamilyDependent, pk=dep_id, family=head.family)
    if request.method == 'POST':
        form = BalanceAdjustForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            is_credit = form.cleaned_data.get('is_credit', False)
            signed = amount if is_credit else -amount
            dep.wallet_balance += signed
            dep.save()
            Transaction.objects.create(
                dependent=dep, transaction_type='adjustment',
                amount=abs(amount), description=form.cleaned_data['reason'],
                category='Adjustment',
            )
            messages.success(request, f'Balance {"credited" if is_credit else "deducted"} ₹{abs(amount)}')
    return redirect('head_accounts')


@head_required
def allowance_set(request, dep_id):
    head = _head(request)
    dep = get_object_or_404(FamilyDependent, pk=dep_id, family=head.family)
    sched, _ = AllowanceSchedule.objects.get_or_create(dependent=dep, defaults={'amount': 0, 'frequency': 'weekly'})
    if request.method == 'POST':
        form = AllowanceForm(request.POST, instance=sched)
        if form.is_valid():
            form.save()
            messages.success(request, 'Allowance schedule updated.')
    return redirect('head_accounts')


@head_required
def approvals(request):
    head = _head(request)
    pending = Chore.objects.filter(family=head.family, status='pending_approval').order_by('deadline')
    pending_data = []
    today = date.today()
    for ch in pending:
        sub = ChoreSubmission.objects.filter(chore=ch, is_approved__isnull=True).order_by('-submitted_at').first()
        pending_data.append({
            'chore': ch,
            'submission': sub,
            'overdue': ch.deadline < today,
        })

    history = ChoreSubmission.objects.filter(
        chore__family=head.family, is_approved__isnull=False
    ).order_by('-reviewed_at')[:30]

    return render(request, 'head/approvals.html', {
        'pending_data': pending_data, 'history': history,
    })


@head_required
def approve_chore(request, pk):
    head = _head(request)
    chore = get_object_or_404(Chore, pk=pk, family=head.family)
    sub = ChoreSubmission.objects.filter(chore=chore, is_approved__isnull=True).first()
    if sub:
        sub.is_approved = True
        sub.reviewed_at = timezone.now()
        sub.save()
    chore.status = 'approved'
    chore.save()
    dep = chore.assigned_to
    dep.wallet_balance += chore.reward_amount
    dep.xp_points += {'easy': 10, 'medium': 25, 'hard': 50}.get(chore.difficulty, 10)
    dep.last_activity = date.today()
    dep.save()
    Transaction.objects.create(
        dependent=dep, transaction_type='reward',
        amount=chore.reward_amount, description=f'Chore: {chore.chore_name}',
        category='Chore Reward', reference_chore=chore,
    )
    earned = check_achievements(dep)
    # Auto-regenerate recurring
    if chore.is_recurring:
        new_deadline = date.today() + timedelta(days=7 if chore.recurring_type == 'weekly' else 30)
        Chore.objects.create(
            family=chore.family, assigned_by=chore.assigned_by, assigned_to=chore.assigned_to,
            category=chore.category, chore_name=chore.chore_name, description=chore.description,
            reward_amount=chore.reward_amount, difficulty=chore.difficulty,
            deadline=new_deadline, is_recurring=True, recurring_type=chore.recurring_type,
        )
    messages.success(request, f'Approved! ₹{chore.reward_amount} credited to {dep.full_name}. 🎉')
    return redirect('head_approvals')


@head_required
def reject_chore(request, pk):
    head = _head(request)
    chore = get_object_or_404(Chore, pk=pk, family=head.family)
    reason = request.POST.get('reason', 'Not satisfactory')
    sub = ChoreSubmission.objects.filter(chore=chore, is_approved__isnull=True).first()
    if sub:
        sub.is_approved = False
        sub.rejection_reason = reason
        sub.reviewed_at = timezone.now()
        sub.save()
    chore.status = 'active'
    chore.save()
    messages.warning(request, 'Submission rejected. Dependent has been notified.')
    return redirect('head_approvals')


@head_required
def spend_logs(request):
    head = _head(request)
    transactions = Transaction.objects.filter(dependent__family=head.family).order_by('-created_at')
    member_filter = request.GET.get('member')
    type_filter = request.GET.get('type')
    if member_filter:
        transactions = transactions.filter(dependent_id=member_filter)
    if type_filter:
        transactions = transactions.filter(transaction_type=type_filter)

    # Per member spending
    member_spending = list(FamilyDependent.objects.filter(family=head.family).annotate(
        total=Sum('transaction__amount', filter=Q(transaction__transaction_type='expense'))
    ).values('full_name', 'total'))

    category_breakdown = list(Transaction.objects.filter(
        dependent__family=head.family, transaction_type='expense'
    ).values('category').annotate(total=Sum('amount')).order_by('-total'))

    dependents = FamilyDependent.objects.filter(family=head.family)
    return render(request, 'head/spend.html', {
        'transactions': transactions[:200],
        'dependents': dependents,
        'member_spending': member_spending,
        'category_breakdown': category_breakdown,
        'member_filter': member_filter,
        'type_filter': type_filter,
    })


@head_required
def analytics(request):
    head = _head(request)
    family = head.family
    today = timezone.now()
    months = []
    networth_trend = []
    rewards_per_month = []
    for i in range(11, -1, -1):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%b'))
        # networth approx = wallet + savings up to that month (simplified)
        rewards_per_month.append(Transaction.objects.filter(
            dependent__family=family, transaction_type='reward',
            created_at__year=d.year, created_at__month=d.month,
        ).aggregate(s=Sum('amount'))['s'] or 0)
        networth_trend.append(SavingsGoal.objects.filter(
            dependent__family=family, created_at__lte=d,
        ).aggregate(s=Sum('current_amount'))['s'] or 0)

    chore_completion = list(FamilyDependent.objects.filter(family=family).annotate(
        completed=Count('chore', filter=Q(chore__status='approved'))
    ).values('full_name', 'completed'))

    spending_by_member = list(FamilyDependent.objects.filter(family=family).annotate(
        total=Sum('transaction__amount', filter=Q(transaction__transaction_type='expense'))
    ).values('full_name', 'total'))

    goals_progress = SavingsGoal.objects.filter(dependent__family=family).order_by('-current_amount')[:8]

    return render(request, 'head/analytics.html', {
        'months': months,
        'networth_trend': networth_trend,
        'rewards_per_month': rewards_per_month,
        'chore_completion': chore_completion,
        'spending_by_member': spending_by_member,
        'goals_progress': goals_progress,
    })


@head_required
def profile(request):
    head = _head(request)
    if request.method == 'POST' and request.POST.get('action') == 'profile':
        form = HeadProfileForm(request.POST)
        if form.is_valid():
            head.full_name = form.cleaned_data['full_name']
            head.phone = form.cleaned_data['phone']
            head.family.family_name = form.cleaned_data['family_name']
            head.family.save()
            head.save()
            request.session['full_name'] = head.full_name
            request.session['family_name'] = head.family.family_name
            messages.success(request, 'Profile updated.')
            return redirect('head_profile')
    elif request.method == 'POST' and request.POST.get('action') == 'password':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            login = head.login
            if not login.check_password(form.cleaned_data['current_password']):
                messages.error(request, 'Current password incorrect.')
            else:
                login.set_password(form.cleaned_data['new_password'])
                login.save()
                messages.success(request, 'Password changed.')
            return redirect('head_profile')
    else:
        form = HeadProfileForm(initial={
            'full_name': head.full_name, 'phone': head.phone,
            'family_name': head.family.family_name,
        })
    return render(request, 'head/profile.html', {
        'head': head, 'form': form, 'pwd_form': ChangePasswordForm(),
    })
