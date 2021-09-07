from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from helpers.mixins import PermissionMixin
from django.contrib import messages
from payroll.models import BonusComponent
from payroll.forms import BonusComponentSettingsUpdateForm
from django.shortcuts import render, redirect, Http404
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from cimbolic.models import Formula, Variable
from helpers.functions import get_organizational_structure


class BonusComponentSettingsUpdate(LoginRequiredMixin, PermissionMixin, FormView):
    """
        Update the Settings of a Bonus Component
    """

    form_class = BonusComponentSettingsUpdateForm
    template_name = "payroll/master/bonus_component/settings/update.html"
    permission_required = 'change_bonuscomponent'

    rule_based_formset_class = inlineformset_factory(
        Variable,
        Formula,
        fields=['variable', 'priority', 'condition', 'rule'],
        extra=0,
        min_num=1,
    )

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['form'] = self.form_class()
        bonus_component = BonusComponent.objects.get(id=self.kwargs.get('pk', ''))
        context['bonus_component'] = bonus_component
        context['rbforms'] = self.rule_based_formset_class(
            instance=bonus_component.variable,
        )
        context['selected_item'] = bonus_component.rule_type
        context['bonus_period'] = bonus_component.bonus_period
        context['bonus_frequency'] = bonus_component.bonus_frequency
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        form = BonusComponentSettingsUpdateForm(request.POST)
        context['form'] = form
        selected_item = request.POST.get('options')
        context['selected_item'] = selected_item
        bonus_period = request.POST.get('bonus_period')
        context['bonus_period'] = bonus_period
        bonus_frequency = request.POST.get('bonus_frequency')
        context['bonus_frequency'] = bonus_frequency

        bonus_component = BonusComponent.objects.get(id=self.kwargs.get('pk', ''))

        if selected_item == 'rule-based':
            rbformset = self.rule_based_formset_class(
                request.POST,
                instance=bonus_component.variable,
            )
            if rbformset.is_valid():
                rbformset.save()
                context['rbforms'] = rbformset
            else:
                messages.error(request, 'Invalid rule form')
                context['rbforms'] = rbformset
                return render(request, self.template_name, context)
        else:
            context['rbforms'] = self.rule_based_formset_class(
                instance=bonus_component.variable,
            )

        if not form.is_valid():
            return render(request, self.template_name, context)

        bonus_component.rule_type = selected_item
        bonus_component.bonus_period = bonus_period
        if bonus_frequency:
            bonus_component.bonus_frequency = int(bonus_frequency)
        else:
            bonus_component.bonus_frequency = None
        bonus_component.save()

        update_message = "Updated "+str(bonus_component)+" settings"
        messages.success(self.request, update_message)
        return redirect(reverse_lazy('beehive_admin:payroll:bonus_component_update', kwargs={'pk': bonus_component.id}))
