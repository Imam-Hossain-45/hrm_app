from django.db import models
from django_countries.fields import CountryField
from helpers.models import Model

STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive')
)

ITEM_CHOICES = (
    ('company', 'Company'),
    ('branch', 'Branch'),
    ('business-unit', 'Business Unit'),
    ('division', 'Division'),
    ('department', 'Department')
)


class PhysicalAddress(Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    state = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, blank=True,
        choices=STATUS_CHOICES,
        default='active'
    )
    address_start_date = models.DateField(blank=True, null=True)
    address_end_date = models.DateField(blank=True, null=True)


class VirtualAddress(Model):
    address_type = models.CharField(max_length=50, blank=True, choices=[
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('website', 'Website'),
        ('fax', 'Fax'),
    ])
    address = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, blank=True,
        choices=STATUS_CHOICES,
        default='active'
    )
    address_start_date = models.DateField(blank=True, null=True)
    address_end_date = models.DateField(blank=True, null=True)


class SocialLink(Model):
    type = models.CharField(max_length=50, blank=True, choices=[
        ('facebook.com', 'facebook.com'),
        ('twitter.com', 'twitter.com'),
        ('instagram.com', 'instagram.com'),
    ])
    link = models.URLField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, blank=True,
        choices=STATUS_CHOICES,
        default='active'
    )
    link_start_date = models.DateField(blank=True, null=True)
    link_end_date = models.DateField(blank=True, null=True)


class Identification(Model):
    different_from_parent = models.BooleanField(default=False, blank=True)
    new_created = models.BooleanField(default=False, blank=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True, null=True)
    document_number = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    attachment_title = models.CharField(max_length=50, blank=True)
    attachment_file = models.ImageField(upload_to='uploads/identifications', blank=True, null=True)
    status = models.CharField(
        max_length=20, blank=True,
        choices=STATUS_CHOICES,
        default='active'
    )
    identification_start_date = models.DateField(blank=True, null=True)
    identification_end_date = models.DateField(blank=True, null=True)


class OrganizationalStructure(Model):
    item = models.CharField(max_length=20, choices=ITEM_CHOICES)
    parent_item = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    order = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.item.replace('-', ' ').capitalize()


class Industry(Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    def __str__(self):
        if self.code:
            return "{} - {}".format(self.code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

    class Meta:
        verbose_name_plural = 'Industries'


class Company(Model):
    OWNERSHIP_TYPE_CHOICE = (
        ('public-limited', 'Public Limited'),
        ('public-limited', 'Joint Venture'),
        ('public-limited', 'Proprietor'),
        ('public-limited', 'Private Limited'),
        ('public-limited', 'Partnership'),
        ('public-limited', 'Others'),
    )

    logo = models.ImageField(upload_to='uploads/companies/', blank=True, null=True)
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100)
    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_TYPE_CHOICE)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True)
    establishment_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mother_company = models.BooleanField(default=False, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    deleted = models.BooleanField(default=False, blank=True)
    company_start_date = models.DateField(blank=True, null=True)
    company_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.short_name:
            return "{} - {}".format(self.short_name.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

    class Meta:
        verbose_name_plural = 'Companies'


class CompanyPhysicalAddress(Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    physical_address = models.ForeignKey(PhysicalAddress, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class CompanyVirtualAddress(Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    virtual_address = models.ForeignKey(VirtualAddress, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class CompanySocialLink(Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    social_link = models.ForeignKey(SocialLink, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class CompanyIdentification(Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    identification = models.ForeignKey(Identification, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class BusinessUnit(Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    parent_item = models.CharField(max_length=50, blank=True, null=True, choices=ITEM_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    business_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey('setting.Branch', on_delete=models.CASCADE, null=True, blank=True)
    division = models.ForeignKey('setting.Division', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey('setting.Department', on_delete=models.CASCADE, null=True, blank=True)
    logo = models.ImageField(upload_to='uploads/business_units/', blank=True, null=True)
    different_physical_address = models.BooleanField(default=False, blank=True)
    different_virtual_address = models.BooleanField(default=False, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    deleted = models.BooleanField(default=False, blank=True)
    business_unit_start_date = models.DateField(blank=True, null=True)
    business_unit_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.code:
            return "{} - {}".format(self.code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

    class Meta:
        verbose_name_plural = 'BusinessUnits'


class BusinessUnitPhysicalAddress(Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    physical_address = models.ForeignKey(PhysicalAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_physical_address = models.ForeignKey(PhysicalAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                   related_name='inherited_phy_add_for_bus')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE,
                                                related_name='business_unit_inherited_phy')
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class BusinessUnitVirtualAddress(Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    virtual_address = models.ForeignKey(VirtualAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_virtual_address = models.ForeignKey(VirtualAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                  related_name='inherited_phy_add_for_bus')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE,
                                                related_name='business_unit_inherited_vir')
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class BusinessUnitSocialLink(Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    social_link = models.ForeignKey(SocialLink, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_social_link = models.ForeignKey(SocialLink, null=True, blank=True, on_delete=models.SET_NULL,
                                              related_name='inherited_social_link_for_bus')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE,
                                                related_name='business_unit_inherited_soc')
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class BusinessUnitIdentification(Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    identification = models.ForeignKey(Identification, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_identification = models.ForeignKey(Identification, null=True, blank=True, on_delete=models.SET_NULL,
                                                 related_name='inherited_identification_for_bus')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE,
                                                related_name='business_unit_inherited_id')
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class Branch(Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    parent_item = models.CharField(max_length=50, blank=True, null=True, choices=ITEM_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    business_unit = models.ForeignKey('setting.BusinessUnit', on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='branch_belongs_to_bu')
    branch = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='branch_belongs_to_branch')
    division = models.ForeignKey('setting.Division', on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='branch_belongs_to_division')
    department = models.ForeignKey('setting.Department', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='branch_belongs_to_department')
    logo = models.ImageField(upload_to='uploads/branches/', blank=True, null=True)
    different_physical_address = models.BooleanField(default=False, blank=True)
    different_virtual_address = models.BooleanField(default=False, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    deleted = models.BooleanField(default=False, blank=True)
    branch_start_date = models.DateField(blank=True, null=True)
    branch_end_date = models.DateField(blank=True, null=True)
    is_head_office = models.BooleanField(
        help_text='Specify whether this branch is a head office',
        default=False,
    )

    def __str__(self):
        if self.code:
            return "{} - {}".format(self.code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

    class Meta:
        verbose_name_plural = 'branches'


class BranchPhysicalAddress(Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    physical_address = models.ForeignKey(PhysicalAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_physical_address = models.ForeignKey(PhysicalAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                   related_name='inherited_phy_add_for_branch')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE,
                                         related_name='branch_inherited_phy')
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class BranchVirtualAddress(Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    virtual_address = models.ForeignKey(VirtualAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_virtual_address = models.ForeignKey(VirtualAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                  related_name='inherited_phy_add_for_branch')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE,
                                         related_name='branch_inherited_vir')
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class BranchSocialLink(Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    social_link = models.ForeignKey(SocialLink, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_social_link = models.ForeignKey(SocialLink, null=True, blank=True, on_delete=models.SET_NULL,
                                              related_name='inherited_social_link_for_branch')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE,
                                         related_name='branch_inherited_soc')
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class BranchIdentification(Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    identification = models.ForeignKey(Identification, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_identification = models.ForeignKey(Identification, null=True, blank=True, on_delete=models.SET_NULL,
                                                 related_name='inherited_identification_for_branch')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE,
                                         related_name='branch_inherited_id')
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class Division(Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    parent_item = models.CharField(max_length=50, blank=True, null=True, choices=ITEM_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='division_belongs_to_bu')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='division_belongs_to_branch')
    division = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='division_belongs_to_division')
    department = models.ForeignKey('setting.Department', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='division_belongs_to_department')
    logo = models.ImageField(upload_to='uploads/divisions/', blank=True, null=True)
    different_physical_address = models.BooleanField(default=False, blank=True)
    different_virtual_address = models.BooleanField(default=False, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    deleted = models.BooleanField(default=False, blank=True)
    division_start_date = models.DateField(blank=True, null=True)
    division_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.code:
            return "{} - {}".format(self.code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

    class Meta:
        verbose_name_plural = 'divisions'


class DivisionPhysicalAddress(Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    physical_address = models.ForeignKey(PhysicalAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_physical_address = models.ForeignKey(PhysicalAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                   related_name='inherited_phy_add_for_division')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE,
                                           related_name='division_inherited_phy')
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class DivisionVirtualAddress(Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    virtual_address = models.ForeignKey(VirtualAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_virtual_address = models.ForeignKey(VirtualAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                  related_name='inherited_phy_add_for_division')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE,
                                           related_name='division_inherited_vir')
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class DivisionSocialLink(Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    social_link = models.ForeignKey(SocialLink, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_social_link = models.ForeignKey(SocialLink, null=True, blank=True, on_delete=models.SET_NULL,
                                              related_name='inherited_social_link_for_division')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE,
                                           related_name='division_inherited_soc')
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class DivisionIdentification(Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    identification = models.ForeignKey(Identification, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_identification = models.ForeignKey(Identification, null=True, blank=True, on_delete=models.SET_NULL,
                                                 related_name='inherited_identification_for_division')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE,
                                           related_name='division_inherited_id')
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


class Department(Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    parent_item = models.CharField(max_length=50, blank=True, null=True, choices=ITEM_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='department_belongs_to_bu')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='department_belongs_to_branch')
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='department_belongs_to_division')
    department = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='department_belongs_to_department')
    logo = models.ImageField(upload_to='uploads/departments/', blank=True, null=True)
    different_physical_address = models.BooleanField(default=False, blank=True)
    different_virtual_address = models.BooleanField(default=False, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    deleted = models.BooleanField(default=False, blank=True)
    department_start_date = models.DateField(blank=True, null=True)
    department_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.code:
            return "{} - {}".format(self.code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)

    class Meta:
        verbose_name_plural = 'departments'


class DepartmentPhysicalAddress(Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    physical_address = models.ForeignKey(PhysicalAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_physical_address = models.ForeignKey(PhysicalAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                   related_name='inherited_phy_add_for_department')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE,
                                             related_name='department_inherited_phy')
    description = models.TextField(blank=True, null=True)


class DepartmentVirtualAddress(Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    virtual_address = models.ForeignKey(VirtualAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_virtual_address = models.ForeignKey(VirtualAddress, null=True, blank=True, on_delete=models.SET_NULL,
                                                  related_name='inherited_phy_add_for_department')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE,
                                             related_name='department_inherited_vir')
    description = models.TextField(blank=True, null=True)


class DepartmentSocialLink(Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    social_link = models.ForeignKey(SocialLink, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_social_link = models.ForeignKey(SocialLink, null=True, blank=True, on_delete=models.SET_NULL,
                                              related_name='inherited_social_link_for_department')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE,
                                             related_name='department_inherited_soc')
    description = models.TextField(blank=True, null=True)


class DepartmentIdentification(Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    identification = models.ForeignKey(Identification, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_identification = models.ForeignKey(Identification, null=True, blank=True, on_delete=models.SET_NULL,
                                                 related_name='inherited_identification_for_department')
    inherited_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey(BusinessUnit, null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE,
                                             related_name='department_inherited_id')
    description = models.TextField(blank=True, null=True)


class Project(Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    project_logo = models.ImageField(upload_to='uploads/projects/', blank=True, null=True)
    belongs_to = models.CharField(max_length=50, blank=True, choices=ITEM_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    different_physical_address = models.BooleanField(default=False, blank=True)
    different_virtual_address = models.BooleanField(default=False, blank=True)
    deleted = models.BooleanField(default=False, blank=True)
    status = models.CharField(
        max_length=20, blank=True,
        choices=STATUS_CHOICES,
        default='active'
    )
    project_start_date = models.DateField(blank=True, null=True)
    project_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        if self.code:
            return "{} - {}".format(self.code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)


class ProjectPhysicalAddress(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    physical_address = models.ForeignKey(PhysicalAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_physical_address = models.ForeignKey(PhysicalAddress, null=True, blank=True, on_delete=models.CASCADE,
                                                   related_name='pro_phy_add_parent')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey('setting.BusinessUnit', null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)


class ProjectVirtualAddress(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    virtual_address = models.ForeignKey(VirtualAddress, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_virtual_address = models.ForeignKey(VirtualAddress, null=True, blank=True, on_delete=models.CASCADE,
                                                  related_name='pro_vir_add_parent')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey('setting.BusinessUnit', null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)


class ProjectSocialLink(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    social_link = models.ForeignKey(SocialLink, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_social_link = models.ForeignKey(SocialLink, null=True, blank=True, on_delete=models.CASCADE,
                                              related_name='pro_soc_link_parent')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey('setting.BusinessUnit', null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)


class ProjectIdentification(Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    identification = models.ForeignKey(Identification, on_delete=models.CASCADE)
    inherited = models.BooleanField(default=False, blank=True)
    inherited_identification = models.ForeignKey(Identification, null=True, blank=True, on_delete=models.CASCADE,
                                                 related_name='pro_id_parent')
    inherited_company = models.ForeignKey('setting.Company', null=True, blank=True, on_delete=models.CASCADE)
    inherited_business_unit = models.ForeignKey('setting.BusinessUnit', null=True, blank=True, on_delete=models.CASCADE)
    inherited_branch = models.ForeignKey('setting.Branch', null=True, blank=True, on_delete=models.CASCADE)
    inherited_division = models.ForeignKey('setting.Division', null=True, blank=True, on_delete=models.CASCADE)
    inherited_department = models.ForeignKey('setting.Department', null=True, blank=True, on_delete=models.CASCADE)


class Designation(Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    short_code = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, blank=True,
        choices=STATUS_CHOICES,
        default='active'
    )

    def __str__(self):
        if self.short_code:
            return "{} - {}".format(self.short_code.upper(), self.name)
        else:
            return "{} - {}".format('', self.name)
