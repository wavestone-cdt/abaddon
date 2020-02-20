from django.shortcuts import render, redirect, get_object_or_404
	
import uuid
import boto3
from botocore.exceptions import ClientError
import subprocess
import os
from random import choices

# TODO: fix this: NameError: boto3 is not defined
from .ec2manager import Ec2Manager
from .cloudfrontmanager import CloudfrontManager
from .s3manager import S3Manager

#   =	=	=	=	=	=	PARSE AWS CREDENTIALS FROM ~/.aws/config AND ~/.aws/credentials =	=	=	=	=	=	#
#   =	=	=	=	=	=	So, you need to follow README and use aws configure :)			 =	=	=	=	=	=	#


f = open(os.path.expanduser("~")+"/.aws/config", "r")
c=f.readlines()[1].split('=')
exec(c[0].strip()+'="'+c[1].strip()+'"')		#Define "region"
f = open(os.path.expanduser("~")+"/.aws/credentials", "r")
lines=f.readlines()
c2=lines[1].split('=')
exec(c2[0].strip()+'="'+c2[1].strip()+'"')		#Define "aws_access_key_id"
c3=lines[2].split('=')
exec(c3[0].strip()+'="'+c3[1].strip()+'"')		#Define "aws_secret_access_key"


#   =	=	=	=	=	=	EC2 =	=	=	=	=	=	#

def get_ec2_instances():
	"""
	Wrapper around get ec2.instances.all
	"""
	ec2 = boto3.resource('ec2')
	try:
		return ec2.instances.all()
	except Exception as e:
		raise e

def ec2_dashboard(request):
	"""
	Displays existing instances
	"""
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		print("Issuing an ec2 instance creation request")
		print('instance_id', instance_id)
	# if a GET (or any other method)
	else:
		print("Displaying ec2 instance creation page")

	all_instances = get_ec2_instances()
	print(all_instances)
	return render(request, 'ec2.html', {'all_instances': all_instances})

def deploy_instance(aws_access_key_id, aws_secret_access_key, region):
	"""
	Deploys a functionnal Gophish on one or several EC2 instances
	"""

	ec2m = Ec2Manager()

	#WORKS with SSM activated => you need to: create a role, create an activation, and associate the IAM role to your EC2 instance
	"""
	1. Create a role here https://console.aws.amazon.com/iam/home#/roles, that "Allows EC2 instances to call AWS services on your behalf." id est with AmazonSSMFullAccess & IAMReadOnlyAccess
	2. In the "Instances" EC2 tab, click on the "Actions" button, then on "Instance parameters > Click/Attach the IAM Role", then chose the previous role
	3. After several minutes, it appears here: https://eu-west-3.console.aws.amazon.com/ec2/home?region=eu-west-3#ManagedInstances:sort=InstanceId
	"""
	# 1. Create
	# => https://stackoverflow.com/questions/47034797/invalidinstanceid-an-error-occurred-invalidinstanceid-when-calling-the-sendco/47036168#47036168?newreg=1bc535995fec49919b21385cd096935a
	# It appears here then: https://eu-west-3.console.aws.amazon.com/ec2/home?region=eu-west-3#ManagedInstances:sort=InstanceId

	group_name = "testgroup"	
	#ec2m.create_ssh_enabled_security_group(ssh_enabled_security_group_name) #WORKS
	key_name = str(uuid.uuid1()) #Generate a true unique name based on host mac and time (uuid1 is guarantee to generate no collision according to RFC4122
	#ec2m.create_user_key_pair(key_name)
	instance_profile_name = "ssm_instance_profile"
	#instance_profile_name = "bidule"
	role_name = "ssm_role"

	# Creates the instance profile
	print("=============== CREATING INSTANCE PROFILE ===============")
	instance_profile_created = ec2m.create_instance_profile(instance_profile_name)
	#=> output = [*] Using existing Instance Profile: ssm_instance_profile

	# Creates the role with a AWSSSMFullAccess Policy
	role_created = ec2m.create_ssm_role(role_name)
	# Add the policies to the role
	policy_attached_to_role = ec2m.attach_AmazonSSMFullAccess_to_ssm_role(role_name)
	# Add the role to the instance profile
	role_added_to_profile = ec2m.add_role_to_profile(instance_profile_name, role_name)

	print("=============== CREATING INSTANCE ===============")
	instance = ec2m.create_ec2_instance(group_name, key_name)
	instance_id = instance[0].id

	print("=============== LIST EXISTING ASSOCIATIONS ===============")
	ec2m.get_associations()

	print("=============== ASSOCIATES THE PROFILE TO OUR INSTANCE ===============")
	instance_id = ec2m.associate_profile_to_ec2_instance(instance_id, instance_profile_name, role_name)
	return instance_id

def deploy_ec2(request):
	"""
	Displays existing instances or deploys one
	"""
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		#print("POSTed data:", request.body)
		print("Issuing an ec2 instance creation request")
		instance_id = deploy_instance(aws_access_key_id, aws_secret_access_key, region)
		#return render(request, 'ec2.html', {'instance_id': instance_id})
		response = redirect('/delivery/ec2/')
		return response
	# if a GET (or any other method)
	else:
		print("Displaying ec2 instance creation page")
		#return render(request, 'ec2.html')
		response = redirect('/delivery/ec2/')
		return response

def launch_gophish_on_instance(instance_ids, commands):
	ec2m = Ec2Manager()
	print(ec2m.run(instance_ids, commands))

def deploy_gophish(request):
	"""
	Deploys gophish on the selected instance_id
	"""
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		instance_id = request.POST.get('instance_id')
		print(instance_id)
		print("Issuing gophish deployment requests")
		ec2m = Ec2Manager()
		key_name = ec2m.get_key_pair_name([instance_id])
		try:
			instances = get_ec2_instances()
			#print(instances)
			for instance in instances:
				if instance.id == instance_id:
					print("Found instance id")
					domain_name = instance.public_dns_name
					print(domain_name)

					key_path = os.getcwd()+"/aws/"+key_name+'.pem'
					command_file = os.getcwd()+"/aws/tools/install.sh"
					ssh_command = "ssh -oStrictHostKeyChecking=no -i "+key_path+" ec2-user@"+domain_name+" 'bash -s' < "+command_file
					print("SSH command being launched:", ssh_command)

					subprocess.call(ssh_command, shell=False)
					response = redirect('/delivery/ec2/')
					return response
		except Exception as e:
			#return render(request, 'ec2.html', {'instance_id': "An error occured during deployment:"+e})
			response = redirect('/delivery/ec2/')
			return response
	# if a GET (or any other method)
	else:
		#TODO: GophishForm()
		print("Displaying ec2 instance creation page")
		#return render(request, 'ec2.html')
		response = redirect('/delivery/ec2/')
		return response

#   =	=	=	=	=	=	S3 =	=	=	=	=	=	#

def create_bucket(origin):
	"""
	Created a bucket to log requests going through the cloudfront distribution & whose name is derived from the origin
	"""
	s3m = S3Manager()
	chain = [str(i) for i in choices(range(9), k=10)]
	bucket_name = "dev-"+''.join(chain)+origin
	#s3m.get_all()
	#s3m.delete("shkeru452-cloudfront-logs")
	s3m.create(bucket_name)
	return bucket_name

#   =	=	=	=	=	=	CLOUDFRONT =	=	=	=	=	=	#

def create_cf_distrib(origin, origin_id):
	"""
	Wrapper around cfrunt_create_distribution
	"""
	cl = CloudfrontManager()
	bucket_name = create_bucket(origin)
	bucket_name_url = bucket_name+".s3.amazonaws.com"
	return cl.cfrunt_create_distribution(origin, origin_id, bucket_name_url) 	# [+] Created new CloudFront distribution E1ZCIG4UGNE1R2

def get_cf_distribs():
	"""
	Wrapper around get get_all_distribs
	"""
	cl = CloudfrontManager()
	try:
		distrib_list = cl.get_all_distribs()
		return distrib_list
	except Exception as e:
		raise e

def display_distribs():
	"""
	Wrapper around get_all_distribs
	"""
	cfm = CloudfrontManager()
	displayed_distrib = []
	keys = ['Id', 'Status', 'DomainName', 'Origins']

	all_distrib = cfm.get_all_distribs()
	if all_distrib != None:
		for distrib in all_distrib:
			tmp=[distrib[k] for k in keys]
			displayed_distrib.append(tmp)

	for d in displayed_distrib:
		print(d)

	return displayed_distrib

#TODO: origin as input !
#def cloudfront_dashboard(request, origin):
def cloudfront_dashboard(request):
	"""
	Displays existing distributions or deploys a domain-fronting ready one
	"""
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		print("Issuing an cloudfront instance creation request")
		#Validate parameter
		origin=request.POST.get('domain')
		origin_id="test-"+origin
		distribution_id = create_cf_distrib(origin, origin_id)
		# [+] Created new CloudFront distribution E14BWTSXYDUP6R
		print('distribution_id', distribution_id)
	# if a GET (or any other method)
	else:
		print("Displaying cloudfront instance creation page")
		#form = cloudfrontForm()
		#print(form)
		#return render(request, 'cloudfront.html', {'form': form})
	
	all_distrib = display_distribs()
	return render(request, 'cloudfront.html', {'all_distrib': all_distrib})

#   =	=	=	=	=	=	ALL =	=	=	=	=	=	#

def infrastructure_dashboard(request):
	instances = get_ec2_instances()
	distributions = get_cf_distribs()
	return render(request, 'infrastructure.html', {'instances': instances, 'distributions': distributions})
	#ec2m.get_associations() #OK
	#instance_id = ec2m.associate_profile_to_ec2_instance(instance_id, instance_profile_name, role_name)
