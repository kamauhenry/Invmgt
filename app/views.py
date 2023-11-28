"""
Definition of views.
"""
from calendar import month
from re import L
from unittest import result
from django.contrib.auth.decorators import login_required
from os import system
from datetime import datetime
from django.core import paginator
from django.shortcuts import render
from django.http import HttpRequest, HttpRequest
from numpy import datetime_as_string
import pyodbc
from app.forms import  *
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import *
import plotly.express as px
from django.contrib.auth import authenticate, login , logout 
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.core.paginator import Page, Paginator
from django.http import HttpResponseRedirect
import pandas as pd 
from django.db.models.functions import TruncMonth
from rest_framework import viewsets
from app.serializers import *

item_units_used = {}

def connsql(request):
	conn=pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};'
					  'Server=JAYDEN;'
					  'Database=fpwdb;'
					  'UID=sa;'
					  'PWD=yrenhke;'
					  'Trusted_Connnection=yes;'
					  'encrypt=no;'  
					  )
	cursor=conn.cursor()
	cursor.execute()
	result=cursor.fetchall()
	print(result)
	return render(request,'index.html',{'sqlserverconn':result})



@login_required
def home(request):
	"""Renders the home page."""
	sqlserverconns = sqlserverconn.objects.order_by('-Date')  
	 
	paginator = Paginator(sqlserverconns, 15)
	page_number = request.GET.get('page')
	page_object = Paginator.get_page(paginator, page_number)
	
	total_records = len(sqlserverconns)
	
	context = {
		'sqlserverconns': sqlserverconns,
		'page_object' : page_object,
		'total_records' : total_records
		} 
	assert isinstance(request, HttpRequest)
	return render(
		request,
		'app/index.html',
		{
			'title': 'Home Page',
			'year': datetime.now().year,
			**context 
		}
	)

@login_required
def return_item_view(request, pk):
	record = IssueItem.objects.get( id = pk )
	return_form = IssueItemForm(request.POST or None, instance = record)
	
	if request.method == 'POST':
		if return_form.is_valid():
			return_form.save()
			messages.success(request, "Record Has Been Updated! ")
			return redirect('issue_item')
		
	return render(request, 'app/return_item.html', {'return_form': return_form})




@login_required
def inventory(request):
	"""Renders the contact page."""
	form = SqlServerConnForm(request.POST or None, request.FILES or None)
	Custom_uom_form = Custom_UOM_form(request.POST or None, request.FILES or None)
	assert isinstance(request, HttpRequest)
	return render(
		request,
		'app/inventory.html',
		{
			'title':'Contact',
			'message':'Your contact page.',
			'year':datetime.now().year,
			'form': form,
			'Custom_uom_form': Custom_uom_form
		}
	)

def add_custom_uom(request):
	Custom_uom_form = Custom_UOM_form(request.POST or None)
	if request.user.is_authenticated:
		if request.method == "POST":
			if Custom_uom_form.is_valid():
				add_custom_uom = Custom_uom_form.save()
				messages.success(request, "Record Added...")
				

				return redirect('app/inventory.html')
		return render(request, 'app/CustomUOM.html', {'Custom_uom_form':Custom_uom_form})
	else:
		messages.success(request, "You Must Be Logged In...") 
	

def add_Person(request):
	

	people = Person.objects.all()
	Person_form = Personform(request.POST or None)
	if request.user.is_authenticated:
		if request.method == "POST":
			if Person_form.is_valid():
				add_Person = Person_form.save()
				messages.success(request, "Record Added...")
				

				return redirect('issue_item_view')
		return render(request, 'app/person.html', {
			'Person_form':Person_form,
			'people':people	}
				)
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('issue_item_view')

def add_record(request):
	form = SqlServerConnForm(request.POST or None)
	if request.user.is_authenticated:
		if request.method == "POST":
			if form.is_valid():
				add_record = form.save()
				messages.success(request, "Record Added...")
				

				return redirect('home')
		return render(request, 'inventory.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('home')
	
@login_required
def update_record(request, pk):
	if request.user.is_authenticated:
		current_record = sqlserverconn.objects.get(Item_id=pk)
		form = SqlServerConnForm(request.POST or None, instance=current_record)
		if form.is_valid():
			form.save()
			messages.success(request, "Record Has Been Updated!")
			return redirect('home')
		return render(request, 'app/update_record.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('home')
	
def delete_record(request, pk):
	if request.user.is_authenticated:
		try:
			delete_it = sqlserverconn.objects.get(Item_id=pk)
			delete_it.delete()
			messages.success(request, 'Record deleted')
		except sqlserverconn.DoesNotExist:
			messages.error(request, 'Record not found')
		
		return redirect('home')
	else:
		messages.success(request, 'You must be logged in')
		return redirect('home')
	



	
def loginView(request):
	if request.method =='POST':
		username = request.POST['username']
		password = request.POST['password']
		
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request,"You Have Been Logged in")
			return redirect('home')
		else:
			messages.success(request, "Error")
			return redirect('home')
	else:
		return render(request, 'index.html')
	
def labourers_view(request):
	form = LabourForm(request.POST or None)
	labourers = Labour.objects.order_by('-Date')
	if request.method == 'POST' and form.is_valid():
		labour = form.save()
		
		messages.success(request, "record added successfully !")
		return redirect ('labourers_view')
	total_amount= Labour.objects.aggregate(total_amount=Sum('sub_total'))['total_amount']
	
	paginator = Paginator(labourers, 8)
	page_number = request.GET.get('page')
	page_object1 = Paginator.get_page(paginator, page_number)
	total_records = len(labourers)

	return render ( request,
		   'app/labourers.html',
		   {'form': form,
			'labourers': labourers,	
			'total_amount': total_amount,
			'page_object1': page_object1,
			'total_records': total_records
	  })


def setup(request):
	form = Custom_UOM_form(request.POST or None)

	labourers = Labour.objects.order_by('-Date')
	if request.method == 'POST' and form.is_valid():
		labour = form.save()
		
		messages.success(request, "record added successfully !")
		return redirect ('setup')
	

	return render ( request,
		   'app/setup.html',
		   {'form': form
			
	  })

def delete_labourer(request, pk):
	if request.user.is_authenticated:
		try:
			delete_it = Labour.objects.get(id=pk)
			delete_it.delete()
			messages.success(request, 'Record deleted')
		except Labour.DoesNotExist:
			messages.error(request, 'Record not found')
		
		return redirect('labourers_view')
	else:
		messages.success(request, 'You must be logged in')
		return redirect('labourers_view')
	
def update_labourer(request, pk):
	if request.user.is_authenticated:
		current_record = Labour.objects.get(id=pk)
		form = LabourForm(request.POST or None, instance=current_record)
		if form.is_valid():
			form.save()
			messages.success(request, "Record Has Been Updated!")
			return redirect('labourers_view')
		return render(request, 'app/update_labourer.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In...")
		return redirect('labourers_view')

def register_user(request):
	form = SignUpForm(request.POST or None)

	if request.method == 'POST' and form.is_valid():
		user = form.save()
		messages.success(request, "User has been successfully registered!")
		return redirect('reg_user')

	return render(request, 'app/reg_user.html', {'form': form})

@login_required
def grouped_itemsv(request):
	search_query = request.GET.get('q', '')

	# Group by 'Item' field and calculate total quantity and subtotal for each group
	grouped_items = sqlserverconn.objects.values('Item').annotate(
		total_units=Sum('Units'),
		total=Sum('Subtotal'),
		)
	total_amount= sqlserverconn.objects.aggregate(total_amount=Sum('Subtotal'))['total_amount']
	
	if search_query:
		grouped_items = grouped_items.filter(Item__icontains=search_query)

	# Get the filtered records for each grouped item
	records_by_item = {}
	for item in grouped_items:
		records = sqlserverconn.objects.filter(Item=item['Item'])
		records_by_item[item['Item']] = records
		
	paginator = Paginator(grouped_items, 8)
	page_number = request.GET.get('page')
	page_object2 = Paginator.get_page(paginator, page_number)

	return render(request, 'app/grouped_items.html',  {
		
		'grouped_items': grouped_items,
		'search_query': search_query,
		'records_by_item': records_by_item,
		'total_amount': total_amount,
		'page_object2' : page_object2
	})



def issue_item_view(request):
	search_query = request.GET.get('q', '')

	grouped_items = GroupedItems.objects.all()
	issue_items = IssueItem.objects.all()
	issue_item_form = IssueItemForm(request.POST or None)
	if search_query:
		
		grouped_items = grouped_items.filter(grouped_item__icontains=search_query)
		
	if request.method == 'POST':
		issue_item_form = IssueItemForm(request.POST)
		if issue_item_form.is_valid():
			issue_item = issue_item_form.save(commit=False)  # Create an unsaved instance
			# Associate the selected grouped_item with the issue_item
			issue_item.grouped_item = issue_item_form.cleaned_data['grouped_item']
			issue_item.save()  # Save the issue_item instance
			return redirect('issue_item_view')
	else:
		issue_item_form = IssueItemForm()
		
	paginator = Paginator(grouped_items, 8)
	page_number = request.GET.get('page')
	page_object3 = Paginator.get_page(paginator, page_number)
	
	return render(request, 'app/issue_item.html', {
		
		'issue_item_form': issue_item_form,
		'search_query': search_query,  
		'issue_items': issue_items,
		'page_object3': page_object3
	})



def loginpartial(request):
	if request.user.is_authenticated:
		logout(request)
		messages.success(request, 'You have been logged out')
	return HttpResponseRedirect('/login')

def Dashboard(request):




	start = request.GET.get('start')
	end = request.GET.get('end')
	monthly_usage = (
		sqlserverconn.objects.annotate(month=TruncMonth('Date'))
		.values('month')
		.annotate(total_usage=Sum('Subtotal'))
		.order_by('month')
	)
	
	
	
	
	df = pd.DataFrame.from_records(monthly_usage)
	if start:
		monthly_usage=monthly_usage.filter(month__gte=start)
	if end:
		monthly_usage = monthly_usage.filter(month__lte=end)
	
	fig = px.line ( df,
		x='month',
		y='total_usage',
		title = 'Total Sales per Month',
		labels={'month': 'Month',
				'total_usage':'Total Usage'}
		)
	
	
	fig.update_layout(
		width=400, 
		height=300 
	)
	chart = fig.to_html()

	date_form = DateForm()

	return render ( request,
		   'app/Dashboard.html',
		   {'chart':chart,
			'form': date_form})


def reports_pdf(request):
	try:
		# Create a PDF document
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="Inventory.pdf"'

		doc = SimpleDocTemplate(response, pagesize=letter)
		data = []

	
		items = sqlserverconn.objects.all()

		
		data.append(['Item', 'Units', 'Unit Cost', 'Unit of Measurement', 'Subtotal', 'Date'])

		for item in items:
			data.append([item.Item, item.Units, item.Unit_cost, item.Unit_of_measurement, item.Subtotal, item.Date])

	
		table = Table(data)

		
		style = TableStyle([
			('BACKGROUND', (0, 0), (-1, 0), colors.grey),
			('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
			('BOTTOMPADDING', (0, 0), (-1, 0), 12),
			('BACKGROUND', (0, 1), (-1, -1), colors.beige),
			('GRID', (0, 0), (-1, -1), 1, colors.black)
		])

		table.setStyle(style)

		# Add the table to the PDF
		elements = [table]

		doc.build(elements)

		return response  # Return the HttpResponse
	 
	except Exception as e:
		# Handle exceptions here, e.g., log the error
		# You can also return an error HttpResponse if needed
		# For example, return a 500 Internal Server Error response
		return HttpResponse("Internal Server Error", status=500)
	


def groupedi_pdf(request):
	try:
		
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="Inventory.pdf"'

		doc = SimpleDocTemplate(response, pagesize=letter)
		data = []

	
		items = GroupedItems.objects.all()

		# Define the table data as a list of lists
		data.append(['Grouped item', 'Total Units', 'Units Used', 'Units Available', 'Total'])

		for item in items:
			data.append([item.grouped_item, item.total_units, item.units_used, item.units_available, item.total])

		# Create a table with the data
		table = Table(data)

		# Define style for the table
		style = TableStyle([
			('BACKGROUND', (0, 0), (-1, 0), colors.grey),
			('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
			('BOTTOMPADDING', (0, 0), (-1, 0), 12),
			('BACKGROUND', (0, 1), (-1, -1), colors.beige),
			('GRID', (0, 0), (-1, -1), 1, colors.black)
		])

		table.setStyle(style)

		# Add the table to the PDF
		elements = [table]

		doc.build(elements)

		return response  # Return the HttpResponse
	 
	except Exception as e:
		# Handle exceptions here, e.g., log the error
		# You can also return an error HttpResponse if needed
		
		return HttpResponse("Internal Server Error", status=500)
	

def issuei_pdf(request):
	try:
		# Create a PDF document
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="Inventory.pdf"'

		doc = SimpleDocTemplate(response, pagesize=letter)
		data = []

		# Fetch data from your database or wherever you have it
		items = IssueItem.objects.all()

		# Define the table data as a list of lists
		data.append(['Item', 'Person', 'Units Issued', 'Units Returned','Units Used', 'Date'])

		for item in items:
			data.append([item.grouped_item, item.person, item.Unit_issued, item.units_returned, item.units_used, item.Date])

		# Create a table with the data
		table = Table(data)

		# Define style for the table
		style = TableStyle([
			('BACKGROUND', (0, 0), (-1, 0), colors.grey),
			('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
			('BOTTOMPADDING', (0, 0), (-1, 0), 12),
			('BACKGROUND', (0, 1), (-1, -1), colors.beige),
			('GRID', (0, 0), (-1, -1), 1, colors.black)
		])

		table.setStyle(style)

		# Add the table to the PDF
		elements = [table]

		doc.build(elements)

		return response  # Return the HttpResponse
	 
	except Exception as e:
		
		return HttpResponse("Internal Server Error", status=500)
	


class SqlServerConnViewSet(viewsets.ModelViewSet):
	queryset = sqlserverconn.objects.all()
	serializer_class = SqlServerConnSerializer
	

class GroupedItemsViewSet(viewsets.ModelViewSet):
	queryset = GroupedItems.objects.all()
	serializer_class = GroupedItemSerializer
	

class IssueItemViewSet(viewsets.ModelViewSet):
	queryset = IssueItem.objects.all()
	serializer_class = IssueItemSerializer
	

class CustomUOMViewSet(viewsets.ModelViewSet):
	queryset = Custom_UOM.objects.all()
	serializer_class = Custom_UOMSerializer

class LabourViewSet(viewsets.ModelViewSet):
	queryset = Labour.objects.all()
	serializer_class = LabourSerializer
	
class LabourViewSet(viewsets.ModelViewSet):
	queryset = Labour.objects.all()
	serializer_class = LabourSerializer
	
class PersonSet(viewsets.ModelViewSet):
	queryset = Person.objects.all()
	serializer_class = personSerializer
	
