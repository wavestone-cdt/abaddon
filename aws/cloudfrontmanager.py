import boto3
import botocore
import os
import time

"""
There is no cloudfront resource in boto3
The available resources are:
   - cloudformation
   - cloudwatch
   - dynamodb
   - ec2
   - glacier
   - iam
   - opsworks
   - s3
   - sns
   - sqs

"""

# Credits: https://github.com/BerryCloud/boto-aws-cloudfront
# Needs CloudFrontFullAccess permission

"""Simplify CloudFront managing for static websites"""

DEFAULT_CONFIG = {
    'cache_forward_cookies_mode': 'none',
    'cache_forward_querystring': False,
    'cache_trusted_signers': [],
    'certificate_arn': None,
    'certificate_iam': None,
    'certificate_source': '',
    'enabled': True,
    'http_version': 'http2',
    'https_behavior': 'redirect-to-https',
    'ipv6': True,
    'price_class': 'PriceClass_100',
    'root_object': '',
}

def clear_dict(config):
    """
    Clear dictionary of null values
    """
    return dict((k, v) for k, v in config.iteritems() if v != None)

def get_list_config(data):
    """
    Get typical AWS compatible list structure
    """
    return {
        'Quantity': len(data),
        'Items': data,
    }

def map_bucket_to_s3_target(bucket_name, region):
    """
    Translate S3 bucket name into origin config base
    """
    s3_source = '%s.s3-website-%s.amazonaws.com' % (bucket_name, region)
    return {
        'DomainName': s3_source,
        'Id': s3_source,
    }

def map_s3_target_to_origin(s3_target):
    """
    Translate target into AWS compatible origin config
    """
    return {
        'DomainName': s3_target['DomainName'],
        'Id': s3_target['Id'],
        'CustomOriginConfig': {
            'HTTPPort': 80,
            'HTTPSPort': 443,
            'OriginProtocolPolicy': 'http-only',
            'OriginSslProtocols': {
                'Quantity': 3,
                'Items': ['TLSv1', 'TLSv1.1', 'TLSv1.2'],
            },
            'OriginReadTimeout': 30,
            'OriginKeepaliveTimeout': 5,
        },
        'OriginPath': '',
        'CustomHeaders': {
            'Quantity': 0,
        },
    }

def map_origin_to_bucket_name(origin):
    """
    Translate origin into S3 bucket name
    """
    if '.s3-website-' in origin['Id']:
        index = origin['Id'].find('.s3-website-')
        return origin['Id'][:index]
    return origin['Id']

def normalize_config(desired_config):
    """
    Fill undefined config values with default config
    """
    normalized_config = DEFAULT_CONFIG.copy()
    normalized_config.update(desired_config)
    return normalized_config

def get_aws_config(desired_config, bucket_name):
    """
    Get AWS config from module config
    """
    distro_config = normalize_config(desired_config)
    buckets = [
        map_bucket_to_s3_target(bucket, distro_config.get('region'))
        for bucket in distro_config.get('s3_buckets')
    ]
    bucket_source = buckets[0]

    signers = distro_config.get('cache_trusted_signers')
    certificate_source = distro_config.get('certificate_source')
    use_default_certificate = False

    if certificate_source == 'acm':
        certificate = distro_config.get('certificate_arn')
    elif certificate_source == 'iam':
        certificate = distro_config.get('certificate_iam')
    else:
        certificate = None
        certificate_source = ''
        use_default_certificate = True

    config = {
        'CacheBehaviors': {'Quantity': 0},
        'Comment': distro_config.get('name'),
        'CustomErrorResponses': {'Quantity': 0},
        'DefaultCacheBehavior': {
            "AllowedMethods": {"CachedMethods": {"Quantity": 2, "Items": ["HEAD", "GET"]}, "Quantity": 7, "Items": ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]},
            'Compress': False,
            'DefaultTTL': 60,
            'ForwardedValues': {
                'Cookies': {'Forward': distro_config.get('cache_forward_cookies_mode')},
                'Headers': {'Quantity': 0},
                'QueryString': distro_config.get('cache_forward_querystring'),
                'QueryStringCacheKeys': {'Quantity': 0},
            },
            'LambdaFunctionAssociations': {
                'Quantity': 0
            },
            'MaxTTL': 3600,
            'MinTTL': 0,
            'SmoothStreaming': False,
            'ViewerProtocolPolicy': distro_config.get('https_behavior'),
            'TargetOriginId': bucket_source['Id'],
            'TrustedSigners': {
                'Enabled': len(signers) > 0,
                'Quantity': len(signers),
                'Items': signers,
            },
        },
        'DefaultRootObject': distro_config.get('root_object'),
        'Enabled': distro_config.get('enabled'),
        'HttpVersion': distro_config.get('http_version'),
        'IsIPV6Enabled': distro_config.get('ipv6'),
        'Logging': {
            'Enabled': True,
            'IncludeCookies': False,
            'Bucket': bucket_name,
            'Prefix': '',
        },
        'PriceClass': distro_config.get('price_class', 'PriceClass_100'),
        'Restrictions': {
            'GeoRestriction': {
                'RestrictionType': 'none',
                'Quantity': 0
            }
        },
        'ViewerCertificate': clear_dict({
            'CloudFrontDefaultCertificate': use_default_certificate,
            'Certificate': certificate,
            'IAMCertificateId': distro_config.get('certificate_iam'),
            'ACMCertificateArn': distro_config.get('certificate_arn'),
            'MinimumProtocolVersion': 'TLSv1',
            'SSLSupportMethod': 'sni-only',
            'CertificateSource': certificate_source,
        }),
        'WebACLId': '',
    }

    config['Aliases'] = get_list_config(distro_config.get('domains'))
    config['Origins'] = get_list_config(map(map_s3_target_to_origin, buckets))

    return clear_dict(config)

class CloudfrontManager:
	"""Helper for managing cloudfront distributions"""

	def __init__(self):
		self.client = boto3.client('cloudfront')

	def find_distrib(self, name):
		"""
		Find distribution and fetch its config
		"""
		try:
			distrib_list = self.get_all_distribs()
			distrib = None
			for item in distrib_list:
				if item.get('Comment', None) == name:
					distrib = item
					#return distrib
					break

			if distrib:
				config = self.get_distrib_config(distrib.get('Id'))
				config['Id'] = distrib['Id']
				config['DomainName'] = distrib['DomainName']
				return config
			return distrib

		except Exception as e:
			raise e

	def get_distrib_config(self, distrib_id):
		"""
		Load distribution config
		"""
		try:
			return self.client.get_distribution_config(Id=distrib_id)
		except Exception as e:
			raise e

	def get_all_distribs(self):
		"""
		Get a list of all distributions
		"""

		try:
			distrib_list = self.client.list_distributions()['DistributionList']
			if distrib_list['Quantity'] > 0:
				return distrib_list['Items']
			else:
				return None
		except Exception as e:
			raise e

	def create_distrib(self, distrib_config, bucket_name):
		"""
		Create distribution
		"""
		try:
			next_config = get_aws_config(distrib_config, bucket_name)
			next_config['CallerReference'] = distrib_config['name']
			self.client.create_distribution(DistributionConfig=next_config)
		except Exception as e:
			raise e

	def update_distrib(self, distrib, distrib_config, bucket_name):
		"""
		Update distribution config
		"""
		try:
			next_config = get_aws_config(distrib_config, bucket_name)
			next_config['CallerReference'] = distrib['DistributionConfig']['CallerReference']
			self.client.update_distribution(
				DistributionConfig=next_config,
				Id=distrib['Id'],
				IfMatch=distrib['ETag'],
			)
		except Exception as e:
			raise e

	@staticmethod
	def did_distrib_change(distribution_config, user_config):
		"""
		Compare distribution config
		"""
		try:
			return ( dict(read_aws_config(distribution_config)) != dict(normalize_config(user_config)) )
		except Exception as e:
			raise e

	def ensure_distrib_existence(self, distrib_config, bucket_name):
		"""
		Create distrib if it does not exist, update its config otherwise
		"""
		try:
			distrib = self.find_distrib(distrib_config.get('name'))
			if not distrib:
				self.create_distrib(distrib_config, bucket_name)
				return 1
			if self.did_distrib_change(distrib['DistributionConfig'], distrib_config):
				self.update_distrib(distrib, distrib_config)
				return 2
			return 3
		except Exception as e:
			raise e

	# add a domain to CloudFront
	def cfrunt_add_domain(self, domain,origin,origin_id,distribution_id):

		if not distribution_id:
			distribution_id = create_distribution(client,origin,origin_id)

		response = None
		while response is None:
			try:
				response = self.client.get_distribution_config(Id=distribution_id)
			except botocore.exceptions.ClientError as e:
				print(' [?] Got boto3 error - ' + e.response['Error']['Code'] + ': ' + e.response['Error']['Message'])
				print(' [?] Retrying...')

		aliases = response['DistributionConfig']['Aliases']

		# default maximum number of CNAMEs for one distribution
		if aliases['Quantity'] == 100:
			distribution_id = create_distribution(client,origin,origin_id)
			response = client.get_distribution_config(Id=distribution_id)
			aliases = response['DistributionConfig']['Aliases']

		if 'Items' in aliases:
			aliases['Items'].append(domain)
		else:
			aliases['Items'] = [domain]

		aliases['Quantity'] += 1
		response['DistributionConfig']['Aliases'] = aliases

		added_domain = None
		while added_domain is None:
			try:
				added_domain = self.client.update_distribution(Id=distribution_id,DistributionConfig=response['DistributionConfig'],IfMatch=response['ETag'])
				print(' [+] Added ' + str(domain) + ' to CloudFront distribution ' + str(distribution_id))
			except self.client.exceptions.CNAMEAlreadyExists as e:
				print(' [?] The domain ' + str(domain) + ' is already part of another distribution.')
				added_domain = False
			except botocore.exceptions.ClientError as e:
				print(' [?] Got boto3 error - ' + e.response['Error']['Code'] + ': ' + e.response['Error']['Message'])
				print(' [?] Retrying...')

		return distribution_id

	def cfrunt_create_distribution(self,origin,origin_id, bucket_name_url):
		"""
		Creates a new CloudFront distribution and returns the associated distribution id
		"""

		# default distribution configuration
		base_cf_config = {
			'Comment': '',
			'Aliases': {
				'Quantity': 0,
				'Items': []
			},
			'Origins': {
				'Quantity': 1,
				'Items': [
					{
						'OriginPath': '',
						'CustomOriginConfig': {
							'OriginSslProtocols': {
								'Items': [
									'TLSv1',
									'TLSv1.1',
									'TLSv1.2'
								],
								'Quantity': 3
							},
							'OriginProtocolPolicy': 'http-only',
							'OriginReadTimeout': 30,
							'HTTPPort': 80,
							'HTTPSPort': 443,
							'OriginKeepaliveTimeout': 5
						},
						'CustomHeaders': {
							'Quantity': 0
						},
						'Id': origin_id,
						'DomainName': origin
					}
				]
			},
			'CacheBehaviors': {
				'Quantity': 0
			},
			'IsIPV6Enabled': True,
			'Logging': {
				'Bucket': bucket_name_url,
				'Prefix': '',
				'Enabled': True,
				'IncludeCookies': False
			},
			'WebACLId': '',
			'DefaultRootObject': '',
			'PriceClass': 'PriceClass_All',
			'Enabled': True,
			'DefaultCacheBehavior': {
				'TrustedSigners': {
					'Enabled': False,
					'Quantity': 0
				},
				'LambdaFunctionAssociations': {
					'Quantity': 0
				},
				'TargetOriginId': origin_id,
				'ViewerProtocolPolicy': 'allow-all',
				'ForwardedValues': {
	                "Headers": {
	                    "Items": [
	                        "*"
	                    ],
	                    "Quantity": 1
	                },
					'Cookies': {
						'Forward': 'all'
					},
					'QueryStringCacheKeys': {
						'Quantity': 0
					},
					'QueryString': True
				},
				'MaxTTL': 31536000,
				'SmoothStreaming': False,
				'DefaultTTL': 86400,
	            "AllowedMethods": {"CachedMethods": {"Quantity": 2, "Items": ["HEAD", "GET"]}, "Quantity": 7, "Items": ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]},
	            #'AllowedMethods': {
	            #    'Quantity': 2,
	            #    'Items': ['GET', 'HEAD'],
	            #    'CachedMethods': {
	            #        'Quantity': 2,
	            #        'Items': ['GET', 'HEAD'],
	            #    },
	            #},
				'MinTTL': 0,
				'Compress': False
			},
			'CallerReference': str(time.time()*10).replace('.', ''),
			'ViewerCertificate': {
				'CloudFrontDefaultCertificate': True,
				'MinimumProtocolVersion': 'TLSv1',
				'CertificateSource': 'cloudfront'
			},
			'CustomErrorResponses': {
				'Quantity': 0
			},
			'HttpVersion': 'http2',
			'Restrictions': {
				'GeoRestriction': {
					'RestrictionType': 'none',
					'Quantity': 0
				}
			},
		}

		response = None
		while response is None:
			try:
				response = self.client.create_distribution(DistributionConfig=base_cf_config)
				distribution_id = response['Distribution']['Id']
				print(' [+] Created new CloudFront distribution ' + str(distribution_id))
			except botocore.exceptions.ClientError as e:
				print(' [?] Got boto3 error - ' + e.response['Error']['Code'] + ': ' + e.response['Error']['Message'])
				print(' [?] Retrying...')

		return distribution_id