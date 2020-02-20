import ast
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
from celery.result import AsyncResult
from aws.ec2manager import Ec2Manager
from .dockerManagement import undeploy_redelk, undeploy_nginx
from .models import Nginx_AWS, RedELK_AWS, RedELK_Local, Infra
from .tasks import deploy_all
from .forms import ServerForm, \
        ChooseEC2InstanceNGINX, \
        ChooseInstanceC2ELK, \
        ChooseEC2Instance, \
        ELKProject

# Contains the form used for each step of the process
FORMS = [("Create a new elk infrastructure", ELKProject),
         ("Choose EC2 instance for Nginx Proxy", ChooseEC2InstanceNGINX),
         ("Choose a deployment target for your C2/REDELK infrastructure", ChooseInstanceC2ELK),
         ("Apache/C2 Configuration", ServerForm)]

# Useful if you want to create steps which uses different templates
TEMPLATES = {"Create a new elk infrastructure": "../templates/redelk_conf_form.html",
             "Choose EC2 instance for Nginx Proxy": "../templates/redelk_conf_form.html",
             "Choose a deployment target for your C2/REDELK infrastructure": "../templates/redelk_conf_form.html",
             "Apache/C2 Configuration": "../templates/redelk_conf_form.html",}

def get_objects_as_list(model):
    """
        Return the field of a "form answer" as a list
    """
    record = []
    for obj in model.objects.all():
        record.append(obj.get_fields_as_list())
    return record

def display_elk_dashboard(request):
    """
        View displaying all information on already deployed elk infrastructure
    """
    nginx_aws_obj = get_objects_as_list(Nginx_AWS)
    redelk_aws_obj = get_objects_as_list(RedELK_AWS)
    redelk_local_obj = get_objects_as_list(RedELK_Local)
    infra_obj = get_objects_as_list(Infra)
    if request.GET.get('error')=='true' and len(Infra.objects.all())>0:
        return render(request, 'redelk_dashboard.html', \
            {'nginx_aws': nginx_aws_obj, \
            'redelk_aws': redelk_aws_obj, \
            'redelk_local': redelk_local_obj, \
            'infra': infra_obj, \
            'infra_already_deployed_error': True})
    return render(request, 'redelk_dashboard.html', \
            {'nginx_aws': nginx_aws_obj, \
            'redelk_aws': redelk_aws_obj, \
            'redelk_local': redelk_local_obj, \
            'infra': infra_obj})

def get_nginx_concrete_object(infra):
    """
        Return the nginx object contained in the django db
    """
    nginx_instance = infra.nginx_instance
    nginx_aws = Nginx_AWS.objects.get(nginx_aws_instance=nginx_instance)
    return nginx_aws

def get_redelk_concrete_object(infra):
    """
        Return the redelk object contained in the django db
    """
    redelk_instance = infra.redelk_instance
    try:
        redelk_aws = RedELK_AWS.objects.get(redelk_aws_instance=redelk_instance)
        return redelk_aws
    except RedELK_AWS.DoesNotExist:
        try:
            redelk_local = RedELK_Local.objects.get(redelk_local_instance=redelk_instance)
            return redelk_local
        except RedELK_Local.DoesNotExist:
            return None


def undeploy(request):
    """
        Undeploy the whole infrastructure
        Redirect to the dashboard.
    """
    if request.method == "POST":
        op_name = request.POST.get("op_name", "")
        try:
            infra = Infra.objects.get(name=op_name)
            nginx_concrete = get_nginx_concrete_object(infra)
            redelk_concrete = get_redelk_concrete_object(infra)
            if isinstance(redelk_concrete, RedELK_AWS):
                undeploy_redelk(redelk_concrete, True, Ec2Manager())
            else:
                undeploy_redelk(redelk_concrete, False)
            undeploy_nginx(Ec2Manager(), nginx_concrete)
        except:
            pass
    return HttpResponseRedirect('/delivery/redelk_dashboard/')

#Test if there is already a running infrastructure. Display an error in this case, start the deployement otherwise.
def launch_configure_elk_instance(request):
    if len(Infra.objects.all())>0:
        return HttpResponseRedirect('/delivery/redelk_dashboard/?error=true')
    else:
        return HttpResponseRedirect('/delivery/redelk_configuration/')


class ElkWizard(SessionWizardView):
    """
        Contains method used by the wizard form (i.e the multi step form)
        used to deploy redelk and C2 infrastructure
    """
    def get_template_names(self):
        """
            Return the template name of the current step
        """
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        informations_instances = []
        informations_server = []
        name = ""
        #first configuration is always for nginx, second is always for apache/redelk
        for i in form_list:
            if isinstance(i, ChooseEC2Instance):
                info = i['instance_id'].value()
                info = ast.literal_eval(info)
                informations_instances.append({"id": info['id'], \
                                            "ip": info['ip'], \
                                            "dns": info['public_dns']})
            elif isinstance(i, ServerForm):
                informations_server.append({"http": i['http_port'].value(), \
                                            "ssl": i['ssl_port'].value(), \
                                            "listener_port": i['listener_port'].value(), \
                                            "C2_ip": i['C2_ip'].value()})
            elif isinstance(i, ELKProject):
                name = i['name'].value()

        # deploy_all is called as a celery task in order to allow us to display
        # a progress bar. Indeed, as the deployment is quite a long process
        # it could be hard for the user to know wether the deployment was over or not.

        job = deploy_all.delay(informations_instances, informations_server, name)

        return render(self.request, 'deployment_progress.html', {'job': job.id})

### https://djangosnippets.org/snippets/2898/
def progress_deployment(requests, job_id):
    """
        Retrieve and send information on the specified celery task
    """
    job = AsyncResult(job_id)
    data = {'state': job.state, 'info': job.info}
    return HttpResponse(json.dumps(data), content_type='application/json')
