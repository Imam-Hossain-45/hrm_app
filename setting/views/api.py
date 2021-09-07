from django.http import Http404, JsonResponse
from django.views.generic import View
from setting.models import *


class AjaxMixin(object):
    def dispath(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404('This is an ajax request')
        return super().dispatch(request, *args, **kwargs)


class GetIdentificationJson(AjaxMixin, View):
    def get(self, request, *args, **kwargs):
        company_ids = CompanyIdentification.objects.all()
        company_data = {}
        for company_id in company_ids:
            company_data[str(company_id.identification.id)] = {
                'title': company_id.identification.title,
                'short_description': company_id.identification.short_description
            }

        business_unit_ids = BusinessUnitIdentification.objects.all()
        business_unit_data = {}
        for business_unit_id in business_unit_ids:
            business_unit_data[str(business_unit_id.identification.id)] = {
                'title': business_unit_id.identification.title,
                'short_description': business_unit_id.identification.short_description
            }

        branch_ids = BranchIdentification.objects.all()
        branch_data = {}
        for branch_id in branch_ids:
            branch_data[str(branch_id.identification.id)] = {
                'title': branch_id.identification.title,
                'short_description': branch_id.identification.short_description
            }

        division_ids = DivisionIdentification.objects.all()
        division_data = {}
        for division_id in division_ids:
            division_data[str(division_id.identification.id)] = {
                'title': division_id.identification.title,
                'short_description': division_id.identification.short_description
            }

        department_ids = DepartmentIdentification.objects.all()
        department_data = {}
        for department_id in department_ids:
            department_data[str(department_id.identification.id)] = {
                'title': department_id.identification.title,
                'short_description': department_id.identification.short_description
            }
        data = {'company': company_data, 'business_unit': business_unit_data, 'branch': branch_data,
                'division': division_data, 'department': department_data}

        return JsonResponse(data)
