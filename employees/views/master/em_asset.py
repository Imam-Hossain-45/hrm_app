from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import CreateView, DeleteView, ListView
from django.urls import reverse_lazy
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from helpers.functions import get_organizational_structure


class AssetListView(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'employees/master/asset/list.html'
    model = emp_models.Asset
    permission_required = 'view_asset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        asset_list = emp_models.Asset.objects.filter(employee_id=self.kwargs['pk'])

        paginator = Paginator(asset_list, 50)
        page = self.request.GET.get('page')
        context['asset_list'] = paginator.get_page(page)
        index = context['asset_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class AssetCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Add new asset
        Access: Super-Admin, Admin
        Url: /employee/<pk>/asset/create
    """
    form_class = AssetForm
    template_name = 'employees/master/asset/create.html'
    permission_required = ['add_asset', 'change_asset', 'view_asset',
                           'delete_asset']

    def get_queryset(self):
        return emp_models.Asset.objects.filter(employee_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        if 'asset_id' in self.kwargs:
            get_object_or_404(emp_models.Asset, pk=self.kwargs['asset_id'])
        if 'asset_form' not in context:
            if self.get_information():
                context['asset_form'] = self.form_class(instance=self.get_information())
            else:
                context['asset_form'] = self.form_class()
        context['object_list'] = self.get_queryset()
        return context

    def get_information(self):
        if 'asset_id' in self.kwargs:
            data = emp_models.Asset.objects.filter(id=self.kwargs['asset_id']).last()
        else:
            data = emp_models.Asset.objects.filter(employee_id=self.kwargs['pk']).last()
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        if 'asset_form' not in context:
            if self.get_information():
                context['asset_form'] = self.form_class(instance=self.get_information())
            else:
                context['asset_form'] = self.form_class()
        context['pk'] = self.kwargs['pk']
        context['object_list'] = self.get_queryset()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        if 'form1' in request.POST:
            context['asset_form'] = self.form_class(request.POST)
            asset_form = context['asset_form']
            if asset_form.is_valid():
                if 'asset_id' in self.kwargs:
                    updated = emp_models.Asset.objects.filter(id=self.kwargs['asset_id'],
                                                              employee_id=self.kwargs['pk']). \
                        update(asset_category=asset_form.cleaned_data['asset_category'],
                               asset_brand_name=asset_form.cleaned_data['asset_brand_name'],
                               description=asset_form.cleaned_data['description'],
                               serial_number=asset_form.cleaned_data['serial_number'],
                               date_loaned=asset_form.cleaned_data['date_loaned'],
                               date_returned=asset_form.cleaned_data['date_returned'])
                    messages.success(self.request, "Updated asset")
                    return redirect('employees:employee_asset_list', self.kwargs['pk'])
                else:
                    data, created = emp_models.Asset.objects. \
                        get_or_create(employee_id=self.kwargs['pk'],
                                      asset_category=asset_form.cleaned_data['asset_category'],
                                      asset_brand_name=asset_form.cleaned_data['asset_brand_name'],
                                      description=asset_form.cleaned_data['description'],
                                      serial_number=asset_form.cleaned_data['serial_number'],
                                      date_loaned=asset_form.cleaned_data['date_loaned'],
                                      date_returned=asset_form.cleaned_data['date_returned'],
                                      defaults={'asset_category': asset_form.cleaned_data['asset_category'],
                                                'asset_brand_name': asset_form.cleaned_data['asset_brand_name'],
                                                'description': asset_form.cleaned_data['description'],
                                                'serial_number': asset_form.cleaned_data['serial_number'],
                                                'date_loaned': asset_form.cleaned_data['date_loaned'],
                                                'date_returned': asset_form.cleaned_data['date_returned']})

                    if created:
                        messages.success(self.request, "Created asset")
                    else:
                        messages.success(self.request, "Already created.")
                return redirect('employees:employee_asset_create', self.kwargs['pk'])

        return render(request, self.template_name, context)


class AssetDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete a selected asset
        Access: Super-Admin, Admin
    """
    model = emp_models.Asset
    permission_required = 'delete_asset'
    success_message = "Deleted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(AssetDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('employees:employee_asset_create', args=[self.kwargs['employee_pk']])
