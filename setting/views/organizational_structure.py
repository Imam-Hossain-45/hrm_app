from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from helpers.mixins import PermissionMixin
from setting.models import OrganizationalStructure, ITEM_CHOICES
from django.shortcuts import redirect
from helpers.functions import get_organizational_structure


class OrganizationalStructureList(LoginRequiredMixin, PermissionMixin, ListView):
    permission_required = [
        'view_organizationalstructure',
        'add_organizationalstructure',
        'update_organizationalstructure',
        'delete_organizationalstructure'
    ]
    template_name = 'setting/organizational-structure/list.html'
    model = OrganizationalStructure

    def get_unused_options(self, existing_qs):
        items = ITEM_CHOICES
        return_items = list(ITEM_CHOICES)
        for item in items:
            counter = 0
            for existing_item in existing_qs:
                if item[0] == existing_item.item:
                    break
                counter += 1
            if counter != len(existing_qs):
                return_items.remove(item)
        if ('company', 'Company') in return_items:
            return_items.remove(('company', 'Company'))
        return return_items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        org_structure_qs = OrganizationalStructure.objects.all().order_by('order')
        context['orgs'] = org_structure_qs
        context['unused_items'] = self.get_unused_options(existing_qs=org_structure_qs)
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST['org-structure']
        if data == '':
            data = 'company'
        data_list = data.split(",")

        if '' in data_list:
            data_list.remove('')

        existing_structure_qs = OrganizationalStructure.objects.all()
        to_delete_items_list = []
        for obj_item in existing_structure_qs:
            if obj_item.item not in data_list:
                to_delete_items_list.append(obj_item.item)
        print(to_delete_items_list)
        for item in to_delete_items_list:
            try:
                OrganizationalStructure.objects.get(item=item).delete()
            except:
                pass

        i = 0
        parent = None
        while i < len(data_list):
            if i == 0:
                try:
                    parent, created = OrganizationalStructure.objects.update_or_create(
                        item=data_list[i], defaults={'parent_item': None, 'order': i+1}
                    )
                except:
                    break
            else:
                try:
                    parent, created = OrganizationalStructure.objects.update_or_create(
                        item=data_list[i], defaults={'parent_item': parent, 'order': i+1}
                    )
                except:
                    break
            i += 1

        return redirect(request.META['HTTP_REFERER'])


class OrganizationalStructureCreate(LoginRequiredMixin, PermissionMixin, CreateView):
    permission_required = 'add_organizationalstructure'
    template_name = 'setting/organizational-structure/create.html'
    model = OrganizationalStructure
    fields = '__all__'
    success_url = reverse_lazy('beehive_admin:setting:organizational_structure_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class OrganizationalStructureUpdate(LoginRequiredMixin, PermissionMixin, UpdateView):
    permission_required = 'update_organizationalstructure'
    template_name = 'setting/organizational-structure/update.html'
    model = OrganizationalStructure
    fields = '__all__'
    context_object_name = 'orgs'
    success_url = reverse_lazy('beehive_admin:setting:organizational_structure_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class OrganizationalStructureDelete(LoginRequiredMixin, PermissionMixin, DeleteView):
    permission_required = 'update_organizationalstructure'
    template_name = 'setting/organizational-structure/delete.html'
    model = OrganizationalStructure
    fields = '__all__'
    success_url = reverse_lazy('beehive_admin:setting:organizational_structure_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context
