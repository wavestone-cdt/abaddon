import boto3
import botocore
import os
# Needs  AmazonEC2FullAccess, IAMFullAccess, AmazonSSMFullAccess

class Ec2Manager:
	"""Helper for managing ec2 buckets. See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#instance"""

	def __init__(self):
		self.ec2c = boto3.client('ec2')
		self.ec2r = boto3.resource('ec2')
		self.iamc = boto3.client('iam')
		self.ssm_client = boto3.client('ssm')

	# besoin
	def create_instance_profile(self, instance_profile_name):
		"""
		Creates an instance profile to which we will later attach a role
		Reference: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html
		If you manage your roles from the AWS CLI or the AWS API, you create roles and instance profiles as separate actions.
		Because roles and instance profiles can have different names, you must know the names of your instance profiles as well as the names of roles they contain.
		That way you can choose the correct instance profile when you launch an EC2 instance.
		"""

		try:
			profiles = self.iamc.list_instance_profiles()

			for profile in profiles['InstanceProfiles']:
				if instance_profile_name in profile['InstanceProfileName']:
					print('[*] Using existing Instance Profile: {}'.format(profile['InstanceProfileName']))
					return True

			instance_profile = self.iamc.create_instance_profile(InstanceProfileName=instance_profile_name)

			if instance_profile['ResponseMetadata']['HTTPStatusCode'] is 200:
				print('[*] A new Instance Profile named "{}" has been created'.format(instance_profile_name))
				return True
			else:
				print('[*] Failed to create a new Instance Profile: {}'.format(instance_profile))
				return False

		except Exception as e:
			print('[***] Failed to create an Instance Profile: {}'.format(e))
			return False


	def create_ssm_role(self, role_name):
		"""
		Creates a role to which we will later attach an EC2 instance strategy
		"""

		try:
			roles = self.iamc.list_roles()

			for role in roles['Roles']:
				if role_name in role['RoleName']:
					print('[*] Using existing Role: {}'.format(role['RoleName']))
					return True

			role = self.iamc.create_role(
				RoleName=role_name,
				AssumeRolePolicyDocument='{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}',
				Description='A role to allow SSM access the {} instance for monitoring & command execution'.format(role_name)
				)

			if role['ResponseMetadata']['HTTPStatusCode'] is 200:
				print('[*] A new Role named "{}" has been created'.format(role_name))
				return True
			else:
				print('[***] Failed to create a new Role: {}'.format(role))
				return False

		except Exception as e:
			print('[***] Failed to create a new Role: {}'.format(e))
			return False


	def attach_AmazonSSMFullAccess_to_ssm_role(self, role_name):
		"""
		Attach the AmazonSSMFullAccess strategy to role_name 
		"""

		try:
			response = self.iamc.attach_role_policy(
				PolicyArn='arn:aws:iam::aws:policy/AmazonSSMFullAccess',
				RoleName=role_name,
				)
			if response['ResponseMetadata']['HTTPStatusCode'] == 200:
				print('[*] Successfully attached a Policy to Role: {}'.format(role_name))
				return True
			else:
				print('[***] Failed to attach a Policy to Role: {}'.format(response))
				return False

		except Exception as e:
			print('[***] Failed to attach a Policy to Role: {}'.format(e))
			return False


	def add_role_to_profile(self, instance_profile_name, role_name):

		try:
			profile = self.iamc.get_instance_profile(InstanceProfileName=instance_profile_name)

			if len(profile['InstanceProfile']['Roles']) > 0:
				for role in profile['InstanceProfile']['Roles']:
					if role['RoleName'] in role_name:
						print('[*] The Profile: "{}" already has a Role: "{}" associated'.format(instance_profile_name, role_name))
						return True
					else:
						print('[***] The Profile "{}" has an incorrect Role "{}" associated'.format(instance_profile_name, role_name))
						return False

			else:
				add_role = self.iamc.add_role_to_instance_profile(InstanceProfileName=instance_profile_name, RoleName=role_name)

				if add_role['ResponseMetadata']['HTTPStatusCode'] is 200:
					print('[*] Added Role: "{}" to the Instance Profile: "{}"'.format(role_name, instance_profile_name))
					return True
				else:
					print('[*] Failed to add the Role: "()" to the Profiel: {}'.format(role_name, instance_profile_name))
					return False

		except Exception as e:
			print('[***] Failed to create an Instance Profile: {}'.format(e))
			return False


	def create_iam_profile(self, instance_name):
		instance_profile_name = '{}InstanceProfile'.format(instance_name)
		role_name = '{}Role'.format(instance_name)

		#iam = boto3.client('iam')

		if self.create_instance_profile(instance_profile_name):
			if self.create_ssm_role(role_name):
				if self.attach_AmazonSSMFullAccess_to_ssm_role(role_name):
					if self.add_role_to_profile(instance_profile_name, role_name):
						return True
					else:
						return False

	def check_command_status(client, command_id):
		try:
			response = client.list_command_invocations(CommandId=command_id)

			if response['CommandInvocations'][0]['Status'] == 'Success':
				return 200
			else:
				time.sleep(5)
				check_command_status(client, command_id)

		except Exception as e:
			print('[***] Failed to check the SSM command status: {}'.format(e))
			return False
		
	def create_ssh_enabled_security_group(self, group_name):
		"""
		Checks if a security group with the name group_name exists: if not, creates it
		"""

		print("[*] Associating the EC2 instance with an SSH/HTTP(s) enabled security group")
		try:
			#Parameter in input must be one of: Filters, GroupIds, GroupNames, DryRun, NextToken, MaxResults
			sec_groups = self.ec2c.describe_security_groups()['SecurityGroups']

			for g in sec_groups:
				if g['GroupName'] == group_name:
					sec_group_id = g['GroupId']
					print("[*] "+group_name+" exists, it has the following group id: {}".format(sec_group_id))
					return sec_group_id

			#if no return, creates it
			print("[*] "+group_name+" does NOT exist")
			print("[*] Creating "+group_name)
			
			#https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-security-group.html
			vpcs = self.ec2c.describe_vpcs()
			vpc_id = vpcs.get('Vpcs', [{}])[0].get('VpcId', '')

			response = self.ec2c.create_security_group(GroupName=group_name,
				Description='group_name',
				VpcId=vpc_id)

			sec_group_id = response['GroupId']
			print('[*] Security Group Created %s in vpc %s.' % (sec_group_id, vpc_id))

			data = self.ec2c.authorize_security_group_ingress(
				GroupId=sec_group_id,
				IpPermissions=[
				{'IpProtocol': 'tcp',
				'FromPort': 80,
				'ToPort': 80,
				'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
				{'IpProtocol': 'tcp',
				'FromPort': 443,
				'ToPort': 443,
				'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
				{'IpProtocol': 'tcp',
				'FromPort': 3333,
				'ToPort': 3333,
				'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
				{'IpProtocol': 'tcp',
				'FromPort': 22,
				'ToPort': 22,
				'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
				])
			print('Ingress Successfully Set %s' % data)

		except botocore.exceptions.ClientError as ce:
			print("[***] botocore.exceptions.ClientError:", ce)

		except Exception as e:
			raise e

		return sec_group_id

	def get_key_pair_name(self, instance_id):
		"""
		Retrieves the name of the associated key_pair
		"""
		try:
			desc = self.ec2c.describe_instances(InstanceIds=instance_id)
			return desc['Reservations'][0]['Instances'][0]['KeyName']
		except Exception as e:
			raise e
			

	def create_user_key_pair(self, key_name):
		"""
		Checks if a key pair with the name key_name exists: if not, creates it 
		"""

		print("[*] Generating a Key Pair")
		try:
			#Parameter in input must be one of: Filters, KeyNames, DryRun
			key_pairs = self.ec2c.describe_key_pairs()['KeyPairs']
			for k in key_pairs:
				if k['KeyName'] == key_name:
					print("[*] "+key_name+" exists")
					return key_name

			#If the key does not exist, create it
			#Needs to be 0400, for security reasons and to make scp work :)
			#https://stackoverflow.com/questions/36745577/how-do-you-create-in-python-a-file-with-permissions-other-users-can-write
			key_pair = self.ec2c.create_key_pair(KeyName=key_name)
			#print(key_pair)
			str_key_pair = str(key_pair['KeyMaterial'])
			#print("Current dir is:", os.getcwd())
			key_path = os.getcwd()+"/aws/"+key_name+'.pem'
			with open(key_path, "w") as outfile:
				#print("Writing key to {} !".format(key_path))
				outfile.write(str_key_pair)
			os.chmod(key_path, 0o400)

		except botocore.exceptions.ClientError as ce:
			print("[***] botocore.exceptions.ClientError:", ce)

		except Exception as e:
			raise e

		return key_name


	def create_ec2_instance(self, group_name, key_name):
		"""
		Creates an EC2 instance
		"""

		linux_ami = "ami-06340c8c12baa6a09"

		print("[*] Creating the EC2 instance")
		sec_group_id = self.create_ssh_enabled_security_group(group_name)
		ec2_key_name = self.create_user_key_pair(key_name)

		try:
			instance = self.ec2r.create_instances(
				ImageId=linux_ami,
				MinCount=1,
				MaxCount=1,
				KeyName = ec2_key_name,
				InstanceType='t2.micro',
				NetworkInterfaces=[{'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group_id]}]
				)
			instance[0].wait_until_running()
			instance_id = instance[0].id
			print("[*] Instance {} is running!".format(instance_id))
		except Exception as e:
			raise e
		
		return instance

	def associate_profile_to_ec2_instance(self, instance_id, instance_profile_name, role_name):
		"""
		Associates an IAM instance profile with a role which has a AWSSSMFullAccess Policy to a previously created EC2 instance
		"""
		print("[*] Associating profile {} to EC2 instance {}".format(instance_profile_name , instance_id))

		try:
			for instance in self.ec2r.instances.all():
				if instance.id == instance_id:
					print("Found instance id")

					# Test is there is an existing association for the given instance_profile_name & instance_id
					associations = self.ec2c.describe_iam_instance_profile_associations()

					for a in associations['IamInstanceProfileAssociations']:
						if instance_id == a['InstanceId']:
							print('[*] Using existing IAM Instance Profile Association: {} for Instance {}'.format(a['IamInstanceProfile']['Arn'], instance_id))
							return instance_id

					self.ec2c.associate_iam_instance_profile(
						#InstanceProfileName=instance_profile_name
						IamInstanceProfile = {
						#'Arn': 'arn:aws:iam::054732315499:instance-profile/{}InstanceProfile'.format(instance_name),
											  'Name': instance_profile_name
											  },
						InstanceId=instance_id)
					print('[*] Added the required permissions to allow SSM')

					print('[*] Waiting for the instance to finish starting up')
					#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#waiters
					waiter = self.ec2c.get_waiter('instance_status_ok')
					waiter.wait(InstanceIds=[instance_id])
					print('[*] The new Instance ({}) is now ready to go'.format(instance_id))
					return instance_id
		except Exception as e:
			raise e

	def get_associations(self):
		"""
		Describes your IAM instance profile associations
		"""
		print('[*] Describing existing associations')
		ec2cli = boto3.client('ec2')
		associations = self.ec2c.describe_iam_instance_profile_associations()

		for a in associations['IamInstanceProfileAssociations']:
			print(a)
			print(a['InstanceId'])

		return associations


	def getAll(self):
		"""Print out ec2 names"""

		for instance in self.ec2r.instances.all():
			print(instance)
			print(instance.id, instance.state)

	#for every actions on ec2.Instance(id), see dir(ec2.Instance(id))
	def changeState(self, id, command):
		"""Terminate an EC2 instance"""
		instance = self.ec2r.Instance(id)
		print(instance)

		if command == "start":
			response = instance.start()
		elif command == "stop":
			response = instance.stop()
		elif command == "terminate":
			response = instance.terminate()

		print(response)
		return response

	def run(self, instance_ids, commands):
		"""
		Runs commands on remote linux instances
		:param client: a boto/boto3 ssm client
		:param commands: a list of strings, each one a command to execute on the instances
		:param instance_ids: a list of instance_id strings, of the instances on which to execute the command
		:return: the response from the send_command function (check the boto3 docs for ssm client.send_command()
		"""

		try:
			response = self.ssm_client.send_command(
				DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
				InstanceIds=instance_ids,
				Parameters={'commands': commands},
				)
			return response
		except Exception as e:
			raise e

	def get_command_status(self, command_id):
		"""
			Wrapper for ssm command : list_command
		"""
		try :
			return self.ssm_client.list_commands(CommandId=command_id)['Commands'][0]['Status']
		except Exception as e:
			print("[***] Error : can't retrieve information on command execution")
			raise e

	def get_command_status_detailled(self, command_id, instance_id):
		"""
			Wrapper for ssm command : list_command
		"""
		try :
			return self.ssm_client.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
		except Exception as e:
			print("[***] Error : can't retrieve information on command execution")
			raise e

	def deployGophish(self, instanceId, gophishPath):
		"""
		Checks if an instance (referenced by its instance id) is available, scp Gophish to it, unzip and launch it
		"""

		print('[*] Preparing to install Gophish')
		commands = [
		'git clone https://github.com/Status-418/gophish-aws-deploy.git',
		'cd gophish-aws-deploy/tools',
		'sudo bash install.sh'
		]

		try:
			for instance in self.ec2r.instances.all():
				if instance.id == instanceId:
					print("Found instance id")
					ec2_dn = instance.public_dns_name
					instance_ids = [instanceId]
					print(ec2m.run(instance_ids, commands))
					print('[*] The setup of Gophish is complete ! Please try to connect to the admin pannel at: https://{}:3333'.format(ec2_dn))

		except Exception as e:
			raise e
