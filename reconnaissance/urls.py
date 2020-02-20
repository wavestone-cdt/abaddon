from reconnaissance import views
#active_scans, passive_scans
from django.urls import path
from django.conf.urls import include

urlpatterns = [
    path('', views.ReconView.as_view(), name='recon'),
    path('passive-scans/', views.ReconView.as_view(), name='recon'),
    path('active-scans/', include('reconnaissance.active_scans.urls')),

    path('passive-scans/recon-ng', views.ReconNgView.as_view(), name='recon-ng'),
    path('passive-scans/hunterio', views.HunterioView.as_view(), name='hunterio'),
]
