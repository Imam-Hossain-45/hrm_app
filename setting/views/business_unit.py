from django.views.generic import ListView, FormView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from helpers.mixins import PermissionMixin
from setting.forms import (BusinessUnitGeneralForm, PhysicalAddressForm, VirtualAddressForm, SocialLinkForm,
                           IdentificationForm)
from setting.models import *
from django.shortcuts import redirect, render, get_object_or_404
from datetime import datetime
from django.forms import modelformset_factory
from django.db.models import Q
from helpers.functions import get_organizational_structure
from django.core.paginator import Paginator


def get_parent_item():
    if OrganizationalStructure.objects.filter(item='business-unit').exists():
        structure_object = OrganizationalStructure.objects.get(item='business-unit')
        if structure_object.parent_item:
            return str(structure_object.parent_item.item)
    return None


class BusinessUnitList(LoginRequiredMixin, PermissionMixin, ListView):
    """List of business units."""

    template_name = 'setting/business_unit/list.html'
    model = BusinessUnit
    permission_required = ['add_businessunit', 'update_businessunit', 'view_businessunit', 'delete_businessunit']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        query_list = BusinessUnit.objects.filter(deleted=False).order_by('id')
        paginator = Paginator(query_list, 50)
        page = self.request.GET.get('page')
        context['business_units'] = paginator.get_page(page)
        index = context['business_units'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class BusinessUnitCreate(LoginRequiredMixin, PermissionMixin, FormView):
    """Create and save a newly created business unit."""

    permission_required = 'add_businessunit'
    template_name = 'setting/business_unit/create.html'
    form_class = BusinessUnitGeneralForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['parent_item'] = get_parent_item()
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
        parent_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                          extra=1)
        context['parent_identification_form'] = parent_identification_form(queryset=Identification.objects.none(),
                                                                           prefix='parent_identification_form_prefix')
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
        context['parent_item'] = get_parent_item()
        business_unit_general_form = self.form_class(request.POST, request.FILES)
        context['general_form'] = business_unit_general_form
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

        parent_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                          extra=1, min_num=0, validate_min=True)

        # submitted_parent_identification_formset = \
        #     parent_identification_form(request.POST, request.FILES, prefix='parent_identification_form_prefix')

        submitted_parent_identification_formset = []

        valid_parent_identification_form = True
        for form in submitted_parent_identification_formset:
            if form.my_is_valid():
                different_from_parent = form.cleaned_data.get('different_from_parent')
                if different_from_parent and not form.is_valid():
                    valid_parent_identification_form = False

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

        parent_identification_form_set = parent_identification_form(request.POST, request.FILES,
                                                                    prefix='parent_identification_form_prefix')
        context['parent_identification_form'] = parent_identification_form_set

        new_identification_form_set = new_identification_form(request.POST, request.FILES,
                                                              prefix='new_identification_form_prefix')
        context['new_identification_form'] = new_identification_form_set

        if business_unit_general_form.is_valid():
            business_unit = business_unit_general_form.save(commit=False)
            different_physical_address = business_unit_general_form.cleaned_data['different_physical_address']
            different_virtual_address = business_unit_general_form.cleaned_data['different_virtual_address']

            if ((different_physical_address and not valid_physical_form) or
                    not valid_parent_identification_form or
                    (add_new_identification and not valid_new_identification_form) or
                    (different_virtual_address and not (valid_phone_form and valid_email_form and valid_website_form and
                                                        valid_fax_form and valid_social_link_form))):
                return render(request, self.template_name, {**context})

            belongs_to = get_parent_item()
            company = business_unit_general_form.cleaned_data['company']
            bus_unit = business_unit_general_form.cleaned_data['business_unit']
            branch = business_unit_general_form.cleaned_data['branch']
            division = business_unit_general_form.cleaned_data['division']
            department = business_unit_general_form.cleaned_data['department']

            if belongs_to is not None:
                if company:
                    business_unit.company = company
                if bus_unit:
                    business_unit.business_unit = bus_unit
                if branch:
                    business_unit.branch = branch
                if division:
                    business_unit.division = division
                if department:
                    business_unit.department = department

            business_unit.save()

            if different_physical_address:
                for physical_address_form in physical_address_form_set:
                    physical_address = physical_address_form.save(commit=False)
                    physical_address.address_start_date = datetime.now()
                    physical_address.save()
                    BusinessUnitPhysicalAddress.objects.create(business_unit=business_unit,
                                                               physical_address=physical_address)

            else:
                if "company".__eq__(belongs_to):
                    if CompanyPhysicalAddress.objects.filter(company=company,
                                                             physical_address__status='active').exists():
                        company_physical_addresses = \
                            CompanyPhysicalAddress.objects.filter(company=company, physical_address__status='active')
                        for address in company_physical_addresses:
                            parent_address = address.physical_address
                            new_address = \
                                BusinessUnitPhysicalAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                           physical_address=address.physical_address,
                                                                           inherited_physical_address=parent_address,
                                                                           inherited_company=company)
                            physical_address = address.physical_address
                            physical_address.pk = None
                            physical_address.address_start_date = datetime.now()
                            physical_address.save()
                            new_address.physical_address = physical_address
                            new_address.save()

                elif "business-unit".__eq__(belongs_to):
                    if BusinessUnitPhysicalAddress.objects.filter(business_unit=bus_unit,
                                                                  physical_address__status='active').exists():
                        business_unit_physical_addresses = \
                            BusinessUnitPhysicalAddress.objects.filter(business_unit=bus_unit,
                                                                       physical_address__status='active')
                        for address in business_unit_physical_addresses:
                            parent_address = address.physical_address
                            new_address = \
                                BusinessUnitPhysicalAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                           physical_address=address.physical_address,
                                                                           inherited_physical_address=parent_address,
                                                                           inherited_business_unit=bus_unit)
                            physical_address = address.physical_address
                            physical_address.pk = None
                            physical_address.address_start_date = datetime.now()
                            physical_address.save()
                            new_address.physical_address = physical_address
                            new_address.save()

                elif "branch".__eq__(belongs_to):
                    if BranchPhysicalAddress.objects.filter(branch=branch, physical_address__status='active').exists():
                        branch_physical_addresses = \
                            BranchPhysicalAddress.objects.filter(branch=branch, physical_address__status='active')
                        for address in branch_physical_addresses:
                            parent_address = address.physical_address
                            new_address = \
                                BusinessUnitPhysicalAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                           physical_address=address.physical_address,
                                                                           inherited_physical_address=parent_address,
                                                                           inherited_branch=branch)
                            physical_address = address.physical_address
                            physical_address.pk = None
                            physical_address.address_start_date = datetime.now()
                            physical_address.save()
                            new_address.physical_address = physical_address
                            new_address.save()

                elif "division".__eq__(belongs_to):
                    if DivisionPhysicalAddress.objects.filter(division=division,
                                                              physical_address__status='active').exists():
                        division_physical_addresses = \
                            DivisionPhysicalAddress.objects.filter(division=division, physical_address__status='active')
                        for address in division_physical_addresses:
                            parent_address = address.physical_address
                            new_address = \
                                BusinessUnitPhysicalAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                           physical_address=address.physical_address,
                                                                           inherited_physical_address=parent_address,
                                                                           inherited_division=division)
                            physical_address = address.physical_address
                            physical_address.pk = None
                            physical_address.address_start_date = datetime.now()
                            physical_address.save()
                            new_address.physical_address = physical_address
                            new_address.save()

                elif "department".__eq__(belongs_to):
                    if DepartmentPhysicalAddress.objects.filter(department=department,
                                                                physical_address__status='active').exists():
                        department_physical_addresses = \
                            DepartmentPhysicalAddress.objects.filter(department=department,
                                                                     physical_address__status='active')
                        for address in department_physical_addresses:
                            parent_address = address.physical_address
                            new_address = \
                                BusinessUnitPhysicalAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                           physical_address=address.physical_address,
                                                                           inherited_physical_address=parent_address,
                                                                           inherited_department=department)
                            physical_address = address.physical_address
                            physical_address.pk = None
                            physical_address.address_start_date = datetime.now()
                            physical_address.save()
                            new_address.physical_address = physical_address
                            new_address.save()

            if different_virtual_address:
                for phone_form in phone_form_set:
                    phone = phone_form.save(commit=False)
                    if phone_form.cleaned_data.get('address'):
                        phone.address_type = 'phone'
                        phone.address_start_date = datetime.now()
                        phone.save()
                        BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, virtual_address=phone)

                for email_form in email_form_set:
                    email = email_form.save(commit=False)
                    if email_form.cleaned_data.get('address'):
                        email.address_type = 'email'
                        email.address_start_date = datetime.now()
                        email.save()
                        BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, virtual_address=email)

                for website_form in website_form_set:
                    website = website_form.save(commit=False)
                    if website_form.cleaned_data.get('address'):
                        website.address_type = 'website'
                        website.address_start_date = datetime.now()
                        website.save()
                        BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, virtual_address=website)

                for fax_form in fax_form_set:
                    fax = fax_form.save(commit=False)
                    if fax_form.cleaned_data.get('address'):
                        fax.address_type = 'fax'
                        fax.address_start_date = datetime.now()
                        fax.save()
                        BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, virtual_address=fax)

                for social_link_form in social_link_form_set:
                    social_link = social_link_form.save(commit=False)
                    if social_link_form.cleaned_data.get('link') and social_link_form.cleaned_data.get('type'):
                        social_link.address_start_date = datetime.now()
                        social_link.save()
                        BusinessUnitSocialLink.objects.create(business_unit=business_unit, social_link=social_link)

            else:
                if "company".__eq__(belongs_to):
                    if CompanyVirtualAddress.objects.filter(company=company, virtual_address__status='active').exists():
                        company_virtual_addresses = \
                            CompanyVirtualAddress.objects.filter(company=company, virtual_address__status='active')
                        for address in company_virtual_addresses:
                            parent_address = address.virtual_address
                            new_address = \
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                          virtual_address=address.virtual_address,
                                                                          inherited_virtual_address=parent_address,
                                                                          inherited_company=company)

                            virtual_address = address.virtual_address
                            virtual_address.pk = None
                            virtual_address.address_start_date = datetime.now()
                            virtual_address.save()
                            new_address.virtual_address = virtual_address
                            new_address.save()

                    if CompanySocialLink.objects.filter(company=company, social_link__status='active').exists():
                        company_social_links = \
                            CompanySocialLink.objects.filter(company=company, social_link__status='active')
                        for link in company_social_links:
                            parent_link = link.social_link
                            new_link = \
                                BusinessUnitSocialLink.objects.create(business_unit=business_unit, inherited=True,
                                                                      social_link=link.social_link,
                                                                      inherited_social_link=parent_link,
                                                                      inherited_company=company)
                            social_link = link.social_link
                            social_link.pk = None
                            social_link.link_start_date = datetime.now()
                            social_link.save()
                            new_link.social_link = social_link
                            new_link.save()

                elif "business-unit".__eq__(belongs_to):
                    if BusinessUnitVirtualAddress.objects.filter(business_unit=bus_unit,
                                                                 virtual_address__status='active').exists():
                        business_unit_virtual_addresses = \
                            BusinessUnitVirtualAddress.objects.filter(business_unit=bus_unit,
                                                                      virtual_address__status='active')
                        for address in business_unit_virtual_addresses:
                            parent_address = address.virtual_address
                            new_address = \
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                          virtual_address=address.virtual_address,
                                                                          inherited_virtual_address=parent_address,
                                                                          inherited_business_unit=bus_unit)
                            virtual_address = address.virtual_address
                            virtual_address.pk = None
                            virtual_address.address_start_date = datetime.now()
                            virtual_address.save()
                            new_address.virtual_address = virtual_address
                            new_address.save()

                    if BusinessUnitSocialLink.objects.filter(business_unit=bus_unit,
                                                             social_link__status='active').exists():
                        business_unit_social_links = \
                            BusinessUnitSocialLink.objects.filter(business_unit=bus_unit,
                                                                  social_link__status='active')
                        for link in business_unit_social_links:
                            parent_link = link.social_link
                            new_link = \
                                BusinessUnitSocialLink.objects.create(business_unit=business_unit, inherited=True,
                                                                      social_link=link.social_link,
                                                                      inherited_social_link=parent_link,
                                                                      inherited_business_unit=bus_unit)
                            social_link = link.social_link
                            social_link.pk = None
                            social_link.link_start_date = datetime.now()
                            social_link.save()
                            new_link.social_link = social_link
                            new_link.save()

                elif "branch".__eq__(belongs_to):
                    if BranchVirtualAddress.objects.filter(branch=branch, virtual_address__status='active').exists():
                        branch_virtual_addresses = \
                            BranchVirtualAddress.objects.filter(branch=branch, virtual_address__status='active')
                        for address in branch_virtual_addresses:
                            parent_address = address.virtual_address
                            new_address = \
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                          virtual_address=address.virtual_address,
                                                                          inherited_virtual_address=parent_address,
                                                                          inherited_branch=branch)
                            virtual_address = address.virtual_address
                            virtual_address.pk = None
                            virtual_address.address_start_date = datetime.now()
                            virtual_address.save()
                            new_address.virtual_address = virtual_address
                            new_address.save()

                    if BranchSocialLink.objects.filter(branch=branch, social_link__status='active').exists():
                        branch_social_links = \
                            BranchSocialLink.objects.filter(branch=branch, social_link__status='active')
                        for link in branch_social_links:
                            parent_link = link.social_link
                            new_link = \
                                BusinessUnitSocialLink.objects.create(business_unit=business_unit, inherited=True,
                                                                      social_link=link.social_link,
                                                                      inherited_social_link=parent_link,
                                                                      inherited_branch=branch)
                            social_link = link.social_link
                            social_link.pk = None
                            social_link.link_start_date = datetime.now()
                            social_link.save()
                            new_link.social_link = social_link
                            new_link.save()

                elif "division".__eq__(belongs_to):
                    if DivisionVirtualAddress.objects.filter(division=division,
                                                             virtual_address__status='active').exists():
                        division_virtual_addresses = \
                            DivisionVirtualAddress.objects.filter(division=division, virtual_address__status='active')
                        for address in division_virtual_addresses:
                            parent_address = address.virtual_address
                            new_address = \
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                          virtual_address=address.virtual_address,
                                                                          inherited_virtual_address=parent_address,
                                                                          inherited_division=division)
                            virtual_address = address.virtual_address
                            virtual_address.pk = None
                            virtual_address.address_start_date = datetime.now()
                            virtual_address.save()
                            new_address.virtual_address = virtual_address
                            new_address.save()

                    if DivisionSocialLink.objects.filter(division=division, social_link__status='active').exists():
                        division_social_links = \
                            DivisionSocialLink.objects.filter(division=division, social_link__status='active')
                        for link in division_social_links:
                            parent_link = link.social_link
                            new_link = \
                                BusinessUnitSocialLink.objects.create(business_unit=business_unit, inherited=True,
                                                                      social_link=link.social_link,
                                                                      inherited_social_link=parent_link,
                                                                      inherited_division=division)
                            social_link = link.social_link
                            social_link.pk = None
                            social_link.link_start_date = datetime.now()
                            social_link.save()
                            new_link.social_link = social_link
                            new_link.save()
                elif "department".__eq__(belongs_to):
                    if DepartmentVirtualAddress.objects.filter(department=department,
                                                               virtual_address__status='active').exists():
                        department_virtual_addresses = \
                            DepartmentVirtualAddress.objects.filter(department=department,
                                                                    virtual_address__status='active')
                        for address in department_virtual_addresses:
                            parent_address = address.virtual_address
                            new_address = \
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit, inherited=True,
                                                                          virtual_address=address.virtual_address,
                                                                          inherited_virtual_address=parent_address,
                                                                          inherited_department=department)
                            virtual_address = address.virtual_address
                            virtual_address.pk = None
                            virtual_address.address_start_date = datetime.now()
                            virtual_address.save()
                            new_address.virtual_address = virtual_address
                            new_address.save()

                    if DepartmentSocialLink.objects.filter(department=department,
                                                           social_link__status='active').exists():
                        department_social_links = \
                            DepartmentSocialLink.objects.filter(department=department, social_link__status='active')
                        for link in department_social_links:
                            parent_link = link.social_link
                            new_link = \
                                BusinessUnitSocialLink.objects.create(business_unit=business_unit, inherited=True,
                                                                      social_link=link.social_link,
                                                                      inherited_social_link=parent_link,
                                                                      inherited_department=department)
                            social_link = link.social_link
                            social_link.pk = None
                            social_link.link_start_date = datetime.now()
                            social_link.save()
                            new_link.social_link = social_link
                            new_link.save()

            for parent_identification_form in submitted_parent_identification_formset:
                if parent_identification_form.my_is_valid():
                    # different from parent, but get the title and short description of the parent
                    identification = parent_identification_form.save(commit=False)
                    if parent_identification_form.is_valid():
                        if ((parent_identification_form.cleaned_data.get('title')) and
                                (parent_identification_form.cleaned_data.get('short_description'))):
                                if parent_identification_form.cleaned_data.get('different_from_parent'):
                                    identification.different_from_parent = True

                                identification.identification_start_date = datetime.now()
                                identification.save()
                                BusinessUnitIdentification.objects.create(business_unit=business_unit,
                                                                          identification=identification)
                else:
                    title = parent_identification_form.get_title()
                    short_description = parent_identification_form.get_short_description()

                    if "company".__eq__(belongs_to):
                        if CompanyIdentification.objects.filter(company=company, identification__title=title,
                                                                identification__short_description=short_description,
                                                                identification__status='active').exists():
                            identification_qs = \
                                Identification.objects.filter(companyidentification__company=company, title=title,
                                                              short_description=short_description, status='active')

                            if identification_qs.exists():
                                for identification in identification_qs:
                                    new_identification = \
                                        BusinessUnitIdentification.objects.create(
                                            business_unit=business_unit, inherited=True, identification=identification,
                                            inherited_identification=identification, inherited_company=company)

                                    identification.pk = None
                                    identification.different_from_parent = False
                                    identification.new_created = False
                                    identification.identification_start_date = datetime.now()
                                    identification.save()

                                    new_identification.identification = identification
                                    new_identification.save()

                    elif "business-unit".__eq__(belongs_to):
                        if BusinessUnitIdentification.objects.filter(
                            business_unit=bus_unit, identification__title=title, identification__status='active',
                            identification__short_description=short_description
                        ).exists():
                            identification_qs = \
                                Identification.objects.filter(
                                    businessunitidentification__business_unit=bus_unit, title=title,
                                    status='active', short_description=short_description
                                )

                            if identification_qs.exists():
                                for identification in identification_qs:
                                    new_identification = \
                                        BusinessUnitIdentification.objects.create(
                                            business_unit=business_unit, inherited=True, identification=identification,
                                            inherited_identification=identification, inherited_business_unit=bus_unit
                                        )

                                    identification.pk = None
                                    identification.different_from_parent = False
                                    identification.new_created = False
                                    identification.identification_start_date = datetime.now()
                                    identification.save()

                                    new_identification.identification = identification
                                    new_identification.save()

                    elif "branch".__eq__(belongs_to):
                        if BranchIdentification.objects.filter(
                            branch=branch, identification__title=title,
                            identification__short_description=short_description, identification__status='active'
                        ).exists():
                            identification_qs = \
                                Identification.objects.filter(
                                    branchidentification__branch=branch, title=title, status='active',
                                    short_description=short_description
                                )

                            if identification_qs.exists():
                                for identification in identification_qs:
                                    new_identification = \
                                        BusinessUnitIdentification.objects.create(
                                            business_unit=business_unit, inherited=True, identification=identification,
                                            inherited_identification=identification, inherited_branch=branch
                                        )

                                    identification.pk = None
                                    identification.different_from_parent = False
                                    identification.new_created = False
                                    identification.identification_start_date = datetime.now()
                                    identification.save()

                                    new_identification.identification = identification
                                    new_identification.save()

                    elif "division".__eq__(belongs_to):
                        if DivisionIdentification.objects.filter(
                            division=division, identification__title=title,
                            identification__short_description=short_description, identification__status='active'
                        ).exists():
                            identification_qs = \
                                Identification.objects.filter(
                                    divisionidentification__division=division, title=title, status='active',
                                    short_description=short_description
                                )

                            if identification_qs.exists():
                                for identification in identification_qs:
                                    new_identification = \
                                        BusinessUnitIdentification.objects.create(
                                            business_unit=business_unit, inherited=True, identification=identification,
                                            inherited_identification=identification, inherited_division=division
                                        )

                                    identification.pk = None
                                    identification.different_from_parent = False
                                    identification.new_created = False
                                    identification.identification_start_date = datetime.now()
                                    identification.save()

                                    new_identification.identification = identification
                                    new_identification.save()

                    elif "department".__eq__(belongs_to):
                        if DepartmentIdentification.objects.filter(
                            department=department, identification__title=title,
                            identification__short_description=short_description, identification__status='active'
                        ).exists():
                            identification_qs = \
                                Identification.objects.filter(
                                    departmentidentification__department=department, title=title, status='active',
                                    short_description=short_description
                                )

                            if identification_qs.exists():
                                for identification in identification_qs:
                                    new_identification = \
                                        BusinessUnitIdentification.objects.create(
                                            business_unit=business_unit, inherited=True, identification=identification,
                                            inherited_identification=identification, inherited_department=department
                                        )

                                    identification.pk = None
                                    identification.different_from_parent = False
                                    identification.new_created = False
                                    identification.identification_start_date = datetime.now()
                                    identification.save()

                                    new_identification.identification = identification
                                    new_identification.save()

            if add_new_identification:
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
                            BusinessUnitIdentification.objects.create(business_unit=business_unit,
                                                                      identification=identification)

            return redirect(reverse_lazy('beehive_admin:setting:business_unit_list'))

        return render(request, self.template_name, {**context})


class BusinessUnitUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """Update the specified business unit."""

    template_name = 'setting/business_unit/update.html'
    form_class = BusinessUnitGeneralForm
    permission_required = 'change_businessunit'

    def get_object(self, queryset=None):
        business_unit = BusinessUnit.objects.get(id=self.kwargs.get('pk', ''))
        return get_object_or_404(BusinessUnit, pk=business_unit.id)

    def get_parent_item(self):
        if OrganizationalStructure.objects.filter(item='business-unit').exists():
            structure_object = OrganizationalStructure.objects.get(item='business-unit')
            if structure_object.parent_item:
                return str(structure_object.parent_item)
        return None

    def get_physical_address_qs(self):
        physical_addresses = \
            PhysicalAddress.objects.filter(businessunitphysicaladdress__business_unit=self.get_object(),
                                           businessunitphysicaladdress__inherited=False, status='active')
        return physical_addresses

    def get_virtual_address_phone_qs(self):
        virtual_addresses_phone = \
            VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=self.get_object(),
                                          businessunitvirtualaddress__inherited=False, status='active',
                                          address_type='phone')
        return virtual_addresses_phone

    def get_virtual_address_email_qs(self):
        virtual_addresses_email = \
            VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=self.get_object(),
                                          businessunitvirtualaddress__inherited=False, status='active',
                                          address_type='email')
        return virtual_addresses_email

    def get_virtual_address_website_qs(self):
        virtual_addresses_website = \
            VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=self.get_object(),
                                          businessunitvirtualaddress__inherited=False, status='active',
                                          address_type='website')
        return virtual_addresses_website

    def get_virtual_address_fax_qs(self):
        virtual_addresses_fax = \
            VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=self.get_object(),
                                          businessunitvirtualaddress__inherited=False, status='active',
                                          address_type='fax')
        return virtual_addresses_fax

    def get_social_link_qs(self):
        social_link = SocialLink.objects.filter(businessunitsociallink__business_unit=self.get_object(),
                                                businessunitsociallink__inherited=False, status='active')
        return social_link

    def get_parent_identification_qs(self):
        identification = Identification.objects.filter(businessunitidentification__business_unit=self.get_object(),
                                                       new_created=False, status='active')
        return identification

    def get_new_identification_qs(self):
        identification = Identification.objects.filter(businessunitidentification__business_unit=self.get_object(),
                                                       new_created=True, status='active')
        return identification

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business_unit = BusinessUnit.objects.get(id=self.kwargs.get('pk', ''))
        initial = {
            'name': business_unit.name,
            'code': business_unit.code,
            'description': business_unit.description,
            'logo': business_unit.logo,
            'company': business_unit.company,
            'business_unit': business_unit.business_unit,
            'branch': business_unit.branch,
            'division': business_unit.division,
            'department': business_unit.department,
            'different_physical_address': business_unit.different_physical_address,
            'different_virtual_address': business_unit.different_virtual_address,
            'status': business_unit.status,
            'business_unit_start_date': business_unit.business_unit_start_date,
            'business_unit_end_date': business_unit.business_unit_end_date,
        }
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['parent_item'] = get_parent_item()
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

        parent_identification_qs = self.get_parent_identification_qs()
        if not parent_identification_qs.exists():
            parent_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                              extra=1)
        else:
            parent_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                              extra=0)
        context['parent_identification_form'] = parent_identification_form(queryset=parent_identification_qs,
                                                                           prefix='parent_identification_form_prefix')

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
        context['parent_item'] = get_parent_item()
        business_unit_general_form = self.form_class(request.POST, request.FILES)
        context['general_form'] = business_unit_general_form
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

        if not self.get_parent_identification_qs().exists():
            parent_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                              extra=1, validate_min=True)
        else:
            parent_identification_form = modelformset_factory(Identification, form=IdentificationForm, can_delete=True,
                                                              extra=0, validate_min=True)

        # submitted_parent_identification_formset = \
        #     parent_identification_form(request.POST, request.FILES, prefix='parent_identification_form_prefix')

        submitted_parent_identification_formset = []

        valid_parent_identification_form = True
        for form in submitted_parent_identification_formset:
            if form.my_is_valid():
                different_from_parent = form.cleaned_data.get('different_from_parent')
                if different_from_parent and not form.is_valid():
                    valid_parent_identification_form = False

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

        parent_identification_form_set = parent_identification_form(request.POST, request.FILES,
                                                                    prefix='parent_identification_form_prefix')
        context['parent_identification_form'] = parent_identification_form_set

        new_identification_form_set = new_identification_form(request.POST, request.FILES,
                                                              prefix='new_identification_form_prefix')
        context['new_identification_form'] = new_identification_form_set

        if business_unit_general_form.is_valid():
            different_physical_address = business_unit_general_form.cleaned_data['different_physical_address']
            different_virtual_address = business_unit_general_form.cleaned_data['different_virtual_address']

            if ((different_physical_address and not valid_physical_form) or
                not valid_parent_identification_form or
                (add_new_identification and not valid_new_identification_form) or
                (different_virtual_address and not (valid_phone_form and valid_email_form and valid_website_form and
                                                    valid_fax_form and valid_social_link_form))):
                return render(request, self.template_name, {**context})

            business_unit = BusinessUnit.objects.get(id=self.get_object().id)

            belongs_to = get_parent_item()
            company = business_unit_general_form.cleaned_data['company']
            bus_unit = business_unit_general_form.cleaned_data['business_unit']
            branch = business_unit_general_form.cleaned_data['branch']
            division = business_unit_general_form.cleaned_data['division']
            department = business_unit_general_form.cleaned_data['department']

            if belongs_to is not None:
                if company:
                    business_unit.company = company
                if bus_unit:
                    business_unit.business_unit = bus_unit
                if branch:
                    business_unit.branch = branch
                if division:
                    business_unit.division = division
                if department:
                    business_unit.department = department

            business_unit.name = business_unit_general_form.cleaned_data['name']
            business_unit.code = business_unit_general_form.cleaned_data['code']
            business_unit.description = business_unit_general_form.cleaned_data['description']
            business_unit.logo = business_unit_general_form.cleaned_data['logo']
            business_unit.different_physical_address = different_physical_address
            business_unit.different_virtual_address = different_virtual_address
            business_unit.status = business_unit_general_form.cleaned_data['status']
            business_unit.business_unit_start_date = business_unit_general_form.cleaned_data['business_unit_start_date']
            business_unit.business_unit_end_date = business_unit_general_form.cleaned_data['business_unit_end_date']
            business_unit.save()

            if different_physical_address:
                if PhysicalAddress.objects.filter(businessunitphysicaladdress__business_unit=business_unit,
                                                  businessunitphysicaladdress__inherited=True,
                                                  status='active').exists():
                    PhysicalAddress.objects.filter(businessunitphysicaladdress__business_unit=business_unit,
                                                   businessunitphysicaladdress__inherited=True,
                                                   status='active').update(
                        status='inactive',
                        address_end_date=datetime.now()
                    )

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
                                title=physical_address_form.cleaned_data.get('title'),
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
                            BusinessUnitPhysicalAddress.objects.create(business_unit=business_unit,
                                                                       physical_address=physical_address)

            else:
                if PhysicalAddress.objects.filter(
                    businessunitphysicaladdress__business_unit=business_unit,
                    businessunitphysicaladdress__inherited=False, status='active'
                ).exists():
                    PhysicalAddress.objects.filter(
                        businessunitphysicaladdress__business_unit=business_unit,
                        businessunitphysicaladdress__inherited=False, status='active').update(
                        status='inactive',
                        address_end_date=datetime.now()
                    )

                if "company".__eq__(belongs_to):
                    other_company_physical_addresses = \
                        PhysicalAddress.objects.filter(~Q(businessunitphysicaladdress__inherited_company=company),
                                                       businessunitphysicaladdress__business_unit=business_unit,
                                                       businessunitphysicaladdress__inherited=True, status='active')
                    if other_company_physical_addresses.exists():
                        other_company_physical_addresses.update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if CompanyPhysicalAddress.objects.filter(company=company,
                                                             physical_address__status='active').exists():
                        company_physical_addresses = \
                            CompanyPhysicalAddress.objects.filter(company=company, physical_address__status='active')
                        for address in company_physical_addresses:
                            if BusinessUnitPhysicalAddress.objects.filter(
                                business_unit=business_unit, inherited=True, physical_address__status='active',
                                inherited_physical_address=address.physical_address,
                                inherited_physical_address__status='active', inherited_company=company
                            ).exists():
                                PhysicalAddress.objects.filter(
                                    businessunitphysicaladdress__business_unit=business_unit,
                                    businessunitphysicaladdress__inherited=True,
                                    businessunitphysicaladdress__inherited_physical_address=address.physical_address,
                                    businessunitphysicaladdress__physical_address__status='active',
                                    businessunitphysicaladdress__inherited_physical_address__status='active',
                                    businessunitphysicaladdress__inherited_company=company).\
                                    update(
                                    title=address.physical_address.title,
                                    address_line_1=address.physical_address.address_line_1,
                                    address_line_2=address.physical_address.address_line_2,
                                    country=address.physical_address.country,
                                    state=address.physical_address.state,
                                    city=address.physical_address.city,
                                    area=address.physical_address.area,
                                    postal_code=address.physical_address.postal_code,
                                    description=address.physical_address.description
                                )
                            else:
                                physical_address = address.physical_address
                                new_address = \
                                    BusinessUnitPhysicalAddress.objects.create(
                                        business_unit=business_unit, physical_address=physical_address, inherited=True,
                                        inherited_physical_address=physical_address, inherited_company=company
                                    )

                                physical_address.pk = None
                                physical_address.address_start_date = datetime.now()
                                physical_address.save()

                                new_address.physical_address = physical_address
                                new_address.save()

                elif "business-unit".__eq__(belongs_to):
                    other_bu_physical_addresses = \
                        PhysicalAddress.objects.filter(~Q(businessunitphysicaladdress__inherited_business_unit=bus_unit),
                                                       businessunitphysicaladdress__business_unit=business_unit,
                                                       businessunitphysicaladdress__inherited=True, status='active')
                    if other_bu_physical_addresses.exists():
                        other_bu_physical_addresses.update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if BusinessUnitPhysicalAddress.objects.filter(business_unit=business_unit,
                                                                  physical_address__status='active').exists():
                        business_unit_physical_addresses = \
                            BusinessUnitPhysicalAddress.objects.filter(business_unit=business_unit,
                                                                       physical_address__status='active')
                        for address in business_unit_physical_addresses:
                            if BusinessUnitPhysicalAddress.objects.filter(
                                business_unit=business_unit, inherited=True, physical_address__status='active',
                                inherited_physical_address=address.physical_address,
                                inherited_physical_address__status='active', inherited_business_unit=bus_unit
                            ).exists():
                                PhysicalAddress.objects.filter(
                                    businessunitphysicaladdress__business_unit=business_unit,
                                    businessunitphysicaladdress__inherited=True,
                                    businessunitphysicaladdress__inherited_physical_address=address,
                                    businessunitphysicaladdress__inherited_physical_address__status='active',
                                    businessunitphysicaladdress__inherited_business_unit=bus_unit).\
                                    update(
                                    title=address.physical_address.title,
                                    address_line_1=address.address_line_1,
                                    address_line_2=address.address_line_2,
                                    country=address.country,
                                    state=address.state,
                                    city=address.city,
                                    area=address.area,
                                    postal_code=address.postal_code,
                                    description=address.description
                                )
                            else:
                                physical_address = address.physical_address
                                new_address = \
                                    BusinessUnitPhysicalAddress.objects.create(
                                        business_unit=business_unit, physical_address=physical_address, inherited=True,
                                        inherited_physical_address=physical_address, inherited_business_unit=bus_unit
                                    )

                                physical_address.pk = None
                                physical_address.address_start_date = datetime.now()
                                physical_address.save()

                                new_address.physical_address = physical_address
                                new_address.save()

                elif "branch".__eq__(belongs_to):
                    other_branch_physical_addresses = \
                        PhysicalAddress.objects.filter(~Q(businessunitphysicaladdress__inherited_branch=branch),
                                                       businessunitphysicaladdress__business_unit=business_unit,
                                                       businessunitphysicaladdress__inherited=True, status='active')
                    if other_branch_physical_addresses.exists():
                        other_branch_physical_addresses.update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if BranchPhysicalAddress.objects.filter(branch=branch, physical_address__status='active').exists():
                        branch_physical_addresses = \
                            BranchPhysicalAddress.objects.filter(branch=branch, physical_address__status='active')
                        for address in branch_physical_addresses:
                            if BusinessUnitPhysicalAddress.objects.filter(
                                business_unit=business_unit, inherited=True, physical_address__status='active',
                                inherited_physical_address=address.physical_address,
                                inherited_physical_address__status='active', inherited_branch=branch
                            ).exists():
                                PhysicalAddress.objects.filter(
                                    businessunitphysicaladdress__business_unit=business_unit,
                                    businessunitphysicaladdress__inherited=True,
                                    businessunitphysicaladdress__inherited_physical_address=address,
                                    businessunitphysicaladdress__inherited_physical_address__status='active',
                                    businessunitphysicaladdress__inherited_branch=branch).\
                                    update(
                                    title=address.physical_address.title,
                                    address_line_1=address.address_line_1,
                                    address_line_2=address.address_line_2,
                                    country=address.country,
                                    state=address.state,
                                    city=address.city,
                                    area=address.area,
                                    postal_code=address.postal_code,
                                    description=address.description
                                )
                            else:
                                physical_address = address.physical_address
                                new_address = \
                                    BusinessUnitPhysicalAddress.objects.create(
                                        business_unit=business_unit, physical_address=physical_address, inherited=True,
                                        inherited_physical_address=physical_address, inherited_branch=branch
                                    )

                                physical_address.pk = None
                                physical_address.address_start_date = datetime.now()
                                physical_address.save()

                                new_address.physical_address = physical_address
                                new_address.save()

                elif "division".__eq__(belongs_to):
                    other_division_physical_addresses = \
                        PhysicalAddress.objects.filter(~Q(businessunitphysicaladdress__inherited_division=division),
                                                       businessunitphysicaladdress__business_unit=business_unit,
                                                       businessunitphysicaladdress__inherited=True, status='active')
                    if other_division_physical_addresses.exists():
                        other_division_physical_addresses.update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if DivisionPhysicalAddress.objects.filter(division=division,
                                                              physical_address__status='active').exists():
                        division_physical_addresses = \
                            DivisionPhysicalAddress.objects.filter(division=division, physical_address__status='active')
                        for address in division_physical_addresses:
                            if BusinessUnitPhysicalAddress.objects.filter(
                                business_unit=business_unit, inherited=True, physical_address__status='active',
                                inherited_physical_address=address.physical_address,
                                inherited_physical_address__status='active', inherited_division=division
                            ).exists():
                                PhysicalAddress.objects.filter(
                                    businessunitphysicaladdress__business_unit=business_unit, businessunitphysicaladdress__inherited=True,
                                    businessunitphysicaladdress__inherited_physical_address=address,
                                    businessunitphysicaladdress__inherited_physical_address__status='active',
                                    businessunitphysicaladdress__inherited_division=division).\
                                    update(
                                    title=address.physical_address.title,
                                    address_line_1=address.address_line_1,
                                    address_line_2=address.address_line_2,
                                    country=address.country,
                                    state=address.state,
                                    city=address.city,
                                    area=address.area,
                                    postal_code=address.postal_code,
                                    description=address.description
                                )
                            else:
                                physical_address = address.physical_address
                                new_address = \
                                    BusinessUnitPhysicalAddress.objects.create(
                                        business_unit=business_unit, physical_address=physical_address, inherited=True,
                                        inherited_physical_address=physical_address, inherited_division=division
                                    )

                                physical_address.pk = None
                                physical_address.address_start_date = datetime.now()
                                physical_address.save()

                                new_address.physical_address = physical_address
                                new_address.save()

                elif "department".__eq__(belongs_to):
                    other_department_physical_addresses = \
                        PhysicalAddress.objects.filter(~Q(businessunitphysicaladdress__inherited_department=department),
                                                       businessunitphysicaladdress__business_unit=business_unit,
                                                       businessunitphysicaladdress__inherited=True, status='active')
                    if other_department_physical_addresses.exists():
                        other_department_physical_addresses.update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if DepartmentPhysicalAddress.objects.filter(department=department,
                                                                physical_address__status='active').exists():
                        department_physical_addresses = \
                            DepartmentPhysicalAddress.objects.filter(department=department,
                                                                     physical_address__status='active')
                        for address in department_physical_addresses:
                            if BusinessUnitPhysicalAddress.objects.filter(
                                business_unit=business_unit, inherited=True, physical_address__status='active',
                                inherited_physical_address=address.physical_address,
                                inherited_physical_address__status='active', inherited_department=department
                            ).exists():
                                PhysicalAddress.objects.filter(
                                    businessunitphysicaladdress__business_unit=business_unit,
                                    businessunitphysicaladdress__inherited=True,
                                    businessunitphysicaladdress__inherited_physical_address=address,
                                    businessunitphysicaladdress__inherited_physical_address__status='active',
                                    businessunitphysicaladdress__inherited_department=department).\
                                    update(
                                    title=address.physical_address.title,
                                    address_line_1=address.address_line_1,
                                    address_line_2=address.address_line_2,
                                    country=address.country,
                                    state=address.state,
                                    city=address.city,
                                    area=address.area,
                                    postal_code=address.postal_code,
                                    description=address.description
                                )
                            else:
                                physical_address = address.physical_address
                                new_address = \
                                    BusinessUnitPhysicalAddress.objects.create(
                                        business_unit=business_unit, physical_address=physical_address, inherited=True,
                                        inherited_physical_address=physical_address, inherited_department=department
                                    )

                                physical_address.pk = None
                                physical_address.address_start_date = datetime.now()
                                physical_address.save()

                                new_address.physical_address = physical_address
                                new_address.save()

            if different_virtual_address:
                if VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=business_unit,
                                                 businessunitvirtualaddress__inherited=True,
                                                 status='active').exists():
                    VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=business_unit,
                                                  businessunitvirtualaddress__inherited=True,
                                                  status='active').update(
                        status='inactive',
                        address_end_date=datetime.now()
                    )

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
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit,
                                                                          virtual_address=phone)

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
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit,
                                                                          virtual_address=email)

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
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit,
                                                                          virtual_address=website)

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
                                BusinessUnitVirtualAddress.objects.create(business_unit=business_unit,
                                                                          virtual_address=fax)

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
                                    link=social_link_form.cleaned_data.get('link'),
                                    type=social_link_form.cleaned_data.get('type'),
                                    description=social_link_form.cleaned_data.get('description')
                                )
                            else:
                                social_link.link_start_date = datetime.now()
                                social_link.save()
                                BusinessUnitSocialLink.objects.create(business_unit=business_unit,
                                                                      social_link=social_link)

            else:
                if VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=business_unit,
                                                 businessunitvirtualaddress__inherited=False, status='active').exists():
                    VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=business_unit,
                                                  businessunitvirtualaddress__inherited=False, status='active').update(
                        status='inactive',
                        address_end_date=datetime.now()
                    )

                if SocialLink.objects.filter(businessunitsociallink__business_unit=business_unit,
                                             businessunitsociallink__inherited=False, status='active').exists():
                    SocialLink.objects.filter(businessunitsociallink__business_unit=business_unit,
                                              businessunitsociallink__inherited=False, status='active').update(
                        status='inactive',
                        link_end_date=datetime.now()
                    )

                if "company".__eq__(belongs_to):
                    if VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_company=company),
                                                     businessunitvirtualaddress__business_unit=business_unit,
                                                     businessunitvirtualaddress__inherited=True, status='active').exists():
                        VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_company=company),
                                                      businessunitvirtualaddress__business_unit=business_unit,
                                                      businessunitvirtualaddress__inherited=True, status='active').update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if CompanyVirtualAddress.objects.filter(company=company, virtual_address__status='active').exists():
                        company_virtual_addresses = \
                            CompanyVirtualAddress.objects.filter(company=company, virtual_address__status='active')
                        for address in company_virtual_addresses:
                            if BusinessUnitVirtualAddress.objects.filter(
                                business_unit=business_unit, inherited=True, virtual_address__status='active',
                                inherited_virtual_address=address.virtual_address,
                                inherited_virtual_address__status='active', inherited_company=company
                            ).exists():
                                VirtualAddress.objects.filter(
                                    businessunitvirtualaddress__business_unit=business_unit,
                                    businessunitvirtualaddress__inherited=True,
                                    businessunitvirtualaddress__inherited_virtual_address=address.virtual_address,
                                    businessunitvirtualaddress__inherited_virtual_address__status='active',
                                    businessunitvirtualaddress__virtual_address__status='active',
                                    businessunitvirtualaddress__inherited_company=company).\
                                    update(
                                    address_type=address.virtual_address.address_type,
                                    address=address.virtual_address.address,
                                    description=address.virtual_address.description
                                )
                            else:
                                virtual_address = address.virtual_address
                                new_address = \
                                    BusinessUnitVirtualAddress.objects.create(
                                        business_unit=business_unit, inherited=True, virtual_address=virtual_address,
                                        inherited_virtual_address=virtual_address, inherited_company=company)

                                virtual_address.pk = None
                                virtual_address.address_start_date = datetime.now()
                                virtual_address.save()

                                new_address.virtual_address = virtual_address
                                new_address.save()

                    if CompanySocialLink.objects.filter(company=company, social_link__status='active').exists():
                        company_social_links = \
                            CompanySocialLink.objects.filter(company=company, social_link__status='active')
                        for link in company_social_links:
                            if BusinessUnitSocialLink.objects.filter(
                                business_unit=business_unit, inherited=True, inherited_social_link=link.social_link,
                                inherited_social_link__status='active', social_link__status='active',
                                inherited_company=company
                            ).exists():
                                SocialLink.objects.filter(
                                    businessunitsociallink__business_unit=business_unit,
                                    businessunitsociallink__inherited=True,
                                    businessunitsociallink__inherited_social_link=link.social_link,
                                    businessunitsociallink__inherited_social_link__status='active',
                                    businessunitsociallink__social_link__status='active',
                                    businessunitsociallink__inherited_company=company). \
                                    update(
                                    type=link.social_link.type,
                                    link=link.social_link.link,
                                    description=link.social_link.description
                                )
                            else:
                                social_link = link.social_link
                                new_link = \
                                    BusinessUnitSocialLink.objects.create(
                                        business_unit=business_unit, inherited=True, social_link=social_link,
                                        inherited_social_link=social_link, inherited_company=company)

                                social_link.pk = None
                                social_link.link_start_date = datetime.now()
                                social_link.save()

                                new_link.social_link = social_link
                                new_link.save()

                elif "business-unit".__eq__(belongs_to):
                    if VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_business_unit=bus_unit),
                                                     businessunitvirtualaddress__business_unit=business_unit,
                                                     businessunitvirtualaddress__inherited=True, status='active'
                                                     ).exists():
                        VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_business_unit=bus_unit),
                                                      businessunitvirtualaddress__business_unit=business_unit,
                                                      businessunitvirtualaddress__inherited=True, status='active'
                                                      ).update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if BusinessUnitVirtualAddress.objects.filter(business_unit=bus_unit,
                                                                 virtual_address__status='active').exists():
                        business_unit_virtual_addresses = \
                            BusinessUnitVirtualAddress.objects.filter(business_unit=bus_unit,
                                                                      virtual_address__status='active')
                        for address in business_unit_virtual_addresses:
                            if BusinessUnitVirtualAddress.objects.filter(
                                business_unit=business_unit, inherited=True, virtual_address__status='active',
                                inherited_virtual_address=address.virtual_address,
                                inherited_virtual_address__status='active', inherited_business_unit=bus_unit
                            ).exists():
                                VirtualAddress.objects.filter(
                                    businessunitvirtualaddress__business_unit=business_unit,
                                    businessunitvirtualaddress__inherited=True,
                                    businessunitvirtualaddress__inherited_virtual_address=address.virtual_address,
                                    businessunitvirtualaddress__inherited_virtual_address__status='active',
                                    businessunitvirtualaddress__virtual_address__status='active',
                                    businessunitvirtualaddress__inherited_business_unit=bus_unit). \
                                    update(
                                    address_type=address.virtual_address.address_type,
                                    address=address.virtual_address.address,
                                    description=address.virtual_address.description
                                )
                            else:
                                virtual_address = address.virtual_address
                                new_address = \
                                    BusinessUnitVirtualAddress.objects.create(
                                        business_unit=business_unit, inherited=True, virtual_address=virtual_address,
                                        inherited_virtual_address=virtual_address, inherited_business_unit=bus_unit)

                                virtual_address.pk = None
                                virtual_address.address_start_date = datetime.now()
                                virtual_address.save()

                                new_address.virtual_address = virtual_address
                                new_address.save()

                    if BusinessUnitSocialLink.objects.filter(business_unit=bus_unit,
                                                             social_link__status='active').exists():
                        business_unit_social_links = \
                            BusinessUnitSocialLink.objects.filter(business_unit=bus_unit,
                                                                  social_link__status='active')
                        for link in business_unit_social_links:
                            if BusinessUnitSocialLink.objects.filter(
                                business_unit=business_unit, inherited=True, inherited_social_link=link.social_link,
                                inherited_social_link__status='active', social_link__status='active',
                                inherited_business_unit=bus_unit
                            ).exists():
                                SocialLink.objects.filter(
                                    businessunitsociallink__business_unit=business_unit,
                                    businessunitsociallink__inherited=True,
                                    businessunitsociallink__inherited_social_link=link.social_link,
                                    businessunitsociallink__inherited_social_link__status='active',
                                    businessunitsociallink__social_link__status='active',
                                    businessunitsociallink__inherited_business_unit=bus_unit). \
                                    update(
                                    type=link.social_link.type,
                                    link=link.social_link.link,
                                    description=link.social_link.description
                                )
                            else:
                                social_link = link.social_link
                                new_link = \
                                    BusinessUnitSocialLink.objects.create(
                                        business_unit=business_unit, inherited=True, social_link=social_link,
                                        inherited_social_link=social_link, inherited_business_unit=bus_unit)

                                social_link.pk = None
                                social_link.link_start_date = datetime.now()
                                social_link.save()

                                new_link.social_link = social_link
                                new_link.save()

                elif "branch".__eq__(belongs_to):
                    if VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_branch=branch),
                                                     businessunitvirtualaddress__business_unit=business_unit,
                                                     businessunitvirtualaddress__inherited=True, status='active'
                                                     ).exists():
                        VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_branch=branch),
                                                      businessunitvirtualaddress__business_unit=business_unit,
                                                      businessunitvirtualaddress__inherited=True, status='active'
                                                      ).update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if BranchVirtualAddress.objects.filter(branch=branch, virtual_address__status='active').exists():
                        branch_virtual_addresses = \
                            BranchVirtualAddress.objects.filter(branch=branch, virtual_address__status='active')
                        for address in branch_virtual_addresses:
                            if BusinessUnitVirtualAddress.objects.filter(
                                business_unit=business_unit, inherited=True, virtual_address__status='active',
                                inherited_virtual_address=address.virtual_address,
                                inherited_virtual_address__status='active', inherited_branch=branch
                            ).exists():
                                VirtualAddress.objects.filter(
                                    businessunitvirtualaddress__business_unit=business_unit,
                                    businessunitvirtualaddress__inherited=True,
                                    businessunitvirtualaddress__inherited_virtual_address=address.virtual_address,
                                    businessunitvirtualaddress__inherited_virtual_address__status='active',
                                    businessunitvirtualaddress__virtual_address__status='active',
                                    businessunitvirtualaddress__inherited_branch=branch
                                ).update(
                                    address_type=address.virtual_address.address_type,
                                    address=address.virtual_address.address,
                                    description=address.virtual_address.description
                                )
                            else:
                                virtual_address = address.virtual_address
                                new_address = \
                                    BusinessUnitVirtualAddress.objects.create(
                                        business_unit=business_unit, inherited=True, virtual_address=virtual_address,
                                        inherited_virtual_address=virtual_address, inherited_branch=branch)

                                virtual_address.pk = None
                                virtual_address.address_start_date = datetime.now()
                                virtual_address.save()

                                new_address.virtual_address = virtual_address
                                new_address.save()

                    if BranchSocialLink.objects.filter(branch=branch, social_link__status='active').exists():
                        branch_social_links = \
                            BranchSocialLink.objects.filter(branch=branch, social_link__status='active')
                        for link in branch_social_links:
                            if BusinessUnitSocialLink.objects.filter(
                                business_unit=business_unit, inherited=True, inherited_social_link=link.social_link,
                                inherited_social_link__status='active', social_link__status='active',
                                inherited_branch=branch
                            ).exists():
                                SocialLink.objects.filter(
                                    businessunitsociallink__business_unit=business_unit,
                                    businessunitsociallink__inherited=True,
                                    businessunitsociallink__inherited_social_link=link.social_link,
                                    businessunitsociallink__inherited_social_link__status='active',
                                    businessunitsociallink__social_link__status='active',
                                    businessunitsociallink__inherited_branch=branch
                                ).update(
                                    type=link.social_link.type,
                                    link=link.social_link.link,
                                    description=link.social_link.description
                                )
                            else:
                                social_link = link.social_link
                                new_link = \
                                    BusinessUnitSocialLink.objects.create(
                                        business_unit=business_unit, inherited=True, social_link=social_link,
                                        inherited_social_link=social_link, inherited_branch=branch)

                                social_link.pk = None
                                social_link.link_start_date = datetime.now()
                                social_link.save()

                                new_link.social_link = social_link
                                new_link.save()

                elif "division".__eq__(belongs_to):
                    if VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_division=division),
                                                     businessunitvirtualaddress__business_unit=business_unit,
                                                     businessunitvirtualaddress__inherited=True, status='active'
                                                     ).exists():
                        VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_division=division),
                                                      businessunitvirtualaddress__business_unit=business_unit,
                                                      businessunitvirtualaddress__inherited=True, status='active'
                                                      ).update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if DivisionVirtualAddress.objects.filter(division=division,
                                                             virtual_address__status='active').exists():
                        division_virtual_addresses = \
                            DivisionVirtualAddress.objects.filter(division=division, virtual_address__status='active')
                        for address in division_virtual_addresses:
                            if BusinessUnitVirtualAddress.objects.filter(
                                business_unit=business_unit, inherited=True, virtual_address__status='active',
                                inherited_virtual_address=address.virtual_address,
                                inherited_virtual_address__status='active', inherited_division=division
                            ).exists():
                                VirtualAddress.objects.filter(
                                    businessunitvirtualaddress__business_unit=business_unit,
                                    businessunitvirtualaddress__inherited=True,
                                    businessunitvirtualaddress__inherited_virtual_address=address.virtual_address,
                                    businessunitvirtualaddress__inherited_virtual_address__status='active',
                                    businessunitvirtualaddress__virtual_address__status='active',
                                    businessunitvirtualaddress__inherited_division=division
                                ).update(
                                    address_type=address.virtual_address.address_type,
                                    address=address.virtual_address.address,
                                    description=address.virtual_address.description
                                )
                            else:
                                virtual_address = address.virtual_address
                                new_address = \
                                    BusinessUnitVirtualAddress.objects.create(
                                        business_unit=business_unit, inherited=True, virtual_address=virtual_address,
                                        inherited_virtual_address=virtual_address, inherited_division=division)

                                virtual_address.pk = None
                                virtual_address.address_start_date = datetime.now()
                                virtual_address.save()

                                new_address.virtual_address = virtual_address
                                new_address.save()

                    if DivisionSocialLink.objects.filter(division=division, social_link__status='active').exists():
                        division_social_links = \
                            DivisionSocialLink.objects.filter(division=division, social_link__status='active')
                        for link in division_social_links:
                            if BusinessUnitSocialLink.objects.filter(
                                business_unit=business_unit, inherited=True, inherited_social_link=link.social_link,
                                inherited_social_link__status='active', social_link__status='active',
                                inherited_division=division
                            ).exists():
                                SocialLink.objects.filter(
                                    businessunitsociallink__business_unit=business_unit,
                                    businessunitsociallink__inherited=True,
                                    businessunitsociallink__inherited_social_link=link.social_link,
                                    businessunitsociallink__inherited_social_link__status='active',
                                    businessunitsociallink__social_link__status='active',
                                    businessunitsociallink__inherited_division=division). \
                                    update(
                                    type=link.social_link.type,
                                    link=link.social_link.link,
                                    description=link.social_link.description
                                )
                            else:
                                social_link = link.social_link
                                new_link = \
                                    BusinessUnitSocialLink.objects.create(
                                        business_unit=business_unit, inherited=True, social_link=social_link,
                                        inherited_social_link=social_link, inherited_division=division)

                                social_link.pk = None
                                social_link.link_start_date = datetime.now()
                                social_link.save()

                                new_link.social_link = social_link
                                new_link.save()

                elif "department".__eq__(belongs_to):
                    if VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_department=department),
                                                     businessunitvirtualaddress__business_unit=business_unit,
                                                     businessunitvirtualaddress__inherited=True, status='active'
                                                     ).exists():
                        VirtualAddress.objects.filter(~Q(businessunitvirtualaddress__inherited_department=department),
                                                      businessunitvirtualaddress__business_unit=business_unit,
                                                      businessunitvirtualaddress__inherited=True, status='active'
                                                      ).update(
                            status='inactive',
                            address_end_date=datetime.now()
                        )

                    if DepartmentVirtualAddress.objects.filter(department=department,
                                                               virtual_address__status='active').exists():
                        department_virtual_addresses = \
                            DepartmentVirtualAddress.objects.filter(department=department,
                                                                    virtual_address__status='active')
                        for address in department_virtual_addresses:
                            if BusinessUnitVirtualAddress.objects.filter(
                                business_unit=business_unit, inherited=True, virtual_address__status='active',
                                inherited_virtual_address=address.virtual_address,
                                inherited_virtual_address__status='active', inherited_department=department
                            ).exists():
                                VirtualAddress.objects.filter(
                                    businessunitvirtualaddress__business_unit=business_unit,
                                    businessunitvirtualaddress__inherited=True,
                                    businessunitvirtualaddress__inherited_virtual_address=address.virtual_address,
                                    businessunitvirtualaddress__inherited_virtual_address__status='active',
                                    businessunitvirtualaddress__virtual_address__status='active',
                                    businessunitvirtualaddress__inherited_department=department
                                ).update(
                                    address_type=address.virtual_address.address_type,
                                    address=address.virtual_address.address,
                                    description=address.virtual_address.description
                                )
                            else:
                                virtual_address = address.virtual_address
                                new_address = \
                                    BusinessUnitVirtualAddress.objects.create(
                                        business_unit=business_unit, inherited=True, virtual_address=virtual_address,
                                        inherited_virtual_address=virtual_address, inherited_department=department)

                                virtual_address.pk = None
                                virtual_address.address_start_date = datetime.now()
                                virtual_address.save()

                                new_address.virtual_address = virtual_address
                                new_address.save()

                    if DepartmentSocialLink.objects.filter(department=department,
                                                           social_link__status='active').exists():
                        department_social_links = \
                            DepartmentSocialLink.objects.filter(department=department, social_link__status='active')
                        for link in department_social_links:
                            if BusinessUnitSocialLink.objects.filter(
                                business_unit=business_unit, inherited=True, inherited_social_link=link.social_link,
                                inherited_social_link__status='active', social_link__status='active',
                                inherited_department=department
                            ).exists():
                                SocialLink.objects.filter(
                                    businessunitsociallink__business_unit=business_unit,
                                    businessunitsociallink__inherited=True,
                                    businessunitsociallink__inherited_social_link=link.social_link,
                                    businessunitsociallink__inherited_social_link__status='active',
                                    businessunitsociallink__social_link__status='active',
                                    businessunitsociallink__inherited_department=department). \
                                    update(
                                    type=link.social_link.type,
                                    link=link.social_link.link,
                                    description=link.social_link.description
                                )
                            else:
                                social_link = link.social_link
                                new_link = \
                                    BusinessUnitSocialLink.objects.create(
                                        business_unit=business_unit, inherited=True, social_link=social_link,
                                        inherited_social_link=social_link, inherited_department=department)

                                social_link.pk = None
                                social_link.link_start_date = datetime.now()
                                social_link.save()

                                new_link.social_link = social_link
                                new_link.save()

            for parent_identification_form in submitted_parent_identification_formset:
                title = parent_identification_form.get_title()
                short_description = parent_identification_form.get_short_description()
                if title and short_description:
                    if parent_identification_form.my_is_valid():
                        # different from parent, but get the title and short description of the parent
                        identification = parent_identification_form.save(commit=False)
                        if Identification.objects.filter(
                            businessunitidentification__business_unit=business_unit, different_from_parent=False,
                            short_description=short_description, title=title, status='active'
                        ).exists():
                            Identification.objects.filter(
                                businessunitidentification__business_unit=business_unit, different_from_parent=False,
                                short_description=short_description, title=title, status='active').update(
                                status='inactive',
                                identification_end_date=datetime.now()
                            )

                        if parent_identification_form.cleaned_data.get('delete'):
                            if parent_identification_form.cleaned_data.get('id'):
                                Identification.objects.filter(
                                    id=parent_identification_form.cleaned_data.get('id').id).update(
                                    status='inactive',
                                    identification_end_date=datetime.now()
                                )
                            else:
                                identification.delete()
                        else:
                            if parent_identification_form.is_valid():
                                if ((parent_identification_form.cleaned_data.get('title')) and
                                        (parent_identification_form.cleaned_data.get('short_description')) and
                                        (parent_identification_form.cleaned_data.get('document_number'))):
                                    current_identification = Identification.objects.filter(
                                        businessunitidentification__business_unit=business_unit, status='active',
                                        different_from_parent=True, short_description=short_description, title=title
                                    )

                                    if current_identification.exists():
                                        current_identification.update(
                                            different_from_parent=True,
                                            document_number=parent_identification_form.cleaned_data.get(
                                                'document_number'),
                                            issue_date=parent_identification_form.cleaned_data.get('issue_date'),
                                            expiry_date=parent_identification_form.cleaned_data.get('expiry_date'),
                                            attachment_title=parent_identification_form.cleaned_data.get(
                                                'attachment_title')
                                        )
                                        if parent_identification_form.cleaned_data.get('attachment_file'):
                                            for id in identification:
                                                id.attachment_file = \
                                                    parent_identification_form.cleaned_data.get('attachment_file')
                                                id.save()

                                    else:
                                        new_identification =\
                                            Identification.objects.create(
                                                different_from_parent=True, new_created=False, title=title,
                                                short_description=short_description,
                                                document_number=parent_identification_form.cleaned_data.get(
                                                    'document_number'),
                                                issue_date=parent_identification_form.cleaned_data.get('issue_date'),
                                                expiry_date=parent_identification_form.cleaned_data.get('expiry_date'),
                                                attachment_title=parent_identification_form.cleaned_data.get(
                                                    'attachment_title'),
                                                identification_start_date=datetime.now()
                                            )
                                        if parent_identification_form.cleaned_data.get('attachment_file'):
                                            new_identification.attachment_file = \
                                                parent_identification_form.cleaned_data.get('attachment_file')
                                            new_identification.save()

                                        BusinessUnitIdentification.objects.create(business_unit=business_unit,
                                                                                  identification=new_identification)

                    else:
                        if parent_identification_form.is_valid():
                            parent_identification_form.save(commit=False)
                            if Identification.objects.filter(businessunitidentification__business_unit=business_unit,
                                                             short_description=short_description, title=title,
                                                             status='active', different_from_parent=True).exists():
                                Identification.objects.filter(businessunitidentification__business_unit=business_unit,
                                                              short_description=short_description, title=title,
                                                              status='active', different_from_parent=True).update(
                                    status='inactive',
                                    identification_end_date=datetime.now()
                                )

                            if "company".__eq__(belongs_to):
                                if Identification.objects.filter(~Q(businessunitidentification__inherited_company=
                                                                    company),
                                                                 businessunitidentification__business_unit=
                                                                 business_unit,
                                                                 businessunitidentification__inherited=True,
                                                                 short_description=short_description, title=title,
                                                                 different_from_parent=True, status='active').exists():
                                    Identification.objects.filter(~Q(businessunitidentification__inherited_company=
                                                                     company),
                                                                  businessunitidentification__business_unit=
                                                                  business_unit,
                                                                  businessunitidentification__inherited=True,
                                                                  short_description=short_description, title=title,
                                                                  different_from_parent=True, status='active').update(
                                        status='inactive',
                                        identification_end_date=datetime.now()
                                    )

                                existing_identification = \
                                    Identification.objects.filter(
                                        businessunitidentification__business_unit=business_unit, title=title,
                                        businessunitidentification__inherited_company=company,
                                        short_description=short_description, status='active')

                                if existing_identification.exists():
                                    for id in existing_identification:
                                        existing_identification.update(
                                            different_from_parent=False,
                                            title=id.title,
                                            short_description=id.short_description,
                                            document_number=id.document_number,
                                            issue_date=id.issue_date,
                                            expiry_date=id.expiry_date,
                                            attachment_title=id.attachment_title,
                                            attachment_file=id.attachment_file
                                        )
                                else:
                                    identification_qs = \
                                        Identification.objects.filter(companyidentification__company=company,
                                                                      title=title, short_description=short_description)
                                    if identification_qs.exists():
                                        for identification in identification_qs:
                                            new_identification = \
                                                BusinessUnitIdentification.objects.create(
                                                    business_unit=business_unit, inherited=True,
                                                    identification=identification,
                                                    inherited_identification=identification,
                                                    inherited_company=company)

                                            identification.pk = None
                                            identification.different_from_parent = False
                                            identification.new_created = False
                                            identification.identification_start_date = datetime.now()
                                            identification.save()

                                            new_identification.identification = identification
                                            new_identification.save()

                            elif "business-unit".__eq__(belongs_to):
                                if Identification.objects.filter(~Q(businessunitidentification__inherited_business_unit=
                                                                    bus_unit),
                                                                 businessunitidentification__business_unit=
                                                                 business_unit,
                                                                 businessunitidentification__inherited=True,
                                                                 different_from_parent=True, status='active').exists():
                                    Identification.objects.filter(~Q(
                                        businessunitidentification__inherited_business_unit=bus_unit),
                                                                  businessunitidentification__business_unit=
                                                                  business_unit,
                                                                  businessunitidentification__inherited=True,
                                                                  different_from_parent=True, status='active').update(
                                        status='inactive',
                                        identification_end_date=datetime.now()
                                    )

                                existing_identification = \
                                    Identification.objects.filter(
                                        businessunitidentification__business_unit=business_unit, title=title,
                                        businessunitidentification__identification=
                                        parent_identification_form.cleaned_data.get('id'),
                                        short_description=short_description, status='active')

                                if existing_identification.exists():
                                    for id in existing_identification:
                                        existing_identification.update(
                                            different_from_parent=False,
                                            title=id.title,
                                            short_description=id.short_description,
                                            document_number=id.document_number,
                                            issue_date=id.issue_date,
                                            expiry_date=id.expiry_date,
                                            attachment_title=id.attachment_title,
                                            attachment_file=id.attachment_file
                                        )
                                else:
                                    identification_qs = \
                                        Identification.objects.filter(
                                            businessunitidentification__business_unit=bus_unit, title=title,
                                            short_description=short_description)

                                    if identification_qs.exists():
                                        for identification in identification_qs:
                                            new_identification = \
                                                BusinessUnitIdentification.objects.create(
                                                    business_unit=business_unit, inherited=True,
                                                    identification=identification,
                                                    inherited_identification=identification,
                                                    inherited_business_unit=bus_unit)

                                            identification.pk = None
                                            identification.different_from_parent = False
                                            identification.new_created = False
                                            identification.identification_start_date = datetime.now()
                                            identification.save()

                                            new_identification.identification = identification
                                            new_identification.save()

                            elif "branch".__eq__(belongs_to):
                                if Identification.objects.filter(~Q(businessunitidentification__inherited_branch=
                                                                    branch),
                                                                 businessunitidentification__business_unit=
                                                                 business_unit,
                                                                 businessunitidentification__inherited=True,
                                                                 different_from_parent=True, status='active').exists():
                                    Identification.objects.filter(~Q(
                                        businessunitidentification__inherited_branch=branch),
                                                                  businessunitidentification__business_unit=
                                                                  business_unit,
                                                                  businessunitidentification__inherited=True,
                                                                  different_from_parent=True, status='active').update(
                                        status='inactive',
                                        identification_end_date=datetime.now()
                                    )

                                existing_identification = \
                                    Identification.objects.filter(
                                        businessunitidentification__business_unit=business_unit, title=title,
                                        businessunitidentification__identification=
                                        parent_identification_form.cleaned_data.get('id'),
                                        short_description=short_description, status='active')

                                if existing_identification.exists():
                                    for id in existing_identification:
                                        existing_identification.update(
                                            different_from_parent=False,
                                            title=id.title,
                                            short_description=id.short_description,
                                            document_number=id.document_number,
                                            issue_date=id.issue_date,
                                            expiry_date=id.expiry_date,
                                            attachment_title=id.attachment_title,
                                            attachment_file=id.attachment_file
                                        )
                                else:
                                    identification_qs = \
                                        Identification.objects.filter(branchidentification__branch=branch, title=title,
                                                                      short_description=short_description)
                                    if identification_qs.exists():
                                        for identification in identification_qs:
                                            new_identification = \
                                                BusinessUnitIdentification.objects.create(
                                                    business_unit=business_unit, inherited=True,
                                                    identification=identification,
                                                    inherited_identification=identification,
                                                    inherited_branch=branch)

                                            identification.pk = None
                                            identification.different_from_parent = False
                                            identification.new_created = False
                                            identification.identification_start_date = datetime.now()
                                            identification.save()

                                            new_identification.identification = identification
                                            new_identification.save()

                            elif "division".__eq__(belongs_to):
                                if Identification.objects.filter(~Q(businessunitidentification__inherited_division=
                                                                    division),
                                                                 businessunitidentification__business_unit=
                                                                 business_unit,
                                                                 businessunitidentification__inherited=True,
                                                                 different_from_parent=True, status='active').exists():
                                    Identification.objects.filter(~Q(businessunitidentification__inherited_division=
                                                                     division),
                                                                  businessunitidentification__business_unit=
                                                                  business_unit,
                                                                  businessunitidentification__inherited=True,
                                                                  different_from_parent=True, status='active').update(
                                        status='inactive',
                                        identification_end_date=datetime.now()
                                    )

                                existing_identification = \
                                    Identification.objects.filter(
                                        businessunitidentification__business_unit=business_unit, title=title,
                                        businessunitidentification__identification=
                                        parent_identification_form.cleaned_data.get('id'),
                                        short_description=short_description, status='active')

                                if existing_identification.exists():
                                    for id in existing_identification:
                                        existing_identification.update(
                                            different_from_parent=False,
                                            title=id.title,
                                            short_description=id.short_description,
                                            document_number=id.document_number,
                                            issue_date=id.issue_date,
                                            expiry_date=id.expiry_date,
                                            attachment_title=id.attachment_title,
                                            attachment_file=id.attachment_file
                                        )
                                else:
                                    identification_qs = \
                                        Identification.objects.filter(divisionidentification__division=division,
                                                                      title=title, short_description=short_description)
                                    if identification_qs.exists():
                                        for identification in identification_qs:
                                            new_identification = \
                                                BusinessUnitIdentification.objects.create(
                                                    business_unit=business_unit, inherited=True,
                                                    identification=identification,
                                                    inherited_identification=identification,
                                                    inherited_division=division)

                                            identification.pk = None
                                            identification.different_from_parent = False
                                            identification.new_created = False
                                            identification.identification_start_date = datetime.now()
                                            identification.save()

                                            new_identification.identification = identification
                                            new_identification.save()

                            elif "department".__eq__(belongs_to):
                                if Identification.objects.filter(~Q(businessunitidentification__inherited_department=
                                                                    department),
                                                                 businessunitidentification__business_unit=
                                                                 business_unit,
                                                                 businessunitidentification__inherited=True,
                                                                 different_from_parent=True, status='active').exists():
                                    Identification.objects.filter(~Q(businessunitidentification__inherited_department=
                                                                     department),
                                                                  businessunitidentification__business_unit=
                                                                  business_unit,
                                                                  businessunitidentification__inherited=True,
                                                                  different_from_parent=True, status='active').update(
                                        status='inactive',
                                        identification_end_date=datetime.now()
                                    )

                                existing_identification = \
                                    Identification.objects.filter(
                                        businessunitidentification__business_unit=business_unit, title=title,
                                        businessunitidentification__identification=
                                        parent_identification_form.cleaned_data.get('id'),
                                        short_description=short_description, status='active')

                                if existing_identification.exists():
                                    for id in existing_identification:
                                        existing_identification.update(
                                            different_from_parent=False,
                                            title=id.title,
                                            short_description=id.short_description,
                                            document_number=id.document_number,
                                            issue_date=id.issue_date,
                                            expiry_date=id.expiry_date,
                                            attachment_title=id.attachment_title,
                                            attachment_file=id.attachment_file
                                        )
                                else:
                                    identification_qs = \
                                        Identification.objects.filter(departmentidentification__department=department,
                                                                      title=title, short_description=short_description)
                                    if identification_qs.exists():
                                        for identification in identification_qs:
                                            new_identification = \
                                                BusinessUnitIdentification.objects.create(
                                                    business_unit=business_unit, inherited=True,
                                                    identification=identification,
                                                    inherited_identification=identification,
                                                    inherited_department=department)

                                            identification.pk = None
                                            identification.different_from_parent = False
                                            identification.new_created = False
                                            identification.identification_start_date = datetime.now()
                                            identification.save()

                                            new_identification.identification = identification
                                            new_identification.save()

            if add_new_identification:
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
                                    BusinessUnitIdentification.objects.create(business_unit=business_unit,
                                                                              identification=identification)

            return redirect(reverse_lazy('beehive_admin:setting:business_unit_list'))

        return render(request, self.template_name, {**context})


class BusinessUnitDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    """Delete the specified business unit."""

    model = BusinessUnit
    permission_required = 'delete_businessunit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def post(self, request, *args, **kwargs):
        """
        overriding delete method
        """

        business_unit_object = self.get_object()
        business_unit = BusinessUnit.objects.get(id=business_unit_object.id)
        business_unit.deleted = True
        business_unit.status = 'inactive'
        business_unit.save()

        business_unit_physical_addresses = \
            PhysicalAddress.objects.filter(businessunitphysicaladdress__business_unit=business_unit, status='active')

        if business_unit_physical_addresses.exists():
            for address in business_unit_physical_addresses:
                address.status = 'inactive'
                address.address_end_date = datetime.now()
                address.save()

        business_unit_virtual_addresses = \
            VirtualAddress.objects.filter(businessunitvirtualaddress__business_unit=business_unit, status='active')

        if business_unit_virtual_addresses.exists():
            for address in business_unit_virtual_addresses:
                address.status = 'inactive'
                address.address_end_date = datetime.now()
                address.save()

        business_unit_social_links = \
            SocialLink.objects.filter(businessunitsociallink__business_unit=business_unit, status='active')

        if business_unit_social_links.exists():
            for link in business_unit_social_links:
                link.status = 'inactive'
                link.address_end_date = datetime.now()
                link.save()

        business_unit_identifications = \
            Identification.objects.filter(businessunitidentification__business_unit=business_unit, status='active')

        if business_unit_identifications.exists():
            for identification in business_unit_identifications:
                identification.status = 'inactive'
                identification.address_end_date = datetime.now()
                identification.save()

        return redirect(reverse_lazy('beehive_admin:setting:business_unit_list'))
