from django import forms
from django.forms import modelformset_factory
from django.apps import apps
from .models import *


class OrganizationalStructureForm(forms.ModelForm):
    class Meta:
        model = OrganizationalStructure
        fields = '__all__'


class ProjectGeneralForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def clean_belongs_to(self):
        cleaned_data = super().clean()
        belongs_to = cleaned_data.get("belongs_to")
        if belongs_to is None:
            raise forms.ValidationError('This field is required')
        return belongs_to

    def clean_company(self):
        cleaned_data = super().clean()
        belongs_to = cleaned_data.get("belongs_to")
        if belongs_to is not None:
            if "company".__eq__(belongs_to):
                company = self.cleaned_data['company']
                if company is None:
                    raise forms.ValidationError('This field is required')
                return company

    def clean_business_unit(self):
        cleaned_data = super().clean()
        belongs_to = cleaned_data.get("belongs_to")
        if belongs_to is not None:
            if "business-unit".__eq__(belongs_to):
                business_unit = self.cleaned_data['business_unit']
                if business_unit is None:
                    raise forms.ValidationError('This field is required')
                return business_unit

    def clean_branch(self):
        cleaned_data = super().clean()
        belongs_to = cleaned_data.get("belongs_to")
        if belongs_to is not None:
            if "branch".__eq__(belongs_to):
                branch = self.cleaned_data['branch']
                if branch is None:
                    raise forms.ValidationError('This field is required')
                return branch

    def clean_division(self):
        cleaned_data = super().clean()
        belongs_to = cleaned_data.get("belongs_to")
        if belongs_to is not None:
            if "division".__eq__(belongs_to):
                division = self.cleaned_data['division']
                if division is None:
                    raise forms.ValidationError('This field is required')
                return division

    def clean_department(self):
        cleaned_data = super().clean()
        belongs_to = cleaned_data.get("belongs_to")
        if belongs_to is not None:
            if "department".__eq__(belongs_to):
                department = self.cleaned_data['department']
                if department is None:
                    raise forms.ValidationError('This field is required')
                return department


class PhysicalAddressForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    class Meta:
        model = PhysicalAddress
        fields = '__all__'


class VirtualAddressForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    class Meta:
        model = VirtualAddress
        fields = '__all__'


class SocialLinkForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    class Meta:
        model = SocialLink
        fields = '__all__'


class IdentificationForm(forms.ModelForm):
    add_new = forms.BooleanField(required=False)
    delete = forms.BooleanField(required=False)

    class Meta:
        model = Identification
        fields = '__all__'

    def my_is_valid(self):
        self.full_clean()
        different_from_parent = self.cleaned_data.get('different_from_parent')
        if not different_from_parent:
            return False
        return different_from_parent

    def get_title(self):
        return self.cleaned_data.get('title')

    def get_short_description(self):
        return self.cleaned_data.get('short_description')


class CompanyGeneralForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

    def clean_logo(self):
        image = self.cleaned_data.get('logo', False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2mb )")
        return image


class BusinessUnitGeneralForm(forms.ModelForm):
    try:
        OrganizationalStructure.objects.get(item='business-unit')
        if OrganizationalStructure.objects.filter(item='business-unit', parent_item__item='company').exists():
            company = forms.ModelChoiceField(queryset=Company.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='business-unit', parent_item__item='business-unit').exists():
            business_unit = forms.ModelChoiceField(queryset=BusinessUnit.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='business-unit', parent_item__item='branch').exists():
            branch = forms.ModelChoiceField(queryset=Branch.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='business-unit', parent_item__item='division').exists():
            division = forms.ModelChoiceField(queryset=Division.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='business-unit', parent_item__item='department').exists():
            department = forms.ModelChoiceField(queryset=Department.objects.filter(status='active'))
    except:
        pass

    class Meta:
        model = BusinessUnit
        fields = '__all__'

    def clean_logo(self):
        image = self.cleaned_data.get('logo', False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2mb )")
        return image


class BranchGeneralForm(forms.ModelForm):
    try:
        OrganizationalStructure.objects.get(item='branch')
        if OrganizationalStructure.objects.filter(item='branch', parent_item__item='company').exists():
            company = forms.ModelChoiceField(queryset=Company.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='branch', parent_item__item='business-unit').exists():
            business_unit = forms.ModelChoiceField(queryset=BusinessUnit.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='branch', parent_item__item='branch').exists():
            branch = forms.ModelChoiceField(queryset=Branch.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='branch', parent_item__item='division').exists():
            division = forms.ModelChoiceField(queryset=Division.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='branch', parent_item__item='department').exists():
            department = forms.ModelChoiceField(queryset=Department.objects.filter(status='active'))
    except:
        pass

    class Meta:
        model = Branch
        fields = '__all__'

    def clean_logo(self):
        image = self.cleaned_data.get('logo', False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2mb )")
        return image


class DivisionGeneralForm(forms.ModelForm):
    try:
        OrganizationalStructure.objects.get(item='division')
        if OrganizationalStructure.objects.filter(item='division', parent_item__item='company').exists():
            company = forms.ModelChoiceField(queryset=Company.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='division', parent_item__item='business-unit').exists():
            business_unit = forms.ModelChoiceField(queryset=BusinessUnit.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='division', parent_item__item='branch').exists():
            branch = forms.ModelChoiceField(queryset=Branch.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='division', parent_item__item='division').exists():
            division = forms.ModelChoiceField(queryset=Division.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='division', parent_item__item='department').exists():
            department = forms.ModelChoiceField(queryset=Department.objects.filter(status='active'))
    except:
        pass

    class Meta:
        model = Division
        fields = '__all__'

    def clean_logo(self):
        image = self.cleaned_data.get('logo', False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2mb )")
        return image


class DepartmentGeneralForm(forms.ModelForm):
    try:
        OrganizationalStructure.objects.get(item='department')
        if OrganizationalStructure.objects.filter(item='department', parent_item__item='company').exists():
            company = forms.ModelChoiceField(queryset=Company.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='department', parent_item__item='business-unit').exists():
            business_unit = forms.ModelChoiceField(queryset=BusinessUnit.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='department', parent_item__item='branch').exists():
            branch = forms.ModelChoiceField(queryset=Branch.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='department', parent_item__item='division').exists():
            division = forms.ModelChoiceField(queryset=Division.objects.filter(status='active'))
        if OrganizationalStructure.objects.filter(item='department', parent_item__item='department').exists():
            department = forms.ModelChoiceField(queryset=Department.objects.filter(status='active'))
    except:
        pass

    class Meta:
        model = Department
        fields = '__all__'

    def clean_logo(self):
        image = self.cleaned_data.get('logo', False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2mb )")
        return image


OrganizationalStructureFormSet = modelformset_factory(OrganizationalStructure, form=OrganizationalStructureForm)
