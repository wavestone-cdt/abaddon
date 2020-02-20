import boto3
import botocore
import os

# Needs AmazonS3FullAccess permission
# These functions are not used in Abaddon

class S3Manager:
	"""Helper for managing S3 buckets"""

	def __init__(self):
		self.s3c = boto3.client('s3')
		self.s3r = boto3.resource('s3')

	def create(self, bucket_name):
		"""
		Wrapper around boto3.client('s3').create_bucket
		"""		
		try:
			#ERROR ! Solution: https://stackoverflow.com/questions/49665155/boto3-aws-s3-bucket-creation-error
			response = self.s3c.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-3'})
			#response = s3.create_bucket(Bucket=bucket_name, Region="eu-west-3")
			#Unknown parameter in input: "Region", must be one of: ACL, Bucket, CreateBucketConfiguration, GrantFullControl, GrantRead, GrantReadACP, GrantWrite, GrantWriteACP
		except Exception as e:
			raise e
		
		print(response)
		return response

	def get_all(self):
		"""
		Prints all bucket names
		"""
		# Print out string representation of buckets
		try:
			# Call S3 to list current buckets
			response = self.s3c.list_buckets()
			# Get a list of all bucket names from the response
			buckets = [bucket['Name'] for bucket in response['Buckets']]
			# Print out the bucket list
			print("Bucket List: %s" % buckets)
		except Exception as e:
			raise e

	def find(self, bucket_name):
		"""
		Find a bucket by its name
		"""
		# Print out string representation of buckets
		try:
			bucket = self.s3r.Bucket(bucket_name)
			return bucket
		except Exception as e:
			raise e

	def upload_data(self, fileName, bucket_name):
		# Upload a new file
		data = open(fileName, 'rb')
		# Uploads the given file using a managed uploader, which will split up large
		# files automatically and upload parts in parallel.
		self.s3c.upload_file(filename, bucket_name)

	def upload_tools(self, tools_path, bucket_url):
		"""
		TODO:
		- zip the abaddon/aws/tools directory
		- upload it to the S3 bucket
		- return the .zip URL
		"""
		pass

	def delete(self, bucket_name):
		"""
		Delete a bucket by its name
		"""
		try:
			bucket = self.find(bucket_name)
			#bucket.objects.all().delete()
			for key in bucket.objects.all():
			    key.delete()
			bucket.delete()
		except Exception as e:
			raise e
		