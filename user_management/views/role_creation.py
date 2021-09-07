from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.apps import apps
from helpers.mixins import PermissionMixin
from helpers.functions import get_organizational_structure


def tabular_permission():
    permissions = Permission.objects.all()
    permission_list = []
    label_done = ''
    model_done = ''

    for permission in permissions:
        if permission.content_type.app_label != label_done:
            app_label = permission.content_type.app_label
            app_label_verbose = apps.get_app_config(permission.content_type.app_label).verbose_name
            app_permission = []

            for permission2 in permissions:
                if permission.content_type.app_label == permission2.content_type.app_label:
                    model_permissions = []

                    if permission2.content_type.model != model_done:
                        model_done = permission2.content_type.model
                        model = ''
                        model_verbose = ''

                        for permission3 in permissions:
                            if permission3.content_type.model == permission2.content_type.model:
                                model = permission3.content_type.model

                                try:
                                    model_verbose = permission3.content_type.model_class()._meta.verbose_name.capitalize()
                                except:
                                    pass

                                model_permissions.append({
                                    'permission_name': permission3.name,
                                    'permission_id': permission3.id,
                                    'permission_code': permission3.codename
                                })

                        app_permission.append({
                            'name': model,
                            'name_verbose': model_verbose,
                            'permissions': model_permissions
                        })

            permission_list.append({
                'app_label': app_label,
                'app_label_verbose': app_label_verbose,
                'models': app_permission
            })

            label_done = permission.content_type.app_label

    return permission_list


class RoleCreationListView(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'user_management/role_creation/list.html'
    model = Group
    context_object_name = 'groups'
    permission_required = ['add_group', 'change_group', 'delete_group', 'view_group']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class RoleCreationCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    template_name = 'user_management/role_creation/create.html'
    model = Group
    fields = '__all__'
    success_url = reverse_lazy('user_management:roles_list')
    permission_required = 'add_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['permission_list'] = tabular_permission()
        context['org_items_list'] = get_organizational_structure()
        return context


class RoleCreationUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    template_name = 'user_management/role_creation/update.html'
    model = Group
    fields = '__all__'
    success_url = reverse_lazy('user_management:roles_list')
    permission_required = 'change_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permission_list'] = tabular_permission()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        role_permission_list = []
        permissions_codename = []
        app_label_list = []
        for permission in self.object.permissions.all():
            permissions_codename.append(permission.codename)
            role_permission_list.append(permission.id)
            if permission.content_type.app_label not in app_label_list:
                app_label_list.append(permission.content_type.app_label)

        context['role_permission_list'] = role_permission_list

        model_name_list = []
        for codename in permissions_codename:
            split_codename = codename.split('_')
            model_name = split_codename[1]
            if model_name not in model_name_list:
                model_name_list.append(model_name)

        # add, change, view, delete content type
        selected_model = []
        for model in model_name_list:
            if 'add_' + model in permissions_codename and 'change_' + model in permissions_codename and \
                    'view_' + model in permissions_codename and 'delete_' + model in permissions_codename:
                selected_model.append(model)
        context['selected_model'] = selected_model

        # all add content type selected
        create_app_list = []
        update_app_list = []
        view_app_list = []
        delete_app_list = []
        for app_label in app_label_list:
            create = True
            update = True
            delete = True
            view = True
            all_app_label = Permission.objects.filter(content_type__app_label=app_label)
            for content in all_app_label:
                if content.codename.startswith('add_'):
                    if content.id not in role_permission_list:
                        create = False
                        continue

                elif content.codename.startswith('change_'):
                    if content.id not in role_permission_list:
                        update = False
                        continue

                elif content.codename.startswith('delete_'):
                    if content.id not in role_permission_list:
                        delete = False
                        continue

                elif content.codename.startswith('view_'):
                    if content.id not in role_permission_list:
                        view = False
                        continue
            if create:
                create_app_list.append(app_label)

            if update:
                update_app_list.append(app_label)

            if view:
                view_app_list.append(app_label)

            if delete:
                delete_app_list.append(app_label)

        context['create_app_list'] = create_app_list
        context['update_app_list'] = update_app_list
        context['view_app_list'] = view_app_list
        context['delete_app_list'] = delete_app_list

        return context


class RoleCreationDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    template_name = 'user_management/role_creation/delete.html'
    model = Group
    success_url = reverse_lazy('user_management:roles_list')
    permission_required = 'delete_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context
