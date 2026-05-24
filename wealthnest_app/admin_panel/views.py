from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from accounts.decorators import admin_required
from accounts.models import Login
from families.models import Family
from heads.models import HouseholdHead
from dependents.models import FamilyDependent
from chores.models import Chore
from transactions.models import Transaction
from goals.models import SavingsGoal
from complaints.models import Complaint
from feedback.models import Feedback
from .models import ExpenseCategory, ChoreCategoryAdmin, GoalCategory


@admin_required
def dashboard(request):
    total_families = Family.objects.count()
    active_dependents = FamilyDependent.objects.filter(login__is_active=True).count()
    total_chores_done = Chore.objects.filter(status='approved').count()
    total_rewarded = Transaction.objects.filter(transaction_type='reward').aggregate(s=Sum('amount'))['s'] or 0
    complaints_count = Complaint.objects.exclude(status='resolved').count()
    feedback_count = Feedback.objects.count()

    # Charts data
    months = []
    family_counts = []
    chore_counts = []
    today = timezone.now()
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%b'))
        family_counts.append(Family.objects.filter(
            created_at__year=d.year, created_at__month=d.month).count())
        chore_counts.append(Chore.objects.filter(
            status='approved', updated_at__year=d.year, updated_at__month=d.month).count())

    age_groups = {
        'child': FamilyDependent.objects.filter(dependent_type='child').count(),
        'teen': FamilyDependent.objects.filter(dependent_type='teen').count(),
        'young_adult': FamilyDependent.objects.filter(dependent_type='young_adult').count(),
    }
    goals_completed_per_month = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=30 * i)
        goals_completed_per_month.append(SavingsGoal.objects.filter(
            is_completed=True, completed_at__year=d.year, completed_at__month=d.month).count())

    recent_families = Family.objects.order_by('-created_at')[:8]
    total_savings = SavingsGoal.objects.aggregate(s=Sum('current_amount'))['s'] or 0
    
    ctx = {
        'total_families': total_families,
        'active_dependents': active_dependents,
        'total_chores_done': total_chores_done,
        'total_rewarded': total_rewarded,
        'total_savings': total_savings,
        'complaints_count': complaints_count,
        'feedback_count': feedback_count,
        'months': months,
        'family_counts': family_counts,
        'chore_counts': chore_counts,
        'age_groups': age_groups,
        'goals_completed_per_month': goals_completed_per_month,
        'recent_families': recent_families,
    }
    return render(request, 'admin/dashboard.html', ctx)


@admin_required
def enrollment(request):
    families = Family.objects.all().order_by('-created_at')
    rows = []
    for f in families:
        try:
            head = f.householdhead
            head_name = head.full_name
        except HouseholdHead.DoesNotExist:
            head_name = '-'
        rows.append({
            'family': f,
            'head_name': head_name,
            'members': f.member_count,
            'status': 'Active' if f.is_active else 'Suspended',
        })
    return render(request, 'admin/enrollment.html', {'rows': rows})


@admin_required
def family_view(request, pk):
    family = get_object_or_404(Family, pk=pk)
    head = HouseholdHead.objects.filter(family=family).first()
    dependents = FamilyDependent.objects.filter(family=family)
    return render(request, 'admin/family_detail.html', {
        'family': family, 'head': head, 'dependents': dependents,
    })


@admin_required
def family_toggle(request, pk):
    family = get_object_or_404(Family, pk=pk)
    family.is_active = not family.is_active
    family.save()
    # Suspend all members
    Login.objects.filter(householdhead__family=family).update(is_suspended=not family.is_active)
    Login.objects.filter(familydependent__family=family).update(is_suspended=not family.is_active)
    messages.success(request, f'Family {"activated" if family.is_active else "suspended"}.')
    return redirect('admin_enrollment')


@admin_required
def telemetry(request):
    today = timezone.now()
    months = []
    transactions_per_month = []
    rewards_per_month = []
    for i in range(11, -1, -1):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%b'))
        transactions_per_month.append(Transaction.objects.filter(
            created_at__year=d.year, created_at__month=d.month).count())
        rewards_per_month.append(Transaction.objects.filter(
            transaction_type='reward', created_at__year=d.year, created_at__month=d.month
        ).aggregate(s=Sum('amount'))['s'] or 0)

    ctx = {
        'total_transactions': Transaction.objects.count(),
        'total_chores': Chore.objects.count(),
        'total_goals': SavingsGoal.objects.count(),
        'total_logins': Login.objects.count(),
        'months': months,
        'transactions_per_month': transactions_per_month,
        'rewards_per_month': rewards_per_month,
    }
    return render(request, 'admin/telemetry.html', ctx)


@admin_required
def admin_complaints(request):
    complaints = Complaint.objects.all()
    return render(request, 'admin/complaints.html', {'complaints': complaints})


@admin_required
def admin_complaint_resolve(request, pk):
    c = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        c.admin_response = request.POST.get('response', '')
        c.status = request.POST.get('status', 'resolved')
        if c.status == 'resolved':
            c.resolved_at = timezone.now()
        c.save()
        messages.success(request, 'Complaint updated.')
    return redirect('admin_complaints')


@admin_required
def admin_feedback(request):
    feedback_list = Feedback.objects.all()
    return render(request, 'admin/feedback.html', {'feedback_list': feedback_list})


@admin_required
def categories(request):
    groups = [
        ('expense', '💸 Expense Categories', list(ExpenseCategory.objects.all())),
        ('chore', '📋 Chore Categories', list(ChoreCategoryAdmin.objects.all())),
        ('goal', '🎯 Goal Categories', list(GoalCategory.objects.all())),
    ]
    return render(request, 'admin/categories.html', {'groups': groups})


@admin_required
def category_create(request, kind):
    model_map = {'expense': ExpenseCategory, 'chore': ChoreCategoryAdmin, 'goal': GoalCategory}
    Model = model_map.get(kind)
    if not Model:
        return redirect('admin_categories')
    if request.method == 'POST':
        Model.objects.create(
            name=request.POST.get('name', '').strip(),
            icon=request.POST.get('icon', '💰').strip()[:10] or '💰',
            color=request.POST.get('color', '#1E1B4B'),
        )
        messages.success(request, 'Category created.')
    return redirect('admin_categories')


@admin_required
def category_delete(request, kind, pk):
    model_map = {'expense': ExpenseCategory, 'chore': ChoreCategoryAdmin, 'goal': GoalCategory}
    Model = model_map.get(kind)
    if Model:
        Model.objects.filter(pk=pk).delete()
        messages.success(request, 'Category deleted.')
    return redirect('admin_categories')
