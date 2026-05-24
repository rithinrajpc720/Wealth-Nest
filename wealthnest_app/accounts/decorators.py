from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_type') != 'admin':
            messages.error(request, 'Admin access required.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def head_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_type') != 'head':
            messages.error(request, 'Household Head access required.')
            return redirect('head_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def dependent_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_type') != 'dependent':
            messages.error(request, 'Family Dependent access required.')
            return redirect('dependent_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def family_member_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_type') not in ('head', 'dependent'):
            messages.error(request, 'Login required.')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required_any(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_id'):
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper
