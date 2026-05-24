from django import forms
from goals.models import SavingsGoal


class ExpenseForm(forms.Form):
    category = forms.CharField(max_length=50)
    description = forms.CharField(max_length=200)
    amount = forms.FloatField(min_value=0.01)


class GoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['goal_name', 'target_amount', 'target_date', 'category', 'icon', 'description']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class ContributionForm(forms.Form):
    amount = forms.FloatField(min_value=0.01)


class DependentProfileForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
