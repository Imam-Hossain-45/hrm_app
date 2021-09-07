from employees import models as emp_models
from setting.models import States, Cities
from helpers.multi_field import *


class ContactForm(forms.ModelForm):
    official_cell_number = TestMultiField(required=True)
    personal_cell_number = TestMultiField(required=True)
    dial_code = forms.CharField(required=False)

    class Meta:
        model = emp_models.AddressAndContact
        fields = ('official_cell_number', 'personal_cell_number')
        exclude = ('official_cell_number', 'personal_cell_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dial_code'] = forms.ChoiceField(
            choices=(x for x in Countries.objects.all().values_list('id', 'dial_code')),
            required=False)
        if 'official_cell_number' in self.data:
            try:
                value = self.data.get('official_cell_number').split(':::')[0:2]
                self.fields['official_cell_number'].initial = [value[0], value[1]]
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.official_cell_number not in ['',
                                                                             None] and ':::' in self.instance.official_cell_number:
            value = self.instance.official_cell_number.split(':::')[0:2]
            self.fields['official_cell_number'].initial = [value[0], value[1]]
        else:
            self.fields['official_cell_number'].initial = ['18']

        if 'personal_cell_number' in self.data:
            try:
                value = self.data.get('personal_cell_number').split(':::')[0:2]
                self.fields['personal_cell_number'].initial = [value[0], value[1]]
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.personal_cell_number not in ['',
                                                                             None] and ':::' in self.instance.personal_cell_number:
            value = self.instance.personal_cell_number.split(':::')[0:2]
            self.fields['personal_cell_number'].initial = [value[0], value[1]]
        else:
            self.fields['personal_cell_number'].initial = ['18']


class EmailForm(forms.ModelForm):
    class Meta:
        model = emp_models.AddressAndContact
        fields = ('official_email_ID', 'personal_email_ID')


class EmergencyContactForm(forms.ModelForm):
    contact = TestMultiField(required=True)
    dial_code = forms.CharField(required=False)

    class Meta:
        model = emp_models.EmergencyContact
        fields = ('name', 'relationship', 'address', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dial_code'] = forms.ChoiceField(
            choices=(x for x in Countries.objects.all().values_list('id', 'dial_code')),
            required=False)
        if 'contact' in self.data:
            try:
                value = self.data.get('contact').split(':::')[0:2]
                self.fields['contact'].initial = [value[0], value[1]]
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.contact not in ['', None] and ':::' in self.instance.contact:
            value = self.instance.contact.split(':::')[0:2]
            self.fields['contact'].initial = [value[0], value[1]]
        else:
            self.fields['contact'].initial = ['18']


class AddressForm(forms.ModelForm):
    same_as_present_address = forms.BooleanField(required=False)
    present_phone_number = TestMultiField(required=True)
    permanent_phone_number = TestMultiField(required=False)
    dial_code = forms.CharField(required=False)

    class Meta:
        model = emp_models.AddressAndContact
        fields = (
            'present_address', 'present_country', 'present_city', 'present_state', 'present_thana',
            'present_postal_code',
            'present_contact_person', 'permanent_address', 'permanent_country',
            'permanent_city',
            'permanent_state', 'permanent_thana', 'permanent_postal_code', 'permanent_contact_person',)

    def clean(self):
        same_as_present_address = self.cleaned_data.get('same_as_present_address')
        if same_as_present_address not in ['', None, False]:
            self.cleaned_data['permanent_address'] = self.cleaned_data.get('present_address')
            self.cleaned_data['permanent_country'] = self.cleaned_data.get('present_country')
            self.cleaned_data['permanent_city'] = self.cleaned_data.get('present_city')
            self.cleaned_data['permanent_state'] = self.cleaned_data.get('present_state')
            self.cleaned_data['permanent_thana'] = self.cleaned_data.get('present_thana')
            self.cleaned_data['permanent_postal_code'] = self.cleaned_data.get('present_postal_code')
            self.cleaned_data['permanent_contact_person'] = self.cleaned_data.get('present_contact_person')
            self.cleaned_data['permanent_phone_number'] = self.cleaned_data.get('present_phone_number')
        else:
            self.cleaned_data['permanent_address'] = self.cleaned_data.get('permanent_address')
            self.cleaned_data['permanent_country'] = self.cleaned_data.get('permanent_country')
            self.cleaned_data['permanent_city'] = self.cleaned_data.get('permanent_city')
            self.cleaned_data['permanent_state'] = self.cleaned_data.get('permanent_state')
            self.cleaned_data['permanent_thana'] = self.cleaned_data.get('permanent_thana')
            self.cleaned_data['permanent_postal_code'] = self.cleaned_data.get('permanent_postal_code')
            self.cleaned_data['permanent_contact_person'] = self.cleaned_data.get('permanent_contact_person')
            self.cleaned_data['permanent_phone_number'] = self.cleaned_data.get('permanent_phone_number')
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dial_code'] = forms.ChoiceField(
            choices=(x for x in Countries.objects.all().values_list('id', 'dial_code')),
            required=False)
        self.fields['present_state'].queryset = States.objects.none()
        self.fields['present_city'].queryset = Cities.objects.none()
        self.fields['permanent_state'].queryset = States.objects.none()
        self.fields['permanent_city'].queryset = Cities.objects.none()

        if 'present_country' in self.data:
            try:
                country_id = int(self.data.get('present_country'))
                self.fields['present_state'].queryset = States.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.present_country:
            self.fields['present_state'].queryset = self.instance.present_country.states_set.order_by('name')

        if 'present_state' in self.data:
            try:
                state_id = int(self.data.get('present_state'))
                self.fields['present_city'].queryset = Cities.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.present_state:
            self.fields['present_city'].queryset = self.instance.present_state.cities_set.order_by('name')

        if 'permanent_country' in self.data:
            try:
                country_id = int(self.data.get('permanent_country'))
                self.fields['permanent_state'].queryset = States.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.permanent_country:
            self.fields['permanent_state'].queryset = self.instance.permanent_country.states_set.order_by('name')

        if 'permanent_state' in self.data:
            try:
                state_id = int(self.data.get('permanent_state'))
                self.fields['permanent_city'].queryset = Cities.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.permanent_state:
            self.fields['permanent_city'].queryset = self.instance.permanent_state.cities_set.order_by('name')

        if 'present_phone_number' in self.data:
            try:
                value = self.data.get('present_phone_number').split(':::')[0:2]
                self.fields['present_phone_number'].initial = [value[0], value[1]]
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.present_phone_number and ':::' in self.instance.present_phone_number:
            value = self.instance.present_phone_number.split(':::')[0:2]
            self.fields['present_phone_number'].initial = [value[0], value[1]]
        else:
            self.fields['present_phone_number'].initial = ['18']

        if 'permanent_phone_number' in self.data:
            try:
                value = self.data.get('permanent_phone_number').split(':::')[0:2]
                self.fields['permanent_phone_number'].initial = [value[0], value[1]]
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.permanent_phone_number and ':::' in self.instance.permanent_phone_number:
            value = self.instance.permanent_phone_number.split(':::')[0:2]
            self.fields['permanent_phone_number'].initial = [value[0], value[1]]
        else:
            self.fields['permanent_phone_number'].initial = ['18']
