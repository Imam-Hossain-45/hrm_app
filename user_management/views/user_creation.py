from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from helpers.mixins import PermissionMixin
from user_management.forms import UserCreationCreateForm, UserCreationUpdateForm, UserCreationPasswordChangeForm
from user_management.models import User, UserGroup
from helpers.functions import get_organizational_structure


class UserCreationListView(LoginRequiredMixin, PermissionMixin, ListView):
    template_name = 'user_management/user_creation/list.html'
    model = User
    context_object_name = 'users'
    permission_required = ['add_user', 'change_user', 'delete_user', 'view_user']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context


class UserCreationCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    template_name = 'user_management/user_creation/create.html'
    form_class = UserCreationCreateForm
    permission_required = 'add_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def form_valid(self, form):
        model = form.save(commit=False)

        if self.request.POST.get('send_credential', False):
            form.send_email(model)

        model.set_password(model.password)
        model.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_management:users_update', kwargs={'pk': self.object.pk})


class UserCreationUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    template_name = 'user_management/user_creation/update.html'
    model = User
    context_object_name = 'user'
    form_class = UserCreationUpdateForm
    success_url = reverse_lazy('user_management:users_list')
    permission_required = 'change_user'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.object})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['password_reset_form'] = UserCreationPasswordChangeForm(self.object)

        return context

    def form_valid(self, form):
        model = form.save()
        data = []

        for company in self.request.POST.getlist('companies'):
            for role in self.request.POST.getlist('role_for_company_' + str(int(company) - 1)):
                data.append({
                    'user_id': model.id,
                    'group_id': role,
                    'company_id': company
                })

        UserGroup.objects.bulk_create([
            UserGroup(**d)
            for d in data
        ])

        return super().form_valid(form)


class ResetPasswordView(LoginRequiredMixin, PermissionMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect(reverse_lazy('user_management:users_update', kwargs={'pk': self.kwargs['pk']}))

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['pk'])
        form = UserCreationPasswordChangeForm(user, request.POST)

        if not form.is_valid():
            return render(request, 'user_management/user_creation/update.html', {
                'form': UserCreationUpdateForm(user=user),
                'update': True,
                'permissions': self.get_current_user_permission_list(),
                'password_reset_form': form,
                'password_reset_error': True
            })

        if request.POST.get('send_to_email', False):
            form.send_email(user)

        form.save()
        messages.success(request, 'Password has been changed successfully')

        return redirect(reverse_lazy('user_management:users_update', kwargs={'pk': self.kwargs['pk']}))


class UserCreationDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    template_name = 'user_management/user_creation/delete.html'
    model = User
    success_url = reverse_lazy('user_management:users_list')
    permission_required = 'delete_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context
