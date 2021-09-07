from django import forms
from payroll.models import SalaryPaymentMethod, PaymentDisbursedInfo
from datetime import datetime
from setting.models import Bank


class PaymentForm(forms.ModelForm):
    class Meta:
        model = SalaryPaymentMethod
        fields = ('payment_mode',)


class DisburseForm(forms.ModelForm):
    mixed_bank_name = forms.ModelChoiceField(required=False, queryset=Bank.objects.all(), label='Employee Bank Name', empty_label="-------")
    mixed_bank_account_name = forms.CharField(required=False, label='Employee Bank A/C Name')
    mixed_branch_code = forms.CharField(required=False, label='Bank branch code')
    mixed_ac_no = forms.IntegerField(required=False, label='Bank A/C No')
    mixed_routing_no = forms.CharField(required=False, label='Routing number')
    mixed_cheque_number = forms.IntegerField(required=False, label='Cheque number')
    mixed_service = forms.ChoiceField(required=False,
                                      choices=(('', '-------'), ('bkash', 'bkash'), ('rocket', 'Rocket'),
                                               ('upay', 'Upay'),
                                               ('nagad', 'Nagad'), ('mcash', 'mCash'), ('dmoney', 'Dmoney'),
                                               ('other', 'Other')), label='Select Service')
    mixed_mobile_number = forms.CharField(required=False, label='Mobile number')
    disbursed_date = forms.DateField(label='Date of Disbursement', initial=datetime.now())

    class Meta:
        model = PaymentDisbursedInfo
        exclude = ('payment_method',)


class DisburseGroupForm(forms.Form):
    disbursed_date = forms.DateField(label='Date of Disbursement', initial=datetime.now())
    cheque_number = forms.IntegerField(required=False)
