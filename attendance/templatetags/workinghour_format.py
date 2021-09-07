from django import template

register = template.Library()


@register.filter()
def workinghour_format(value):
    if value:
        data = str(value).split(":")
        return data[0]+"."+data[1]
    return 0.00
