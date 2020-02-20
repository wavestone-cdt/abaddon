from import_export import resources
from .models import Nmap
#from import_export import resources
#from export_download.views import ResourceDownloadMixin
#from django.views.generic import ListView

class NmapResource(resources.ModelResource):
    class Meta:
        model = Nmap

#class NmapListView(ResourceDownloadMixin,ListView):
#	model = Nmap
#	resource_class = Nmap