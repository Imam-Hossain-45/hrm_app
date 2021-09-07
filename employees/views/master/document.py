from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from employees.forms import *
from django.shortcuts import render, redirect, get_object_or_404
from helpers.mixins import PermissionMixin
from django.contrib import messages
from django.views.generic.edit import FormMixin
from helpers.functions import get_organizational_structure


class DocumentView(LoginRequiredMixin, PermissionMixin, FormMixin, TemplateView):
    """
        Add document
        Access: Super-Admin, Admin
        Url: /employee/<pk>/document/
    """
    form_class = DocumentForm
    tax_form_class = TaxDocumentForm
    edu_doc_form_class = EducationalDocumentForm
    others_doc_form_class = OtherDocumentForm
    template_name = 'employees/master/document/create.html'
    permission_required = ['add_document', 'change_document', 'view_document',
                           'delete_document']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()
        context['pk'] = self.kwargs['pk']

        if 'document_form' not in context:
            if self.get_document():
                context['document_form'] = self.form_class(instance=self.get_document())
            else:
                context['document_form'] = self.form_class()
        if 'tax_form' not in context:
            if self.get_tax():
                context['tax_form'] = self.tax_form_class(instance=self.get_tax())
            else:
                context['tax_form'] = self.tax_form_class()

        if 'edu_doc_form' not in context:
            context['edu_doc_form'] = [self.edu_doc_form_class(instance=x) for x in self.get_edu_doc()]

        if self.get_others_doc():
            context['others_doc_object'] = self.get_others_doc()
        if 'others_doc_form' not in context:
            context['others_doc_form'] = self.others_doc_form_class()

        return context

    def get_document(self):
        data = emp_models.Documents.objects.filter(employee_id=self.kwargs['pk']).last()
        return data

    def get_tax(self):
        data = emp_models.Personal.objects.filter(employee_id=self.kwargs['pk']).last()
        return data

    def get_edu_doc(self):
        instance = list(emp_models.Education.objects.filter(employee_id=self.kwargs['pk']))
        return instance

    def get_others_doc(self):
        data = emp_models.OthersDocuments.objects.filter(employee_id=self.kwargs['pk'])
        return data

    def post(self, request, *args, **kwargs):
        context = dict()
        get_object_or_404(emp_models.EmployeeIdentification, pk=self.kwargs['pk'])
        if 'document_form' not in context:
            if self.get_document():
                context['document_form'] = self.form_class(instance=self.get_document())
            else:
                context['document_form'] = self.form_class()
        if 'tax_form' not in context:
            if self.get_tax():
                context['tax_form'] = self.tax_form_class(instance=self.get_tax())
            else:
                context['tax_form'] = self.tax_form_class()

        if 'edu_doc_form' not in context:
            context['edu_doc_form'] = [self.edu_doc_form_class(instance=x) for x in self.get_edu_doc()]

        if self.get_others_doc():
            context['others_doc_object'] = self.get_others_doc()
        if 'others_doc_form' not in context:
            context['others_doc_form'] = self.others_doc_form_class()

        context['pk'] = self.kwargs['pk']
        context['permissions'] = self.get_current_user_permission_list()
        context['org_items_list'] = get_organizational_structure()

        if 'form1' in request.POST:
            """
                Other documents upload
            """
            context['others_doc_form'] = self.others_doc_form_class(request.POST, request.FILES)
            others_doc_form = context['others_doc_form']
            others = emp_models.OthersDocuments.objects
            if request.FILES.get('file') is not None:
                if others_doc_form.is_valid():
                    created = others.create(employee_id=self.kwargs['pk'], title=request.POST['title'], file=request.FILES['file'])
                    if created:
                        messages.success(self.request, "Upload documents")
                else:
                    return render(request, self.template_name, context)
            if request.POST.get('file-clear'):
                deleted = others.get(id=request.POST.get('file-clear'))
                deleted.delete()
                if deleted:
                    messages.error(self.request, 'Deleted Documents.')
            """
                Education certificate upload
            """
            context['edu_doc_form'] = [self.edu_doc_form_class(instance=x) for x in self.get_edu_doc()]
            edu_doc_form = context['edu_doc_form']

            education = emp_models.Education.objects
            if request.POST.get('certificate-clear'):
                deleted = education.get(id=request.POST.get('certificate-clear'))
                if deleted.degree is not None:
                    deleted.certificate = None
                    deleted.save()
                else:
                    deleted.delete()
                if deleted:
                    messages.error(self.request, 'Deleted Certificate')
            if request.FILES.get('certificate') is not None:
                created = education.create(employee_id=self.kwargs['pk'], certificate=request.FILES['certificate'])
                if created:
                    messages.success(self.request, "Upload documents")

            """
                Personal documents upload
            """
            context['tax_form'] = self.tax_form_class(request.POST, request.FILES, instance=self.get_tax())
            tax_form = context['tax_form']

            if tax_form.is_valid():
                key = ''
                value = ''
                if request.FILES.get('TIN') is not None:
                    key = 'TIN'
                    value = request.FILES['TIN']
                elif request.POST.get('TIN-clear') is not None:
                    key = 'TIN'
                    value = None
                elif request.FILES.get('work_permit_doc') is not None:
                    key = 'work_permit_doc'
                    value = request.FILES['work_permit_doc']
                elif request.POST.get('work_permit_doc-clear') is not None:
                    key = 'work_permit_doc'
                    value = None
                elif request.FILES.get('signature') is not None:
                    key = 'signature'
                    value = request.FILES['signature']
                elif request.POST.get('signature-clear') is not None:
                    key = 'signature'
                    value = None
                elif request.FILES.get('nid') is not None:
                    key = 'nid'
                    value = request.FILES['nid']
                elif request.POST.get('nid-clear') is not None:
                    key = 'nid'
                    value = None
                elif request.FILES.get('birth_certificate') is not None:
                    key = 'birth_certificate'
                    value = request.FILES['birth_certificate']
                elif request.POST.get('birth_certificate-clear') is not None:
                    key = 'birth_certificate'
                    value = None
                if key != '' and value != '':
                    data, created = emp_models.Personal.objects. \
                        update_or_create(employee_id=self.kwargs['pk'],
                                         defaults={key: value})
                    if created:
                        messages.success(self.request, "Upload documents")
                    else:
                        messages.success(self.request, "Change documents.")

            """
                Appointment letter, resign letter, cover letter upload
            """
            context['document_form'] = self.form_class(request.POST, request.FILES, instance=self.get_document())
            document_form = context['document_form']

            if document_form.is_valid():
                key = ''
                value = ''
                if request.FILES.get('resume') is not None:
                    key = 'resume'
                    value = request.FILES['resume']
                elif request.FILES.get('cover_letter') is not None:
                    key = 'cover_letter'
                    value = request.FILES['cover_letter']
                elif request.FILES.get('appointment_letter') is not None:
                    key = 'appointment_letter'
                    value = request.FILES['appointment_letter']
                elif request.FILES.get('resign_letter') is not None:
                    key = 'resign_letter'
                    value = request.FILES['resign_letter']
                elif request.POST.get('resume-clear') is not None:
                    key = 'resume'
                    value = None
                elif request.POST.get('cover_letter-clear') is not None:
                    key = 'cover_letter'
                    value = None
                elif request.POST.get('appointment_letter-clear') is not None:
                    key = 'appointment_letter'
                    value = None
                elif request.POST.get('resign_letter-clear') is not None:
                    key = 'resign_letter'
                    value = None
                if key != '' and value != '':
                    data, created = emp_models.Documents.objects. \
                        update_or_create(employee_id=self.kwargs['pk'],
                                         defaults={key: value})
                    if created:
                        messages.success(self.request, "Created document")
                    else:
                        messages.success(self.request, "Updated document.")
            return redirect('employees:employee_document', self.kwargs['pk'])
        return render(request, self.template_name, context)
