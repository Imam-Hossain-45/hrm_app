from django import template
from datetime import datetime

register = template.Library()


@register.filter()
def weekenday(date):
    weeken = datetime.strftime(date, '%A')
    if weeken == "Monday":
        value = int(1)
    elif weeken == 'Tuesday':
        value = int(2)
    elif weeken == 'Wednesday':
        value = int(3)
    elif weeken == 'Thursday':
        value = int(4)
    elif weeken == 'Friday':
        value = int(5)
    elif weeken == 'Saturday':
        value = int(6)
    else:
        value = int(7)

    return value

