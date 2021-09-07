from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy
from leave.forms import *
from django.shortcuts import render, redirect
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.forms.models import inlineformset_factory
from helpers.functions import get_organizational_structure


class LeaveMasterListView(LoginRequiredMixin, PermissionMixin, ListView):
    permission_required = ['view_leavemaster']
    template_name = 'leave/master/leave_creation/list.html'
    model = LeaveMaster

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['leave_list'] = paginator.get_page(page)
        index = context['leave_list'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class LeaveMasterCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Add new Leave creation
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_creation
    """
    form_class = LeaveMasterForm
    second_form_class = PartialLeaveConverterForm
    template_name = 'leave/master/leave_creation/create.html'
    permission_required = ['add_leavemaster']

    def get_queryset(self):
        return LeaveMaster.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['form'] = self.form_class()
        partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter, form=PartialLeaveConverterForm,
                                               extra=1,
                                               can_delete=True)
        context['partial_leave_converter'] = partialformset(prefix='converterForm')
        return context

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['form'] = self.form_class(self.request.POST)
        if request.POST.get('partial_leave_allowed'):
            partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter, form=PartialLeaveConverterForm,
                                                   extra=1,
                                                   can_delete=True, min_num=1, validate_min=True)
        else:
            partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter, form=PartialLeaveConverterForm,
                                                   extra=1,
                                                   can_delete=True)
        context['partial_leave_converter'] = partialformset(self.request.POST, prefix='converterForm')
        if 'form1' in request.POST:
            form = self.form_class(self.request.POST)
            if request.POST.get('partial_leave_allowed'):
                partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter,
                                                       form=PartialLeaveConverterForm, extra=1,
                                                       can_delete=True, min_num=1, validate_min=True)
                partial_leave_converter = partialformset(self.request.POST, prefix='converterForm')
            else:
                partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter,
                                                       form=PartialLeaveConverterForm, extra=1,
                                                       can_delete=True)
                partial_leave_converter = partialformset(request.POST, prefix='converterForm')
            print(form.errors)
            print(partial_leave_converter.errors)
            if form.is_valid() and partial_leave_converter.is_valid():
                form = form.save(commit=False)
                form.save()
                for converter in partial_leave_converter:
                    if form.partial_leave_allowed is False:
                        converter.cleaned_data = {}
                    if converter.cleaned_data.get('partial_leave_hours') is not None and converter.cleaned_data.get(
                        'partial_leave_day') is not None:
                        convert = converter.save(commit=False)
                        convert.leave = form
                        convert.save()
                messages.success(self.request, "Successfully created.")
                return redirect('beehive_admin:leave:leave_master_list')
        return render(request, self.template_name, context)


class LeaveMasterUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    """
        Edit Leave creation
        Access: Super-Admin, Admin
        Url: /admin/leave/leave_creation
    """
    form_class = LeaveMasterForm
    second_form_class = PartialLeaveConverterForm
    template_name = 'leave/master/leave_creation/update.html'
    permission_required = ['change_leavemaster']

    def get_queryset(self):
        return LeaveMaster.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['form'] = self.form_class(instance=self.get_instance())
        partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter, form=PartialLeaveConverterForm,
                                               extra=1,
                                               can_delete=True)
        context['partial_leave_converter'] = partialformset(instance=self.get_instance(), prefix='converterForm')
        return context

    def get_instance(self):
        if 'pk' in self.kwargs:
            data = LeaveMaster.objects.get(id=self.kwargs['pk'])
            return data

    def post(self, request, *args, **kwargs):
        context = dict()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['object_list'] = self.get_queryset()
        context['form'] = self.form_class(self.request.POST, instance=self.get_instance())
        if request.POST.get('partial_leave_allowed'):
            partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter, form=PartialLeaveConverterForm,
                                                   extra=1,
                                                   can_delete=True, min_num=1, validate_min=True)
        else:
            partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter, form=PartialLeaveConverterForm,
                                                   extra=1,
                                                   can_delete=True)
        context['partial_leave_converter'] = partialformset(self.request.POST, instance=self.get_instance(),
                                                            prefix='converterForm')
        if 'form1' in request.POST:
            form = context['form']
            if request.POST.get('partial_leave_allowed'):
                partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter,
                                                       form=PartialLeaveConverterForm, extra=1,
                                                       can_delete=True, min_num=1, validate_min=True)
                partial_leave_converter = partialformset(self.request.POST, instance=self.get_instance(),
                                                         prefix='converterForm')
            else:
                partialformset = inlineformset_factory(LeaveMaster, PartialLeaveConverter,
                                                       form=PartialLeaveConverterForm, extra=1,
                                                       can_delete=True)
                partial_leave_converter = partialformset(request.POST, instance=self.get_instance(),
                                                         prefix='converterForm')
            if form.is_valid() and partial_leave_converter.is_valid():
                form = form.save(commit=False)
                form.save()
                for converter in partial_leave_converter:
                    if form.partial_leave_allowed is False:
                        converter.cleaned_data = {}
                        PartialLeaveConverter.objects.filter(leave=self.get_instance()).delete()
                    forms = partial_leave_converter.save(commit=False)
                    for obj in partial_leave_converter.deleted_objects:
                        obj.delete()
                    if converter.cleaned_data.get('partial_leave_hours') is not None and converter.cleaned_data.get(
                        'partial_leave_day') is not None:
                        convert = converter.save(commit=False)
                        convert.leave = form
                        convert.save()
                messages.success(self.request, "Successfully updated.")
                return redirect('beehive_admin:leave:leave_master_list')
        return render(request, self.template_name, context)


class LeaveDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    """
        Delete a selected leave
        Access: Super-Admin, Admin
    """
    model = LeaveMaster
    permission_required = 'delete_leavemaster'
    success_message = "Deleted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(LeaveDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('beehive_admin:leave:leave_master_list')
