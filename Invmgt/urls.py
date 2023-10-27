"""
Definition of urls for Invmgt.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.db.models.query_utils import RegisterLookupMixin
from django.contrib.auth import views as auth_view







urlpatterns = [
    path('', views.home, name='home'),
    path('inventory/', views.inventory, name='inventory'),
    path('add_record/', views.add_record, name='add_record'),
    path('add_custom_uom/', views.add_custom_uom, name='add_custom_uom'),
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
    path('reports_pdf/', views.reports_pdf, name='reports_pdf'),
    path('groupedi_pdf/', views.groupedi_pdf, name='groupedi_pdf'),
    path('issuei_pdf/', views.issuei_pdf, name='issuei_pdf'),
    
    

    

]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()