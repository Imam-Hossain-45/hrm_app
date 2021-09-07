from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render
from helpers.mixins import PermissionMixin
from attendance.forms import *
from django.forms.models import inlineformset_factory
from datetime import datetime
from helpers.functions import get_organizational_structure
from django.contrib import messages


class ScheduleMasterListView(LoginRequiredMixin, PermissionMixin, ListView):
    permission_required = ['add_schedulemaster', 'change_schedulemaster', 'delete_schedulemaster',
                           'view_schedulemaster']
    template_name = 'attendance/master/schedule/list.html'
    model = ScheduleMaster

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        paginator = Paginator(self.object_list, 50)
        page = self.request.GET.get('page')
        context['schedules'] = paginator.get_page(page)
        index = context['schedules'].number - 1
        max_index = len(paginator.page_range)
        start_index = index - 0 if index >= 3 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        context['page_range'] = list(paginator.page_range)[start_index:end_index]

        return context


class ScheduleMasterCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    permission_required = 'add_schedulemaster'
    template_name = 'attendance/master/schedule/create.html'
    form_class = ScheduleMasterForm
    timetable_form = ScheduleMasterTimeTableForm
    fixedformset = inlineformset_factory(TimeTable, BreakTime, form=ScheduleMasterBreakTimeForm, extra=1,
                                         can_delete=True)
    hourlyformset = inlineformset_factory(TimeTable, TimeDuration, form=ScheduleMasterTimeDurationForm, extra=1,
                                          can_delete=True)
    flexible_form = ScheduleMasterFlexibleTypeForm
    success_url = reverse_lazy('beehive_admin:attendance:master_schedule_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['timetable_form'] = self.timetable_form
        context['fixed_formset'] = self.fixedformset(prefix='fixedForm')
        context['hourly_formset'] = self.hourlyformset(prefix='hourlyForm')
        context['flexible_form'] = self.flexible_form
        for days in range(1, 8):
            context[str(days) + '_freelancing_formset'] = self.fixedformset(prefix=days)

        return context

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """

        parent_id = self.request.GET.get('parent_id')

        def get_instance():
            return TimeTable.objects.filter(schedule_master_id=parent_id).last()

        def get_flexible_instance():
            myFlex = []
            for data in FlexibleType.objects.filter(schedule_master_id=parent_id):
                flex = {
                    'day': data.days.id,
                    'hour': data.working_hour,
                    'unit': data.working_hour_unit,
                }
                myFlex.append(flex)
            return myFlex

        def get_freelancing_instance():
            freelancing = []
            for data in TimeTable.objects.filter(schedule_master_id=parent_id):
                freelance = {
                    'day': data.days.id,
                    'in_time': data.in_time,
                    'out_time': data.out_time,
                }
                freelancing.append(freelance)
            return freelancing

        if self.request.is_ajax():
            if parent_id not in EMPTY_VALUES:
                context['form'] = self.form_class(instance=ScheduleMaster.objects.filter(id=parent_id).first())
                context['permissions'] = self.get_current_user_permission_list()
                context['org_items_list'] = get_organizational_structure()
                context['timetable_form'] = ScheduleMasterTimeTableForm(instance=get_instance())
                context['day'] = TimeTable.objects.filter(schedule_master_id=parent_id).values_list('days', flat=True)
                context['fixed_formset'] = self.fixedformset(instance=get_instance(), prefix='fixedForm')
                hourlyformset = inlineformset_factory(TimeTable, TimeDuration, form=ScheduleMasterTimeDurationForm,
                                                      extra=1,
                                                      can_delete=True)
                context['hourly_formset'] = hourlyformset(instance=get_instance(), prefix='hourlyForm')
                context['flexible_instance'] = get_flexible_instance()
                context['freelancing_instance'] = get_freelancing_instance()
                context['flexible_form'] = self.flexible_form()
                for days in range(1, 8):
                    ins = TimeTable.objects.filter(schedule_master_id=parent_id)
                    context[str(days) + '_freelancing_formset'] = self.fixedformset(
                        instance=ins.filter(days=days).last(),
                        prefix=days)
                return render(self.request, 'attendance/master/schedule/parent_form.html', context)
        else:
            return super(CreateView, self).render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        context = dict()
        form = self.form_class(self.request.POST or None)
        context['form'] = form
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['timetable_form'] = self.timetable_form
        context['fixed_formset'] = self.fixedformset(prefix='fixedForm')
        context['hourly_formset'] = self.hourlyformset(prefix='hourlyForm')
        context['flexible_form'] = self.flexible_form
        post_dict = self.request.POST.copy()

        for days in range(1, 8):
            context[str(days) + '_freelancing_formset'] = self.fixedformset(prefix=days)

        def convert_time(t):
            parts = t.split(':')
            if len(parts[0]) == 1:
                parts[0] = '0{}'.format(parts[0])
                return ':'.join(parts)
            else:
                return t

        if self.request.POST.get('schedule_type') in ['regular-fixed-time', 'fixed-day', 'weekly', 'day']:
            # Timetable form validation
            if self.request.POST.get('in_time').strip() not in ['', None]:
                post_dict['in_time'] = datetime.strptime(convert_time(self.request.POST['in_time']), '%I:%M %p')
                post_dict['in_time'] = post_dict['in_time'].strftime('%H:%M')
            if self.request.POST.get('out_time').strip() not in ['', None]:
                post_dict['out_time'] = datetime.strptime(convert_time(self.request.POST['out_time']), '%I:%M %p')
                post_dict['out_time'] = post_dict['out_time'].strftime('%H:%M')
            timetable_form = self.timetable_form(post_dict)
            context['timetable_form'] = timetable_form

            timetable_form.fields['in_time'].required = True
            timetable_form.fields['out_time'].required = True

            # fixed formset validation
            data = {
                'fixedForm-TOTAL_FORMS': self.request.POST['fixedForm-TOTAL_FORMS'],
                'fixedForm-INITIAL_FORMS': self.request.POST['fixedForm-INITIAL_FORMS'],
                'fixedForm-MIN_NUM_FORMS': self.request.POST['fixedForm-MIN_NUM_FORMS'],
            }

            for i in range(int(data['fixedForm-TOTAL_FORMS'])):
                if self.request.POST.get('fixedForm-' + str(i) + '-break_start') not in ['', None]:
                    break_start = datetime.strptime(
                        convert_time(self.request.POST['fixedForm-' + str(i) + '-break_start']), '%I:%M %p')
                    data['fixedForm-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                if self.request.POST.get('fixedForm-' + str(i) + '-break_end') not in ['', None]:
                    break_end = datetime.strptime(convert_time(self.request.POST['fixedForm-' + str(i) + '-break_end']),
                                                  '%I:%M %p')
                    data['fixedForm-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                if self.request.POST.get('fixedForm-' + str(i) + '-DELETE'):
                    data['fixedForm-' + str(i) + '-DELETE'] = self.request.POST['fixedForm-' + str(i) + '-DELETE']
                else:
                    data['fixedForm-' + str(i) + '-DELETE'] = ''

            fixed_formset = self.fixedformset(data, prefix='fixedForm')
            context['fixed_formset'] = fixed_formset
            context['day'] = [int(i) for i in self.request.POST.getlist('days')]

            if not timetable_form.is_valid():
                return render(self.request, self.template_name, context)

            if not fixed_formset.is_valid():
                return render(self.request, self.template_name, context)

            obj = form.save()
            for day in self.request.POST.getlist('days'):
                timetable = TimeTable.objects.create(
                    schedule_master=obj,
                    days_id=day,
                    in_time=timetable_form.cleaned_data.get('in_time'),
                    out_time=timetable_form.cleaned_data.get('out_time')
                )
                for fixed in fixed_formset:
                    if fixed.cleaned_data.get('break_start') is not None:
                        BreakTime.objects.create(
                            timetable=timetable,
                            break_start=fixed.cleaned_data.get('break_start'),
                            break_end=fixed.cleaned_data.get('break_end')
                        )
        else:
            timetable_form = self.timetable_form(post_dict)
            context['timetable_form'] = timetable_form

            if self.request.POST.get('schedule_type') in ['hourly']:

                # hourly formset validation
                data = {
                    'hourlyForm-TOTAL_FORMS': self.request.POST['hourlyForm-TOTAL_FORMS'],
                    'hourlyForm-INITIAL_FORMS': self.request.POST['hourlyForm-INITIAL_FORMS'],
                    'hourlyForm-MIN_NUM_FORMS': self.request.POST['hourlyForm-MIN_NUM_FORMS'],
                }

                for i in range(int(data['hourlyForm-TOTAL_FORMS'])):
                    if self.request.POST.get('hourlyForm-' + str(i) + '-work_start') not in ['', None]:
                        work_start = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-work_start']), '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-work_start'] = work_start.strftime('%H:%M')
                    if self.request.POST.get('hourlyForm-' + str(i) + '-work_end') not in ['', None]:
                        work_end = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-work_end']),
                            '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-work_end'] = work_end.strftime('%H:%M')
                    if self.request.POST.get('hourlyForm-' + str(i) + '-break_start') not in ['', None]:
                        break_start = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-break_start']), '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                    if self.request.POST.get('hourlyForm-' + str(i) + '-break_end') not in ['', None]:
                        break_end = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-break_end']),
                            '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                    if self.request.POST.get('hourlyForm-' + str(i) + '-DELETE'):
                        data['hourlyForm-' + str(i) + '-DELETE'] = self.request.POST['hourlyForm-' + str(i) + '-DELETE']
                    else:
                        data['hourlyForm-' + str(i) + '-DELETE'] = ''

                hourly_formset = self.hourlyformset(data, prefix='hourlyForm')
                context['hourly_formset'] = hourly_formset
                context['day'] = [int(i) for i in self.request.POST.getlist('days')]

                if not timetable_form.is_valid():
                    return render(self.request, self.template_name, context)

                if not hourly_formset.is_valid():
                    return render(self.request, self.template_name, context)

                obj = form.save()
                for day in self.request.POST.getlist('days'):
                    timetable = TimeTable.objects.create(
                        schedule_master=obj,
                        days_id=day
                    )
                    for hourly in hourly_formset:
                        if hourly.cleaned_data.get('break_start') is not None:
                            TimeDuration.objects.create(
                                timetable=timetable,
                                work_start=hourly.cleaned_data.get('work_start'),
                                work_end=hourly.cleaned_data.get('work_end'),
                                break_start=hourly.cleaned_data.get('break_start'),
                                break_end=hourly.cleaned_data.get('break_end')
                            )
            elif (self.request.POST.get('schedule_type') in ['freelancing']) or (
                self.request.POST.get('schedule_type') in ['roster'] and
                    self.request.POST.get('roster_type') == 'fixed-roster'):

                # for old value stay in form when form is error
                in_time_error = False
                for days in range(1, 8):
                    # freelancing formset validation
                    data = {
                        str(days) + '-TOTAL_FORMS': self.request.POST[str(days) + '-TOTAL_FORMS'],
                        str(days) + '-INITIAL_FORMS': self.request.POST[str(days) + '-INITIAL_FORMS'],
                        str(days) + '-MIN_NUM_FORMS': self.request.POST[str(days) + '-MIN_NUM_FORMS'],
                    }

                    for i in range(int(data[str(days) + '-TOTAL_FORMS'])):
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_start') not in ['', None]:
                            break_start = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_start']), '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_end') not in ['', None]:
                            break_end = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_end']),
                                '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                        if self.request.POST.get(str(days) + '-' + str(i) + '-DELETE'):
                            data[str(days) + '-' + str(i) + '-DELETE'] = self.request.POST[
                                str(days) + '-' + str(i) + '-DELETE']
                        else:
                            data[str(days) + '-' + str(i) + '-DELETE'] = ''
                    context[str(days) + '_freelancing_formset'] = self.fixedformset(data, prefix=days)

                context['freelancing_instance'] = [
                    {'day': int(i),
                     'in_time': datetime.strptime(str(self.request.POST.getlist('in_time')[int(i) - 1]), '%I:%M %p')
                     if (self.request.POST.getlist('in_time')[int(i) - 1]).strip() else '',
                     'out_time': datetime.strptime(str(self.request.POST.getlist('out_time')[int(i) - 1]), '%I:%M %p')
                     if (self.request.POST.getlist('out_time')[int(i) - 1]).strip() else ''
                     }
                    for i in self.request.POST.getlist('days')
                ]
                day = []

                for i in self.request.POST.getlist('days'):
                    day.append(int(i))
                    if (self.request.POST.getlist('in_time')[int(i) - 1]).strip() in EMPTY_VALUES:
                        in_time_error = True
                    if (self.request.POST.getlist('out_time')[int(i) - 1]).strip() in EMPTY_VALUES:
                        in_time_error = True
                context['day'] = day

                if timetable_form.is_valid() is False or in_time_error is True:
                    return render(self.request, self.template_name, context)

                for days in self.request.POST.getlist('days'):
                    # freelancing formset validation
                    data = {
                        str(days) + '-TOTAL_FORMS': self.request.POST[str(days) + '-TOTAL_FORMS'],
                        str(days) + '-INITIAL_FORMS': self.request.POST[str(days) + '-INITIAL_FORMS'],
                        str(days) + '-MIN_NUM_FORMS': self.request.POST[str(days) + '-MIN_NUM_FORMS'],
                    }

                    for i in range(int(data[str(days) + '-TOTAL_FORMS'])):
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_start') not in ['', None]:
                            break_start = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_start']), '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_end') not in ['', None]:
                            break_end = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_end']),
                                '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                        if self.request.POST.get(str(days) + '-' + str(i) + '-DELETE'):
                            data[str(days) + '-' + str(i) + '-DELETE'] = self.request.POST[
                                str(days) + '-' + str(i) + '-DELETE']
                        else:
                            data[str(days) + '-' + str(i) + '-DELETE'] = ''
                    fixed_formset = self.fixedformset(data, prefix=days)
                    context[str(days) + '_freelancing_formset'] = fixed_formset

                    if not fixed_formset.is_valid():
                        return render(self.request, self.template_name, context)

                obj = form.save()
                for day in self.request.POST.getlist('days'):
                    timetable = TimeTable.objects.create(
                        schedule_master=obj, days_id=day,
                        in_time=self.request.POST.getlist('in_time')[int(day) - 1],
                        out_time=self.request.POST.getlist('out_time')[int(day) - 1]
                    )
                    for form_data in context[str(day) + '_freelancing_formset']:
                        if form_data.cleaned_data.get('break_start') is not None:
                            BreakTime.objects.create(
                                timetable=timetable,
                                break_start=form_data.cleaned_data.get('break_start'),
                                break_end=form_data.cleaned_data.get('break_end')
                            )
            else:
                if self.request.POST.get('schedule_type') in ['flexible']:
                    flexible_form = self.flexible_form(self.request.POST, prefix='flexible')
                    context['flexible_form'] = flexible_form
                    # for old value stay in form when form is error
                    context['flexible_instance'] = [
                        {'day': int(i),
                         'hour': int(self.request.POST.getlist('working_hour')[int(i) - 1])
                         if (self.request.POST.getlist('working_hour')[int(i) - 1]).strip() else '',
                         'unit': self.request.POST.getlist('working_hour_unit')[int(i) - 1]
                         if (self.request.POST.getlist('working_hour_unit')[int(i) - 1]).strip() else '',
                         }
                        for i in self.request.POST.getlist('days')
                    ]
                    day = []
                    working_hour_error = False
                    for i in self.request.POST.getlist('days'):
                        day.append(int(i))
                        if (self.request.POST.getlist('working_hour')[int(i) - 1]).strip() in EMPTY_VALUES:
                            working_hour_error = True
                        if (self.request.POST.getlist('working_hour_unit')[int(i) - 1]).strip() in EMPTY_VALUES:
                            working_hour_error = True
                    context['day'] = day
                    if day not in EMPTY_VALUES:
                        flexible_form.fields['days'].required = False

                    if flexible_form.is_valid() is False or working_hour_error is True:
                        return render(self.request, self.template_name, context)

                    obj = form.save()
                    FlexibleType.objects.bulk_create([
                        FlexibleType(
                            schedule_master=obj,
                            days_id=day,
                            working_hour=self.request.POST.getlist('working_hour')[int(day) - 1],
                            working_hour_unit=self.request.POST.getlist('working_hour_unit')[int(day) - 1]
                        )
                        for day in self.request.POST.getlist('days')
                    ])
                elif self.request.POST.get('schedule_type') in ['roster'] and \
                        self.request.POST.get('roster_type') == 'variable-roster':

                    context['day'] = [int(i) for i in self.request.POST.getlist('days')]
                    timetable_form.fields['days'].required = False

                    if not timetable_form.is_valid():
                        return render(self.request, self.template_name, context)

                    obj = form.save()
                    TimeTable.objects.bulk_create([
                        TimeTable(
                            schedule_master=obj,
                            days_id=day,
                        )
                        for day in self.request.POST.getlist('days')
                    ])

        return super().form_valid(form)

    def form_invalid(self, form):
        # for old value stay in form when form is error
        freelancing_instance = []
        flexible_instance = []
        timetable_form = self.timetable_form
        fixed_formset = self.fixedformset(prefix='fixedForm')
        flexible_form = self.flexible_form

        def convert_time(t):
            parts = t.split(':')
            if len(parts[0]) == 1:
                parts[0] = '0{}'.format(parts[0])
                return ':'.join(parts)
            else:
                return t

        post_dict = self.request.POST.copy()
        if self.request.POST.get('schedule_type') in ['regular-fixed-time', 'fixed-day', 'weekly', 'day']:
            # Timetable form validation
            if self.request.POST.get('in_time').strip() not in ['', None]:
                post_dict['in_time'] = datetime.strptime(convert_time(self.request.POST['in_time']), '%I:%M %p')
                post_dict['in_time'] = post_dict['in_time'].strftime('%H:%M')
            if self.request.POST.get('out_time').strip() not in ['', None]:
                post_dict['out_time'] = datetime.strptime(convert_time(self.request.POST['out_time']), '%I:%M %p')
                post_dict['out_time'] = post_dict['out_time'].strftime('%H:%M')
            timetable_form = self.timetable_form(post_dict)

            timetable_form.fields['in_time'].required = True
            timetable_form.fields['out_time'].required = True

            # fixed formset validation
            data = {
                'fixedForm-TOTAL_FORMS': self.request.POST['fixedForm-TOTAL_FORMS'],
                'fixedForm-INITIAL_FORMS': self.request.POST['fixedForm-INITIAL_FORMS'],
                'fixedForm-MIN_NUM_FORMS': self.request.POST['fixedForm-MIN_NUM_FORMS'],
            }
            for i in range(int(data['fixedForm-TOTAL_FORMS'])):
                if self.request.POST.get('fixedForm-' + str(i) + '-break_start') not in ['', None]:
                    break_start = datetime.strptime(
                        convert_time(self.request.POST['fixedForm-' + str(i) + '-break_start']), '%I:%M %p')
                    data['fixedForm-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                if self.request.POST.get('fixedForm-' + str(i) + '-break_end') not in ['', None]:
                    break_end = datetime.strptime(convert_time(self.request.POST['fixedForm-' + str(i) + '-break_end']),
                                                  '%I:%M %p')
                    data['fixedForm-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                if self.request.POST.get('fixedForm-' + str(i) + '-DELETE'):
                    data['fixedForm-' + str(i) + '-DELETE'] = self.request.POST['fixedForm-' + str(i) + '-DELETE']
                else:
                    data['fixedForm-' + str(i) + '-DELETE'] = ''

            fixed_formset = self.fixedformset(data, prefix='fixedForm')

        elif (self.request.POST.get('schedule_type') in ['freelancing']) or (
            self.request.POST.get('schedule_type') in ['roster'] and
                self.request.POST.get('roster_type') == 'fixed-roster'):
            freelancing_instance = [
                {'day': int(i),
                 'in_time': datetime.strptime(str(self.request.POST.getlist('in_time')[int(i) - 1]), '%I:%M %p')
                 if (self.request.POST.getlist('in_time')[int(i) - 1]).strip() else '',
                 'out_time': datetime.strptime(str(self.request.POST.getlist('out_time')[int(i) - 1]), '%I:%M %p')
                 if (self.request.POST.getlist('out_time')[int(i) - 1]).strip() else ''
                 }
                for i in self.request.POST.getlist('days')
            ]

        elif self.request.POST.get('schedule_type') in ['flexible']:
            flexible_form = self.flexible_form(self.request.POST, prefix='flexible')
            # for old value stay in form when form is error
            flexible_instance = [
                {'day': int(i),
                 'hour': int(self.request.POST.getlist('working_hour')[int(i) - 1])
                 if (self.request.POST.getlist('working_hour')[int(i) - 1]).strip() else '',
                 'unit': self.request.POST.getlist('working_hour_unit')[int(i) - 1]
                 if (self.request.POST.getlist('working_hour_unit')[int(i) - 1]).strip() else '',
                 }
                for i in self.request.POST.getlist('days')
            ]

        day = []
        for i in self.request.POST.getlist('days'):
            day.append(int(i))

        if self.request.POST.get('schedule_type') in ['flexible'] and day not in EMPTY_VALUES:
            flexible_form.fields['days'].required = False

        context = dict()
        context['form'] = self.form_class(self.request.POST or None)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['timetable_form'] = timetable_form
        context['fixed_formset'] = fixed_formset
        context['hourly_formset'] = self.hourlyformset(prefix='hourlyForm')
        context['flexible_form'] = flexible_form
        context['freelancing_instance'] = freelancing_instance
        context['flexible_instance'] = flexible_instance
        context['day'] = day

        for days in range(1, 8):
            context[str(days) + '_freelancing_formset'] = self.fixedformset(prefix=days)

        if (self.request.POST.get('schedule_type') in ['freelancing']) or (
            self.request.POST.get('schedule_type') in ['roster'] and
                self.request.POST.get('roster_type') == 'fixed-roster'):

            for days in range(1, 8):
                # freelancing formset validation
                data = {
                    str(days) + '-TOTAL_FORMS': self.request.POST[str(days) + '-TOTAL_FORMS'],
                    str(days) + '-INITIAL_FORMS': self.request.POST[str(days) + '-INITIAL_FORMS'],
                    str(days) + '-MIN_NUM_FORMS': self.request.POST[str(days) + '-MIN_NUM_FORMS'],
                }

                for i in range(int(data[str(days) + '-TOTAL_FORMS'])):
                    if self.request.POST.get(str(days) + '-' + str(i) + '-break_start') not in ['', None]:
                        break_start = datetime.strptime(
                            convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_start']), '%I:%M %p')
                        data[str(days) + '-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                    if self.request.POST.get(str(days) + '-' + str(i) + '-break_end') not in ['', None]:
                        break_end = datetime.strptime(
                            convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_end']),
                            '%I:%M %p')
                        data[str(days) + '-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                    if self.request.POST.get(str(days) + '-' + str(i) + '-DELETE'):
                        data[str(days) + '-' + str(i) + '-DELETE'] = self.request.POST[
                            str(days) + '-' + str(i) + '-DELETE']
                    else:
                        data[str(days) + '-' + str(i) + '-DELETE'] = ''
                context[str(days) + '_freelancing_formset'] = self.fixedformset(data, prefix=days)

        return render(self.request, self.template_name, context)


class ScheduleMasterUpdateView(LoginRequiredMixin, PermissionMixin, UpdateView):
    permission_required = 'change_schedulemaster'
    template_name = 'attendance/master/schedule/update.html'
    form_class = ScheduleMasterForm
    flexible_form = ScheduleMasterFlexibleTypeForm
    fixedformset = inlineformset_factory(TimeTable, BreakTime, form=ScheduleMasterBreakTimeForm, extra=1,
                                         can_delete=True)
    success_url = reverse_lazy('beehive_admin:attendance:master_schedule_list')

    def get_queryset(self):
        return ScheduleMaster.objects.all()

    def get_instance(self):
        return TimeTable.objects.filter(schedule_master=self.object).last()

    def get_timetable_form(self):
        instance = self.get_instance()
        timetable_form = ScheduleMasterTimeTableForm(instance=instance)
        return timetable_form

    def get_fixed_formset(self):
        instance = self.get_instance()
        if instance and instance.breaktime_model.all():
            extra_value = 0
        else:
            extra_value = 1

        fixedformset = inlineformset_factory(TimeTable, BreakTime, form=ScheduleMasterBreakTimeForm, extra=extra_value,
                                             can_delete=True)
        fixed = fixedformset(instance=self.get_instance(), prefix='fixedForm')
        return fixed

    def get_hourly_formset(self):
        hourlyformset = inlineformset_factory(TimeTable, TimeDuration, form=ScheduleMasterTimeDurationForm, extra=1,
                                              can_delete=True)
        hourly = hourlyformset(instance=self.get_instance(), prefix='hourlyForm')
        return hourly

    def get_flexible_instance(self):
        myFlex = []
        for data in FlexibleType.objects.filter(schedule_master=self.object):
            flex = {
                'day': data.days.id,
                'hour': data.working_hour,
                'unit': data.working_hour_unit,
            }
            myFlex.append(flex)
        return myFlex

    def get_freelancing_instance(self):
        freelancing = []
        for data in TimeTable.objects.filter(schedule_master=self.object):
            freelance = {
                'day': data.days.id,
                'in_time': data.in_time,
                'out_time': data.out_time,
            }
            freelancing.append(freelance)
        return freelancing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timetable_form'] = self.get_timetable_form()
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['day'] = TimeTable.objects.filter(schedule_master=self.object).values_list('days', flat=True)
        context['fixed_formset'] = self.get_fixed_formset()
        context['hourly_formset'] = self.get_hourly_formset()
        context['flexible_instance'] = self.get_flexible_instance()
        context['freelancing_instance'] = self.get_freelancing_instance()
        context['flexible_form'] = self.flexible_form()

        for days in range(1, 8):
            ins = TimeTable.objects.filter(schedule_master=self.object)
            if ins.filter(days=days).last() and ins.filter(days=days).last().breaktime_model.all():
                extra_value = 0
            else:
                extra_value = 1
            fixedformset = inlineformset_factory(TimeTable, BreakTime, form=ScheduleMasterBreakTimeForm,
                                                 extra=extra_value,
                                                 can_delete=True)
            context[str(days) + '_freelancing_formset'] = fixedformset(instance=ins.filter(days=days).last(),
                                                                            prefix=days)

        return context

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """

        parent_id = self.request.GET.get('parent_id')

        def get_instance():
            return TimeTable.objects.filter(schedule_master_id=parent_id).last()

        def get_flexible_instance():
            myFlex = []
            for data in FlexibleType.objects.filter(schedule_master_id=parent_id):
                flex = {
                    'day': data.days.id,
                    'hour': data.working_hour,
                    'unit': data.working_hour_unit,
                }
                myFlex.append(flex)
            return myFlex

        def get_freelancing_instance():
            freelancing = []
            for data in TimeTable.objects.filter(schedule_master_id=parent_id):
                freelance = {
                    'day': data.days.id,
                    'in_time': data.in_time,
                    'out_time': data.out_time,
                }
                freelancing.append(freelance)
            return freelancing

        if self.request.is_ajax():
            if parent_id not in EMPTY_VALUES:
                instant = get_instance()
                context['form'] = self.form_class(instance=ScheduleMaster.objects.filter(id=parent_id).first())
                context['permissions'] = self.get_current_user_permission_list()
                context['org_items_list'] = get_organizational_structure()
                context['timetable_form'] = ScheduleMasterTimeTableForm(instance=instant)
                context['day'] = TimeTable.objects.filter(schedule_master_id=parent_id).values_list('days', flat=True)
                if instant.breaktime_model.all():
                    extra_value = 0
                else:
                    extra_value = 1
                fixedformset = inlineformset_factory(TimeTable, BreakTime, form=ScheduleMasterBreakTimeForm,
                                                     extra=extra_value,
                                                     can_delete=True)
                context['fixed_formset'] = fixedformset(instance=instant, prefix='fixedForm')
                hourlyformset = inlineformset_factory(TimeTable, TimeDuration, form=ScheduleMasterTimeDurationForm,
                                                      extra=1,
                                                      can_delete=True)
                context['hourly_formset'] = hourlyformset(instance=get_instance(), prefix='hourlyForm')
                context['flexible_instance'] = get_flexible_instance()
                context['freelancing_instance'] = get_freelancing_instance()
                context['flexible_form'] = self.flexible_form()
                for days in range(1, 8):
                    ins = TimeTable.objects.filter(schedule_master_id=parent_id)
                    ins_obj = ins.filter(days=days).last()
                    if ins_obj and ins_obj.breaktime_model.all():
                        extra_value = 0
                    else:
                        extra_value = 1
                    fixedformset = inlineformset_factory(TimeTable, BreakTime, form=ScheduleMasterBreakTimeForm,
                                                         extra=extra_value,
                                                         can_delete=True)
                    context[str(days) + '_freelancing_formset'] = fixedformset(
                        instance=ins_obj,
                        prefix=days)
                return render(self.request, 'attendance/master/schedule/parent_form.html', context)
        else:
            return super(UpdateView, self).render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        context = dict()
        form = self.form_class(self.request.POST, instance=self.object)
        context['form'] = form
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['timetable_form'] = ScheduleMasterTimeTableForm(instance=self.get_instance())
        context['day'] = TimeTable.objects.filter(schedule_master=self.object).values_list('days', flat=True)
        context['fixed_formset'] = self.get_fixed_formset()
        context['hourly_formset'] = self.get_hourly_formset()
        context['flexible_form'] = self.flexible_form()
        for days in range(1, 8):
            ins = TimeTable.objects.filter(schedule_master=self.object)
            if ins.filter(days=days).last() and ins.filter(days=days).last().breaktime_model.all():
                extra_value = 0
            else:
                extra_value = 1
            fixedformset = inlineformset_factory(TimeTable, BreakTime, form=ScheduleMasterBreakTimeForm,
                                                 extra=extra_value,
                                                 can_delete=True)
            context[str(days) + '_freelancing_formset'] = fixedformset(instance=ins.filter(days=days).last(),
                                                                            prefix=days)

        def convert_time(t):
            parts = t.split(':')
            if len(parts[0]) == 1:
                parts[0] = '0{}'.format(parts[0])
                return ':'.join(parts)
            else:
                return t

        post_dict = self.request.POST.copy()
        if self.request.POST.get('schedule_type') in ['regular-fixed-time', 'fixed-day', 'weekly', 'day']:

            # Timetable form validation
            if self.request.POST.get('in_time') not in ['', None]:
                post_dict['in_time'] = datetime.strptime(convert_time(self.request.POST['in_time']), '%I:%M %p')
                post_dict['in_time'] = post_dict['in_time'].strftime('%H:%M')
            if self.request.POST.get('out_time') not in ['', None]:
                post_dict['out_time'] = datetime.strptime(convert_time(self.request.POST['out_time']), '%I:%M %p')
                post_dict['out_time'] = post_dict['out_time'].strftime('%H:%M')
            timetable_form = ScheduleMasterTimeTableForm(post_dict, instance=self.get_instance())
            context['timetable_form'] = timetable_form
            timetable_form.fields['in_time'].required = True
            timetable_form.fields['out_time'].required = True

            # fixed formset validation
            data = {
                'fixedForm-TOTAL_FORMS': self.request.POST['fixedForm-TOTAL_FORMS'],
                'fixedForm-INITIAL_FORMS': self.request.POST['fixedForm-INITIAL_FORMS'],
                'fixedForm-MIN_NUM_FORMS': self.request.POST['fixedForm-MIN_NUM_FORMS'],
            }
            for i in range(int(data['fixedForm-TOTAL_FORMS'])):
                if self.request.POST.get('fixedForm-' + str(i) + '-break_start') not in ['', None]:
                    break_start = datetime.strptime(
                        convert_time(self.request.POST['fixedForm-' + str(i) + '-break_start']), '%I:%M %p')
                    data['fixedForm-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                if self.request.POST.get('fixedForm-' + str(i) + '-break_end') not in ['', None]:
                    break_end = datetime.strptime(convert_time(self.request.POST['fixedForm-' + str(i) + '-break_end']),
                                                  '%I:%M %p')
                    data['fixedForm-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                data['fixedForm-' + str(i) + '-id'] = self.request.POST['fixedForm-' + str(i) + '-id']
                if self.request.POST.get('fixedForm-' + str(i) + '-DELETE'):
                    data['fixedForm-' + str(i) + '-DELETE'] = self.request.POST['fixedForm-' + str(i) + '-DELETE']
                else:
                    data['fixedForm-' + str(i) + '-DELETE'] = ''

            fixed_formset = self.fixedformset(data, prefix='fixedForm')
            context['fixed_formset'] = fixed_formset
            if not timetable_form.is_valid():
                return render(self.request, self.template_name, context)

            if not fixed_formset.is_valid():
                return render(self.request, self.template_name, context)

            obj = form.save()
            TimeTable.objects.filter(schedule_master=obj).delete()
            FlexibleType.objects.filter(schedule_master=obj).delete()

            for day in self.request.POST.getlist('days'):
                timetable = TimeTable.objects.create(
                    schedule_master=obj,
                    days_id=day,
                    in_time=timetable_form.cleaned_data.get('in_time'),
                    out_time=timetable_form.cleaned_data.get('out_time')
                )
                for fixed in fixed_formset:
                    if fixed.cleaned_data.get('break_start') is not None:
                        if not fixed.cleaned_data.get('DELETE'):
                            BreakTime.objects.create(
                                timetable=timetable,
                                break_start=fixed.cleaned_data.get('break_start'),
                                break_end=fixed.cleaned_data.get('break_end')
                            )
        else:
            timetable_form = ScheduleMasterTimeTableForm(post_dict, instance=self.get_instance())
            context['timetable_form'] = timetable_form

            if self.request.POST.get('schedule_type') in ['hourly']:

                # hourly formset validation
                data = {
                    'hourlyForm-TOTAL_FORMS': self.request.POST['hourlyForm-TOTAL_FORMS'],
                    'hourlyForm-INITIAL_FORMS': self.request.POST['hourlyForm-INITIAL_FORMS'],
                    'hourlyForm-MIN_NUM_FORMS': self.request.POST['hourlyForm-MIN_NUM_FORMS'],
                }
                for i in range(int(data['hourlyForm-TOTAL_FORMS'])):
                    if self.request.POST.get('hourlyForm-' + str(i) + '-work_start') not in ['', None]:
                        work_start = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-work_start']), '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-work_start'] = work_start.strftime('%H:%M')
                    if self.request.POST.get('hourlyForm-' + str(i) + '-work_end') not in ['', None]:
                        work_end = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-work_end']),
                            '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-work_end'] = work_end.strftime('%H:%M')
                    if self.request.POST.get('hourlyForm-' + str(i) + '-break_start') not in ['', None]:
                        break_start = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-break_start']), '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                    if self.request.POST.get('hourlyForm-' + str(i) + '-break_end') not in ['', None]:
                        break_end = datetime.strptime(
                            convert_time(self.request.POST['hourlyForm-' + str(i) + '-break_end']),
                            '%I:%M %p')
                        data['hourlyForm-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                    data['hourlyForm-' + str(i) + '-id'] = self.request.POST['hourlyForm-' + str(i) + '-id']
                    if self.request.POST.get('hourlyForm-' + str(i) + '-DELETE'):
                        data['hourlyForm-' + str(i) + '-DELETE'] = self.request.POST['hourlyForm-' + str(i) + '-DELETE']
                    else:
                        data['hourlyForm-' + str(i) + '-DELETE'] = ''

                hourlyformset = inlineformset_factory(TimeTable, TimeDuration, form=ScheduleMasterTimeDurationForm,
                                                      extra=1,
                                                      can_delete=True)
                hourly_formset = hourlyformset(data, prefix='hourlyForm')
                context['hourly_formset'] = hourly_formset

                if not timetable_form.is_valid():
                    return render(self.request, self.template_name, context)

                if not hourly_formset.is_valid():
                    return render(self.request, self.template_name, context)

                obj = form.save()
                TimeTable.objects.filter(schedule_master=obj).delete()

                for day in self.request.POST.getlist('days'):
                    timetable = TimeTable.objects.create(
                        schedule_master=obj,
                        days_id=day
                    )
                    for hourly in hourly_formset:
                        if hourly.cleaned_data.get('break_start') is not None:
                            if not hourly.cleaned_data.get('DELETE'):
                                TimeDuration.objects.create(
                                    timetable=timetable,
                                    work_start=hourly.cleaned_data.get('work_start'),
                                    work_end=hourly.cleaned_data.get('work_end'),
                                    break_start=hourly.cleaned_data.get('break_start'),
                                    break_end=hourly.cleaned_data.get('break_end')
                                )

            elif (self.request.POST.get('schedule_type') in ['freelancing']) or (
                self.request.POST.get('schedule_type') in ['roster'] and self.request.POST.get(
                    'roster_type') == 'fixed-roster'):

                # for old value stay in form when form is error
                in_time_error = False
                for days in range(1, 8):
                    # freelancing formset validation
                    data = {
                        str(days) + '-TOTAL_FORMS': self.request.POST[str(days) + '-TOTAL_FORMS'],
                        str(days) + '-INITIAL_FORMS': self.request.POST[str(days) + '-INITIAL_FORMS'],
                        str(days) + '-MIN_NUM_FORMS': self.request.POST[str(days) + '-MIN_NUM_FORMS'],
                    }

                    for i in range(int(data[str(days) + '-TOTAL_FORMS'])):
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_start') not in ['', None]:
                            break_start = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_start']), '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_end') not in ['', None]:
                            break_end = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_end']),
                                '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                        data[str(days) + '-' + str(i) + '-id'] = self.request.POST[str(days) + '-' + str(i) + '-id']
                        if self.request.POST.get(str(days) + '-' + str(i) + '-DELETE'):
                            data[str(days) + '-' + str(i) + '-DELETE'] = self.request.POST[
                                str(days) + '-' + str(i) + '-DELETE']
                        else:
                            data[str(days) + '-' + str(i) + '-DELETE'] = ''
                    context[str(days) + '_freelancing_formset'] = self.fixedformset(data, prefix=days)

                context['freelancing_instance'] = [
                    {'day': int(i),
                     'in_time': datetime.strptime(str(self.request.POST.getlist('in_time')[int(i) - 1]), '%I:%M %p')
                     if (self.request.POST.getlist('in_time')[int(i) - 1]).strip() else '',
                     'out_time': datetime.strptime(str(self.request.POST.getlist('out_time')[int(i) - 1]), '%I:%M %p')
                     if (self.request.POST.getlist('out_time')[int(i) - 1]).strip() else ''
                     }
                    for i in self.request.POST.getlist('days')
                ]
                day = []

                for i in self.request.POST.getlist('days'):
                    day.append(int(i))
                    if (self.request.POST.getlist('in_time')[int(i) - 1]).strip() in EMPTY_VALUES:
                        in_time_error = True
                    if (self.request.POST.getlist('out_time')[int(i) - 1]).strip() in EMPTY_VALUES:
                        in_time_error = True
                context['day'] = day
                print(timetable_form.errors)

                if timetable_form.is_valid() is False or in_time_error is True:
                    return render(self.request, self.template_name, context)

                for days in self.request.POST.getlist('days'):
                    # freelancing formset validation
                    data = {
                        str(days) + '-TOTAL_FORMS': self.request.POST[str(days) + '-TOTAL_FORMS'],
                        str(days) + '-INITIAL_FORMS': self.request.POST[str(days) + '-INITIAL_FORMS'],
                        str(days) + '-MIN_NUM_FORMS': self.request.POST[str(days) + '-MIN_NUM_FORMS'],
                    }

                    for i in range(int(data[str(days) + '-TOTAL_FORMS'])):
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_start') not in ['', None]:
                            break_start = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_start']), '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_start'] = break_start.strftime('%H:%M')
                        if self.request.POST.get(str(days) + '-' + str(i) + '-break_end') not in ['', None]:
                            break_end = datetime.strptime(
                                convert_time(self.request.POST[str(days) + '-' + str(i) + '-break_end']),
                                '%I:%M %p')
                            data[str(days) + '-' + str(i) + '-break_end'] = break_end.strftime('%H:%M')
                        data[str(days) + '-' + str(i) + '-id'] = self.request.POST[str(days) + '-' + str(i) + '-id']
                        if self.request.POST.get(str(days) + '-' + str(i) + '-DELETE'):
                            data[str(days) + '-' + str(i) + '-DELETE'] = self.request.POST[
                                str(days) + '-' + str(i) + '-DELETE']
                        else:
                            data[str(days) + '-' + str(i) + '-DELETE'] = ''

                    fixed_formset = self.fixedformset(data, prefix=days)
                    context[str(days) + '_freelancing_formset'] = fixed_formset
                    print(fixed_formset.errors)

                    if not fixed_formset.is_valid():
                        return render(self.request, self.template_name, context)

                obj = form.save()
                TimeTable.objects.filter(schedule_master=obj).delete()
                FlexibleType.objects.filter(schedule_master=obj).delete()

                for day in self.request.POST.getlist('days'):
                    timetable = TimeTable.objects.create(schedule_master=obj, days_id=day,
                                                         in_time=self.request.POST.getlist('in_time')[int(day) - 1],
                                                         out_time=self.request.POST.getlist('out_time')[
                                                             int(day) - 1])
                    for form_data in context[str(day) + '_freelancing_formset']:
                        if form_data.cleaned_data.get('break_start') is not None:
                            if not form_data.cleaned_data.get('DELETE'):
                                BreakTime.objects.create(
                                    timetable=timetable,
                                    break_start=form_data.cleaned_data.get('break_start'),
                                    break_end=form_data.cleaned_data.get('break_end')
                                )

            else:
                if self.request.POST.get('schedule_type') in ['flexible']:
                    flexible_form = self.flexible_form(self.request.POST, prefix='flexible')
                    context['flexible_form'] = flexible_form
                    # for old value stay in form when form is error
                    context['flexible_instance'] = [
                        {'day': int(i),
                         'hour': int(self.request.POST.getlist('working_hour')[int(i) - 1])
                         if (self.request.POST.getlist('working_hour')[int(i) - 1]).strip() else '',
                         'unit': self.request.POST.getlist('working_hour_unit')[int(i) - 1]
                         if (self.request.POST.getlist('working_hour_unit')[int(i) - 1]).strip() else '',
                         }
                        for i in self.request.POST.getlist('days')
                    ]
                    day = []
                    working_hour_error = False

                    for i in self.request.POST.getlist('days'):
                        day.append(int(i))
                        if (self.request.POST.getlist('working_hour')[int(i) - 1]).strip() in EMPTY_VALUES:
                            working_hour_error = True
                        if (self.request.POST.getlist('working_hour_unit')[int(i) - 1]).strip() in EMPTY_VALUES:
                            working_hour_error = True
                    context['day'] = day

                    if day not in EMPTY_VALUES:
                        flexible_form.fields['days'].required = False

                    if flexible_form.is_valid() is False or working_hour_error is True:
                        return render(self.request, self.template_name, context)

                    if not timetable_form.is_valid():
                        return render(self.request, self.template_name, context)

                    obj = form.save()
                    TimeTable.objects.filter(schedule_master=obj).delete()
                    FlexibleType.objects.filter(schedule_master=obj).delete()

                    FlexibleType.objects.bulk_create([
                        FlexibleType(
                            schedule_master=obj,
                            days_id=day,
                            working_hour=self.request.POST.getlist('working_hour')[int(day) - 1],
                            working_hour_unit=self.request.POST.getlist('working_hour_unit')[int(day) - 1]
                        )
                        for day in self.request.POST.getlist('days')
                    ])

                elif self.request.POST.get('schedule_type') in ['roster'] and \
                        self.request.POST.get('roster_type') == 'variable-roster':

                    timetable_form.fields['days'].required = False

                    if not timetable_form.is_valid():
                        return render(self.request, self.template_name, context)

                    obj = form.save()
                    TimeTable.objects.filter(schedule_master=obj).delete()
                    FlexibleType.objects.filter(schedule_master=obj).delete()

                    TimeTable.objects.bulk_create([
                        TimeTable(
                            schedule_master=obj,
                            days_id=day,
                        )
                        for day in self.request.POST.getlist('days')
                    ])

        return super().form_valid(form)


class ScheduleMasterDeleteView(LoginRequiredMixin, PermissionMixin, DeleteView):
    permission_required = 'delete_schedulemaster'
    model = ScheduleMaster
    success_url = reverse_lazy('beehive_admin:attendance:master_schedule_list')
    success_message = "Deleted successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.error(self.request, self.success_message % obj.__dict__)
        return super(ScheduleMasterDeleteView, self).delete(request, *args, **kwargs)
