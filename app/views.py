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
import openai


openai.api_key = 'f549c621241c4ae693bfef95c58127be'


item_units_used = {}


def projects(request):
    
    return render(request, 'app/projects.html')

def create_project(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            feasibility_report = generate_feasibility_report(project)
            project.feasibility_report = feasibility_report
            project.save()
            pdf_url = generate_pdf(feasibility_report)
            return JsonResponse({'success': True, 'pdf_url': pdf_url})
    else:
        form = CreateProjectForm()
    return render(request, 'app/create_project.html', {'form': form,
                                                       'year': datetime.now().year,})
    form = CreateProjectForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.project_owner = request.user  # Assuming project owner is the logged-in user
            form_instance.save()
            return redirect('projects')  # Redirect to the projects page after successful creation
    
    
    return render(
        request,
        'app/create_project.html',
        {
            'title': 'Create Project',
            'message': 'Create project page.',
            'year': datetime.now().year,
            'form': form,
        }
    )


def create_task(request):
        # Access tenant information directly from current_user.tenant
   # project_id = request.GET.get('project_id')
   # if not project_id:
        # Handle the case where project_id is not provided
        #return redirect('login')  # Redirect to a default page or show an error
        # Get the project object
    #project = get_object_or_404(Project, id=project_id)

    
    form = CreateTaskForm(request.POST or None, request.FILES or None )
   # , initial={'project': project}

    if request.method == 'POST':
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.project_owner = request.user  # Assuming project owner is the logged-in user
            form_instance.save()
            return redirect('projects')  # Redirect to the projects page after successful creation
    
    
    return render(
        request,
        'app/create_task.html',
        {
            'title': 'Create task',
            'message': 'Create task page.',
            'year': datetime.now().year,
            'form': form,
        }
    )



def tasks(request):
    
    return render(request, 'app/tasks.html', {
        'title': 'Task n Calendar',
        'message': ' displaying tasks.',
        'year': datetime.now().year,
    })



def task_events(request):
    tasks = Task.objects.all()
    events = []

    for task in tasks:
        events.append({
            'title': task.name,
            'start': task.start_date.isoformat(),
            'end': task.due_date.isoformat(),
            'description': task.description,
        })

    return JsonResponse(events, safe=False)


@login_required
def home(request):
    """Renders the home page."""

    # Get the project_id from the request, e.g., from query parameters
    project_id = request.GET.get('project_id')
    if not project_id:
        #Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

    # Filter records based on the project_id
    sqlserverconns = sqlserverconn.objects.filter(project=project).order_by('-Date')

    paginator = Paginator(sqlserverconns, 15)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)

    total_records = len(sqlserverconns)

    context = {
        'sqlserverconns': sqlserverconns,
        'page_object': page_object,
        'total_records': total_records,
        'project': project,
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


    # Access tenant information directly from current_user.tenant
    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

    
    # Make sure the IssueItem belongs to the current user's tenant
    record = get_object_or_404(IssueItem, id=pk, project=project)
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

    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

  
    
    form = SqlServerConnForm(request.POST or None, request.FILES or None, initial={'project': project})
    Custom_uom_form = Custom_UOM_form(request.POST or None, request.FILES or None, initial={'project': project})
    
    if request.method == 'POST':
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.project = project
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


    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

  
    if request.user.is_authenticated:
        form = SqlServerConnForm(request.POST or None, initial={'project': project})

        if request.method == "POST":
            form = SqlServerConnForm(request.POST)
            if form.is_valid():
                record_instance = form.save(commit=False)
                record_instance.project = project
                record_instance.save()
                messages.success(request, "Record Added...")
                return redirect('home')

        return render(request, 'inventory.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')
		


#modified
def add_Person(request):


    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

   

    people = Employee.objects.filter(project=project)
    Person_form = Personform(request.POST or None)
    
    if request.user.is_authenticated:
        if request.method == "POST":
            Person_form = Personform(request.POST)
            if Person_form.is_valid():
                person_instance = Person_form.save(commit=False)
                person_instance.project = project
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

    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)



    current_record = get_object_or_404(sqlserverconn, project=project, Item_id=pk)
    
    form = SqlServerConnForm(request.POST or None, instance=current_record, initial={'project': project})

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
			print("Successful login, redirecting to projects")
			return redirect('projects')
	else:
		return render(request, 'projects.html')

	
#modified
@login_required
def labourers_view(request):


    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id) 

    form = LabourForm(request.POST or None, initial={'project': project})
    labourers = Labour.objects.filter(project=project).order_by('-Date')

    if request.method == 'POST' and form.is_valid():
        labour = form.save()
        messages.success(request, "Record added successfully!")
        return redirect('labourers_view')

    total_amount = Labour.objects.filter(project=project).aggregate(total_amount=Sum('sub_total'))['total_amount']

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


    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

    if request.user.is_authenticated:
        try:
            delete_it = Labour.objects.get(id=pk, projectt=project)
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


    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

    if request.user.is_authenticated:
        current_record = Labour.objects.get(id=pk, project=project)
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


    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

    # Group by 'Item' field and calculate total quantity and subtotal for each group
    grouped_items = sqlserverconn.objects.filter(project=project).values('Item').annotate(
        total_units=Sum('Units'),
        total=Sum('Subtotal'),
    )
    total_amount = sqlserverconn.objects.filter(project=project).aggregate(total_amount=Sum('Subtotal'))['total_amount']

    if search_query:
        grouped_items = grouped_items.filter(Item__icontains=search_query)

    # Get the filtered records for each grouped item
    records_by_item = {}
    for item in grouped_items:
        records = sqlserverconn.objects.filter(project=project, Item=item['Item'])
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

    
    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)

    grouped_items = GroupedItems.objects.filter(project=project)
    issue_items = IssueItem.objects.all()
    issue_item_form = IssueItemForm(request.POST or None)

    if search_query:
        grouped_items = grouped_items.filter(grouped_item__icontains=search_query)

    if request.method == 'POST':
        issue_item_form = IssueItemForm(request.POST)
        if issue_item_form.is_valid():
            issue_item = issue_item_form.save(commit=False)
            issue_item.grouped_item = issue_item_form.cleaned_data['grouped_item']
            issue_item.project = project  # Set the tenant for the issue_item
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
   
    
    project_id = request.GET.get('project_id')
    if not project_id:
        # Handle the case where project_id is not provided
        return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
    project = get_object_or_404(Project, id=project_id)
    
 

    # Assuming GroupedItems has a ForeignKey to sqlserverconn named 'sql_server_conn'
    grouped_items = GroupedItems.objects.filter(project=project)
    labour_total = Labour.objects.filter(project=project).aggregate(total_amount=Sum('sub_total'))['total_amount']
    labourer_num = Labour.objects.filter(project=project).aggregate(total_no=Sum('NOL'))['total_no']
    invt_total = sqlserverconn.objects.filter(project=project).aggregate(invt_total=Sum('Subtotal'))['invt_total']

    monthly_usage = (
        sqlserverconn.objects.filter(project=project)
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
        'project': project,
        'chart_data': data_json,
        'labour_total': labour_total,
        'invt_total': invt_total,
        'data': itemperc_json,
        'labourer_num': labourer_num,
    })



@login_required
def reports_pdf(request):
    try:
        project_id = request.GET.get('project_id')
        if not project_id:
            # Handle the case where project_id is not provided
            return redirect('login')  # Redirect to a default page or show an error

        # Get the project object
        project = get_object_or_404(Project, id=project_id)

        # Create an Excel workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Item', 'Units', 'Unit Cost', 'Unit of Measurement', 'Subtotal', 'Date']
        worksheet.append(header)
        

        # Add data to the worksheet
        items = sqlserverconn.objects.filter(project=project)
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




    #modified
@login_required
def groupedi_pdf(request):
    try:
        project_id = request.GET.get('project_id')
        if not project_id:
        # Handle the case where project_id is not provided
            return redirect('login')  # Redirect to a default page or show an error

        # Get the project object
        project = get_object_or_404(Project, id=project_id)
        # Create a new workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Grouped item', 'Total Units', 'Units Used', 'Units Available', 'Total']
        worksheet.append(header)
        


        # Add data to the worksheet
        items = GroupedItems.objects.filter(project=project)
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



#modified
@login_required
def groupedi_pdf(request):
    try:
        project_id = request.GET.get('project_id')
        if not project_id:
            # Handle the case where project_id is not provided
            return redirect('login')  # Redirect to a default page or show an error

    # Get the project object
        project = get_object_or_404(Project, id=project_id)
        # Create a new workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Grouped item', 'Total Units', 'Units Used', 'Units Available', 'Total']
        worksheet.append(header)


        # Add data to the worksheet
        items = GroupedItems.objects.filter(project=project)
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


def issuei_pdf(request):
    try:
        project_id = request.GET.get('project_id')
        if not project_id:
        # Handle the case where project_id is not provided
            return redirect('login')  # Redirect to a default page or show an error

        # Get the project object
        project = get_object_or_404(Project, id=project_id)
        
        # Create a new workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Write header row
        header = ['Person', 'Item', 'Units Issued', 'Units Returned', 'Used Units', 'Date']
        worksheet.append(header)


        # Add data to the worksheet
        items = IssueItem.objects.filter(project=project)
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
	

def project_list(request):
    # Fetch all projects from the database
    projects = Project.objects.filter(project_owner=request.user).values('name')
    return JsonResponse(list(projects), safe=False)

def generate_feasibility_report(project):
    project_data = {
        'name': project.name,
        'project_owner': project.project_owner.username,
        'start_date': project.start_date,
        'end_date': project.end_date,
        'project_type': project.project_type,
        'location': project.location,
        'description': project.description,
        'building_area': project.building_area,
        'number_of_floors': project.number_of_floors,
        'materials': project.materials,
        'building_codes': project.building_codes,
        'site_conditions': project.site_conditions,
        'drawings': project.drawings,
        'project_requirements': project.project_requirements,
        'sustainability_considerations': project.sustainability_considerations,
        'external_factors': project.external_factors,
        'estimated_completion_time': project.estimated_completion_time,
        'required_employees': project.required_employees,
        'detailed_materials_list': project.detailed_materials_list
    }

    prompt = f"Generate a feasibility report based on the following project data:\n\n{project_data}\n\nAnalyze the project's viability, identify potential risks, and suggest improvements."

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1500
    )

    return response.choices[0].text

def generate_pdf(report_text):
    from fpdf import FPDF

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Feasibility Report', 0, 1, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(10)

        def chapter_body(self, body):
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, body)
            self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title('Feasibility Report')
    pdf.chapter_body(report_text)
    pdf_output_path = '/app/static/app/images/feasibility_report.pdf'
    pdf.output(pdf_output_path)

    return pdf_output_path