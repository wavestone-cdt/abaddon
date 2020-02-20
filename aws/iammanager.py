import boto3
import json

#Reference: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/iam-example-policies.html
class IamManager:

	def __init__(self):
		self.iamc = boto3.client('iam')

	def create_ssm_policy(self, policy_name):
		"""
		Created an SSM policy
		"""

		my_managed_policy = {
		    "Version": "2012-10-17",
		    "Statement": [
		        {
		            "Effect": "Allow",
		            "Action": "logs:CreateLogGroup",
		            "Resource": "RESOURCE_ARN"
		        },
		        {
		            "Effect": "Allow",
		            "Action": [
		                "dynamodb:DeleteItem",
		                "dynamodb:GetItem",
		                "dynamodb:PutItem",
		                "dynamodb:Scan",
		                "dynamodb:UpdateItem"
		            ],
		            "Resource": "RESOURCE_ARN"
		        }
		    ]
		}
		response = self.iamc.create_policy(
		  PolicyName='myDynamoDBPolicy',
		  PolicyDocument=json.dumps(my_managed_policy)
		)
		print(response)

	def attach_managed_role_policy(self):
		"""
		Attach a managed policy to an IAM role. using attach_role_policy.
		"""

		# Attach a role policy
		self.iamc.attach_role_policy(
		    PolicyArn='arn:aws:iam::aws:policy/AmazonSSMFullAccess',
		    RoleName='AmazonSSMFullAccess'
		)