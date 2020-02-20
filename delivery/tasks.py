import time
from django.utils import timezone
from celery import current_task, task
from aws.ec2manager import Ec2Manager
from .models import Nginx, Nginx_AWS, RedELK, RedELK_AWS, RedELK_Local, Infra
from .dockerManagement import deploy_nginx, deploy_redelk

STATUS = ['Error',
          'Inserting objects in database',
          'Deploying NGINX',
          'Deploying RedELK and SILENTTRINITY',
          'Done !']

def delete_objects(recorded):
    """
        Delete object in the list recorded of the django database
    """
    for obj in recorded:
        try:
            obj.delete()
        except:
            print("Error while reverting operation in database")

@task(name="deployment all")
def deploy_all(informations_instances, informations_server, name):
    """
        Run the whole deployment process
    """
    def status_update(index):
        """
            Local function updating the state of the deployment process.
            This function is useful for the deployment progress bar
        """
        current_task.update_state(
            state=STATUS[index],
            meta={
                'current': index,
                'total': len(STATUS) - 1,
            }
        )

    ec2m = Ec2Manager()

    # Keep a track of key objects inserted in database to remove
    # them in case of failure
    recorded_objects = []
    aws_deployment = informations_instances[1]["id"] != "Local Deployment"

    ### Create Nginx objects in database

    try:
        status_update(1)
        nginx_object = Nginx(ip=informations_instances[0]["ip"], launch_time=timezone.now())
        nginx_object.save()

        recorded_objects.append(nginx_object)

        nginx_aws_object = Nginx_AWS(nginx_aws_instance=nginx_object, \
                            aws_id=informations_instances[0]["id"], \
                            dns_public_name=informations_instances[0]["dns"])
        nginx_aws_object.save()

        ### Create RedELK objects in database
        redelk_object = RedELK(ip=informations_instances[1]["ip"], launch_time=timezone.now())
        redelk_object.save()
        recorded_objects.append(redelk_object)
        infra = Infra(name=name, redelk_instance=redelk_object, nginx_instance=nginx_object)
        infra.save()
        recorded_objects.append(infra)
    except Exception as e:
        print("Error : can't insert objects in db")
        print(e)
        delete_objects(recorded_objects)
        status_update(0)
        return

    status_update(2)
    ## Deploy Nginx instance
    try:
        if not deploy_nginx(ec2m, [informations_instances[0]["id"]], \
                        informations_instances[0]["ip"], \
                        informations_server[0]["http"], \
                        informations_server[0]["ssl"], \
                        informations_instances[1]["ip"]):
            print("Error during Nginx deployment")
            delete_objects(recorded_objects)
            status_update(0)
            return
    except:
        print("Error during Nginx deployment")
        delete_objects(recorded_objects)
        status_update(0)
        return



    status_update(3)
    ### Deploy redelk

    try:
        kibana_ip = deploy_redelk(informations_instances[0]["ip"], \
                                informations_instances[1]["ip"], \
                                aws_deployment, \
                                informations_server[0]["http"], \
                                informations_server[0]["ssl"], \
                                ec2m, \
                                informations_instances[1]["id"], \
                                informations_server[0]["listener_port"], \
                                informations_server[0]["C2_ip"])
    except:
        print("Error during RedELK/C2 deployment")
        delete_objects(recorded_objects)
        status_update(0)
        return

    if not kibana_ip:
        print("Error during RedELK/C2 deployment")
        status_update(0)
        delete_objects(recorded_objects)
        return

    recorded_objects = []
    try:
        redelk_spec_object = None
        if aws_deployment:
            redelk_spec_object = RedELK_AWS(redelk_aws_instance=redelk_object, \
                                    aws_id=informations_instances[1]["id"], \
                                    dns_public_name=informations_instances[1]["dns"])
            redelk_spec_object.save()
        else:
            redelk_spec_object = RedELK_Local(redelk_local_instance=redelk_object,\
                                                kibana_access=kibana_ip, \
                                                listener_port=informations_server[0]["listener_port"],
                                                serveur_ip=informations_server[0]["C2_ip"])
            redelk_spec_object.save()

        status_update(4)
        time.sleep(5) #Wait to be sure that the deployment_progress script could retrieve the information
    except Exception as e:
        print("Error : can't insert objects in db")
        delete_objects(recorded_objects)
        status_update(0)
        return
