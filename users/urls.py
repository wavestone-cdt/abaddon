# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views, apis
from reportings import views as rep_views


urlpatterns = [

    # Views
    path('', rep_views.homepage_dashboard_view, name='homepage_dashboard_view'),
    path('list', views.list_users_view, name='list_users_view'),
    path('dashboard', rep_views.homepage_dashboard_view, name='homepage_dashboard_view'),
    path('details', views.user_details_view, name='user_details_view'),
    path('add', views.add_user_view, name='add_user_view'),

    # REST-API Endpoints
    path('users/api/v1/details/<int:user_id>', apis.user_details_api, name='user_details_api'),
    path('users/api/v1/list', apis.list_users_api, name='list_users_api'),
    path('users/api/v1/authtoken/get', apis.get_curruser_authtoken_api, name='get_curruser_authtoken_api'),
    path('users/api/v1/authtoken/get/<int:user_id>', apis.get_user_authtoken_api, name='get_user_authtoken_api'),
    path('users/api/v1/authtoken/renew', apis.renew_curruser_authtoken_api, name='renew_curruser_authtoken_api'),
    path('users/api/v1/authtoken/renew/<int:user_id>', apis.renew_user_authtoken_api, name='renew_user_authtoken_api'),
    path('users/api/v1/authtoken/delete', apis.delete_curruser_authtoken_api, name='delete_curruser_authtoken_api'),
    path('users/api/v1/authtoken/delete/<int:user_id>', apis.delete_user_authtoken_api, name='delete_user_authtoken_api'),
]
