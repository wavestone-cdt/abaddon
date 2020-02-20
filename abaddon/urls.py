"""abaddon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path
from dashboard import views
from django.conf.urls import include

from django.views.generic.base import TemplateView # new

#from users.forms import LoginForm
#from users import views as user_views

urlpatterns = [

    #Useful: https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/
    #Reference diffult to understand: https://docs.djangoproject.com/fr/2.1/topics/auth/default/#module-django.contrib.auth.views
    #path('', include('django.contrib.auth.urls')),
    #path('home/', TemplateView.as_view(template_name='home.html'), name='home'), # new

    #https://github.com/sibtc/django-auth-tutorial-example/blob/master/mysite/urls.py
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='main_dashboard'),

    #path('signup/', views.signup, name='signup'),
    #path('secret/', views.secret_page, name='secret'),
    #path('secret2/', views.SecretPage.as_view(), name='secret2'),
    path('accounts/', include('django.contrib.auth.urls')),

    #Global access: https://docs.djangoproject.com/en/2.0/topics/auth/default/#limiting-access-to-logged-in-users
    # /!\ => https://stackoverflow.com/questions/2164069/best-way-to-make-djangos-login-required-the-default /!\

    #Useful reminders: https://docs.djangoproject.com/fr/2.1/ref/urls/#path
    path('admin/', admin.site.urls),

    #TODO: make theses URLs kill-chain homogeneous
    #path('atoms/', include('atoms.urls')),
    #path('admin_wave/', include('exploitation.urls')), #VS admin.site.urls
    path('recon/', include('reconnaissance.urls')),
    path('weaponization/', include('weaponization.urls')), #the trailing slash IS necessary !
    #path('delivery/', include('aws.urls')), # => MOVE aws in delivery 
    path('delivery/', include('delivery.urls')), # => MOVE aws in delivery 
    path('exploitation/', include('exploitation.urls')),
    path('post-exploitation/', include('post-exploitation.urls')),

]