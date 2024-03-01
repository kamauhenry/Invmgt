from django.db import models
from django.db.models import Model, Sum, F
import pyodbc
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_save
from datetime import *
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, Group
import hashlib

def generate_unique_username():
    # Set a default name or use a constant
    default_name = "user"

    # Combine the name with a random string to ensure uniqueness
    unique_username = f"{default_name}_{get_random_string(length=8)}"

    # Ensure the generated username is unique
    while User.objects.filter(username=unique_username).exists():
        unique_username = f"{default_name}_{get_random_string(length=8)}"

    return unique_username

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, tenant=None, **extra_fields):
        if tenant is None:
            tenant = Tenant.create_for_user(self)
        user = self.model(email=email, tenant=tenant, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, password=None, tenant=None, **extra_fields):
        tenant = Tenant.create_for_user(self)    
        user = self.create_user(email, password=password, tenant=tenant, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    # Add fields specific to your user model
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True)
    objects = CustomUserManager()
    
    class Meta:
        # Add any additional options as needed
        pass


CustomUser._meta.get_field('groups').remote_field.related_name = 'customuser_groups'
CustomUser._meta.get_field('user_permissions').remote_field.related_name = 'customuser_user_permissions'

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    @classmethod
    def create_for_user(cls, user):
        # Automatically create a Tenant instance for the user
        return cls.objects.create(user=user)
    
    def save(self, *args, **kwargs):
        if not self.user:
            unique_username = generate_unique_username()
            self.user = User.objects.create(username=unique_username)
        super().save(*args, **kwargs)



# Define the sqlserverconn model with Subtotal property
class sqlserverconn(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	Item_id = models.BigAutoField(primary_key=True, db_column='Item_id' )
	Item = models.CharField(max_length=30, db_index=True , db_column='Item')
	Item_Description = models.CharField(max_length=30, null=True, blank=True)
	Units =models.DecimalField(max_digits=15, decimal_places=4, default=0)
	Unit_of_measurement = models.CharField(max_length=15, null=True , blank=True )
	Unit_cost =models.DecimalField(max_digits=15, decimal_places=4, default=0)
	Date = models.DateField()
	Subtotal = models.DecimalField(max_digits=15, decimal_places=4, default=0)
	grouped_item = models.ForeignKey(
		'GroupedItems', 
		on_delete=models.CASCADE,
		related_name='sqlserverconns',
		to_field='grouped_item',
	)
	def associate_similar_items(self):
		print("Value of self.Item:", self.Item)
		grouped_item, created = GroupedItems.objects.get_or_create(grouped_item=self.Item)
		
		print("Value of grouped_item:", grouped_item)
		self.grouped_item = grouped_item
		self.save()

	

	def __str__(self):
		return f"{self.Item}"

	
	def save(self, *args, **kwargs):
		self.associate_similar_items()
		self.Subtotal = self.Unit_cost * self.Units
	
		super().save(*args, **kwargs)
		
		self.grouped_item.calculate_totals()
	class Meta:
		indexes = [
			models.Index(fields=['Item'], name='item_idx'),
		]
		

	
class Labour(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	labour_type = models.CharField(max_length=20)
	NOL = models.PositiveIntegerField()
	Date = models.DateField(default=timezone.now)
	#NOL = number of labourers
	labourer_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
	sub_total = models.DecimalField(max_digits=15, decimal_places=4, default=0)
	
	

	def __str__(self):
		return self.labour_type
	
	def save(self, *args, **kwargs):
		self.sub_total = self.labourer_cost * self.NOL
		super(Labour, self).save(*args, **kwargs)	

# Define the GroupedItems model
class GroupedItems(models.Model):
	
	id = models.BigAutoField(primary_key=True)
	grouped_item = models.CharField(max_length=30, unique=True)
	total_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
	total = models.DecimalField(max_digits=15, decimal_places=4, default=0)
	used_units = models.DecimalField(max_digits=15, decimal_places=4, default=0)
	units_available = models.DecimalField(max_digits=15, decimal_places=4, default=0)
	
		
		
	def calculate_totals(self):
		issue_items = self.issue_items.all()
		
	   
		self.used_units = issue_items.aggregate(units_used=Sum('units_used'))['units_used'] or 0
		
	
		
		
		self.units_available = F('total_units')  - F('used_units')
		

		sqlserverconn_aggregate = sqlserverconn.objects.filter(grouped_item=self).aggregate(
			total_units = Sum('Units'),
			total=Sum(F('Subtotal'))
		)
		self.total_units = sqlserverconn_aggregate['total_units'] or 0
		self.total = sqlserverconn_aggregate['total'] or 0
	
		
	
		
		
	def __str__(self):
		return f"{self.grouped_item}"

	def save(self, *args, **kwargs):
		# Get tenant from the related sqlserverconn
		sqlserverconn_instance = sqlserverconn.objects.filter(grouped_item=self.grouped_item).first()
		if sqlserverconn_instance:
			self.tenant = sqlserverconn_instance.tenant
		super().save(*args, **kwargs)

	class Meta:
		indexes = [
			models.Index(fields=['grouped_item', 'total_units'], name='grouped_item_total_units_idx'),
		]
	

class Person(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	person = models.CharField(max_length=20)

	def __str__(self):
		return self.person


class IssueItem(models.Model):
	
	id = models.BigAutoField(primary_key=True)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
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
		self.tenant = self.grouped_item.tenant
		
		self.units_used = self.units_issued - self.units_returned
		self.grouped_item.calculate_totals()
		
		super().save(*args, **kwargs)
		
	def __str__(self):
		return str(self.person) 
	
	

class Custom_UOM(models.Model):
	UOM = models.CharField(max_length=20, primary_key=True)
	
	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
	
	def __str__(self):
		return self.UOM





@receiver(post_save, sender=IssueItem)
@receiver(post_save, sender=sqlserverconn)
def update_totals_on_related_save(sender, instance, **kwargs):
	instance.grouped_item.calculate_totals()


@receiver(post_save, sender=sqlserverconn)
def create_issue_item(sender, instance, **kwargs):
	if sender == sqlserverconn:
		grouped_item, _ = GroupedItems.objects.get_or_create(grouped_item=instance.Item)
		instance.grouped_item = grouped_item
		if instance.pk is None:
			grouped_item.save()


@receiver(post_save, sender=GroupedItems)
def calculate_totals_for_grouped_items(sender, instance, **kwargs):
	if sender == GroupedItems:
		instance.calculate_totals()
	

@receiver(post_save, sender=IssueItem)
def calculate_totals_for_issue_items(sender, instance, **kwargs):
	if sender ==IssueItem:
		instance.grouped_item.calculate_totals()
	


@receiver(post_save, sender=sqlserverconn)
@receiver(post_save, sender=IssueItem)
def calculate_totals(sender, instance, **kwargs):
	if sender ==sqlserverconn:
		
		instance.grouped_item.calculate_totals()
		
	if sender ==IssueItem:
		instance.grouped_item.save()
	
