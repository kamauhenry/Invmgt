"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _
from .models import *
from django.contrib.auth.models import User
from django.forms import DateInput, ModelForm
from django.utils import timezone
from app.custom_widgets import SelectOrTextInput


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 50 characters or fewer. Letters, digits, and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class SqlServerConnForm(forms.ModelForm): 
    UNIT_CHOICES = (
        ('', 'Select Unit'),  # Blank option
        ('m', 'm'),
        ('ft', 'ft'),
        ('kg', 'kg'),
        ('bag', 'bag'),
        ('pcs', 'pcs'),
        ('trips', 'trips'),
        ('Rolls', 'Rolls'),
        ('fundis', 'fundis'),
        ('contractor', 'contractor'),
        ('litres', 'litres'),
        ('other', 'other'),
        
        
    )

    Item = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    Item_Description = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    Units = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    Unit_of_measurement = forms.ChoiceField(
        choices=UNIT_CHOICES,
        required = False,
        widget= SelectOrTextInput(choices=UNIT_CHOICES, attrs={'class': 'form-control custom-select' , 'id': 'UOM_id'})
    )
    Unit_cost = forms.FloatField(
        widget = forms.NumberInput(attrs={'class': 'form-control'})
    )
    Date = forms.DateField(
        widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    Subtotal = forms.FloatField(
        required=False,
        widget = forms.NumberInput(attrs={'class': 'form-control','readOnly': True})
    )
    class Meta:
        widgets = {'Date': DateInput()}
        model = sqlserverconn
        exclude = ['Subtotal']
        fields = [
            'Item',
            'Item_Description',
            'Units',
            'Unit_of_measurement',
            'Unit_cost',
            'Date',
            
        ]
        
    def clean(self):
        cleaned_data = super().clean()
        
class IssueItemForm(forms.ModelForm):
    Date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now()
    )

    class Meta:
        model = IssueItem
        fields = ['person', 'grouped_item', 'units_issued', 'Date']

    def __init__(self, *args, **kwargs):
        super(IssueItemForm, self).__init__(*args, **kwargs)
        self.fields['grouped_item'].queryset = GroupedItems.objects.all()

    def clean_units_issued(self):
        units_issued = self.cleaned_data.get('units_issued')
        grouped_item = self.cleaned_data.get('grouped_item')

        if units_issued > grouped_item.units_available:
            
            self.errors.pop('units_issued', None)

            raise forms.ValidationError('You have exceeded the number of Units available.')

        return units_issued     
        
class Custom_UOM_form(forms.ModelForm):
    Item = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        Model = Custom_UOM
        
    def __init__(self, *args, **kwargs):
        super(Custom_UOM_form, self).__init__(*args, **kwargs)
 
    