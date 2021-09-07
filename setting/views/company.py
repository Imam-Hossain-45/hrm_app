from django.views.generic import ListView, FormView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from helpers.mixins import PermissionMixin
from setting.forms import (CompanyGeneralForm, PhysicalAddressForm, VirtualAddressForm, SocialLinkForm,
                           IdentificationForm)
from setting.models import *
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime
from django.forms import modelformset_factory
from helpers.functions import get_organizational_structure
from django.core.paginator import Paginator


class CompanyList(LoginRequiredMixin, PermissionMixin, ListView):
    permission_required = ['add_company', 'update_company', 'view_company', 'delete_company']
    template_name = 'setting/company/list.html'
    model = Company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        query_list = Company.objects.filter(deleted=False).order_by('id')
        paginator = Paginator(query_list, 50)
        page = self.request.GET.get('page')
        context['companies'] = paginator.get_page(page)
        index = context['companies'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class CompanyCreate(LoginRequiredMixin, PermissionMixin, FormView):
    permission_required = 'add_company'
    template_name = 'setting/company/create.html'
    form_class = CompanyGeneralForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['general_form'] = self.form_class()
        physical_form = modelformset_factory(PhysicalAddress, form=PhysicalAddressForm, can_delete=True, extra=1)
        context['physical_address_form'] = physical_form(queryset=PhysicalAddress.objects.none(),
                                                         prefix='physical_address_form_prefix')
        phone_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        context['phone_form'] = phone_form(queryset=VirtualAddress.objects.none(), prefix='phone_form_prefix')
        email_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        context['email_form'] = email_form(queryset=VirtualAddress.objects.none(), prefix='email_form_prefix')
        website_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        context['website_form'] = website_form(queryset=VirtualAddress.objects.none(), prefix='website_form_prefix')
        fax_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        context['fax_form'] = fax_form(queryset=VirtualAddress.objects.none(), prefix='fax_form_prefix')
        social_link_form = modelformset_factory(SocialLink, form=SocialLinkForm, can_delete=True, extra=1)
        context['social_link_form'] = social_link_form(queryset=SocialLink.objects.none(),
                                                       prefix='social_link_form_prefix')
        new_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                       extra=1)
        context['new_identification_form'] = new_identification_form(queryset=Identification.objects.none(),
                                                                     prefix='new_identification_form_prefix')
        context['form_type'] = 'create'
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        company_general_form = self.form_class(request.POST, request.FILES)
        context['general_form'] = company_general_form
        context['form_type'] = 'create'

        physical_form = modelformset_factory(PhysicalAddress, form=PhysicalAddressForm, can_delete=True, extra=1,
                                             min_num=1, validate_min=True)
        valid_physical_form = physical_form(request.POST, prefix='physical_address_form_prefix').is_valid()

        phone_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1, min_num=1,
                                          validate_min=True)
        valid_phone_form = phone_form(request.POST, prefix='phone_form_prefix').is_valid()

        email_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1, min_num=1,
                                          validate_min=True)
        valid_email_form = email_form(request.POST, prefix='email_form_prefix').is_valid()

        website_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1,
                                            min_num=1, validate_min=True)
        valid_website_form = website_form(request.POST, prefix='website_form_prefix').is_valid()

        fax_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1, min_num=1,
                                        validate_min=True)
        valid_fax_form = fax_form(request.POST, prefix='fax_form_prefix').is_valid()

        social_link_form = modelformset_factory(SocialLink, form=SocialLinkForm, can_delete=True, extra=1, min_num=1,
                                                validate_min=True)
        valid_social_link_form = social_link_form(request.POST, prefix='social_link_form_prefix').is_valid()

        new_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                       extra=1, min_num=1, validate_min=True)
        valid_new_identification_form = new_identification_form(request.POST, request.FILES,
                                                                prefix='new_identification_form_prefix').is_valid()
        add_new_identification = False
        if request.POST['add_new'].__eq__("1"):
            add_new_identification = True

        physical_address_form_set = physical_form(request.POST, prefix='physical_address_form_prefix')
        context['physical_address_form'] = physical_address_form_set

        phone_form_set = phone_form(request.POST, prefix='phone_form_prefix')
        context['phone_form'] = phone_form_set

        email_form_set = email_form(request.POST, prefix='email_form_prefix')
        context['email_form'] = email_form_set

        website_form_set = website_form(request.POST, prefix='website_form_prefix')
        context['website_form'] = website_form_set

        fax_form_set = fax_form(request.POST, prefix='fax_form_prefix')
        context['fax_form'] = fax_form_set

        social_link_form_set = social_link_form(request.POST, prefix='social_link_form_prefix')
        context['social_link_form'] = social_link_form_set

        new_identification_form_set = new_identification_form(request.POST, request.FILES,
                                                              prefix='new_identification_form_prefix')
        context['new_identification_form'] = new_identification_form_set

        if company_general_form.is_valid():
            company = company_general_form.save(commit=False)
            mother_company = company_general_form.cleaned_data.get('mother_company')
            current_mother_company = Company.objects.filter(mother_company=True)
            if mother_company:
                if current_mother_company.exists():
                    for com in current_mother_company:
                        com.mother_company = False
                        com.save()
            else:
                if not current_mother_company.exists():
                    company.mother_company = True

            logo = company_general_form.cleaned_data.get('logo')
            if logo:
                company.logo = logo

            company.company_start_date = datetime.now()
            company.save()

            if valid_physical_form:
                for physical_address_form in physical_address_form_set:
                    physical_address = physical_address_form.save(commit=False)
                    physical_address.address_start_date = datetime.now()
                    physical_address.save()
                    CompanyPhysicalAddress.objects.create(company=company,
                                                          physical_address=physical_address)

            if valid_phone_form:
                for phone_form in phone_form_set:
                    phone = phone_form.save(commit=False)
                    if phone_form.cleaned_data.get('address'):
                        phone.address_type = 'phone'
                        phone.address_start_date = datetime.now()
                        phone.save()
                        CompanyVirtualAddress.objects.create(company=company,
                                                             virtual_address=phone)

            if valid_email_form:
                for email_form in email_form_set:
                    email = email_form.save(commit=False)
                    if email_form.cleaned_data.get('address'):
                        email.address_type = 'email'
                        email.address_start_date = datetime.now()
                        email.save()
                        CompanyVirtualAddress.objects.create(company=company,
                                                             virtual_address=email)

            if valid_website_form:
                for website_form in website_form_set:
                    website = website_form.save(commit=False)
                    if website_form.cleaned_data.get('address'):
                        website.address_type = 'website'
                        website.address_start_date = datetime.now()
                        website.save()
                        CompanyVirtualAddress.objects.create(company=company,
                                                             virtual_address=website)

            if valid_fax_form:
                for fax_form in fax_form_set:
                    fax = fax_form.save(commit=False)
                    if fax_form.cleaned_data.get('address'):
                        fax.address_type = 'fax'
                        fax.address_start_date = datetime.now()
                        fax.save()
                        CompanyVirtualAddress.objects.create(company=company,
                                                             virtual_address=fax)

            if valid_social_link_form:
                for social_link_form in social_link_form_set:
                    social_link = social_link_form.save(commit=False)
                    if social_link_form.cleaned_data.get('link') and social_link_form.cleaned_data.get('type'):
                        social_link.link_start_date = datetime.now()
                        social_link.save()
                        CompanySocialLink.objects.create(company=company,
                                                         social_link=social_link)

            if add_new_identification and valid_new_identification_form:
                for new_identification_form in new_identification_form_set:
                    if new_identification_form.is_valid():
                        identification = new_identification_form.save(commit=False)
                        if ((new_identification_form.cleaned_data.get('title')) and
                                (new_identification_form.cleaned_data.get('short_description')) and
                                (new_identification_form.cleaned_data.get('document_number'))):
                            identification.different_from_parent = True
                            identification.new_created = True
                            identification.identification_start_date = datetime.now()
                            identification.save()
                            CompanyIdentification.objects.create(company=company,
                                                                 identification=identification)

            return redirect(reverse_lazy('beehive_admin:setting:company_list'))

        return render(request, self.template_name, {**context})


class CompanyUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """Update the specified company."""

    template_name = 'setting/company/update.html'
    form_class = CompanyGeneralForm
    permission_required = 'change_company'

    def get_object(self, queryset=None):
        company = Company.objects.get(id=self.kwargs.get('pk', ''))
        return get_object_or_404(Company, pk=company.id)

    def get_physical_address_qs(self):
        physical_addresses = PhysicalAddress.objects.filter(companyphysicaladdress__company=self.get_object(),
                                                            status='active')
        return physical_addresses

    def get_virtual_address_phone_qs(self):
        virtual_addresses_phone = VirtualAddress.objects.filter(companyvirtualaddress__company=self.get_object(),
                                                                address_type='phone', status='active')
        return virtual_addresses_phone

    def get_virtual_address_email_qs(self):
        virtual_addresses_email = VirtualAddress.objects.filter(companyvirtualaddress__company=self.get_object(),
                                                                address_type='email', status='active')
        return virtual_addresses_email

    def get_virtual_address_website_qs(self):
        virtual_addresses_website = VirtualAddress.objects.filter(companyvirtualaddress__company=self.get_object(),
                                                                  address_type='website', status='active')
        return virtual_addresses_website

    def get_virtual_address_fax_qs(self):
        virtual_addresses_fax = VirtualAddress.objects.filter(companyvirtualaddress__company=self.get_object(),
                                                              address_type='fax', status='active')
        return virtual_addresses_fax

    def get_social_link_qs(self):
        social_link = SocialLink.objects.filter(companysociallink__company=self.get_object(), status='active')
        return social_link

    def get_new_identification_qs(self):
        identification = Identification.objects.filter(companyidentification__company=self.get_object(),
                                                       new_created=True, status='active')
        return identification

    def change_children_physical_address(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = Company.objects.get(id=self.kwargs.get('pk', ''))
        initial = {
            'name': company.name,
            'short_name': company.short_name,
            'ownership_type': company.ownership_type,
            'industry': company.industry,
            'establishment_date': company.establishment_date,
            'description': company.description,
            'mother_company': company.mother_company,
            'status': company.status,
            'logo': company.logo,
        }
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['general_form'] = self.form_class(initial=initial)

        physical_address_qs = self.get_physical_address_qs()
        if not physical_address_qs.exists():
            physical_form = modelformset_factory(PhysicalAddress, form=PhysicalAddressForm, can_delete=True, extra=1)
        else:
            physical_form = modelformset_factory(PhysicalAddress, form=PhysicalAddressForm, can_delete=True, extra=0)
        context['physical_address_form'] = physical_form(queryset=physical_address_qs,
                                                         prefix='physical_address_form_prefix')

        virtual_address_phone_qs = self.get_virtual_address_phone_qs()
        if not virtual_address_phone_qs.exists():
            phone_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        else:
            phone_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0)
        context['phone_form'] = phone_form(queryset=virtual_address_phone_qs, prefix='phone_form_prefix')

        virtual_address_email_qs = self.get_virtual_address_email_qs()
        if not virtual_address_email_qs.exists():
            email_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        else:
            email_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0)
        context['email_form'] = email_form(queryset=virtual_address_email_qs, prefix='email_form_prefix')

        virtual_address_website_qs = self.get_virtual_address_website_qs()
        if not virtual_address_website_qs.exists():
            website_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        else:
            website_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0)
        context['website_form'] = website_form(queryset=virtual_address_website_qs, prefix='website_form_prefix')

        virtual_address_fax_qs = self.get_virtual_address_fax_qs()
        if not virtual_address_fax_qs.exists():
            fax_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1)
        else:
            fax_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0)
        context['fax_form'] = fax_form(queryset=virtual_address_fax_qs, prefix='fax_form_prefix')

        social_link_qs = self.get_social_link_qs()
        if not social_link_qs.exists():
            social_link_form = modelformset_factory(SocialLink, form=SocialLinkForm, can_delete=True, extra=1)
        else:
            social_link_form = modelformset_factory(SocialLink, form=SocialLinkForm, can_delete=True, extra=0)
        context['social_link_form'] = social_link_form(queryset=social_link_qs, prefix='social_link_form_prefix')

        new_identification_qs = self.get_new_identification_qs()
        if not new_identification_qs.exists():
            new_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                           extra=1)
        else:
            new_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                           extra=0)
        context['new_identification_form'] = new_identification_form(queryset=new_identification_qs,
                                                                     prefix='new_identification_form_prefix')
        context['form_type'] = 'update'
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        company_general_form = self.form_class(request.POST, request.FILES)
        context['general_form'] = company_general_form
        context['form_type'] = 'update'

        if not self.get_physical_address_qs().exists():
            physical_form = modelformset_factory(PhysicalAddress, form=PhysicalAddressForm, can_delete=True, extra=1,
                                                 validate_min=True)
        else:
            physical_form = modelformset_factory(PhysicalAddress, form=PhysicalAddressForm, can_delete=True, extra=0,
                                                 validate_min=True)
        valid_physical_form = physical_form(request.POST, prefix='physical_address_form_prefix').is_valid()

        if not self.get_virtual_address_phone_qs().exists():
            phone_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1,
                                              validate_min=True)
        else:
            phone_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0,
                                              validate_min=True)
        valid_phone_form = phone_form(request.POST, prefix='phone_form_prefix').is_valid()

        if not self.get_virtual_address_email_qs().exists():
            email_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1,
                                              validate_min=True)
        else:
            email_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0,
                                              validate_min=True)
        valid_email_form = email_form(request.POST, prefix='email_form_prefix').is_valid()

        if not self.get_virtual_address_website_qs().exists():
            website_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1,
                                                validate_min=True)
        else:
            website_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0,
                                                validate_min=True)
        valid_website_form = website_form(request.POST, prefix='website_form_prefix').is_valid()

        if not self.get_virtual_address_fax_qs().exists():
            fax_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=1,
                                            validate_min=True)
        else:
            fax_form = modelformset_factory(VirtualAddress, form=VirtualAddressForm, can_delete=True, extra=0,
                                            validate_min=True)
        valid_fax_form = fax_form(request.POST, prefix='fax_form_prefix').is_valid()

        if not self.get_social_link_qs().exists():
            social_link_form = modelformset_factory(SocialLink, form=SocialLinkForm, can_delete=True, extra=1,
                                                    validate_min=True)
        else:
            social_link_form = modelformset_factory(SocialLink, form=SocialLinkForm, can_delete=True, extra=0,
                                                    validate_min=True)
        valid_social_link_form = social_link_form(request.POST, prefix='social_link_form_prefix').is_valid()

        if not self.get_new_identification_qs().exists():
            new_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                           extra=1, validate_min=True)
        else:
            new_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                           extra=0, validate_min=True)
        valid_new_identification_form = new_identification_form(request.POST, request.FILES,
                                                                prefix='new_identification_form_prefix').is_valid()
        add_new_identification = False
        if request.POST['add_new'].__eq__("1"):
            add_new_identification = True

        physical_address_form_set = physical_form(request.POST, prefix='physical_address_form_prefix')
        context['physical_address_form'] = physical_address_form_set

        phone_form_set = phone_form(request.POST, prefix='phone_form_prefix')
        context['phone_form'] = phone_form_set

        email_form_set = email_form(request.POST, prefix='email_form_prefix')
        context['email_form'] = email_form_set

        website_form_set = website_form(request.POST, prefix='website_form_prefix')
        context['website_form'] = website_form_set

        fax_form_set = fax_form(request.POST, prefix='fax_form_prefix')
        context['fax_form'] = fax_form_set

        social_link_form_set = social_link_form(request.POST, prefix='social_link_form_prefix')
        context['social_link_form'] = social_link_form_set

        new_identification_form_set = new_identification_form(request.POST, request.FILES,
                                                              prefix='new_identification_form_prefix')
        context['new_identification_form'] = new_identification_form_set

        if company_general_form.is_valid():
            company = Company.objects.get(id=self.get_object().id)

            mother_company = company_general_form.cleaned_data.get('mother_company')
            current_mother_company = Company.objects.filter(mother_company=True)
            if mother_company and not company.mother_company:
                if current_mother_company.exists():
                    for com in current_mother_company:
                        com.mother_company = False
                        com.save()
                company.mother_company = True

            company.name = company_general_form.cleaned_data.get('name')
            company.short_name = company_general_form.cleaned_data.get('short_name')
            company.ownership_type = company_general_form.cleaned_data.get('ownership_type')
            company.industry = company_general_form.cleaned_data.get('industry')
            company.description = company_general_form.cleaned_data.get('description')
            company.status = company_general_form.cleaned_data.get('status')

            logo = company_general_form.cleaned_data.get('logo')
            if logo:
                company.logo = logo

            if company_general_form.cleaned_data.get('establishment_date'):
                company.establishment_date = company_general_form.cleaned_data.get('establishment_date')
            company.save()

            if valid_physical_form:
                for physical_address_form in physical_address_form_set:
                    physical_address = physical_address_form.save(commit=False)
                    if physical_address_form.cleaned_data.get('delete'):
                        if physical_address_form.cleaned_data.get('id'):
                            PhysicalAddress.objects.filter(
                                id=physical_address_form.cleaned_data.get('id').id).update(
                                status='inactive',
                                address_end_date=datetime.now()
                            )
                        else:
                            physical_address.delete()
                    else:
                        if physical_address_form.cleaned_data.get('id'):
                            PhysicalAddress.objects.filter(
                                id=physical_address_form.cleaned_data.get('id').id).update(
                                address_line_1=physical_address_form.cleaned_data.get('address_line_1'),
                                address_line_2=physical_address_form.cleaned_data.get('address_line_2'),
                                country=physical_address_form.cleaned_data.get('country'),
                                state=physical_address_form.cleaned_data.get('state'),
                                city=physical_address_form.cleaned_data.get('city'),
                                area=physical_address_form.cleaned_data.get('area'),
                                postal_code=physical_address_form.cleaned_data.get('postal_code'),
                                description=physical_address_form.cleaned_data.get('description')
                            )
                        else:
                            physical_address.address_start_date = datetime.now()
                            physical_address.save()
                            CompanyPhysicalAddress.objects.create(company=company,
                                                                  physical_address=physical_address)

            if valid_phone_form:
                for phone_form in phone_form_set:
                    phone = phone_form.save(commit=False)
                    if phone_form.cleaned_data.get('delete'):
                        if phone_form.cleaned_data.get('id'):
                            VirtualAddress.objects.filter(
                                id=phone_form.cleaned_data.get('id').id).update(
                                status='inactive',
                                address_end_date=datetime.now()
                            )
                        else:
                            phone.delete()
                    else:
                        if phone_form.cleaned_data.get('address'):
                            if phone_form.cleaned_data.get('id'):
                                VirtualAddress.objects.filter(id=phone_form.cleaned_data.get('id').id).update(
                                    address=phone_form.cleaned_data.get('address'),
                                    description=phone_form.cleaned_data.get('description')
                                )
                            else:
                                phone.address_type = 'phone'
                                phone.address_start_date = datetime.now()
                                phone.save()
                                CompanyVirtualAddress.objects.create(company=company, virtual_address=phone)

            if valid_email_form:
                for email_form in email_form_set:
                    email = email_form.save(commit=False)
                    if email_form.cleaned_data.get('delete'):
                        if email_form.cleaned_data.get('id'):
                            VirtualAddress.objects.filter(id=email_form.cleaned_data.get('id').id).update(
                                status='inactive',
                                address_end_date=datetime.now()
                            )
                        else:
                            email.delete()
                    else:
                        if email_form.cleaned_data.get('address'):
                            if email_form.cleaned_data.get('id'):
                                VirtualAddress.objects.filter(id=email_form.cleaned_data.get('id').id).update(
                                    address=email_form.cleaned_data.get('address'),
                                    description=email_form.cleaned_data.get('description')
                                )
                            else:
                                email.address_type = 'email'
                                email.address_start_date = datetime.now()
                                email.save()
                                CompanyVirtualAddress.objects.create(company=company, virtual_address=email)

            if valid_website_form:
                for website_form in website_form_set:
                    website = website_form.save(commit=False)
                    if website_form.cleaned_data.get('delete'):
                        if website_form.cleaned_data.get('id'):
                            VirtualAddress.objects.filter(id=website_form.cleaned_data.get('id').id).update(
                                status='inactive',
                                address_end_date=datetime.now()
                            )
                        else:
                            website.delete()
                    else:
                        if website_form.cleaned_data.get('address'):
                            if website_form.cleaned_data.get('id'):
                                VirtualAddress.objects.filter(id=website_form.cleaned_data.get('id').id).update(
                                    address=website_form.cleaned_data.get('address'),
                                    description=website_form.cleaned_data.get('description')
                                )
                            else:
                                website.address_type = 'website'
                                website.address_start_date = datetime.now()
                                website.save()
                                CompanyVirtualAddress.objects.create(company=company, virtual_address=website)

            if valid_fax_form:
                for fax_form in fax_form_set:
                    fax = fax_form.save(commit=False)
                    if fax_form.cleaned_data.get('delete'):
                        if fax_form.cleaned_data.get('id'):
                            VirtualAddress.objects.filter(id=fax_form.cleaned_data.get('id').id).update(
                                status='inactive',
                                address_end_date=datetime.now()
                            )
                        else:
                            fax.delete()
                    else:
                        if fax_form.cleaned_data.get('address'):
                            if fax_form.cleaned_data.get('id'):
                                VirtualAddress.objects.filter(id=fax_form.cleaned_data.get('id').id).update(
                                    address=fax_form.cleaned_data.get('address'),
                                    description=fax_form.cleaned_data.get('description')
                                )
                            else:
                                fax.address_type = 'fax'
                                fax.address_start_date = datetime.now()
                                fax.save()
                                CompanyVirtualAddress.objects.create(company=company, virtual_address=fax)

            if valid_social_link_form:
                for social_link_form in social_link_form_set:
                    social_link = social_link_form.save(commit=False)
                    if social_link_form.cleaned_data.get('delete'):
                        if social_link_form.cleaned_data.get('id'):
                            SocialLink.objects.filter(id=social_link_form.cleaned_data.get('id').id).update(
                                status='inactive',
                                link_end_date=datetime.now()
                            )
                        else:
                            social_link.delete()
                    else:
                        if social_link_form.cleaned_data.get('link') and social_link_form.cleaned_data.get('type'):
                            if social_link_form.cleaned_data.get('id'):
                                SocialLink.objects.filter(id=social_link_form.cleaned_data.get('id').id).update(
                                    type=social_link_form.cleaned_data.get('type'),
                                    link=social_link_form.cleaned_data.get('link'),
                                    description=social_link_form.cleaned_data.get('description')
                                )
                            else:
                                social_link.link_start_date = datetime.now()
                                social_link.save()
                                CompanySocialLink.objects.create(company=company, social_link=social_link)

            if add_new_identification and valid_new_identification_form:
                for new_identification_form in new_identification_form_set:
                    if new_identification_form.is_valid():
                        identification = new_identification_form.save(commit=False)
                        if new_identification_form.cleaned_data.get('delete'):
                            if new_identification_form.cleaned_data.get('id'):
                                Identification.objects.filter(
                                    id=new_identification_form.cleaned_data.get('id').id).update(
                                    status='inactive',
                                    identification_end_date=datetime.now()
                                )
                            else:
                                identification.delete()
                        else:
                            if ((new_identification_form.cleaned_data.get('title')) and
                                    (new_identification_form.cleaned_data.get('short_description')) and
                                    (new_identification_form.cleaned_data.get('document_number'))):
                                if new_identification_form.cleaned_data.get('id'):
                                    identification = Identification.objects.filter(
                                        id=new_identification_form.cleaned_data.get('id').id)
                                    identification.update(
                                        title=new_identification_form.cleaned_data.get('title'),
                                        short_description=new_identification_form.cleaned_data.get('short_description'),
                                        document_number=new_identification_form.cleaned_data.get('document_number'),
                                        issue_date=new_identification_form.cleaned_data.get('issue_date'),
                                        expiry_date=new_identification_form.cleaned_data.get('expiry_date'),
                                        attachment_title=new_identification_form.cleaned_data.get('attachment_title')
                                    )
                                    if new_identification_form.cleaned_data.get('attachment_file'):
                                        for id in identification:
                                            id.attachment_file = \
                                                new_identification_form.cleaned_data.get('attachment_file')
                                            id.save()

                                else:
                                    identification.different_from_parent = True
                                    identification.new_created = True
                                    identification.identification_start_date = datetime.now()
                                    identification.save()
                                    CompanyIdentification.objects.create(company=company,
                                                                         identification=identification)

            return redirect(reverse_lazy('beehive_admin:setting:company_list'))

        return render(request, self.template_name, {**context})


class CompanyDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """Delete the specified company."""

    permission_required = 'delete_company'
    model = Company
    success_url = reverse_lazy('beehive_admin:setting:company_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def post(self, request, *args, **kwargs):
        """
        overriding delete method
        """

        company_object = self.get_object()
        company = Company.objects.get(id=company_object.id)
        company.deleted = True
        company.status = 'inactive'
        company.save()

        company_physical_addresses = PhysicalAddress.objects.filter(companyphysicaladdress__company=company,
                                                                    status='active')
        if company_physical_addresses.exists():
            for address in company_physical_addresses:
                address.status = 'inactive'
                address.address_end_date = datetime.now()
                address.save()

        company_virtual_addresses = VirtualAddress.objects.filter(companyvirtualaddress__company=company,
                                                                  status='active')
        if company_virtual_addresses.exists():
            for address in company_virtual_addresses:
                address.status = 'inactive'
                address.address_end_date = datetime.now()
                address.save()

        company_social_links = SocialLink.objects.filter(companysociallink__company=company, status='active')
        if company_social_links.exists():
            for link in company_social_links:
                link.status = 'inactive'
                link.address_end_date = datetime.now()
                link.save()

        company_identifications = Identification.objects.filter(companyidentification__company=company, status='active')
        if company_identifications.exists():
            for identification in company_identifications:
                identification.status = 'inactive'
                identification.address_end_date = datetime.now()
                identification.save()

        return redirect(reverse_lazy('beehive_admin:setting:company_list'))
