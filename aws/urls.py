#from django.conf.urls import url
from django.contrib import admin
from . import views
from django.urls import path

urlpatterns = [

    path('', views.infrastructure_dashboard, name='infrastructure_dashboard'),
    path('cloudfront/', views.cloudfront_dashboard, name='cloudfront_dashboard'),
    path('ec2/', views.ec2_dashboard, name='ec2_dashboard'),
    path('ec2/deploy-ec2', views.deploy_ec2, name='deploy_ec2'),
    path('ec2/deploy-gophish', views.deploy_gophish, name='deploy_gophish'),

]
