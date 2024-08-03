

from urllib import response
from wsgiref import headers
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F
from django.utils.crypto import get_random_string
import json 
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Utility function to generate a unique username
def generate_unique_username():
    """Generates a unique username with a maximum of 10 retries."""
    default_name = "user"
    max_retries = 10

    for _ in range(max_retries):
        unique_username = f"{default_name}_{get_random_string(length=8)}"
        if not CustomUser.objects.filter(username=unique_username).exists():
            return unique_username

    raise ValueError("Failed to generate unique username after %d attempts" % max_retries)

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if extra_fields.get('tenant') is None:
            extra_fields['tenant'] = self.model.objects.create(username=generate_unique_username())

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User model
class CustomUser(AbstractUser):
    tenant = models.OneToOneField('self', on_delete=models.CASCADE, null=True, related_name='tenant_user')
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

# Project Model
class Project(models.Model):
    name = models.CharField(max_length=100)
    project_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_projects')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    project_type = models.CharField(max_length=50, choices=[('residential', 'Residential'), ('commercial', 'Commercial'), ('infrastructure', 'Infrastructure')], blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    building_area = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    number_of_floors = models.PositiveIntegerField(blank=True, null=True)
    materials = models.JSONField(blank=True, null=True)
    building_codes = models.TextField(blank=True)
    site_conditions = models.TextField(blank=True)
    drawings = models.FileField(upload_to='images/', blank=True, null=True)
    project_requirements = models.TextField(blank=True)
    sustainability_considerations = models.TextField(blank=True)
    external_factors = models.TextField(blank=True)
    estimated_completion_time = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated completion time in days")
    required_employees = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated number of employees required")
    detailed_materials_list = models.JSONField(blank=True, help_text="Detailed list of materials including types and quantities")

    def __str__(self):
        return self.name
    
def send_data_to_azure_ai(instance):
    url = ''
    headers = {'content-type': 'application/json'}
    data = {
    'name': instance.name,
    'start_date': instance.start_date.isoformat(),
    'end_date': instance.end_date.isoformat() if instance.end_date else None,
    'project_type': instance.project_type,
    'location': instance.location,
    'description': instance.description,
    'building_area': str(instance.building_area) if instance.building_area else None,
    'number_of_floors': instance.number_of_floors,
    'materials': instance.materials,
    'building_codes': instance.building_codes,
    'site_conditions': instance.site_conditions,
    'project_requirements': instance.project_requirements,
    'sustainability_considerations': instance.sustainability_considerations,
    'external_factors': instance.external_factors,
    'estimated_completion_time': instance.estimated_completion_time,
    'required_employees': instance.required_employees,
    'detailed_materials_list': instance.detailed_materials_list,
    }
    response = requests.post(url, headers=headers, json= data)




def create_pdf_from_json(json_data, pdf_path):
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    text = c.beginText(40, height - 40)
    text.setFont("Helvetica", 12)

    for key, value in json_data.items():
        text.textLine(f"{key}: {value}")

    c.drawText(text)
    c.showPage()
    c.save()


@receiver(pre_save, sender=Project)
def pre_save_project(sender, instance, **kwargs):
    if instance.status == 'pending':
        json_response = send_data_to_azure_ai(instance)
        pdf_path = f'media/project_{instance.id}.pdf'
        create_pdf_from_json(json_response, pdf_path)
        # Optionally store the PDF path in the instance for later retrieval
        instance.pdf_path = pdf_path
        # Raise an exception to prevent the save; the user will review and amend
        raise ValueError("Review the generated PDF before final submission.")
    
# Task Model
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)
    description = models.TextField()
    assigned_to = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    due_date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Employee Model
class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, related_name='employees')
    employee_title = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

# sqlserverconn Model
class sqlserverconn(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sqlserverconns')
    Item_id = models.BigAutoField(primary_key=True, db_column='Item_id')
    Item = models.CharField(max_length=30, db_index=True, db_column='Item')
    Item_Description = models.CharField(max_length=30, null=True, blank=True)
    Units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    Unit_of_measurement = models.CharField(max_length=15, null=True, blank=True)
    Unit_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    Date = models.DateField()
    Subtotal = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    grouped_item = models.ForeignKey(
        'GroupedItems',
        on_delete=models.CASCADE,
        related_name='sqlserverconns',
        to_field='grouped_item',
    )


    def associate_similar_items(self):
        grouped_item, created = GroupedItems.objects.get_or_create(grouped_item=self.Item, project=self.project)
        self.grouped_item = grouped_item
        self.save()

    def __str__(self):
        return self.Item

    def save(self, *args, **kwargs):
        self.associate_similar_items()
        self.Subtotal = self.Unit_cost * self.Units
        super().save(*args, **kwargs)
        self.grouped_item.calculate_totals()

    class Meta:
        indexes = [
            models.Index(fields=['Item'], name='item_idx'),
        ]
        

# GroupedItems Model
class GroupedItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    grouped_item = models.CharField(max_length=30, unique=True)
    total_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    used_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    units_available = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='groupeditems')

    def calculate_totals(self):
        issue_items = self.issue_items.all()
        self.used_units = issue_items.aggregate(units_used=Sum('units_used'))['units_used'] or 0
        self.units_available = F('total_units') - F('used_units')
        
        sqlserverconn_aggregate = sqlserverconn.objects.filter(grouped_item=self).aggregate(
            total_units=Sum('Units'),
            total=Sum(F('Subtotal'))
        )
        self.total_units = sqlserverconn_aggregate['total_units'] or 0
        self.total = sqlserverconn_aggregate['total'] or 0
        self.save()

    def __str__(self):
        return self.grouped_item

    class Meta:
        indexes = [
            models.Index(fields=['grouped_item', 'total_units'], name='grouped_item_total_units_idx'),
        ]

        
class Labour(models.Model):
    Project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labours')
    labour_type = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='labours')
    NOL = models.PositiveIntegerField()
    Date = models.DateField(default=timezone.now)
    labourer_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    sub_total = models.DecimalField(max_digits=15, decimal_places=4, default=0)

    def __str__(self):
        return self.labour_type

    def save(self, *args, **kwargs):
        self.sub_total = self.labourer_cost * self.NOL
        super().save(*args, **kwargs)


# IssueItem Model
class IssueItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Employee, on_delete=models.CASCADE)
    grouped_item = models.ForeignKey(
        GroupedItems,
        on_delete=models.CASCADE,
        related_name='issue_items'
    )
    units_issued = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    units_returned = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    units_used = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    Date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.units_used = self.units_issued - self.units_returned
        super().save(*args, **kwargs)
        self.grouped_item.calculate_totals()

    def __str__(self):
        return str(self.person)
    
    @staticmethod
    def generate_report():
        report_data = []
        issue_items = IssueItem.objects.all().order_by('-Date')

        for item in issue_items:
            report_data.append({
                'person': item.person.user.username,
                'grouped_item': item.grouped_item.grouped_item,
                'units_issued': item.units_issued,
                'units_returned': item.units_returned,
                'units_used': item.units_used,
                'date': item.Date,
            })

        return report_data

class Custom_UOM(models.Model):
    UOM = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.UOM
    
# Signal handlers
@receiver(post_save, sender=IssueItem)
@receiver(post_save, sender=sqlserverconn)
def update_totals_on_related_save(sender, instance, **kwargs):
    instance.grouped_item.calculate_totals()

@receiver(post_save, sender=sqlserverconn)
def create_issue_item(sender, instance, **kwargs):
    grouped_item, _ = GroupedItems.objects.get_or_create(grouped_item=instance.Item, project=instance.project)
    instance.grouped_item = grouped_item
    if instance.pk is None:
        grouped_item.save()
        

@receiver(post_delete, sender=Project)
def delete_related_entries(sender, instance, **kwargs):
    instance.tasks.all().delete()
    instance.sqlserverconns.all().delete()
    instance.groupeditems.all().delete()
    instance.labours.all().delete()
    

@receiver(pre_save, sender=Project)
def pre_save_project(sender, instance, **kwargs):
    if instance.status == 'pending':
        json_response = send_data_to_azure_ai(instance)
        pdf_path = f'media/project_{instance.id}.pdf'
        create_pdf_from_json(json_response, pdf_path)
        # Optionally store the PDF path in the instance for later retrieval
        instance.pdf_path = pdf_path
        # Raise an exception to prevent the save; the user will review and amend
        raise ValueError("Review the generated PDF before final submission.")