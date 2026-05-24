from django import forms
from .models import Login


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class HeadRegisterForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    password = forms.CharField(min_length=6, widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    family_name = forms.CharField(max_length=100)
    family_size = forms.IntegerField(min_value=1, max_value=10, initial=2)

    def clean_username(self):
        u = self.cleaned_data['username']
        if Login.objects.filter(username=u).exists():
            raise forms.ValidationError('Username already taken.')
        return u

    def clean_email(self):
        e = self.cleaned_data['email']
        if Login.objects.filter(email=e).exists():
            raise forms.ValidationError('Email already registered.')
        return e

    def clean(self):
        d = super().clean()
        if d.get('password') != d.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return d


class DependentRegisterForm(forms.Form):
    DEP_TYPES = [
        ('child', 'Child'),
        ('teen', 'Teen'),
        ('young_adult', 'Young Adult'),
    ]
    full_name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=50)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=15, required=False)
    password = forms.CharField(min_length=6, widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    dependent_type = forms.ChoiceField(choices=DEP_TYPES)
    family_pin = forms.CharField(max_length=4, min_length=4)

    def clean_username(self):
        u = self.cleaned_data['username']
        if Login.objects.filter(username=u).exists():
            raise forms.ValidationError('Username already taken.')
        return u

    def clean_email(self):
        e = self.cleaned_data.get('email')
        if e and Login.objects.filter(email=e).exists():
            raise forms.ValidationError('Email already registered.')
        return e

    def clean(self):
        d = super().clean()
        if d.get('password') != d.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return d


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class OTPForm(forms.Form):
    otp = forms.CharField(min_length=6, max_length=6)


class ResetPasswordForm(forms.Form):
    password = forms.CharField(min_length=6, widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        d = super().clean()
        if d.get('password') != d.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return d
