from django import forms


class CardPaymentForm(forms.Form):
    payer_name = forms.CharField(max_length=100, label='Cardholder Name')
    card_number = forms.CharField(max_length=19, min_length=13, label='Card Number')
    expiry = forms.CharField(max_length=7, label='Expiry MM/YY')
    cvv = forms.CharField(max_length=4, min_length=3, widget=forms.PasswordInput, label='CVV')

    def clean_card_number(self):
        v = self.cleaned_data['card_number'].replace(' ', '').replace('-', '')
        if not v.isdigit():
            raise forms.ValidationError('Card number must contain only digits.')
        if len(v) < 13 or len(v) > 19:
            raise forms.ValidationError('Invalid card number length.')
        return v


class UPIPaymentForm(forms.Form):
    payer_name = forms.CharField(max_length=100, label='Your Name')
    upi_id = forms.CharField(max_length=100, label='UPI ID (e.g. name@bank)')

    def clean_upi_id(self):
        v = self.cleaned_data['upi_id']
        if '@' not in v:
            raise forms.ValidationError('Invalid UPI ID format.')
        return v


class NetBankingForm(forms.Form):
    BANKS = [
        ('SBI', 'State Bank of India'),
        ('HDFC', 'HDFC Bank'),
        ('ICICI', 'ICICI Bank'),
        ('AXIS', 'Axis Bank'),
        ('KOTAK', 'Kotak Mahindra Bank'),
        ('PNB', 'Punjab National Bank'),
        ('OTHER', 'Other'),
    ]
    payer_name = forms.CharField(max_length=100, label='Account Holder Name')
    bank = forms.ChoiceField(choices=BANKS)
