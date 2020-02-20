#from django.conf.urls import url
from django.contrib import admin
from . import views
from django.urls import path

urlpatterns = [

    path('', views.active_scans, name='active_scans'),
    path('results', views.results, name='active_scans_results'),
    path('export', views.export, name='export_results'),
]
