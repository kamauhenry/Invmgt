import json
from calendar import month
from re import L
import openpyxl
from django.core.serializers.json import DjangoJSONEncoder
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
from openpyxl.styles import Font, Alignment
from io import BytesIO
import plotly.express as px
import pandas as pd 
import plotly
from django.shortcuts import render, redirect
import plotly.io as pio
from django.contrib.auth import authenticate, login , logout 
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum, F, ExpressionWrapper, fields
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.core.paginator import Page, Paginator
from django.http import HttpResponseRedirect
import logging
from django.db.models.functions import TruncMonth
from rest_framework import viewsets
from app.serializers import *
from django.http import JsonResponse
from django.http import HttpResponse




item_units_used = {}

#def connsql(request):
#	conn=pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};'
#					  'Server=JAYDEN;'
#					  'Database=fpwdb;'
#					  'UID=sa;'
#					  'PWD=yrenhke;'
#					  'Trusted_Connnection=yes;'
#					  'encrypt=no;'  
#					  )
#	cursor=conn.cursor()
#	cursor.execute()
#	result=cursor.fetchall()
#	print(result)
#	return render(request,'index.html',{'sqlserverconn':result})

def project(request):
    return render(request, 'app/projects.html')



@login_required
def home(request):
    """Renders the home page."""
    current_user = request.user
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    # Filter records based on the current user's tenant
    sqlserverconns = sqlserverconn.objects.filter(tenant=tenant).order_by('-Date')

    paginator = Paginator(sqlserverconns, 15)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)

    total_records = len(sqlserverconns)

    context = {
        'sqlserverconns': sqlserverconns,
        'page_object': page_object,
        'total_records': total_records
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
    current_user = request.user
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant
    
    # Make sure the IssueItem belongs to the current user's tenant
    record = get_object_or_404(IssueItem, id=pk, tenant=tenant)
    return_form = IssueItemForm(request.POST or None, instance = record)
    if request.method == 'POST':
        if return_form.is_valid():
            return_form.save()
            messages.success(request, "Record Has Been Updated! ")
            return redirect('issue_item')
        
    return render(request, 'app/return_item.html', {'return_form': return_form})




#modified 
@login_required
def inventory(request):
    """Renders the contact page."""
    current_user = request.user
    # Assuming your CustomUser model has a 'tenant' field
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant
    
    form = SqlServerConnForm(request.POST or None, request.FILES or None, initial={'tenant': tenant})
    Custom_uom_form = Custom_UOM_form(request.POST or None, request.FILES or None, initial={'tenant': tenant})
    
    if request.method == 'POST':
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.tenant = tenant
            form_instance.save()
    
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/inventory.html',
        {
            'title': 'Contact',
            'message': 'Your contact page.',
            'year': datetime.now().year,
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
				

				return redirect('inventory')
		return render(request, 'app/CustomUOM.html', {'Custom_uom_form':Custom_uom_form})
	else:
		messages.success(request, "You Must Be Logged In...") 
	
# modified
def add_record(request):
    current_user = request.user
    # Assuming your CustomUser model has a 'tenant' field
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    if request.user.is_authenticated:
        form = SqlServerConnForm(request.POST or None, initial={'tenant': tenant})

        if request.method == "POST":
            form = SqlServerConnForm(request.POST)
            if form.is_valid():
                record_instance = form.save(commit=False)
                record_instance.tenant = tenant
                record_instance.save()
                messages.success(request, "Record Added...")
                return redirect('home')

        return render(request, 'inventory.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')
		
#modified
def add_Person(request):
    # Each tenant to have its own view
    current_user = request.user
    # Assuming your CustomUser model has a 'tenant' field
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    people = Employee.objects.filter(tenant=tenant)
    Person_form = Personform(request.POST or None)
    
    if request.user.is_authenticated:
        if request.method == "POST":
            Person_form = Personform(request.POST)
            if Person_form.is_valid():
                person_instance = Person_form.save(commit=False)
                person_instance.tenant = tenant
                person_instance.save()
                messages.success(request, "Record Added...")
                return redirect('issue_item_view')
        
        return render(request, 'app/person.html', {
            'Person_form': Person_form,
            'people': people
        })
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('issue_item_view')
	


	
#modified
@login_required
def update_record(request, pk):
    current_user = request.user
    # Assuming your CustomUser model has a 'tenant' field
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    current_record = get_object_or_404(sqlserverconn, tenant=tenant, Item_id=pk)
    
    form = SqlServerConnForm(request.POST or None, instance=current_record, initial={'tenant': tenant})

    if request.user.is_authenticated:
        if request.method == "POST":
            form = SqlServerConnForm(request.POST, instance=current_record)
            if form.is_valid():
                form.save()
                messages.success(request, "Record Has Been Updated!")
                return redirect('home')

        return render(request, 'app/update_record.html', {'form': form})
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
	



	
def LoginView(request):
	if request.method =='POST':
		username = request.POST['username']
		password = request.POST['password']
		
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request,"You Have Been Logged in")
			return redirect('Dashboard')
		else:
			messages.success(request, "Error")
			print("Successful login, redirecting to Dashboard")
			return redirect('Dashboard')
	else:
		return render(request, 'Dashboard.html')

	
#modified
@login_required
def labourers_view(request):
    current_user = request.user
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant 

    form = LabourForm(request.POST or None, initial={'tenant': tenant})
    labourers = Labour.objects.filter(tenant=tenant).order_by('-Date')

    if request.method == 'POST' and form.is_valid():
        labour = form.save()
        messages.success(request, "Record added successfully!")
        return redirect('labourers_view')

    total_amount = Labour.objects.filter(tenant=tenant).aggregate(total_amount=Sum('sub_total'))['total_amount']

    paginator = Paginator(labourers, 8)
    page_number = request.GET.get('page')
    page_object1 = Paginator.get_page(paginator, page_number)
    total_records = len(labourers)

    return render(request, 'app/labourers.html', {
        'form': form,
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


#modified
@login_required
def delete_labourer(request, pk):
    current_user = request.user
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    if request.user.is_authenticated:
        try:
            delete_it = Labour.objects.get(id=pk, tenant=tenant)
            delete_it.delete()
            messages.success(request, 'Record deleted')
        except Labour.DoesNotExist:
            messages.error(request, 'Record not found')

        return redirect('labourers_view')
    else:
        messages.success(request, 'You must be logged in')
        return redirect('labourers_view')


#modified    
@login_required
def update_labourer(request, pk):
    current_user = request.user
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    if request.user.is_authenticated:
        current_record = Labour.objects.get(id=pk, tenant=tenant)
        form = LabourForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Has Been Updated!")
            return redirect('labourers_view')
        return render(request, 'app/update_labourer.html', {'form': form})
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


#modified
@login_required
def grouped_itemsv(request):
    search_query = request.GET.get('q', '')
    current_user = request.user
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    # Group by 'Item' field and calculate total quantity and subtotal for each group
    grouped_items = sqlserverconn.objects.filter(tenant=tenant).values('Item').annotate(
        total_units=Sum('Units'),
        total=Sum('Subtotal'),
    )
    total_amount = sqlserverconn.objects.filter(tenant=tenant).aggregate(total_amount=Sum('Subtotal'))['total_amount']

    if search_query:
        grouped_items = grouped_items.filter(Item__icontains=search_query)

    # Get the filtered records for each grouped item
    records_by_item = {}
    for item in grouped_items:
        records = sqlserverconn.objects.filter(tenant=tenant, Item=item['Item'])
        records_by_item[item['Item']] = records

    paginator = Paginator(grouped_items, 8)
    page_number = request.GET.get('page')
    page_object2 = Paginator.get_page(paginator, page_number)

    assert isinstance(request, HttpRequest)

    return render(request, 'app/grouped_items.html', {
        'grouped_items': grouped_items,
        'search_query': search_query,
        'records_by_item': records_by_item,
        'total_amount': total_amount,
        'page_object2': page_object2
    })



#modified
@login_required
def issue_item_view(request):
    search_query = request.GET.get('q', '')
    current_user = request.user
    
    sqlserverconns_for_tenant = sqlserverconn.objects.filter(tenant=request.user.tenant)
    if current_user.tenant is None:
        return redirect('login')

    # Access tenant information directly from current_user.tenant
    tenant = current_user.tenant

    grouped_items = GroupedItems.objects.filter(sqlserverconns__in=sqlserverconns_for_tenant)
    issue_items = IssueItem.objects.all()
    issue_item_form = IssueItemForm(request.POST or None)

    if search_query:
        grouped_items = grouped_items.filter(grouped_item__icontains=search_query)

    if request.method == 'POST':
        issue_item_form = IssueItemForm(request.POST)
        if issue_item_form.is_valid():
            issue_item = issue_item_form.save(commit=False)
            issue_item.grouped_item = issue_item_form.cleaned_data['grouped_item']
            issue_item.tenant = tenant  # Set the tenant for the issue_item
            issue_item.save()
            return redirect('issue_item_view')
    else:
        issue_item_form = IssueItemForm()

    paginator = Paginator(grouped_items, 8)
    page_number = request.GET.get('page')
    page_object3 = Paginator.get_page(paginator, page_number)

    assert isinstance(request, HttpRequest)

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

#modified
@login_required
def Dashboard(request):
    current_user = request.user
    # Check if the user has a tenant associated with them
    if not hasattr(current_user, 'tenant'):
        # If not, redirect to login page or any other page you prefer
        return redirect('login')
    tenant = current_user
    sqlserverconns_for_tenant = sqlserverconn.objects.filter(tenant=tenant)
    if tenant is None:
        return redirect('login')
    tenant_identifier = tenant

    # Assuming GroupedItems has a ForeignKey to sqlserverconn named 'sql_server_conn'
    grouped_items = GroupedItems.objects.filter(sqlserverconns__in=sqlserverconns_for_tenant)
    labour_total = Labour.objects.filter(tenant=tenant).aggregate(total_amount=Sum('sub_total'))['total_amount']
    labourer_num = Labour.objects.filter(tenant=tenant).aggregate(total_no=Sum('NOL'))['total_no']
    invt_total = sqlserverconn.objects.filter(tenant=tenant).aggregate(invt_total=Sum('Subtotal'))['invt_total']

    monthly_usage = (
        sqlserverconn.objects.filter(tenant=tenant)
        .annotate(month=TruncMonth('Date'))
        .values('month')
        .annotate(total_usage=Sum('Subtotal'))
        .order_by('month')
    )

    itemperc = {
        'labels': [item.grouped_item for item in grouped_items],
        'data': [item.total_units for item in grouped_items],
    }
    itemperc_json = json.dumps(itemperc, cls=DjangoJSONEncoder)

    data = {
        'labels': [item['month'].strftime('%Y-%m-%d') for item in monthly_usage],
        'series': [{
            'name': 'Total Usage',
            'data': [item['total_usage'] for item in monthly_usage],
        }],
    }

    data_json = json.dumps(data, cls=DjangoJSONEncoder)

    return render(request, 'app/Dashboard.html', {
        'tenant_identifier': tenant_identifier,
        'chart_data': data_json,
        'labour_total': labour_total,
        'invt_total': invt_total,
        'data': itemperc_json,
        'labourer_num': labourer_num,
    })



@login_required
def reports_pdf(request):
    try:
        current_user = request.user
        tenant = current_user.tenant  # Assuming you have a tenant field in your User model

        # Create an Excel workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Item', 'Units', 'Unit Cost', 'Unit of Measurement', 'Subtotal', 'Date']
        worksheet.append(header)

        # Add data to the worksheet
        items = sqlserverconn.objects.filter(tenant=tenant)
        for item in items:
            row_data = [item.Item, item.Units, item.Unit_cost, item.Unit_of_measurement, item.Subtotal, item.Date]
            worksheet.append(row_data)

        # Apply styles to the header row
        header_row = worksheet[1]
        for cell in header_row:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

        # Create a response with appropriate headers for Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Inventory.xlsx"'

        # Save the workbook to the response
        workbook.save(response)

        return response  # Return the HttpResponse

    except Exception as e:
        import traceback
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)

        # If you want to include the error message in the HTTP response for debugging purposes
        return HttpResponse(error_message, status=500)

        # If you prefer to provide a generic error message
        return HttpResponse("Internal Server Error", status=500)




    #modified
@login_required
def groupedi_pdf(request):
    try:
        current_user = request.user
        tenant = current_user.tenant  # Assuming you have a tenant field in your User model

        # Create a new workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Grouped item', 'Total Units', 'Units Used', 'Units Available', 'Total']
        worksheet.append(header)

        # Add data to the worksheet
        items = GroupedItems.objects.filter(tenant=tenant)
        for item in items:
            row_data = [item.grouped_item, item.total_units, item.used_units, item.units_available, item.total]
            worksheet.append(row_data)

        # Set column widths (optional)
        for col_num, value in enumerate(header, 1):
            col_letter = openpyxl.utils.get_column_letter(col_num)
            worksheet.column_dimensions[col_letter].width = max(len(str(value)) + 2, 15)

        # Create a response with appropriate headers for Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Categories.xlsx"'

        # Save the workbook to the response
        workbook.save(response)

        return response

    except Exception as e:
        import traceback
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)

        # If you want to include the error message in the HTTP response for debugging purposes
        return HttpResponse(error_message, status=500)

        # If you prefer to provide a generic error message
        return HttpResponse("Internal Server Error", status=500)

#modified
@login_required
def groupedi_pdf(request):
    try:
        current_user = request.user
        tenant = current_user.tenant  # Assuming you have a tenant field in your User model

        # Create a new workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Grouped item', 'Total Units', 'Units Used', 'Units Available', 'Total']
        worksheet.append(header)

        # Add data to the worksheet
        items = GroupedItems.objects.filter(tenant=tenant)
        for item in items:
            row_data = [item.grouped_item, item.total_units, item.used_units, item.units_available, item.total]
            worksheet.append(row_data)

        # Set column widths (optional)
        for col_num, value in enumerate(header, 1):
            col_letter = openpyxl.utils.get_column_letter(col_num)
            worksheet.column_dimensions[col_letter].width = max(len(str(value)) + 2, 15)

        # Create a response with appropriate headers for Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Categories.xlsx"'

        # Save the workbook to the response
        workbook.save(response)

        return response

    except Exception as e:
        import traceback
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)

        # If you want to include the error message in the HTTP response for debugging purposes
        return HttpResponse(error_message, status=500)

        # If you prefer to provide a generic error message
        return HttpResponse("Internal Server Error", status=500)

def issuei_pdf(request):
    try:
        current_user = request.user
        tenant = current_user.tenant  # Assuming you have a tenant field in your User model

        # Create a new workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Person', 'Item', 'Units Issued', 'Units Returned', 'Used Units', 'Date']
        worksheet.append(header)

        # Add data to the worksheet
        items = IssueItem.objects.filter(tenant=tenant)
        for item in items:
            row_data = [item.person, item.grouped_item, item.units_issued, item.units_returned, item.used_units, item.Date]
            worksheet.append(row_data)

        # Set column widths (optional)
        for col_num, value in enumerate(header, 1):
            col_letter = openpyxl.utils.get_column_letter(col_num)
            worksheet.column_dimensions[col_letter].width = max(len(str(value)) + 2, 15)

        # Create a response with appropriate headers for Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Items Issued.xlsx"'

        # Save the workbook to the response
        workbook.save(response)

        return response

    except Exception as e:
        import traceback
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)

        # If you want to include the error message in the HTTP response for debugging purposes
        return HttpResponse(error_message, status=500)

        # If you prefer to provide a generic error message
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
	queryset = Employee.objects.all()
	serializer_class = personSerializer
	
