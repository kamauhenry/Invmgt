import json
from calendar import month
import logging
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
from django.urls import reverse
from io import BytesIO
from django.core.files.storage import default_storage
from django.shortcuts import render
import os
import google.generativeai as genai
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.core.exceptions import ValidationError
import google.generativeai as genai

# Set up logging
logger = logging.getLogger(__name__)
item_units_used = {}




@login_required
def projects(request):
    
    project_data = project_list(request)
    return render(request, 'app/projects.html', {'project_data': project_data})

def project_list(request, user_id=None):
    if user_id is None:
        # Use the current logged-in user if no user_id is provided
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        user = request.user
    else:
        # Fetch the user object based on user_id
        user = get_object_or_404(CustomUser, id=user_id)
    
    projects = Project.objects.filter(project_owner=user)
    project_data = []
    for project in projects:
        project_data.append({
            'user_id': user.id,   
            'id': project.id,
            'name': project.name,
            'link': reverse('project_details', kwargs={'project_id': project.id})
        })
    return JsonResponse(project_data, safe=False)

# Define your Azure AI and PDF functions




@login_required
def create_project(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST, request.FILES, current_user=request.user)
        if form.is_valid():
            try:
                instance = form.save(commit=False)

                # **AI Integration:**
                project_data = {
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

                system_prompt = "Given the project information, analyze the feasibility of the project by assessing its viability based on the provided parameters, including any potential risks or issues. Provide an estimated budget considering the materials and requirements listed, and evaluate the proposed timeline, suggesting any necessary adjustments. Analyze the required number of employees and resources, and recommend any additional needs or changes. Review the sustainability considerations and offer feedback on potential improvements or compliance with standards. Finally, examine external factors that might affect the project, such as environmental conditions or regulatory requirements, and evaluate their impact on the project's overall success, highlighting challenges and suggesting recommendations for improvement."

                try:
                    ai_response = my_chat_view(system_prompt + json.dumps(project_data))
                    logger.info(f'AI Response: {ai_response}')
                except Exception as e:
                    logger.error(f'Error in AI integration: {e}')
                    messages.error(request, 'There was an error with AI processing. Please try again.')
                    return render(request, 'app/create_project.html', {'form': form})

                # Update project instance with AI response
                instance.save()

                # Generate PDF
                try:
                    template_path = 'app/pdf_template.html'
                    context = {'ai_response': ai_response}
                    html = render_to_string(template_path, context)
                    logger.info(f'HTML Content for PDF: {html}')  # Log the HTML content

                    result = BytesIO()
                    pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)

                    if pdf.err:
                        logger.error(f'PDF generation error: {pdf.err}')
                        return HttpResponse('Error generating PDF')

                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="project_response_{instance.id}.pdf"'
                    response.write(result.getvalue())
                    return response
                
                    return redirect('project_detail', project_id=instance.id)

                except Exception as e:
                    logger.error(f'Error generating PDF: {e}')
                    return HttpResponse('Error generating PDF')

            except ValidationError as e:
                logger.error(f'Form validation error: {e}')
                messages.error(request, 'Invalid form data. Please correct the errors and try again.')
            except Exception as e:
                logger.error(f'Error processing project creation: {e}')
                messages.error(request, 'There was an error processing your request. Please try again.')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors and try again.')
    else:
        form = CreateProjectForm(current_user=request.user)

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


def my_chat_view(prompt):
      # Ensure genai is correctly imported and configured
    GENINI_API_KEY = 'AIzaSyC6oxhi9CRM9QdASCyYvCrqmU74eQG0XXg'  # Replace with your actual API key
    genai.configure(api_key=GENINI_API_KEY)

    generation_config = {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    return response.text



def create_pdf_from_json(json_data, pdf_path):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    text = c.beginText(40, height - 40)
    text.setFont("Helvetica", 12)

    for key, value in json_data.items():
        text.textLine(f"{key}: {value}")

    c.drawText(text)
    c.showPage()
    c.save()
    


@login_required
def project_details (request,project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'app/project_details.html', {'project': project})




@login_required
def update_project(request, pk):
    # Get the project object
    project = get_object_or_404(Project, id=pk)

    # Ensure the user has access to update the project
    if not request.user.is_superuser and request.user != project.project_owner:
        messages.error(request, "You do not have permission to update this project.")
        return redirect('projects')

    form = CreateProjectForm(request.POST or None, instance=project)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Record has been updated!")
            return redirect('projects')

    return render(request, 'app/update_project.html', {'form': form})	



@login_required
def delete_project(request, pk):
    # Get the project object
    project = get_object_or_404(Project, id=pk)

    # Ensure the user has access to delete the project
    if not request.user.is_superuser and request.user != project.project_owner:
        messages.error(request, "You do not have permission to delete this project.")
        return redirect('projects')

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project has been deleted!")
        return redirect('projects')

    return render(request, 'app/confirm_delete.html', {'project': project})
	
@login_required
def create_task(request):
    if request.method == 'POST':
        form = CreateTaskForm(request.POST or None, request.FILES or None)
        
        if form.is_valid():
            form_instance = form.save(commit=False)
            # Automatically set the project from the form or context
            form_instance.project_owner = request.user
            form_instance.save()
            return redirect('home')  # Redirect to the projects page after successful creation
    else:
        form = CreateTaskForm()

    return render(
        request,
        'app/create_task.html',
        {
            'title': 'Create Task',
            'message': 'Create task page.',
            'year': datetime.now().year,
            'form': form,
        }
    )

@login_required
def task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project  # Assuming Task model has a ForeignKey to Project
    tasks = Task.objects.filter(project=project)
    
    return render(request, 'app/task_details.html', {
        'title': 'Task n Calendar',
        'message': ' displaying tasks.',
        'year': datetime.now().year,
        'project': project,
        'tasks': tasks,
    })

@login_required
def delete_task(request, pk):
    # Get the task object
    task = get_object_or_404(Task, pk=pk)

    # Ensure the user has access to delete the task
    if not request.user.is_superuser and request.user != task.project.project_owner:
        messages.error(request, "You do not have permission to delete this task.")
    else:
        task.delete()
        messages.success(request, "Task has been deleted!")
    
    return redirect('tasks', project_id=task.project.id)


@login_required
def tasks(request, project_id):
   

    project = get_object_or_404(Project, id=project_id)
    
    return render(request, 'app/tasks.html', {
        'title': 'Task n Calendar',
        'message': ' displaying tasks.',
        'year': datetime.now().year,
        'project': project,
    })

@login_required
def task_events(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    events = []
    for task in tasks:
        events.append({
            'id': task.id,  # It's good to include the task ID
            'title': task.name,
            'start': task.start_date.isoformat(),
            'end': task.due_date.isoformat(),
            'description': task.description,
        })
    return JsonResponse(events, safe=False)
    
    

@login_required
def task_detail(request):
    
    return render(request, 'app/task_detail.html', {
        'title': 'Task Detail',
        'message': 'Task detail page.',
        'year': datetime.now().year,
    }) 

@login_required
def home(request):
    """Renders the home page."""

    user_projects = Project.objects.filter(project_owner=request.user)
    
    if not user_projects.exists():
        # Handle the case where the user has no projects
        return render(request, 'app/Dashboard.html', {'message': 'You have no projects.'})
    
    # If user has multiple projects, you can select one or the first one
    project = user_projects.first()


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
    """Renders the inventory page."""

    
    form = SqlServerConnForm(request.POST or None, request.FILES or None)
    Custom_uom_form = Custom_UOM_form(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form_instance = form.save(commit=False)
           
            form_instance.save()
            return redirect('app/index.html')  # Redirect to the inventory page to prevent form resubmission
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging
    
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/inventory.html',
        {
            'title': 'Inventory',
            'message': 'Manage your inventory.',
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
    if request.user.is_authenticated:
        if request.method == "POST":
            form = SqlServerConnForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Record Added...")
                return redirect('inventory')
        else:
            form = SqlServerConnForm()

        return render(request, 'add_record.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to add a record.")
        return redirect('login')  # Redirect to login instead of inventory
		

	
#modified
@login_required
def update_record(request, pk):



    current_record = get_object_or_404(sqlserverconn,  Item_id=pk)
    
    form = SqlServerConnForm(request.POST or None, instance=current_record)

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
	



   

def add_Person(request):
    people = Employee.objects.all()
    Person_form = Personform(request.POST or None)

    if request.user.is_authenticated:
        if request.method == "POST":
            Person_form = Personform(request.POST)
            if Person_form.is_valid():
                person_instance = Person_form.save(commit=False)
                # Assuming you will handle the project field in the form
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





	
def LoginView(request):
	if request.method =='POST':
		username = request.POST['username']
		password = request.POST['password']
		
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request,"You Have Been Logged in")
			return redirect('projects')
		else:
			messages.success(request, "Error")
			print("Successful login, redirecting to projects")
			return redirect('login')
	else:
		return render(request, 'app/projects.html')

@login_required
def labourers_view(request):
    form = LabourForm(request.POST or None)

    # Filter labourers based on a project field in the Labour model
    labourers = Labour.objects.all().order_by('-Date')

    if request.method == 'POST' and form.is_valid():
        labour = form.save()
        messages.success(request, "Record added successfully!")
        return redirect('labourers_view')

    total_amount = Labour.objects.aggregate(total_amount=Sum('sub_total'))['total_amount']

    paginator = Paginator(labourers, 8)
    page_number = request.GET.get('page')
    page_object1 = paginator.get_page(page_number)
    total_records = labourers.count()

    return render(request, 'app/labourers.html', {
        'form': form,
        'labourers': labourers,
        'total_amount': total_amount,
        'page_object1': page_object1,
        'total_records': total_records
    })


def setup(request):
	form = Custom_UOM_form(request.POST or None)

	
	if request.method == 'POST' and form.is_valid():
		labour = form.save()
		
		messages.success(request, "record added successfully !")
		return redirect ('setup')
	

	return render ( request,
		   'app/setup.html',
		   {'form': form,
            'labour': labour,
			
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
    user = None  # Initialize user to avoid UnboundLocalError

    if request.method == 'POST' and form.is_valid():
        user = form.save()  # Save the user
        messages.success(request, "User has been successfully registered!")
        return redirect('reg_user')

    return render(request, 'app/reg_user.html', {'form': form, 'user': user})
#modified
@login_required
def grouped_itemsv(request):
    search_query = request.GET.get('q', '')

    # Fetch the projects associated with the current user
    user_projects = Project.objects.filter(project_owner=request.user)
    
    if not user_projects.exists():
        # Handle the case where the user has no projects
        return render(request, 'app/Dashboard.html', {'message': 'You have no projects.'})
    
    # If user has multiple projects, you can select one or the first one
    project = user_projects.first()

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
    page_object2 = paginator.get_page(page_number)

    assert isinstance(request, HttpRequest)

    return render(request, 'app/grouped_items.html', {
        'grouped_items': page_object2,
        'search_query': search_query,
        'records_by_item': records_by_item,
        'total_amount': total_amount,
        'project': project,
        'user_projects': user_projects,
    })



#modified
@login_required
def issue_item_view(request):
    search_query = request.GET.get('q', '')

    # Fetch the projects associated with the current user
    user_projects = Project.objects.filter(project_owner=request.user)
    
    if not user_projects.exists():
        # Handle the case where the user has no projects
        return render(request, 'app/Dashboard.html', {'message': 'You have no projects.'})
    
    # If user has multiple projects, you can select one or the first one
    project = user_projects.first()

    # Fetch all grouped items and issue items related to the selected project
    grouped_items = GroupedItems.objects.filter(project=project)
    issue_items = IssueItem.objects.filter(grouped_item__project=project)
    issue_item_form = IssueItemForm(request.POST or None)

    if search_query:
        grouped_items = grouped_items.filter(grouped_item__icontains=search_query)

    if request.method == 'POST' and issue_item_form.is_valid():
        issue_item = issue_item_form.save(commit=False)
        issue_item.grouped_item = issue_item_form.cleaned_data['grouped_item']
        issue_item.save()
        return redirect('issue_item_view')

    paginator = Paginator(grouped_items, 8)
    page_number = request.GET.get('page')
    page_object3 = paginator.get_page(page_number)

    assert isinstance(request, HttpRequest)

    return render(request, 'app/issue_item.html', {
        'issue_item_form': issue_item_form,
        'search_query': search_query,
        'issue_items': issue_items,
        'page_object3': page_object3,
        'project': project,
        'user_projects': user_projects,
    })


def loginpartial(request):
	if request.user.is_authenticated:
		logout(request)
		messages.success(request, 'You have been logged out')
	return HttpResponseRedirect('/login')

@login_required
def Dashboard(request):
    # Get all projects for the dropdown
    projects = Project.objects.all()

    # Default to the first project if no project is selected
    project_name = request.GET.get('name')
    project = projects.filter(name=project_name).first() if project_name else projects.first()

    if not project:
        messages.error(request, "Project not found.")
        return redirect('Dashboard')

    # Fetch relevant data based on project_name

    labour_total = Labour.objects.filter(project=project.id).aggregate(total_amount=Sum('sub_total'))['total_amount']
    labourer_num = Labour.objects.filter(project=project.id).aggregate(total_no=Sum('NOL'))['total_no']
    invt_total = sqlserverconn.objects.filter(project=project.id).aggregate(invt_total=Sum('Subtotal'))['invt_total']
    grouped_items = GroupedItems.objects.filter(project=project.id) 
    monthly_usage = (
        sqlserverconn.objects.filter(project=project.id)
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
        'projects': projects,  # Pass all projects for the dropdown
    })










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
	



@login_required
def generate_excel_report(request):
    report_type = request.GET.get('type')
    project_name = request.GET.get('name')

    if not report_type or not project_name:
        return HttpResponse("Report type and project name are required.", status=400)  # Bad Request

    project = get_object_or_404(Project, name=project_name)

    # Create an Excel workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active



    if report_type == 'labour':
        header = ['Labourer', 'Total Amount', 'Number of Labourers']
        worksheet.append(header)

        labour_total = Labour.objects.filter(project=project.id).aggregate(total_amount=Sum('sub_total'))['total_amount']
        labourer_num = Labour.objects.filter(project=project.id).aggregate(total_no=Sum('NOL'))['total_no']

        row_data = [project.project_owner.username, labour_total, labourer_num]
        worksheet.append(row_data)


    elif report_type == 'inventory':
            # Generate inventory report
            header = ['Item', 'Units', 'Unit Cost', 'Unit of Measurement', 'Subtotal', 'Date']
            worksheet.append(header)
            
            items = sqlserverconn.objects.filter(project_name=project_name)
            for item in items:
                row_data = [item.Item, item.Units, item.Unit_cost, item.Unit_of_measurement, item.Subtotal, item.Date]
                worksheet.append(row_data)

    elif report_type == 'groupeditems':
        header = ['Grouped Item', 'Total Units']
        worksheet.append(header)

        grouped_items = GroupedItems.objects.all()
        for item in grouped_items:
            row_data = [item.grouped_item, item.total_units]
            worksheet.append(row_data)

    elif report_type == 'issueitem':
        header = ['Person', 'Grouped Item', 'Units Issued', 'Units Returned', 'Units Used', 'Date']
        worksheet.append(header)

        issue_items = IssueItem.objects.filter(grouped_item__project=project).order_by('-Date')
        for item in issue_items:
            row_data = [item.person.user.username, item.grouped_item.grouped_item, item.units_issued, item.units_returned, item.units_used, item.Date]
            worksheet.append(row_data)
    elif report_type == 'tasks':
        header = ['Task Name', 'Assigned To', 'Status', 'Due Date']
        worksheet.append(header)

        tasks = Task.objects.filter(project=project)
        for task in tasks:
            row_data = [task.name, task.assigned_to.user.username, task.status, task.due_date]
            worksheet.append(row_data)




    else:
        return HttpResponse("Invalid report type.", status=400)  # Bad Request

    # Apply styles to the header row
    header_row = worksheet[1]
    for cell in header_row:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    # Create a response with appropriate headers for Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Report.xlsx"'

    # Save the workbook to the response
    workbook.save(response)

    return response  # Return the HttpResponse