from django import forms
from chores.models import Chore, ChoreCategory
from dependents.models import FamilyDependent
from transactions.models import AllowanceSchedule


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ['chore_name', 'category', 'assigned_to', 'reward_amount',
                  'difficulty', 'deadline', 'description', 'is_recurring', 'recurring_type']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class BalanceAdjustForm(forms.Form):
    amount = forms.FloatField()
    is_credit = forms.BooleanField(required=False)
    reason = forms.CharField(max_length=200)


class AllowanceForm(forms.ModelForm):
    class Meta:
        model = AllowanceSchedule
        fields = ['amount', 'frequency', 'day_of_week', 'day_of_month', 'is_active']


class HeadProfileForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15, required=False)
    family_name = forms.CharField(max_length=100)


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(min_length=6, widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        d = super().clean()
        if d.get('new_password') != d.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return d
