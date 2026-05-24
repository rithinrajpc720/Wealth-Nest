"""Auth utility functions."""
from .models import Login


def authenticate_user(username, password, user_type=None):
    """Return Login obj if credentials valid, else None."""
    try:
        if user_type:
            user = Login.objects.get(username=username, user_type=user_type)
        else:
            user = Login.objects.get(username=username)
    except Login.DoesNotExist:
        return None
    if not user.is_active or user.is_suspended:
        return None
    if user.check_password(password):
        return user
    return None


def login_session(request, user):
    """Set session keys for logged-in user."""
    request.session['login_id'] = user.LOGIN_ID
    request.session['username'] = user.username
    request.session['user_type'] = user.user_type
    request.session['email'] = user.email

    if user.user_type == 'head':
        from heads.models import HouseholdHead
        head = HouseholdHead.objects.get(login=user)
        request.session['head_id'] = head.head_id
        request.session['full_name'] = head.full_name
        request.session['family_id'] = head.family.family_id
        request.session['family_name'] = head.family.family_name
        request.session['family_pin'] = head.family.join_pin
    elif user.user_type == 'dependent':
        from dependents.models import FamilyDependent
        dep = FamilyDependent.objects.get(login=user)
        request.session['dependent_id'] = dep.dependent_id
        request.session['full_name'] = dep.full_name
        request.session['family_id'] = dep.family.family_id
        request.session['family_name'] = dep.family.family_name
        request.session['dependent_type'] = dep.dependent_type
    elif user.user_type == 'admin':
        request.session['full_name'] = 'Administrator'


def logout_session(request):
    request.session.flush()
