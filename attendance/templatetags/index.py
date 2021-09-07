from django import template
from setting.models import Countries

register = template.Library()


@register.filter(name='index')
def index(list, i):
    return list[int(i)]


@register.filter(name='split')
def split(value, arg):
    data = value.split(arg)
    dial_code = Countries.objects.get(id=data[0])
    return str(dial_code.dial_code) + str(' ') + str(data[1])


@register.filter(name='get_time_type')
def get_time_type(value):
    if type(value) == str:
        return 'str'
    else:
        return 'datetime.time'


@register.filter(name='get_date_type')
def get_date_type(value):
    if type(value) == str:
        return 'str'
    else:
        return 'datetime.date'
