import uuid, random, datetime, json, copy, os, tempfile, zipfile, time
import shlex

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from wsgiref.util import FileWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
from django.db.models import Count, F, Q#, Min, Sum, Avg
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import PeriodicTask, IntervalSchedule, PeriodicTasks
from import_export import resources
from export_download.views import ResourceDownloadMixin
from django.views.generic import ListView
from celery.task.control import inspect
from datetime import datetime, timedelta
from pytz import timezone
from xmlrpc import client

from abaddon.settings import TIME_ZONE
from .forms import ScanForm, HomeForm
from .back import NmapManager
from .resources import NmapResource
from .models import Nmap


from django.template.response import TemplateResponse
from django.views.generic import TemplateView
    
def file_upload(request):
    save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', request.FILES['file'])
    path = default_storage.save(save_path, request.FILES['file'])
    return default_storage.path(path)

def active_scans(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        scanform = ScanForm(request.POST,request.FILES)
        #print(form)
        # check whether it's valid: https://docs.djangoproject.com/fr/2.1/topics/forms/#field-data
        if scanform.is_valid():
            # process the data in form.cleaned_data as required
            title = scanform.cleaned_data['title']
            description = scanform.cleaned_data['description']
            targets = scanform.cleaned_data['targets']
            file = scanform.cleaned_data['file']
            scanFrequency = scanform.cleaned_data['scanFrequency']
            scanengine = scanform.cleaned_data['scanengine']
            nmapOptions = scanform.cleaned_data['nmapOptions']
            
            #Process nmap or nessus and send response
            if scanengine == "nmap":
                NmapManager.nmapProcess.apply_async((title, targets, file, nmapOptions), eta=scanFrequency)
                #NmapManager.nmapProcess.delay(title,targets,file,nmapOptions)
                output_html = "<html><body>Hello World! from %s </body></html>" % NmapManager.DBtoCSV()
                #return HttpResponse(output_html)
                return redirect('/recon/active-scans/results')
            elif scanengine == "nessus":
                NmapManager.nessusProcess(title,targets,file)
                output_html = "<html><body>Sorry, Nessus is not implemented yet.</body></html>"
                return HttpResponse(output_html)
            else:
                return HttpResponse("<html><body>Scanengine different of nmap or nessus !</body></html>")
        else:
            return HttpResponse("<html><body>Invalid form !</body></html>")

    # if a GET (or any other method) we'll create a blank form
    else:
        scanform = ScanForm()
        return render(request, 'active_scans.html', {
        'scanform': scanform,
        })

def results(request):
    # if this is a GET request we need to send the page
    if request.method == 'GET':
        sql_results = Nmap.objects.all()
        print(sql_results)
        i = inspect()
        scheduled = i.scheduled()
        print(scheduled)
        active = i.active()
        reserved = i.reserved()
        print(reserved)
        print(active)
        #active = 1
        if (active == "{'celery@kw': []}" or active == "NONE") and (scheduled == "{'celery@kw': []}" or scheduled == "NONE"):
            status = 'ended'
        else:
            status = 'on going'

        #json_data = NmapManager.JSONforGraph()
        return render(request, 'report-scan.html', locals(), {'status': status, 'active': active, "scheduled": scheduled, "json_data": 'test'})#json_data})

    # if a POST (or any other method) send a 404
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

def export(request):
    # if this is a GET request we need to send the page
    if request.method == 'GET':
        export_type = request.GET.get('type')
        if export_type == 'CSV':
            data = NmapManager.DBtoCSV()
            response = HttpResponse(data, content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=export.csv'
            return response
        elif export_type == 'JSON':
            data = NmapManager.DBtoJSON()
            response = HttpResponse(data, content_type="application/json")
            response['Content-Disposition'] = 'inline; filename=export.json'
            return response
        elif export_type == 'YAML':
            data = NmapManager.DBtoYAML()
            response = HttpResponse(data, content_type="application/yaml")
            response['Content-Disposition'] = 'inline; filename=export.yaml'
            return response
        else:
            return HttpResponseNotFound('<h1>Page not found</h1>')
        #return render(request, 'export.csv', csv)

    # if a POST (or any other method) we'll send the page
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

def passive_scan(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = HomeForm(request.POST)
        #print(form)
        # check whether it's valid: https://docs.djangoproject.com/fr/2.1/topics/forms/#field-data
        if form.is_valid():
            # process the data in form.cleaned_data as required
            text = form.cleaned_data['post']
            return render(request, 'passive_scan.html', {'form': form, 'text': text})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = HomeForm()
        #print(form)
        return render(request, 'passive_scan.html', {'form': form})
