from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Login, PasswordResetOTP
from .forms import (LoginForm, HeadRegisterForm, DependentRegisterForm,
                    ForgotPasswordForm, OTPForm, ResetPasswordForm)
from .utils import authenticate_user, login_session, logout_session
from families.models import Family
from heads.models import HouseholdHead
from dependents.models import FamilyDependent


def landing(request):
    return render(request, 'public/landing.html')


# ----- HOUSEHOLD HEAD -----
def head_register(request):
    if request.method == 'POST':
        form = HeadRegisterForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            login = Login(
                username=d['username'],
                email=d['email'],
                user_type='head',
                user_phone=d['phone'],
            )
            login.set_password(d['password'])
            login.save()

            family = Family.objects.create(
                family_name=d['family_name'],
                join_pin=Family.generate_pin(),
            )
            HouseholdHead.objects.create(
                login=login, family=family,
                full_name=d['full_name'], phone=d['phone'],
                family_size=d['family_size'],
            )
            messages.success(request, f'Family registered! Your Family PIN is {family.join_pin}. Share with family members.')
            return redirect('head_login')
    else:
        form = HeadRegisterForm()
    return render(request, 'public/head_register.html', {'form': form})


def head_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate_user(form.cleaned_data['username'], form.cleaned_data['password'], 'head')
            if user:
                login_session(request, user)
                messages.success(request, f'Welcome back, {request.session["full_name"]}!')
                return redirect('head_dashboard')
            messages.error(request, 'Invalid credentials or account suspended.')
    else:
        form = LoginForm()
    return render(request, 'public/head_login.html', {'form': form})


# ----- DEPENDENT -----
def dependent_register(request):
    if request.method == 'POST':
        form = DependentRegisterForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                family = Family.objects.get(join_pin=d['family_pin'], is_active=True)
            except Family.DoesNotExist:
                messages.error(request, 'Invalid family PIN. Ask your parent for the correct PIN.')
                return render(request, 'public/dependent_register.html', {'form': form})

            email = d.get('email') or f"{d['username']}@dependent.wealthnest.local"
            login = Login(
                username=d['username'],
                email=email,
                user_type='dependent',
                user_phone=d.get('phone', ''),
            )
            login.set_password(d['password'])
            login.save()
            FamilyDependent.objects.create(
                login=login, family=family,
                full_name=d['full_name'], dob=d['dob'],
                dependent_type=d['dependent_type'],
            )
            messages.success(request, 'Welcome to the family! You can now log in.')
            return redirect('dependent_login')
    else:
        form = DependentRegisterForm()
    return render(request, 'public/dependent_register.html', {'form': form})


def dependent_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate_user(form.cleaned_data['username'], form.cleaned_data['password'], 'dependent')
            if user:
                login_session(request, user)
                messages.success(request, f'Hi {request.session["full_name"]}! 🎉')
                return redirect('dependent_dashboard')
            messages.error(request, 'Invalid credentials or account suspended.')
    else:
        form = LoginForm()
    return render(request, 'public/dependent_login.html', {'form': form})


# ----- ADMIN -----
def admin_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate_user(form.cleaned_data['username'], form.cleaned_data['password'], 'admin')
            if user:
                login_session(request, user)
                return redirect('admin_dashboard')
            messages.error(request, 'Invalid admin credentials.')
    else:
        form = LoginForm()
    return render(request, 'public/admin_login.html', {'form': form})


def logout_view(request):
    user_type = request.session.get('user_type')
    logout_session(request)
    messages.info(request, 'You have been logged out.')
    if user_type == 'admin':
        return redirect('admin_login')
    if user_type == 'dependent':
        return redirect('dependent_login')
    return redirect('head_login')


# ----- PASSWORD RESET -----
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                login = Login.objects.get(email=email)
                otp = PasswordResetOTP.objects.create(
                    login=login, otp_code=PasswordResetOTP.generate_otp(),
                    expires_at=timezone.now() + timedelta(minutes=15),
                )
                request.session['reset_login_id'] = login.LOGIN_ID
                # In real: send email. Console backend prints OTP.
                print(f"[OTP] Password reset for {email}: {otp.otp_code}")
                messages.success(request, f'OTP sent to your email. (Dev: {otp.otp_code})')
                return redirect('verify_otp')
            except Login.DoesNotExist:
                messages.error(request, 'Email not found.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'public/forgot_password.html', {'form': form})


def verify_otp(request):
    if not request.session.get('reset_login_id'):
        return redirect('forgot_password')
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            try:
                otp = PasswordResetOTP.objects.filter(
                    login_id=request.session['reset_login_id'],
                    otp_code=form.cleaned_data['otp'],
                    is_used=False,
                ).latest('created_at')
                if otp.is_valid():
                    request.session['otp_verified'] = True
                    return redirect('reset_password')
                messages.error(request, 'OTP expired.')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid OTP.')
    else:
        form = OTPForm()
    return render(request, 'public/verify_otp.html', {'form': form})


def reset_password(request):
    if not request.session.get('otp_verified'):
        return redirect('forgot_password')
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            login = Login.objects.get(pk=request.session['reset_login_id'])
            login.set_password(form.cleaned_data['password'])
            login.save()
            # Mark OTPs used
            PasswordResetOTP.objects.filter(login=login).update(is_used=True)
            del request.session['reset_login_id']
            del request.session['otp_verified']
            messages.success(request, 'Password reset successful. Please log in.')
            return redirect('landing')
    else:
        form = ResetPasswordForm()
    return render(request, 'public/reset_password.html', {'form': form})


def handler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)
