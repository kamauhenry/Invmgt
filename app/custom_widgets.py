from django import forms
from django.utils.html import format_html


class SelectOrTextInput(forms.Widget):
    def __init__(self, choices, attrs=None):
        self.choices = choices
        self.attrs = attrs or {}

    def render(self, name, value, attrs=None, renderer=None):
        select_attrs = attrs.copy() if attrs else {}
        input_attrs = attrs.copy() if attrs else {}
        select_attrs['class'] = 'form-control'
        input_attrs['class'] = 'form-control'

        # Render a Select widget by default
        select = forms.Select(choices=self.choices)
        select_html = select.render(name, value, attrs=select_attrs, renderer=renderer)

        # Render a TextInput widget with a custom data attribute if 'other' is selected
        if value == 'other':
            input_attrs['data-other'] = 'true'
            input = forms.TextInput()
            input_html = input.render(name, '', attrs=input_attrs, renderer=renderer)
        else:
            input_html = ''

        return select_html + input_html

    def value_from_datadict(self, data, files, name):
        select_value = forms.Select().value_from_datadict(data, files, name)
        text_value = forms.TextInput().value_from_datadict(data, files, name)
        return select_value if select_value != 'other' else text_value
