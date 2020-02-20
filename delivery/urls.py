#from django.conf.urls import url
from django.contrib import admin
from . import views
from django.urls import path
from django.conf.urls import include
from .views import ElkWizard, FORMS

urlpatterns = [

    path('', include('aws.urls')),
    path('redelk_configuration/', ElkWizard.as_view(FORMS), name='configure_elk_instance'),
    path('launch_redelk_configuration/', views.launch_configure_elk_instance, name='launch_configure_elk_instance'),
    path('redelk_dashboard/', views.display_elk_dashboard, name='display_elk_dashboard'),
    path('redelk_undeploy/', views.undeploy, name='undeploy_infra'),
    path('redelk_deployment_progress/<uuid:job_id>', views.progress_deployment, name='progress_deployment'),
	
]
