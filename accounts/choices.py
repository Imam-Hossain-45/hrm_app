import datetime


def year_choices():
    return [(r, r) for r in range(1984, datetime.date.today().year + 1)]


def current_year():
    return datetime.date.today().year


gender_choices = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

user_type_choices = (
    ('', '-------'),
    ('Admin', 'Admin'),
    ('Employee', 'Employee'),
)
