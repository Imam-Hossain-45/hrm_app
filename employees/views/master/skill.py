from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.forms import modelformset_factory
from django.db import IntegrityError
from helpers.functions import get_organizational_structure


class EmployeeSkillCreateView(LoginRequiredMixin, PermissionMixin, CreateView):
    """
        Create and update employee skill information
        Access: Super-Admin, Admin
        Url: /employee/<pk>/skill_training_language/
    """
    form_class = SkillForm
    training_form_class = TrainingForm
    professional_form_class = ProfessionalCertificateForm
    language_form_class = LanguageProficiencyForm
    template_name = 'employees/master/skill/create.html'
    permission_required = ['add_skill', 'change_skill', 'view_skill',
                           'delete_skill', 'add_training', 'change_training', 'view_training',
                           'delete_training', 'add_ProfessionalCertificate', 'change_ProfessionalCertificate',
                           'view_ProfessionalCertificate',
                           'delete_ProfessionalCertificate', 'add_LanguageProficiency', 'change_LanguageProficiency',
                           'view_LanguageProficiency',
                           'delete_LanguageProficiency']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']
        if 'skill_form' not in context:
            skillformset = modelformset_factory(emp_models.Skill, form=SkillForm, extra=1, can_delete=True)
            context['skill_form'] = skillformset(queryset=self.get_skill_information(), prefix='skill')

        if 'training_form' not in context:
            trainingformset = modelformset_factory(emp_models.Training, form=TrainingForm, extra=1, can_delete=True)
            context['training_form'] = trainingformset(queryset=self.get_training_information(), prefix='training')

        if 'professional_form' not in context:
            professionalformset = modelformset_factory(emp_models.ProfessionalCertificate,
                                                       form=ProfessionalCertificateForm, extra=1, can_delete=True)
            context['professional_form'] = professionalformset(queryset=self.get_professional_information(),
                                                               prefix='professional')

        if 'language_form' not in context:
            languageformset = modelformset_factory(emp_models.LanguageProficiency, form=LanguageProficiencyForm,
                                                   extra=1, can_delete=True)
            context['language_form'] = languageformset(queryset=self.get_language_information(), prefix='language')
        return context

    def get_skill_information(self):
        data = emp_models.Skill.objects.filter(employee_id=self.kwargs['pk'])
        return data

    def get_training_information(self):
        data = emp_models.Training.objects.filter(employee_id=self.kwargs['pk'])
        return data

    def get_professional_information(self):
        data = emp_models.ProfessionalCertificate.objects.filter(employee_id=self.kwargs['pk'])
        return data

    def get_language_information(self):
        data = emp_models.LanguageProficiency.objects.filter(employee_id=self.kwargs['pk'])
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if 'skill_form' not in context:
            skillFormSet = modelformset_factory(emp_models.Skill, form=SkillForm, extra=1, can_delete=True)
            context['skill_form'] = skillFormSet(queryset=self.get_skill_information(), prefix='skill')

        if 'form1' in request.POST:
            skillFormSet = modelformset_factory(emp_models.Skill, form=SkillForm, extra=1, can_delete=True,
                                                min_num=1, validate_min=True)
            data = {
                'form-TOTAL_FORMS': request.POST['skill-TOTAL_FORMS'],
                'form-INITIAL_FORMS': request.POST['skill-INITIAL_FORMS'],
                'form-MIN_NUM_FORMS': request.POST['skill-MIN_NUM_FORMS'],
            }
            for i in range(int(data['form-TOTAL_FORMS'])):
                data['skill-' + str(i) + '-skill_name'] = request.POST[
                    'skill-' + str(i) + '-skill_name']
                data['skill-' + str(i) + '-description'] = request.POST[
                    'skill-' + str(i) + '-description']
                data['skill-' + str(i) + '-skill_level'] = request.POST['skill-' + str(i) + '-skill_level']
                if request.POST.get('skill-' + str(i) + '-DELETE'):
                    data['skill-' + str(i) + '-DELETE'] = request.POST['skill-' + str(i) + '-DELETE']
                else:
                    data['skill-' + str(i) + '-DELETE'] = ''
            context['skill_form'] = skillFormSet(request.POST, data, prefix='skill')
            skill_form = context['skill_form']
            if skill_form.is_valid():
                try:
                    for skill in skill_form:
                        forms = skill_form.save(commit=False)
                        for object in skill_form.deleted_objects:
                            object.delete()
                        if skill.cleaned_data.get('skill_name') is not None:
                            em = skill.save(commit=False)
                            em.employee_id = self.kwargs['pk']
                            skill.save()
                    messages.success(self.request, "Updated skill information.")
                except IntegrityError:
                    messages.error(self.request, "Duplicate entry of skill name for this employee.")
                return redirect('employees:employee_skill_info', self.kwargs['pk'])

        if 'training_form' not in context:
            trainingFormSet = modelformset_factory(emp_models.Training, form=TrainingForm, extra=1, can_delete=True)
            context['training_form'] = trainingFormSet(queryset=self.get_training_information(), prefix='training')

        if 'form2' in request.POST:
            trainingFormSet = modelformset_factory(emp_models.Training,
                                                   form=TrainingForm, extra=1, can_delete=True,
                                                   min_num=1, validate_min=True)
            data = {
                'training-TOTAL_FORMS': request.POST['training-TOTAL_FORMS'],
                'training-INITIAL_FORMS': request.POST['training-INITIAL_FORMS'],
                'training-MIN_NUM_FORMS': request.POST['training-MIN_NUM_FORMS'],
            }
            for i in range(int(data['training-TOTAL_FORMS'])):
                data['training-' + str(i) + '-training_title'] = request.POST[
                    'training-' + str(i) + '-training_title']
                data['training-' + str(i) + '-country'] = request.POST[
                    'training-' + str(i) + '-country']
                data['training-' + str(i) + '-training_year'] = request.POST['training-' + str(i) + '-training_year']
                data['training-' + str(i) + '-institute'] = request.POST['training-' + str(i) + '-institute']
                data['training-' + str(i) + '-duration'] = request.POST['training-' + str(i) + '-duration']
                data['training-' + str(i) + '-duration_unit'] = request.POST['training-' + str(i) + '-duration_unit']
                if request.FILES.get('training-' + str(i) + '-certificate'):
                    data['training-' + str(i) + '-certificate'] = request.FILES['training-' + str(i) + '-certificate']
                if request.POST.get('training-' + str(i) + '-certificate-clear'):
                    data['training-' + str(i) + '-certificate-clear'] = request.POST[
                        'training-' + str(i) + '-certificate-clear']
                if request.POST.get('training-' + str(i) + '-DELETE'):
                    data['training-' + str(i) + '-DELETE'] = request.POST['training-' + str(i) + '-DELETE']
                else:
                    data['training-' + str(i) + '-DELETE'] = ''
            context['training_form'] = trainingFormSet(request.POST, request.FILES, data, prefix='training')
            training_form = context['training_form']
            if training_form.is_valid():
                try:
                    for training in training_form:
                        forms = training_form.save(commit=False)
                        for object in training_form.deleted_objects:
                            object.delete()
                        if training.cleaned_data.get('training_title') is not None:
                            em = training.save(commit=False)
                            em.employee_id = self.kwargs['pk']
                            # clear certificate file
                            if training.cleaned_data.get('certificate-clear'):
                                em.certificate = None
                            training.save()
                    messages.success(self.request, "Updated training information.")
                except IntegrityError:
                    messages.error(self.request, "Duplicate entry of training title for this employee.")
                return redirect('employees:employee_skill_info', self.kwargs['pk'])
        if 'professional_form' not in context:
            professionalFormSet = modelformset_factory(emp_models.ProfessionalCertificate,
                                                       form=ProfessionalCertificateForm, extra=1, can_delete=True)
            context['professional_form'] = professionalFormSet(queryset=self.get_professional_information(),
                                                               prefix='professional')

        if 'form3' in request.POST:
            professionalFormSet = modelformset_factory(emp_models.ProfessionalCertificate,
                                                       form=ProfessionalCertificateForm, extra=1, can_delete=True,
                                                       min_num=1, validate_min=True)
            data = {
                'professional-TOTAL_FORMS': request.POST['professional-TOTAL_FORMS'],
                'professional-INITIAL_FORMS': request.POST['professional-INITIAL_FORMS'],
                'professional-MIN_NUM_FORMS': request.POST['professional-MIN_NUM_FORMS'],
            }
            for i in range(int(data['professional-TOTAL_FORMS'])):
                data['professional-' + str(i) + '-certificate_title'] = request.POST[
                    'professional-' + str(i) + '-certificate_title']
                data['professional-' + str(i) + '-country'] = request.POST[
                    'professional-' + str(i) + '-country']
                data['professional-' + str(i) + '-institute'] = request.POST['professional-' + str(i) + '-institute']
                data['professional-' + str(i) + '-institute_address'] = request.POST[
                    'professional-' + str(i) + '-institute_address']
                data['professional-' + str(i) + '-duration'] = request.POST['professional-' + str(i) + '-duration']
                data['professional-' + str(i) + '-duration_unit'] = request.POST[
                    'professional-' + str(i) + '-duration_unit']
                if request.FILES.get('professional-' + str(i) + '-certificate'):
                    data['professional-' + str(i) + '-certificate'] = request.FILES[
                        'professional-' + str(i) + '-certificate']
                if request.POST.get('professional-' + str(i) + '-certificate-clear'):
                    data['professional-' + str(i) + '-certificate-clear'] = request.POST[
                        'professional-' + str(i) + '-certificate-clear']
                if request.POST.get('professional-' + str(i) + '-DELETE'):
                    data['professional-' + str(i) + '-DELETE'] = request.POST['professional-' + str(i) + '-DELETE']
                else:
                    data['professional-' + str(i) + '-DELETE'] = ''
            context['professional_form'] = professionalFormSet(request.POST, request.FILES, data, prefix='professional')
            professional_form = context['professional_form']
            if professional_form.is_valid():
                try:
                    for professional in professional_form:
                        forms = professional_form.save(commit=False)
                        for object in professional_form.deleted_objects:
                            object.delete()
                        if professional.cleaned_data.get('certificate_title') is not None:
                            em = professional.save(commit=False)
                            em.employee_id = self.kwargs['pk']
                            # clear certificate file
                            if professional.cleaned_data.get('certificate-clear'):
                                em.certificate = None
                            professional.save()
                    messages.success(self.request, "Updated professional Certificate.")
                except IntegrityError:
                    messages.error(self.request, "Duplicate entry of professional certificate for this employee.")
                return redirect('employees:employee_skill_info', self.kwargs['pk'])

        if 'language_form' not in context:
            languageFormSet = modelformset_factory(emp_models.LanguageProficiency,
                                                   form=LanguageProficiencyForm, extra=1, can_delete=True)
            context['language_form'] = languageFormSet(queryset=self.get_language_information(),
                                                       prefix='language')

        if 'form4' in request.POST:
            languageFormSet = modelformset_factory(emp_models.LanguageProficiency,
                                                   form=LanguageProficiencyForm, extra=1, can_delete=True,
                                                   min_num=1, validate_min=True)
            data = {
                'language-TOTAL_FORMS': request.POST['language-TOTAL_FORMS'],
                'language-INITIAL_FORMS': request.POST['language-INITIAL_FORMS'],
                'language-MIN_NUM_FORMS': request.POST['language-MIN_NUM_FORMS'],
            }
            for i in range(int(data['language-TOTAL_FORMS'])):
                data['language-' + str(i) + '-language'] = request.POST[
                    'language-' + str(i) + '-language']
                data['language-' + str(i) + '-description'] = request.POST[
                    'language-' + str(i) + '-description']
                data['language-' + str(i) + '-read'] = request.POST['language-' + str(i) + '-read']
                data['language-' + str(i) + '-write'] = request.POST[
                    'language-' + str(i) + '-write']
                data['language-' + str(i) + '-speak'] = request.POST['language-' + str(i) + '-speak']
                if request.POST.get('language-' + str(i) + '-DELETE'):
                    data['language-' + str(i) + '-DELETE'] = request.POST['language-' + str(i) + '-DELETE']
                else:
                    data['language-' + str(i) + '-DELETE'] = ''
            context['language_form'] = languageFormSet(request.POST, data, prefix='language')
            language_form = context['language_form']
            if language_form.is_valid():
                try:
                    for language in language_form:
                        forms = language_form.save(commit=False)
                        for object in language_form.deleted_objects:
                            object.delete()
                        if language.cleaned_data.get('language') is not None:
                            em = language.save(commit=False)
                            em.employee_id = self.kwargs['pk']
                            language.save()
                    messages.success(self.request, "Updated language proficiency.")
                except IntegrityError:
                    messages.error(self.request, "Duplicate entry of language proficiency for this employee.")
                return redirect('employees:employee_skill_info', self.kwargs['pk'])
        return render(request, self.template_name, context)
