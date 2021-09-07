from django.db import models
from helpers.models import Model
from payroll.models import PayScale, PayGrade, SalaryGroup, DeductionGroup, BonusGroup
from leave.models import LeaveGroup
from accounts.choices import gender_choices, year_choices, current_year
from payroll.models import DeductionGroup


class EmployeeIdentification(Model):
    employee_code = models.CharField(max_length=255, unique=True, null=True)
    title = models.CharField(max_length=255, choices=[('mr', 'Mr.'), ('mrs', 'Mrs.'), ('miss', 'Miss')],
                             null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='accounts/profile_pic/', blank=True, null=True)
    employee_id = models.CharField(max_length=255, unique=True, null=True)
    gender = models.CharField(max_length=20, null=True, choices=gender_choices)

    def __str__(self):
        return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)


class JobInformation(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE,
                                 related_query_name='employee_job_informations',
                                 related_name='employee_job_information', null=True)
    company = models.ForeignKey('setting.Company', on_delete=models.SET_NULL, null=True,
                                limit_choices_to={'status': 'active'})
    business_unit = models.ForeignKey('setting.BusinessUnit', on_delete=models.SET_NULL, null=True, blank=True,
                                      limit_choices_to={'status': 'active'})
    division = models.ForeignKey('setting.Division', blank=True, null=True, on_delete=models.SET_NULL,
                                 limit_choices_to={'status': 'active'})
    department = models.ForeignKey('setting.Department', blank=True, null=True, on_delete=models.SET_NULL,
                                   limit_choices_to={'status': 'active'})
    project = models.ForeignKey('setting.Project', on_delete=models.SET_NULL, null=True, blank=True,
                                limit_choices_to={'status': 'active'})

    designation = models.ForeignKey('setting.Designation', blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name='setting_designation', limit_choices_to={'status': 'active'})
    branch = models.ForeignKey('setting.Branch', blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name='setting_branch', limit_choices_to={'status': 'active'})
    report_to = models.ForeignKey(EmployeeIdentification, blank=True, null=True, on_delete=models.SET_NULL,
                                  related_name='report_to')
    additional_report_to = models.ForeignKey(EmployeeIdentification, blank=True, null=True, on_delete=models.SET_NULL,
                                             related_name='additional_report_to')
    pay_group = models.CharField(max_length=10, blank=True, null=True)
    pay_scale = models.ForeignKey(PayScale, blank=True, null=True, on_delete=models.SET_NULL,
                                  limit_choices_to={'status': True})
    pay_grade = models.ForeignKey(PayGrade, blank=True, null=True, on_delete=models.SET_NULL,
                                  limit_choices_to={'status': True})
    job_status = models.ForeignKey('setting.JobStatus', blank=True, null=True, on_delete=models.SET_NULL,
                                   limit_choices_to={'status': True})
    employment_type = models.ForeignKey('setting.EmploymentType', blank=True, null=True, on_delete=models.SET_NULL,
                                        limit_choices_to={'status': True})
    date_of_offer = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(null=True)
    status = models.BooleanField(default=True, blank=True)

    class Meta:
        get_latest_by = ['updated_at']


class Employment(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, related_query_name='employments',
                                 related_name='employment', null=True)
    confirmation_after = models.IntegerField(blank=True, null=True)
    confirmation_after_unit = models.CharField(max_length=10,
                                               choices=[('days', 'Days'), ('months', 'Months'), ('years', 'Years')],
                                               blank=True, null=True)
    confirmation_date = models.DateField(null=True, blank=True)
    date_of_actual_confirmation = models.DateField(null=True, blank=True)


class EndOfContract(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True, blank=True)
    due_on = models.DateField(null=True, blank=True)
    date_of_settlement = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)


class Separation(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    type_of_resign = models.CharField(max_length=50, choices=[('sack', 'Sack'), ('resign', 'Resign'),
                                                              ('accidental_separation', 'Accidental Separation')],
                                      default='sack')
    date_of_sack = models.DateField(blank=True, null=True)
    date_of_resign = models.DateField(blank=True, null=True)
    date_of_settlement = models.DateField(blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)


class Retirement(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    due_on = models.DateField(blank=True, null=True)
    date_of_settlement = models.DateField(blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)


class Payment(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True,
                                 related_name='employee_payment')
    payment_mode = models.CharField(max_length=20, choices=[('bank', 'Bank'), ('cash', 'Cash'), ('cheque', 'Cheque')],
                                    default='Bank')
    pay_schedule = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('weekly', 'Weekly')],
                                    default='monthly')
    employee_bank_name = models.ForeignKey('setting.Bank', on_delete=models.SET_NULL, blank=True, null=True,
                                           limit_choices_to={'status': 'active'})
    employee_bank_AC_name = models.CharField(max_length=255, blank=True, null=True,
                                             verbose_name='Employee Bank A/C Name')
    bank_branch_code = models.CharField(max_length=255, blank=True, null=True)
    bank_AC_no = models.IntegerField(blank=True, null=True, verbose_name='Bank A/C No')
    routing_number = models.CharField(max_length=255, blank=True, null=True)


class SalaryStructure(Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive')
    )

    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True,
                                 related_name='employee_salary_structure')
    salary_group = models.ForeignKey(SalaryGroup, null=True, on_delete=models.SET_NULL,
                                     limit_choices_to={'status': 'active'})
    bonus_group = models.ForeignKey(BonusGroup, blank=True, null=True, on_delete=models.SET_NULL,
                                    limit_choices_to={'status': True})
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    from_date = models.DateField()
    to_date = models.DateField(blank=True, null=True)
    reason_of_salary_modification = models.TextField(blank=True, null=True)


class Personal(Model):
    RELIGION_CHOICES = [
        ('', '-------'),
        ('Islam', 'Islam'),
        ('Hinduism', 'Hinduism'),
        ('Christianity', 'Christianity'),
        ('Buddhism', 'Buddhism'),
        ('Other', 'Other')
    ]
    BLOOD_GROUP_CHOICES = [
        ('', '-------'),
        ('A+', 'A+'),
        ('O+', 'O+'),
        ('B+', 'B+'),
        ('AB+', 'AB+'),
        ('A-', 'A-'),
        ('O-', 'O-'),
        ('B-', 'B-'),
        ('AB-', 'AB-'),
    ]
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True,
                                 related_name='personal_employee')
    date_of_birth = models.DateField(null=True)
    place_of_birth = models.ForeignKey('setting.Countries', on_delete=models.SET_NULL, null=True, blank=True)
    birth_certificate = models.FileField(upload_to='accounts/birth_certificate/', blank=True, null=True)
    nationality = models.CharField(max_length=255, null=True)
    passport_number = models.IntegerField(blank=True, null=True)
    nid_or_ssn_number = models.IntegerField(blank=True, null=True, verbose_name='NID/SSN Number')
    passport_expiry_date = models.DateField(blank=True, null=True)
    nid = models.FileField(upload_to='accounts/nid_pic/', blank=True, null=True, verbose_name='NID')
    passport = models.FileField(upload_to='accounts/passport_pic/', blank=True, null=True)
    tin_number = models.IntegerField(blank=True, null=True, verbose_name='TIN Number')
    TIN = models.FileField(upload_to='accounts/tin_pic/', blank=True, null=True)
    visa_type = models.CharField(max_length=10, blank=True, null=True)
    visa_number = models.IntegerField(blank=True, null=True)
    work_permit_no = models.IntegerField(blank=True, null=True)
    work_permit_expiry_date = models.DateField(blank=True, null=True)
    work_permit_doc = models.FileField(upload_to='accounts/work_permit_pic/', blank=True, null=True)
    driving_licence_no = models.IntegerField(blank=True, null=True)
    driving_licence_expiry_date = models.DateField(blank=True, null=True)
    driving_licence_doc = models.FileField(upload_to='accounts/driving_licence_pic/', blank=True, null=True)

    mothers_name = models.CharField(max_length=255, blank=True, null=True)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=[('married', 'Married'), ('unmarried', 'Unmarried')],
                                      default='married')
    spouse_name = models.CharField(max_length=255, blank=True, null=True)
    no_of_child = models.IntegerField(default=0, blank=True, null=True)
    height_ft = models.IntegerField(blank=True, null=True, verbose_name='Height')
    height_in = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    weight_unit = models.CharField(max_length=10, choices=[('kg', 'kg'), ('gm', 'gm')], default='kg',
                                   null=True)
    blood_group = models.CharField(max_length=20, blank=True, choices=BLOOD_GROUP_CHOICES, default='')
    identification_mark = models.CharField(max_length=255, blank=True, null=True)
    religion = models.CharField(max_length=20, blank=True, choices=RELIGION_CHOICES, default='')
    caste = models.CharField(max_length=255, blank=True, null=True)
    mother_tongue = models.CharField(max_length=255, blank=True, null=True)
    police_station_address = models.TextField(blank=True, null=True)
    fingerprint = models.FileField(upload_to='accounts/fingerprint/', blank=True, null=True)
    signature = models.FileField(upload_to='accounts/signature/', blank=True, null=True)

    preferred_food = models.TextField(blank=True, null=True)
    hobby = models.TextField(blank=True, null=True)


class AddressAndContact(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    official_cell_number = models.CharField(max_length=100, null=True)
    personal_cell_number = models.CharField(max_length=100, null=True)
    official_email_ID = models.EmailField(blank=True, null=True)
    personal_email_ID = models.EmailField(blank=True, null=True)

    present_address = models.TextField(verbose_name='Address Line', null=True)
    present_country = models.ForeignKey('setting.Countries', on_delete=models.SET_NULL, null=True,
                                        verbose_name='Country', related_name='prensent_country')
    present_state = models.ForeignKey('setting.States', on_delete=models.SET_NULL, null=True, verbose_name='State',
                                      related_name='prensent_state')
    present_city = models.ForeignKey('setting.Cities', on_delete=models.SET_NULL, null=True, verbose_name='City',
                                     related_name='prensent_city')
    present_thana = models.CharField(max_length=255, null=True, blank=True, verbose_name='Thana')
    present_postal_code = models.IntegerField(blank=True, null=True, verbose_name='Postal Code')
    present_contact_person = models.CharField(max_length=255, blank=True, null=True, verbose_name='Contact Person')
    present_phone_number = models.CharField(max_length=100, null=True, verbose_name='Phone Number')
    permanent_address = models.TextField(verbose_name='Address Line', null=True, blank=True)

    permanent_country = models.ForeignKey('setting.Countries', on_delete=models.SET_NULL, null=True,
                                          verbose_name='Country', related_name='permanent_country', blank=True)
    permanent_city = models.ForeignKey('setting.Cities', on_delete=models.SET_NULL, null=True, verbose_name='City',
                                       related_name='permanent_city', blank=True)
    permanent_state = models.ForeignKey('setting.States', on_delete=models.SET_NULL, null=True, verbose_name='State',
                                        related_name='permanent_state', blank=True)
    permanent_thana = models.CharField(max_length=255, blank=True, null=True, verbose_name='Thana')
    permanent_postal_code = models.IntegerField(blank=True, null=True, verbose_name='Postal Code')
    permanent_contact_person = models.TextField(blank=True, null=True, verbose_name='Contact Person')
    permanent_phone_number = models.CharField(max_length=100, verbose_name='Phone Number', blank=True, null=True)


class EmergencyContact(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)


class Family(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    name_of_family_member = models.CharField(max_length=255)
    relationship_with_employee = models.CharField(max_length=255)
    DOB = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=20, null=True, choices=gender_choices)
    employed = models.NullBooleanField(default=True)
    dependent = models.NullBooleanField(default=True)


class Education(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    degree = models.CharField(max_length=255, null=True)
    university = models.CharField(max_length=255, verbose_name='University/College/School/Institute', null=True)
    subject = models.CharField(max_length=255, verbose_name='Discipline/Subject', null=True)
    year_of_completion = models.IntegerField(choices=year_choices(), default=current_year, null=True)
    result_type = models.CharField(max_length=10, choices=[('CGPA', 'CGPA'), ('GPA', 'GPA'), ('division', 'Division')],
                                   default='CGPA')
    result_of_gpa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Result')
    out_of = models.CharField(max_length=10, choices=[('4.0', '4.0'), ('5.0', '5.0')], null=True, blank=True)
    result_of_division = models.CharField(max_length=10, choices=[('1st', '1st'), ('2nd', '2nd'), ('3rd', '3rd')],
                                          blank=True, null=True, verbose_name='Result')
    grade = models.CharField(max_length=5,
                             choices=[('A+', 'A+'), ('A', 'A'), ('A-', 'A-'), ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
                                      ('C+', 'C+'), ('C', 'C'), ('D', 'D'), ('F', 'F')], blank=True, null=True)
    marks = models.IntegerField(blank=True, null=True)
    certificate = models.FileField(upload_to='accounts/certificate/', blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'degree')


class Skill(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    skill_name = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    skill_level = models.CharField(max_length=255, null=True,
                                   choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'),
                                            ('developing', 'Developing'), ('expert', 'Expert')], default='beginner')

    class Meta:
        unique_together = ('employee', 'skill_name')


class Training(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    training_title = models.CharField(max_length=255, null=True)
    country = models.ForeignKey('setting.Countries', on_delete=models.SET_NULL, null=True, blank=True)
    training_year = models.IntegerField(choices=year_choices(), default=current_year, null=True)
    institute = models.CharField(max_length=255, null=True)
    duration = models.IntegerField(null=True)
    duration_unit = models.CharField(max_length=10,
                                     choices=[('hours', 'Hours'), ('day', 'Day'), ('month', 'Month'), ('year', 'Year')],
                                     default='hours')
    certificate = models.FileField(upload_to='accounts/certificate/', blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'training_title')


class ProfessionalCertificate(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    certificate_title = models.CharField(max_length=255, null=True)
    country = models.ForeignKey('setting.Countries', on_delete=models.SET_NULL, null=True, blank=True)
    institute = models.CharField(max_length=255, null=True)
    institute_address = models.TextField(blank=True, null=True)
    duration = models.IntegerField(null=True)
    duration_unit = models.CharField(max_length=10, choices=[('day', 'Day'), ('month', 'Month'), ('year', 'Year')],
                                     default='day')
    certificate = models.FileField(upload_to='accounts/certificate/', blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'certificate_title')


class LanguageProficiency(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    language = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    read = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    write = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    speak = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], default='yes')

    class Meta:
        unique_together = ('employee', 'language')


class EmploymentHistory(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    organization = models.CharField(max_length=255, null=True)
    designation = models.CharField(max_length=255, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    start_from = models.DateField(verbose_name='From', null=True)
    to = models.DateField(null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salary (Gross)', null=True, blank=True)


class Reference(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    ref_person_name = models.CharField(max_length=255, verbose_name='Ref. Person Name', null=True)
    relationship = models.CharField(max_length=255, null=True)
    designation = models.CharField(max_length=255, null=True)
    official_cell_number = models.CharField(max_length=255, verbose_name='Cell Number (Official)', null=True)
    personal_cell_number = models.CharField(max_length=255, verbose_name='Cell Number (Personal)', null=True,
                                            blank=True)
    official_email = models.EmailField(verbose_name='Email Address (Official)', null=True)
    personal_email = models.EmailField(verbose_name='Email Address (Personal)', null=True, blank=True)
    organization_name = models.CharField(max_length=255)
    address_line = models.TextField(null=True)
    country = models.ForeignKey('setting.Countries', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('setting.Cities', on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey('setting.States', on_delete=models.SET_NULL, null=True, blank=True)
    thana = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.IntegerField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True, verbose_name='Contact Person Name')
    phone_number = models.CharField(max_length=100, null=True)


class Asset(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    asset_category = models.CharField(max_length=255, null=True)
    asset_brand_name = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    serial_number = models.CharField(max_length=255, null=True)
    date_loaned = models.DateField(null=True)
    date_returned = models.DateField(null=True)


class Documents(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    resume = models.FileField(upload_to='accounts/resume/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='accounts/cover_letter/', blank=True, null=True)
    appointment_letter = models.FileField(upload_to='accounts/appointment_letter/', blank=True, null=True)
    resign_letter = models.FileField(upload_to='accounts/resign_letter/', blank=True, null=True)


class OthersDocuments(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, null=True)
    file = models.FileField(upload_to='accounts/others_documents/', blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'title')


class Attendance(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True,
                                 related_name='employee_attendance')
    schedule_type = models.ForeignKey('attendance.ScheduleMaster', on_delete=models.SET_NULL, null=True, blank=True,
                                      limit_choices_to={'status': True})
    punching_id = models.CharField(max_length=100, verbose_name='Punching ID', blank=True, null=True)
    calendar_master = models.ForeignKey('attendance.CalendarMaster', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='employee_calendar', verbose_name='Calendar',
                                        limit_choices_to={'status': True})


class LeaveManage(Model):
    employee = models.ForeignKey(EmployeeIdentification, on_delete=models.CASCADE, null=True)
    leave_group = models.ForeignKey(LeaveGroup, on_delete=models.SET_NULL, null=True, blank=True,
                                    limit_choices_to={'status': True})
    overtime = models.BooleanField(default=False)
    overtime_group = models.ForeignKey('attendance.OvertimeRule', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='employee_overtime', verbose_name='Select Overtime')
    deduction = models.BooleanField(default=False)
    deduction_group = models.ForeignKey(DeductionGroup, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='employee_leave_deduction', limit_choices_to={'status': 'active'})
