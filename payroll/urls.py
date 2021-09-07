from django.urls import path
from . import views
from leave.views import LeaveEntrySearchView

app_name = 'payroll'

component_patterns = [
    path('master/salary-components/', views.PayrollComponentList.as_view(), name='component_list'),
    path('master/salary-components/create/', views.PayrollComponentCreate.as_view(), name='component_create'),
    path('master/salary-components/<pk>/update/', views.PayrollComponentUpdate.as_view(), name='component_update'),
    path('master/salary-components/<pk>/delete/', views.PayrollComponentDelete.as_view(), name='component_delete'),
]

salary_group_patterns = [
    path('master/salary-group/', views.SalaryGroupList.as_view(), name='salary_group_list'),
    path('master/salary-group/create/', views.SalaryGroupCreate.as_view(), name='salary_group_create'),
    path('master/salary-group/<pk>/update/', views.SalaryGroupUpdate.as_view(), name='salary_group_update'),
    path('master/salary-group/<pk>/delete/', views.SalaryGroupDelete.as_view(), name='salary_group_delete'),
]

salary_group_settings_patterns = [
    path('master/salary-group/<pk>/settings', views.SalaryGroupSettingsList.as_view(),
         name='salary_group_settings_list'),
    path('master/salary-group/<pk>/settings/<pk2>/update', views.SalaryGroupSettingsUpdate.as_view(),
         name='salary_group_settings_update'),
]

deduction_component_patterns = [
    path('master/deduction-components/', views.DeductionComponentList.as_view(), name='deduction_component_list'),
    path('master/deduction-components/create/', views.DeductionComponentCreate.as_view(),
         name='deduction_component_create'),
    path('master/deduction-components/<pk>/update/', views.DeductionComponentUpdate.as_view(),
         name='deduction_component_update'),
    path('master/deduction-components/<pk>/delete/', views.DeductionComponentDelete.as_view(),
         name='deduction_component_delete'),
]

deduction_component_setting_patterns = [
    path('master/deduction-components/<pk>/settings/', views.DeductionComponentSettingRedirect.as_view(),
         name='deduction_component_settings'),
    path('master/deduction-components/<pk>/settings/absent/', views.DeductionAbsentSetting.as_view(),
         name='deduction_absent_settings'),
    path('master/deduction-components/<pk>/settings/late/', views.DeductionLateSetting.as_view(),
         name='deduction_late_settings'),
    path('master/deduction-components/<pk>/settings/early-out/', views.DeductionEarlyOutSetting.as_view(),
         name='deduction_early_out_settings'),
    path('master/deduction-components/<pk>/settings/under-work/', views.DeductionUnderWorkSetting.as_view(),
         name='deduction_under_work_settings'),
]

late_slab_patterns = [
    path('master/deduction-components/<pk>/settings/late/slab/create/', views.LateSlabCreate.as_view(),
         name='late_slab_create'),
    path('master/deduction-components/<pk>/settings/late/slab/<pk2>/update/', views.LateSlabUpdate.as_view(),
         name='late_slab_update'),
    path('master/deduction-components/<pk>/settings/late/slab/<pk2>/delete/', views.LateSlabDelete.as_view(),
         name='late_slab_delete'),
]

early_out_slab_patterns = [
    path('master/deduction-components/<pk>/settings/early-out/slab/create/', views.EarlyOutSlabCreate.as_view(),
         name='early_out_slab_create'),
    path('master/deduction-components/<pk>/settings/early-out/slab/<pk2>/update/', views.EarlyOutSlabUpdate.as_view(),
         name='early_out_slab_update'),
    path('master/deduction-components/<pk>/settings/early-out/slab/<pk2>/delete/', views.EarlyOutSlabDelete.as_view(),
         name='early_out_slab_delete'),
]

under_work_slab_patterns = [
    path('master/deduction-components/<pk>/settings/under-work/slab/create/', views.UnderWorkSlabCreate.as_view(),
         name='under_work_slab_create'),
    path('master/deduction-components/<pk>/settings/under-work/slab/<pk2>/update/', views.UnderWorkSlabUpdate.as_view(),
         name='under_work_slab_update'),
    path('master/deduction-components/<pk>/settings/under-work/slab/<pk2>/delete/', views.UnderWorkSlabDelete.as_view(),
         name='under_work_slab_delete'),
]

deduction_group_patterns = [
    path('master/deduction-groups/', views.DeductionGroupList.as_view(), name='deduction_group_list'),
    path('master/deduction-groups/create/', views.DeductionGroupCreate.as_view(),
         name='deduction_group_create'),
    path('master/deduction-groups/<pk>/update/', views.DeductionGroupUpdate.as_view(),
         name='deduction_group_update'),
    path('master/deduction-groups/<pk>/delete/', views.DeductionGroupDelete.as_view(),
         name='deduction_group_delete'),
]

bonus_component_patterns = [
    path('master/bonus-components/', views.BonusComponentList.as_view(), name='bonus_component_list'),
    path('master/bonus-components/create/', views.BonusComponentCreate.as_view(), name='bonus_component_create'),
    path('master/bonus-components/<pk>/update/', views.BonusComponentUpdate.as_view(), name='bonus_component_update'),
    path('master/bonus-components/<pk>/delete/', views.BonusComponentDelete.as_view(), name='bonus_component_delete'),
]

bonus_group_patterns = [
    path('master/bonus-groups/', views.BonusGroupList.as_view(), name='bonus_group_list'),
    path('master/bonus-groups/create/', views.BonusGroupCreate.as_view(), name='bonus_group_create'),
    path('master/bonus-groups/<pk>/update/', views.BonusGroupUpdate.as_view(), name='bonus_group_update'),
    path('master/bonus-groups/<pk>/delete/', views.BonusGroupDelete.as_view(), name='bonus_group_delete'),
]

bonus_component_settings_patterns = [
    path('master/bonus-components/<pk>/settings/', views.BonusComponentSettingsUpdate.as_view(),
         name='bonus_component_settings'),
]

# Updated

grade_patterns = [
    path('grade/', views.GradeListView.as_view(), name='paygrade_list'),
    path('grade/create/', views.GradeCreateView.as_view(), name='paygrade_create'),
    path('grade/<pk>/update/', views.GradeUpdateView.as_view(), name='paygrade_update'),
    path('grade/<pk>/delete/', views.GradeDeleteView.as_view(), name='paygrade_delete'),
]

# pay_scale_patterns = [
#     path('pay-scale/', views.PayScaleListView.as_view(), name='pay_scale_list'),
#     path('pay-scale/create/', views.PayScaleCreateView.as_view(), name='pay_scale_create'),
#     path('pay-scale/<pk>/update/', views.PayScaleUpdateView.as_view(), name='pay_scale_update'),
#     path('pay-scale/<pk>/delete/', views.PayScaleDeleteView.as_view(), name='pay_scale_delete'),
# ]

# process patterns

payroll_process_patterns = [
    path('process/salary/', views.SalaryProcessGenerate.as_view(), name='salary_process_employee_selection'),
]

payroll_adjustment_patterns = [
    path('process/salary/adjustment/', views.SalaryAdjustmentGenerate.as_view(), name='salary_adjustment'),
    path('process/salary/adjustment/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/salary/adjustment/<pk>/', views.SalaryAdjustmentList.as_view(), name='employee_salary_adjust_list'),
    path('process/salary/confirmation/', views.SalaryConfirmationGenerate.as_view(), name='salary_confirmation'),
    path('process/salary/confirmation/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/salary/disbursement/', views.SalaryDisbursementGenerate.as_view(), name='salary_disbursement'),
    path('process/salary/disbursement/leave_entry_search/', LeaveEntrySearchView.as_view(), name='entry_search_employee'),
    path('process/salary/disbursement/<pk>/details/', views.SalaryDisbursementDetails.as_view(), name='salary_disbursement_details'),
    path('process/salary/disbursement/<pk>/edit/', views.SalaryDisbursementEdit.as_view(), name='salary_disbursement_edit'),
    path('process/salary/disbursement/group/<pk>/', views.SalaryDisbursementGroup.as_view(), name='salary_disbursement_all'),
    path('process/salary/disbursement/<pk>/salary_breakdown/', views.SalaryBreakdownlList.as_view(), name='salary_breakdown_details'),
]

payroll_report_patterns = [
    path('report/payslip/', views.PayslipReportView.as_view(), name='report_payslip'),
    path('report/payslip/leave_entry_search/', LeaveEntrySearchView.as_view(), name='leave_entry_search'),
    path('report/pay-sheet/', views.PaySheetReportView.as_view(), name='report_pay_sheet'),
    path('report/pay-sheet/leave_entry_search/', LeaveEntrySearchView.as_view(), name='leave_entry_search'),
    path('report/pay-suggestions/', views.PaySuggestionsReportView.as_view(), name='report_pay_suggestions'),
    path('report/pay-suggestions/leave_entry_search/', LeaveEntrySearchView.as_view(), name='leave_entry_search'),
]

urlpatterns = component_patterns + salary_group_patterns + salary_group_settings_patterns + \
              deduction_component_patterns + deduction_group_patterns + bonus_component_patterns +\
              bonus_group_patterns + bonus_component_settings_patterns + deduction_component_setting_patterns +\
              late_slab_patterns + early_out_slab_patterns + under_work_slab_patterns + grade_patterns + \
              payroll_process_patterns + payroll_adjustment_patterns + payroll_report_patterns
