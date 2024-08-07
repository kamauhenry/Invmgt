"""
Definition of forms.
"""

from msilib.schema import CustomAction
from pyexpat import model
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
        model = CustomUser
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
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
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
    Unit_of_measurement = forms.ModelChoiceField(
        queryset=Custom_UOM.objects.all().order_by('UOM'),
        empty_label='Select Unit',
        widget=forms.Select(attrs={'class': 'form-control custom-select', 'id': 'UOM_id'})
    )
    Unit_cost = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    Date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    Subtotal = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readOnly': True})
    )

    class Meta:
        model = sqlserverconn
        exclude = ['Subtotal']
        fields = [
            'project',
            'Item',
            'Item_Description',
            'Units',
            'Unit_of_measurement',
            'Unit_cost',
            'Date',
        ]

    def clean(self):
        cleaned_data = super().clean()
        # Additional cleaning can be performed here if needed
        return cleaned_data
       
        
 
    
class IssueItemForm(forms.ModelForm):
    Date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now()
    )
    
    
    class Meta:
        model = IssueItem
        fields = ['person', 'grouped_item', 'units_issued','units_returned', 'Date']

    def __init__(self, *args, **kwargs):
        super(IssueItemForm, self).__init__(*args, **kwargs)
        self.fields['grouped_item'].queryset = GroupedItems.objects.all()

        
class Custom_UOM_form(forms.ModelForm):
    UOM  = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Custom_UOM
        fields = ['UOM']
        
    def __init__(self, *args, **kwargs):
        super(Custom_UOM_form, self).__init__(*args, **kwargs)
 
class Personform(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    employee_title = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(), #t with an empty queryset
        widget=forms.Select(attrs={'class': 'form-control'}) # Hide this field from the form
    )

    class Meta:
        model = Employee
        fields = ['employee_title', 'project', 'user']
        
    def __init__(self, *args, **kwargs):
        super(Personform, self).__init__(*args, **kwargs)

class LabourForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='project',
    )

    Date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now()
    )


    labour_type = forms.ChoiceField(
        choices=[(title, title) for title in Employee.objects.values_list('employee_title', flat=True).distinct()] or [('None', 'No Titles Available')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    NOL = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )

    labourer_cost = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )


    class Meta:
        model = Labour
        fields = ['labour_type', 'NOL', 'Date', 'labourer_cost', 'project'] 

class DateForm(forms.Form):
    start = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}))
    


class CreateProjectForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now()
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now(),
        required=False  # End date might not be available at the time of form creation
    )
    name = forms.CharField(
        max_length=60,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    project_owner = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),  # Populate with all CustomUser instances
        widget=forms.Select(attrs={'class': 'form-control'})  # Use the default select widget
    )
    project_type = forms.ChoiceField(
        choices=[('residential', 'Residential'), ('commercial', 'Commercial'), ('infrastructure', 'Infrastructure')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=450,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        max_length=450,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    building_area = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        max_digits=15, decimal_places=4
    )
    number_of_floors = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    materials = forms.CharField(
        max_length=450,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    building_codes = forms.CharField(
        max_length=40,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    site_conditions = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    drawings = forms.URLField(
        max_length=40,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=False
    )
    project_requirements = forms.CharField(
        max_length=450,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    sustainability_considerations = forms.CharField(
        max_length=450,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    external_factors = forms.CharField(
        max_length=450,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    estimated_completion_time = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    required_employees = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    detailed_materials_list = forms.CharField(
        max_length=450,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'name',
            'project_owner',
            'start_date',
            'end_date',
            'project_type',
            'location',
            'description',
            'building_area',
            'number_of_floors',
            'materials',
            'building_codes',
            'site_conditions',
            'drawings',
            'project_requirements',
            'sustainability_considerations',
            'external_factors',
            'estimated_completion_time',
            'required_employees',
            'detailed_materials_list',
        ]

    def __init__(self, *args, **kwargs):
        # Extract the current user from kwargs
        current_user = kwargs.pop('current_user', None)
        super(CreateProjectForm, self).__init__(*args, **kwargs)

        # Set the project_owner field to the current user
        if current_user:
            self.fields['project_owner'].queryset = CustomUser.objects.filter(id=current_user.id)
            self.fields['project_owner'].initial = current_user

    def save(self, commit=True):
        # Ensure project_owner is set to the current user
        instance = super().save(commit=False)
        if not self.instance.project_owner and self.fields['project_owner'].initial:
            instance.project_owner = self.fields['project_owner'].initial
        if commit:
            instance.save()
        return instance




class CreateTaskForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    assigned_to = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now()
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now()
    )
    completed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Task
        fields = [
            'project',
            'name',
            'description',
            'assigned_to',
            'start_date',
            'due_date',
            'completed'
        ]

    def __init__(self, *args, **kwargs):
        super(CreateTaskForm, self).__init__(*args, **kwargs)