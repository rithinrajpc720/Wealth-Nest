from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta, date
from accounts.decorators import dependent_required
from .models import FamilyDependent
from .forms import ExpenseForm, GoalForm, ContributionForm, DependentProfileForm
from chores.models import Chore, ChoreSubmission
from transactions.models import Transaction
from goals.models import SavingsGoal, GoalContribution
from achievements.models import Achievement, UserAchievement
from achievements.utils import check_achievements
from admin_panel.models import ExpenseCategory, GoalCategory


def _dep(request):
    return FamilyDependent.objects.get(dependent_id=request.session['dependent_id'])


@dependent_required
def dashboard(request):
    dep = _dep(request)
    today = timezone.now()
    active_chores = Chore.objects.filter(assigned_to=dep, status='active').order_by('deadline')
    chores_completed = Chore.objects.filter(assigned_to=dep, status='approved').count()
    rewards_this_month = Transaction.objects.filter(
        dependent=dep, transaction_type='reward',
        created_at__year=today.year, created_at__month=today.month,
    ).aggregate(s=Sum('amount'))['s'] or 0

    goals = SavingsGoal.objects.filter(dependent=dep, is_completed=False)[:5]
    total_target = goals.aggregate(s=Sum('target_amount'))['s'] or 0
    total_current = goals.aggregate(s=Sum('current_amount'))['s'] or 0
    savings_progress = round((total_current / total_target * 100), 1) if total_target else 0

    recent_transactions = Transaction.objects.filter(dependent=dep).order_by('-created_at')[:5]

    earned = UserAchievement.objects.filter(dependent=dep).select_related('achievement')
    locked = Achievement.objects.exclude(
        achievement_id__in=earned.values_list('achievement_id', flat=True)
    )[:6]

    ctx = {
        'dep': dep,
        'active_chores': active_chores[:5],
        'chores_completed': chores_completed,
        'rewards_this_month': rewards_this_month,
        'savings_progress': savings_progress,
        'goals': goals,
        'recent_transactions': recent_transactions,
        'earned_achievements': earned,
        'locked_achievements': locked,
    }
    return render(request, 'dependent/dashboard.html', ctx)


@dependent_required
def chores(request):
    dep = _dep(request)
    filter_status = request.GET.get('status', 'active')
    qs = Chore.objects.filter(assigned_to=dep)
    if filter_status != 'all':
        qs = qs.filter(status=filter_status)
    return render(request, 'dependent/chores.html', {
        'chores': qs.order_by('deadline'),
        'filter_status': filter_status,
    })


@dependent_required
def chore_complete(request, pk):
    dep = _dep(request)
    chore = get_object_or_404(Chore, pk=pk, assigned_to=dep, status='active')
    if request.method == 'POST':
        notes = request.POST.get('completion_notes', '')
        ChoreSubmission.objects.create(
            chore=chore, dependent=dep, completion_notes=notes,
        )
        chore.status = 'pending_approval'
        chore.save()
        # Streak update
        today = date.today()
        if dep.last_activity == today - timedelta(days=1):
            dep.streak_days += 1
        elif dep.last_activity != today:
            dep.streak_days = 1
        dep.last_activity = today
        dep.save()
        messages.success(request, '🎉 Chore submitted for approval!')
        return redirect('dependent_chores')
    return render(request, 'dependent/chore_complete.html', {'chore': chore})


@dependent_required
def spending(request):
    dep = _dep(request)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount > dep.wallet_balance:
                messages.error(request, f'⚠️ Not enough balance! You only have ₹{dep.wallet_balance}')
            else:
                Transaction.objects.create(
                    dependent=dep, transaction_type='expense',
                    amount=amount, description=form.cleaned_data['description'],
                    category=form.cleaned_data['category'],
                )
                dep.wallet_balance -= amount
                dep.save()
                messages.success(request, f'Expense logged: ₹{amount}')
            return redirect('dependent_spending')
    else:
        form = ExpenseForm()

    expenses = Transaction.objects.filter(dependent=dep, transaction_type='expense').order_by('-created_at')
    breakdown = list(Transaction.objects.filter(dependent=dep, transaction_type='expense')
        .values('category').annotate(total=Sum('amount')).order_by('-total'))

    today = timezone.now()
    months = []
    spending_trend = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%b'))
        spending_trend.append(Transaction.objects.filter(
            dependent=dep, transaction_type='expense',
            created_at__year=d.year, created_at__month=d.month,
        ).aggregate(s=Sum('amount'))['s'] or 0)

    return render(request, 'dependent/spending.html', {
        'form': form, 'expenses': expenses,
        'breakdown': breakdown, 'months': months, 'spending_trend': spending_trend,
        'categories': ExpenseCategory.objects.filter(is_active=True),
        'dep': dep,
    })


@dependent_required
def expense_delete(request, pk):
    dep = _dep(request)
    tx = get_object_or_404(Transaction, pk=pk, dependent=dep, transaction_type='expense')
    dep.wallet_balance += tx.amount
    dep.save()
    tx.delete()
    messages.success(request, 'Expense deleted, balance refunded.')
    return redirect('dependent_spending')


@dependent_required
def goals(request):
    dep = _dep(request)
    active = SavingsGoal.objects.filter(dependent=dep, is_completed=False)
    completed = SavingsGoal.objects.filter(dependent=dep, is_completed=True)

    if request.method == 'POST' and request.POST.get('action') == 'create':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.dependent = dep
            goal.save()
            messages.success(request, 'Goal created!')
            return redirect('dependent_goals')
    else:
        form = GoalForm()

    return render(request, 'dependent/goals.html', {
        'active_goals': active, 'completed_goals': completed,
        'form': form, 'dep': dep,
        'goal_categories': GoalCategory.objects.filter(is_active=True),
    })


@dependent_required
def goal_contribute(request, pk):
    dep = _dep(request)
    goal = get_object_or_404(SavingsGoal, pk=pk, dependent=dep)
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
        except ValueError:
            amount = 0
        if amount <= 0:
            messages.error(request, 'Invalid amount.')
        elif amount > dep.wallet_balance:
            messages.error(request, f'Not enough balance. You have ₹{dep.wallet_balance}.')
        else:
            goal.current_amount += amount
            dep.wallet_balance -= amount
            if goal.current_amount >= goal.target_amount and not goal.is_completed:
                goal.is_completed = True
                goal.completed_at = timezone.now()
            goal.save()
            dep.save()
            GoalContribution.objects.create(goal=goal, amount=amount)
            Transaction.objects.create(
                dependent=dep, transaction_type='savings',
                amount=amount, description=f'Saved to: {goal.goal_name}',
                category=goal.category,
            )
            check_achievements(dep)
            if goal.is_completed:
                messages.success(request, f'🎉 Goal reached! "{goal.goal_name}" completed!')
            else:
                messages.success(request, f'Saved ₹{amount} to {goal.goal_name}!')
    return redirect('dependent_goals')


@dependent_required
def goal_delete(request, pk):
    dep = _dep(request)
    goal = get_object_or_404(SavingsGoal, pk=pk, dependent=dep)
    # Refund the saved amount
    if goal.current_amount > 0:
        dep.wallet_balance += goal.current_amount
        dep.save()
        Transaction.objects.create(
            dependent=dep, transaction_type='adjustment',
            amount=goal.current_amount, description=f'Refund from deleted goal: {goal.goal_name}',
            category='Goal Refund',
        )
    goal.delete()
    messages.success(request, 'Goal deleted, savings refunded.')
    return redirect('dependent_goals')


@dependent_required
def progress(request):
    dep = _dep(request)
    earned = UserAchievement.objects.filter(dependent=dep).select_related('achievement')
    earned_ids = list(earned.values_list('achievement_id', flat=True))
    locked = Achievement.objects.exclude(achievement_id__in=earned_ids)

    today = timezone.now()
    months = []
    savings_growth = []
    chores_per_month = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%b'))
        savings_growth.append(Transaction.objects.filter(
            dependent=dep, transaction_type='savings',
            created_at__year=d.year, created_at__month=d.month,
        ).aggregate(s=Sum('amount'))['s'] or 0)
        chores_per_month.append(Chore.objects.filter(
            assigned_to=dep, status='approved',
            updated_at__year=d.year, updated_at__month=d.month,
        ).count())

    spending_pie = list(Transaction.objects.filter(dependent=dep, transaction_type='expense')
        .values('category').annotate(total=Sum('amount')).order_by('-total'))

    return render(request, 'dependent/progress.html', {
        'dep': dep,
        'earned_achievements': earned,
        'locked_achievements': locked,
        'months': months,
        'savings_growth': savings_growth,
        'chores_per_month': chores_per_month,
        'spending_pie': spending_pie,
    })


@dependent_required
def balance(request):
    dep = _dep(request)
    transactions = Transaction.objects.filter(dependent=dep).order_by('-created_at')
    # Spending forecast
    last_30 = Transaction.objects.filter(
        dependent=dep, transaction_type='expense',
        created_at__gte=timezone.now() - timedelta(days=30),
    ).aggregate(s=Sum('amount'))['s'] or 0
    daily_spend = last_30 / 30
    days_until_zero = int(dep.wallet_balance / daily_spend) if daily_spend > 0 else 999
    return render(request, 'dependent/balance.html', {
        'dep': dep, 'transactions': transactions,
        'daily_spend': round(daily_spend, 2),
        'days_until_zero': min(days_until_zero, 365),
    })


@dependent_required
def profile(request):
    dep = _dep(request)
    if request.method == 'POST':
        form = DependentProfileForm(request.POST)
        if form.is_valid():
            dep.full_name = form.cleaned_data['full_name']
            dep.dob = form.cleaned_data['dob']
            dep.save()
            request.session['full_name'] = dep.full_name
            messages.success(request, 'Profile updated.')
            return redirect('dependent_profile')
    else:
        form = DependentProfileForm(initial={'full_name': dep.full_name, 'dob': dep.dob})

    achievements_count = UserAchievement.objects.filter(dependent=dep).count()
    chores_count = Chore.objects.filter(assigned_to=dep, status='approved').count()
    goals_count = SavingsGoal.objects.filter(dependent=dep, is_completed=True).count()
    return render(request, 'dependent/profile.html', {
        'dep': dep, 'form': form,
        'achievements_count': achievements_count,
        'chores_count': chores_count,
        'goals_count': goals_count,
    })
