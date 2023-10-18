from django.db import models
from django.db.models import Model, Sum, F
import pyodbc
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import pre_save

from datetime import *
from django.utils import timezone


# Define the sqlserverconn model with Subtotal property
class sqlserverconn(models.Model):
	Item_id = models.BigAutoField(primary_key=True, )
	Item = models.CharField(max_length=30, db_index=True)
	Item_Description = models.CharField(max_length=30, null=True, blank=True)
	Units = models.PositiveIntegerField()
	Unit_of_measurement = models.CharField(max_length=15)
	Unit_cost = models.FloatField()
	Date = models.DateField()
	Subtotal = models.FloatField(default=0)
	grouped_item = models.ForeignKey(
		'GroupedItems', 
		on_delete=models.CASCADE,
		related_name='sqlserverconns'
	)
	def associate_similar_items(self):
		grouped_item, created = GroupedItems.objects.get_or_create(grouped_item=self.Item)
		self.grouped_item = grouped_item
		self.save()

	
	def __str__(self):
		return f"{self.Item}"

	
	def save(self, *args, **kwargs):
		self.Subtotal = self.Unit_cost * self.Units
	
		super().save(*args, **kwargs)

	class Meta:
		indexes = [
			models.Index(fields=['Item'], name='item_idx'),
		]
		
@receiver(pre_save, sender=sqlserverconn)
def create_grouped_item(sender, instance, **kwargs):
	
	grouped_item, _ = GroupedItems.objects.get_or_create(grouped_item=instance.Item)
	instance.grouped_item = grouped_item
	if instance.pk is None:
		grouped_item.save()
	
	
	

# Define the GroupedItems model
class GroupedItems(models.Model):
	id = models.BigAutoField(primary_key=True)
	grouped_item = models.CharField(max_length=30, unique=True)
	total_units = models.PositiveIntegerField(default=0)
	total = models.PositiveIntegerField(default=0)
	units_used = models.PositiveIntegerField(default=0)
	units_available = models.PositiveIntegerField(default=0)
	Units_returned = models.PositiveIntegerField(default=0)
	


	def calculate_totals(self):
		issue_items = self.issue_items.all()
	   
		self.units_used = issue_items.aggregate(units_issued=Sum('units_issued'))['units_issued'] or 0

		self.units_available = self.total_units - self.units_used
	
	def function(self):
		sqlserverconn_aggregate = sqlserverconn.objects.filter(grouped_item=self).aggregate(
			total_units=Sum('Units'),
			total=Sum(F('Unit_cost') * F('Units'))
		)
		self.total_units = sqlserverconn_aggregate['total_units'] or 0
		self.total = sqlserverconn_aggregate['total'] or 0
	
		
	def __str__(self):
		return f"{self.grouped_item}"

	def save(self, *args, **kwargs):
		
		super().save(*args, **kwargs)

	class Meta:
		indexes = [
			models.Index(fields=['grouped_item', 'total_units'], name='grouped_item_total_units_idx'),
		]




class IssueItem(models.Model):
	id = models.BigAutoField(primary_key=True)
	person = models.CharField(max_length=20)
	grouped_item = models.ForeignKey(
		GroupedItems,
		on_delete=models.CASCADE,
		related_name='issue_items'
	)
	units_issued = models.PositiveIntegerField(default=0)
	Date = models.DateField(default=timezone.now)

	def save(self, *args, **kwargs):
		self.grouped_item.calculate_totals()
		super().save(*args, **kwargs)



	

@receiver(post_save, sender=sqlserverconn)
def create_issue_item(sender, instance, **kwargs):
	grouped_item, _ = GroupedItems.objects.get_or_create(grouped_item=instance.Item)
	instance.grouped_item = grouped_item
	if instance.pk is None:
		grouped_item.save()


@receiver(post_save, sender=GroupedItems)
def calculate_totals_for_grouped_items(sender, instance, **kwargs):
	instance.calculate_totals()
	instance.function()

@receiver(post_save, sender=IssueItem)
def calculate_totals_for_issue_items(sender, instance, **kwargs):
	instance.grouped_item.calculate_totals()
	


@receiver(post_save, sender=sqlserverconn)
@receiver(post_save, sender=IssueItem)
def calculate_totals(sender, instance, **kwargs):
	grouped_item = instance.grouped_item
	grouped_item.calculate_totals()
	grouped_item.function()
	grouped_item.save()
	
@receiver(post_save, sender=sqlserverconn)
def calculate_totals(sender, instance, **kwargs):
	grouped_item = instance.grouped_item
	grouped_item.calculate_totals()
	grouped_item.function()
	grouped_item.save()



class Custom_UOM(models.Model):
	UOM = models.CharField(max_length=20)
	
	def save(self, *args, **kwargs):
		
		super().save(*args, **kwargs)
	

class return_item(models.Model):
	id = models.BigAutoField(primary_key=True)
	person = models.CharField(max_length=20)
	grouped_item = models.ForeignKey(
		GroupedItems,
		on_delete=models.CASCADE,
		related_name='returned_items'
	)
	units_returned = models.PositiveIntegerField(default=0)
	Date = models.DateField(default=timezone.now)

	def save(self, *args, **kwargs):
		self.grouped_item.calculate_totals()
		super().save(*args, **kwargs)
