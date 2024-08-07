"""
Definition of urls for Invmgt.
"""

from datetime import datetime
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.db.models.query_utils import RegisterLookupMixin
from django.contrib.auth import views as auth_view
import debug_toolbar







urlpatterns = [
    path('index/', views.home, name='home'),
    
    
    path('inventory/', views.inventory, name='inventory'),
    path('setup/', views.setup, name='setup'),
    path('Dashboard/', views.Dashboard, name='Dashboard'),
    path('add_record/', views.add_record, name='add_record'),
    path('CustomUOM/', views.add_custom_uom, name='add_custom_uom'),
    path('person/', views.add_Person, name='add_Person'),
    path('update_record/<int:pk>', views.update_record, name='update_record'),
    path('issue_item/', views.issue_item_view, name='issue_item_view'),
    path('labourers/', views.labourers_view, name='labourers_view'),
    path('return_item/<int:pk>', views.return_item_view, name='return_item_view'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('update_labourer/<int:pk>', views.update_labourer, name='update_labourer'),
    path('delete_labourer/<int:pk>', views.delete_labourer, name='delete_labourer'),
    path('grouped_items/', views.grouped_itemsv, name='grouped_items'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('loginpartial/', views.loginpartial, name='loginpartial'),
    path('admin/', admin.site.urls),
    path('reg_user/', views.register_user, name='reg_user'),


    path('generate_excel_report/', views.generate_excel_report , name='generate_excel_report'),


    path('', views.projects, name='projects'),
    path('<int:project_id>/', views.project_details, name='project_details'),
    path('create_project/', views.create_project, name='create_project'),
    path('projects/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('task/<int:pk>/delete/', views.delete_task, name='delete_task'),
    #once done return this parts project/<int:project_id>
    path('<int:project_id>/tasks/', views.tasks, name='tasks'),
    path('create-task/', views.create_task, name='create_task'),
    path('task/<int:task_id>/', views.task, name='task_details'),
    path('<int:project_id>/tasks/tasks-events/', views.task_events, name='task_events'),
    path('<int:project_id>/task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('api/projects/<int:user_id>/', views.project_list, name='project_list'),
    path('app/',include('app.urls')),

    

]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    
urlpatterns += [
    path('__debug__/', include(debug_toolbar.urls)),
]