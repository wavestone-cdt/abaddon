from django.urls import path
from django.contrib import admin
from . import views
import users.views as users_views


urlpatterns = [
    ## WEB Views
    # ex: /settings/
    path('', views.show_settings_menu, name='show_settings_menu'),
    # ex: /settings/users/
    #path('', users_views.list_users_view, name='list_users_view'),
    # ex: /settings/alerts
    #path('', views.list_events, name='list_events'),

    ## API views
    # ex: /settings/api/v1/update
    path('api/v1/update', views.update_setting_api, name='update_setting_api'),
    # ex: /settings/api/v1/add
    path('api/v1/add', views.add_setting_api, name='add_setting_api'),
    # ex: /settings/api/v1/delete/3
    path('api/v1/delete/<int:setting_id>', views.delete_setting_api, name='delete_setting_api'),
    # ex: /settings/api/v1/export
    path('api/v1/export', views.export_settings_api, name='export_settings_api'),

]
