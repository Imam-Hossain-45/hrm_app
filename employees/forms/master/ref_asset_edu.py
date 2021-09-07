from employees import models as emp_models
from django.core.validators import EMPTY_VALUES
from setting.models import States, Cities
from helpers.multi_field import *


class ReferenceForm(forms.ModelForm):
    phone_number = TestMultiField(required=False)
    official_cell_number = TestMultiField(required=True)
    personal_cell_number = TestMultiField(required=True)
    dial_code = forms.CharField(max_length=255, required=False)

    class Meta:
        model = emp_models.Reference
        fields = ('ref_person_name', 'relationship', 'designation',
                  'official_email', 'personal_email', 'organization_name', 'address_line', 'country', 'city', 'state',
                  'thana', 'postal_code', 'contact_person')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dial_code'] = forms.ChoiceField(choices=(x for x in Countries.objects.all().values_list('id', 'dial_code')),
                                                                    required=False)
        self.fields['state'].queryset = States.objects.none()
        self.fields['city'].queryset = Cities.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = States.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.country not in EMPTY_VALUES:
            self.fields['state'].queryset = self.instance.country.states_set.order_by('name')

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['city'].queryset = Cities.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and self.instance.state not in EMPTY_VALUES:
            self.fields['city'].queryset = self.instance.state.cities_set.order_by('name')

        if 'phone_number' in self.data:
            try:
                value = self.data.get('phone_number').split(':::')[0:2]
                self.fields['phone_number'].initial = [value[0], value[1]]
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            value = self.instance.phone_number.split(':::')[0:2]
            self.fields['phone_number'].initial = [value[0], value[1]]
        else:
            self.fields['phone_number'].initial = ['18']

        if 'official_cell_number' in self.data:
            try:
                value = self.data.get('official_cell_number').split(':::')[0:2]
                self.fields['official_cell_number'].initial = [value[0], value[1]]
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
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
        elif self.instance.pk:
            value = self.instance.personal_cell_number.split(':::')[0:2]
            self.fields['personal_cell_number'].initial = [value[0], value[1]]
        else:
            self.fields['personal_cell_number'].initial = ['18']


class AssetForm(forms.ModelForm):
    class Meta:
        model = emp_models.Asset
        fields = ('asset_category', 'asset_brand_name', 'description', 'serial_number', 'date_loaned',
                  'date_returned')

    def clean(self):
        date_loaned = self.cleaned_data.get('date_loaned')
        date_returned = self.cleaned_data.get('date_returned')
        if date_loaned not in EMPTY_VALUES and date_returned not in EMPTY_VALUES:
            if date_loaned > date_returned:
                self._errors['date_returned'] = self.error_class(['Return date should be greater than loan date.'])


class EducationForm(forms.ModelForm):
    class Meta:
        model = emp_models.Education
        fields = ('degree', 'university', 'subject', 'year_of_completion', 'result_type', 'result_of_gpa', 'out_of',
                  'result_of_division', 'grade', 'marks', 'certificate')

    def clean(self):
        result_type = self.cleaned_data.get('result_type')
        if result_type == 'division':
            result_of_division = self.cleaned_data.get('result_of_division')
            self.cleaned_data['result_of_gpa'] = None
            self.cleaned_data['out_of'] = None
            self.cleaned_data['grade'] = None
            if result_of_division in EMPTY_VALUES:
                self._errors['result_of_division'] = self.error_class(['This field is required'])
            marks = self.cleaned_data.get('marks')
            if marks in EMPTY_VALUES:
                self._errors['marks'] = self.error_class(['This field is required'])
        else:
            result_of_gpa = self.cleaned_data.get('result_of_gpa')
            self.cleaned_data['result_of_division'] = None
            self.cleaned_data['marks'] = None
            if result_of_gpa in EMPTY_VALUES:
                self._errors['result_of_gpa'] = self.error_class(['This field is required'])

            out_of = self.cleaned_data.get('out_of')
            if out_of in EMPTY_VALUES:
                self._errors['out_of'] = self.error_class(['This field is required'])
            grade = self.cleaned_data.get('grade')
            if grade in EMPTY_VALUES:
                self._errors['grade'] = self.error_class(['This field is required'])

        # clear certificate file
        if self.data.get('certificate-clear'):
            self.cleaned_data['certificate'] = None


class SkillForm(forms.ModelForm):
    class Meta:
        model = emp_models.Skill
        fields = ('skill_name', 'description', 'skill_level')


class TrainingForm(forms.ModelForm):
    class Meta:
        model = emp_models.Training
        fields = ('training_title', 'country', 'training_year', 'institute', 'duration', 'duration_unit', 'certificate')


class ProfessionalCertificateForm(forms.ModelForm):
    class Meta:
        model = emp_models.ProfessionalCertificate
        fields = (
            'certificate_title', 'country', 'institute', 'institute_address', 'duration', 'duration_unit',
            'certificate')


class LanguageProficiencyForm(forms.ModelForm):
    class Meta:
        model = emp_models.LanguageProficiency
        fields = ('language', 'description', 'read', 'write', 'speak')


class DocumentForm(forms.ModelForm):
    education_certificates = forms.FileField(required=False)
    signature = forms.FileField(required=False)
    nid = forms.FileField(required=False, label='NID')
    birth_certificate = forms.FileField(required=False)
    other_document_title = forms.CharField(max_length=255, required=False)
    other_document = forms.FileField(required=False)

    class Meta:
        model = emp_models.Documents
        fields = ('resume', 'cover_letter', 'appointment_letter', 'resign_letter')


class TaxDocumentForm(forms.ModelForm):
    TIN = forms.FileField(label='Tax documents', required=False)
    work_permit_doc = forms.FileField(label='Visa documents', required=False)
    signature = forms.FileField(required=False)
    nid = forms.FileField(label='NID', required=False)
    birth_certificate = forms.FileField(required=False)

    class Meta:
        model = emp_models.Personal
        fields = ('TIN', 'work_permit_doc', 'signature', 'nid', 'birth_certificate')


class EducationalDocumentForm(forms.ModelForm):
    certificate = forms.FileField(label='Education Certificates', required=False)

    class Meta:
        model = emp_models.Education
        fields = ('certificate',)

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            self.edu_id = kwargs['instance'].id
        super().__init__(*args, **kwargs)


class OtherDocumentForm(forms.ModelForm):
    file = forms.FileField(required=False)
    id = forms.IntegerField()

    class Meta:
        model = emp_models.OthersDocuments
        fields = ('title', 'file',)

    def clean(self):
        if self.cleaned_data.get('file') is not None:
            title = self.cleaned_data.get('title')
            id = self.cleaned_data.get('id')
            if title in EMPTY_VALUES:
                self._errors['title'] = self.error_class(['This title is required'])
            else:
                if emp_models.OthersDocuments.objects.filter(title=self.cleaned_data['title'], employee_id=id).exists():
                    self._errors['title'] = self.error_class(
                        ['Documents with this title already exists for this employee.'])
        return self.cleaned_data
