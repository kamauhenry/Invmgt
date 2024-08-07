

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
from django.conf import settings



# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):


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
  
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

# Project Model
class Project(models.Model):
    name = models.CharField(max_length=100)
    project_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    project_type = models.CharField(max_length=50, choices=[('residential', 'Residential'), ('commercial', 'Commercial'), ('infrastructure', 'Infrastructure')], blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    building_area = models.DecimalField(max_digits=15, decimal_places=4, null=True, blank=True)
    number_of_floors = models.PositiveIntegerField(blank=True, null=True)
    materials = models.TextField(blank=True, null=True)
    building_codes = models.TextField(blank=True)
    site_conditions = models.TextField(blank=True)
    drawings = models.FileField(upload_to='images/', blank=True, null=True)
    project_requirements = models.TextField(blank=True)
    sustainability_considerations = models.TextField(blank=True)
    external_factors = models.TextField(blank=True)
    estimated_completion_time = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated completion time in days")
    required_employees = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated number of employees required")
    detailed_materials_list = models.TextField(blank=True, help_text="Detailed list of materials including types and quantities")

    def __str__(self):
        return self.name
    



    
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
        return self.employee_title

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
        

    def __str__(self):
        return self.Item

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is being created for the first time
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labours')
    labour_type = models.CharField(max_length=30)
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

# Signal handlers
@receiver(post_save, sender=sqlserverconn)
def create_issue_item(sender, instance, **kwargs):
    if not instance.grouped_item_id:
        grouped_item, _ = GroupedItems.objects.get_or_create(grouped_item=instance.Item, project=instance.project)
        instance.grouped_item = grouped_item
        instance.save()
        

@receiver(post_delete, sender=Project)
def delete_related_entries(sender, instance, **kwargs):
    instance.tasks.all().delete()
    instance.sqlserverconns.all().delete()
    instance.groupeditems.all().delete()
    instance.labours.all().delete()
    
