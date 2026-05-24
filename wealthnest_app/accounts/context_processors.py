from accounts.models import Login


def user_session(request):
    ctx = {
        'session_user_type': request.session.get('user_type'),
        'session_username': request.session.get('username'),
        'session_full_name': request.session.get('full_name'),
        'session_family_name': request.session.get('family_name'),
        'session_login_id': request.session.get('login_id'),
        'session_dependent_id': request.session.get('dependent_id'),
        'session_head_id': request.session.get('head_id'),
        'session_family_id': request.session.get('family_id'),
    }
    # Pending approvals badge for heads
    if ctx['session_user_type'] == 'head':
        try:
            from chores.models import Chore
            ctx['pending_approvals_count'] = Chore.objects.filter(
                family_id=ctx['session_family_id'], status='pending_approval'
            ).count()
        except Exception:
            ctx['pending_approvals_count'] = 0
    # Subscription info for heads
    if ctx['session_user_type'] == 'head':
        try:
            from subscriptions.models import Subscription
            sub = Subscription.objects.filter(family_id=ctx['session_family_id']).select_related('plan').first()
            ctx['session_subscription'] = sub
            ctx['session_plan'] = sub.plan if sub else None
        except Exception:
            ctx['session_subscription'] = None
            ctx['session_plan'] = None
    return ctx
