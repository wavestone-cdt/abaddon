import requests
import boto3
from .models import RedELK_Local, RedELK, Nginx, Infra


def get_instances():
    ec2r = boto3.resource('ec2')
    try:
        return ec2r.instances.all()
    except Exception as e:
        raise e

def get_available_instances(validate_ami):
    inst_list = []
    ec2c = boto3.client('ec2')
    available_instances = get_instances()
    if len(Infra.objects.all())==0:
        RedELK_Local.objects.all().delete()
        RedELK.objects.all().delete()
        Nginx.objects.all().delete()
    if validate_ami("Local Deployment") and not RedELK_Local.objects.all():
        my_ip = requests.get('https://api.ipify.org').text
        inst_list.append(({'id': "Local Deployment", 'ip': my_ip, 'public_dns': "N/A"}, "Local Deployment"))
    for inst in available_instances:
        ami_desc = ec2c.describe_images(ImageIds=[inst.image_id])['Images'][0]['Description']
        try:
            RedELK.objects.get(pk=inst.public_ip_address)
            continue
        except RedELK.DoesNotExist:
            pass
        try:
            Nginx.objects.get(pk=inst.public_ip_address)
            continue
        except Nginx.DoesNotExist:
            pass
        if validate_ami(ami_desc) and \
                inst.public_ip_address is not None:
            inst_list.append(({'id': inst.id, 'ip':inst.public_ip_address, 'public_dns': inst.public_dns_name}, inst.id))
    return inst_list

