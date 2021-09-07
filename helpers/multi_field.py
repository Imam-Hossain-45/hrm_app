from django import forms


class TestMultiWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.TextInput(attrs=attrs),
            forms.TextInput(attrs=attrs),
        )
        super(TestMultiWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(':::')[0:2]
        return ['', '']


class TestMultiField(forms.MultiValueField):
    widget = TestMultiWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(),
            forms.CharField(),
        )
        super(TestMultiField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ':::'.join(data_list)
        return ''

