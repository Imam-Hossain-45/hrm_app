from django import forms
from employees import models as emp_models
from datetime import date
from django.forms.widgets import ClearableFileInput
from django.core.validators import EMPTY_VALUES


class MyClearableFileInput(ClearableFileInput):
    initial_text = 'Currently'
    input_text = 'change'
    clear_checkbox_label = 'clear'


class DOBForm(forms.ModelForm):
    birth_certificate = forms.ImageField(required=False, widget=MyClearableFileInput)

    class Meta:
        model = emp_models.Personal
        fields = ('date_of_birth', 'place_of_birth', 'birth_certificate')

    def clean(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth is not None:
            today = date.today()
            if date_of_birth > today:
                self._errors['date_of_birth'] = self.error_class(['Please enter a valid date'])
        # clear birth certificate file
        if self.data.get('birth_certificate-clear'):
            self.cleaned_data['birth_certificate'] = None

        return self.cleaned_data


class NationalityForm(forms.ModelForm):
    nid = forms.ImageField(required=False, widget=MyClearableFileInput, label='NID')
    passport = forms.ImageField(required=False, widget=MyClearableFileInput)

    class Meta:
        model = emp_models.Personal
        fields = ('nationality', 'passport_number', 'nid_or_ssn_number', 'passport_expiry_date', 'nid', 'passport')

    def clean(self):
        # clear nid file
        if self.data.get('nid-clear'):
            self.cleaned_data['nid'] = None

        # clear passport file
        if self.data.get('passport-clear'):
            self.cleaned_data['passport'] = None

        return self.cleaned_data


class TaxForm(forms.ModelForm):
    TIN = forms.ImageField(required=False, widget=MyClearableFileInput, label='TIN')

    class Meta:
        model = emp_models.Personal
        fields = ('tin_number', 'TIN')

    def clean(self):
        # clear nid file
        if self.data.get('TIN-clear'):
            self.cleaned_data['TIN'] = None

        return self.cleaned_data


class VisaForm(forms.ModelForm):
    visa_type = forms.CharField(required=True)
    visa_number = forms.CharField(required=True)
    work_permit_no = forms.CharField(required=True)
    work_permit_doc = forms.ImageField(required=False, widget=MyClearableFileInput)

    class Meta:
        model = emp_models.Personal
        fields = ('visa_type', 'visa_number', 'work_permit_no', 'work_permit_expiry_date', 'work_permit_doc')

    def clean(self):
        # clear nid file
        if self.data.get('work_permit_doc-clear'):
            self.cleaned_data['work_permit_doc'] = None

        return self.cleaned_data


class DrivingForm(forms.ModelForm):
    driving_licence_doc = forms.ImageField(required=False, widget=MyClearableFileInput)

    class Meta:
        model = emp_models.Personal
        fields = ('driving_licence_no', 'driving_licence_expiry_date', 'driving_licence_doc')

    def clean(self):
        # clear nid file
        if self.data.get('driving_licence_doc-clear'):
            self.cleaned_data['driving_licence_doc'] = None

        return self.cleaned_data


class OthersForm(forms.ModelForm):
    fingerprint = forms.ImageField(required=False, widget=MyClearableFileInput)
    signature = forms.ImageField(required=False, widget=MyClearableFileInput)

    class Meta:
        model = emp_models.Personal
        fields = (
            'mothers_name', 'fathers_name', 'marital_status', 'spouse_name', 'no_of_child', 'height_ft', 'height_in',
            'weight', 'weight_unit', 'blood_group', 'identification_mark', 'religion', 'caste', 'mother_tongue',
            'police_station_address', 'fingerprint', 'signature')

    def clean(self):
        marital_status = self.cleaned_data.get('marital_status')
        if marital_status == 'married':
            spouse_name = self.cleaned_data.get('spouse_name')
            if spouse_name in EMPTY_VALUES:
                self._errors['spouse_name'] = self.error_class(['This field is required'])

        # clear fingerprint file
        if self.data.get('fingerprint-clear'):
            self.cleaned_data['fingerprint'] = None

        # clear signature file
        if self.data.get('signature-clear'):
            self.cleaned_data['signature'] = None

        return self.cleaned_data


class FavouriteForm(forms.ModelForm):
    class Meta:
        model = emp_models.Personal
        fields = ('preferred_food', 'hobby')

    def clean(self):
        preferred_food = self.cleaned_data.get('preferred_food')
        if preferred_food is not None:
            if ';' in preferred_food or '.' in preferred_food or '|' in preferred_food or '/' in preferred_food:
                self._errors['preferred_food'] = self.error_class(['Each food name is separated by comma (,)'])
        hobby = self.cleaned_data.get('hobby')
        if hobby is not None:
            if ';' in hobby or '.' in hobby or '|' in hobby or '/' in hobby:
                self._errors['hobby'] = self.error_class(['Each hobby is separated by comma (,)'])
