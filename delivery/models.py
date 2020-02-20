import os
from django.db import models
from django.conf import settings
from datetime import datetime
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class ImmutableModel(models.Model):
    """
        This class should be considered as abstract
        As we don't want some models of the db to be changed
        this class block updates of an object
    """
    def save(self, *args, **kwargs):
        modelType = type(self)
        try:
            modelType.objects.get(pk=self.pk)
            raise ValidationError("{} already exists".format(self._meta.model_name))
        except modelType.DoesNotExist:
            super().save(*args, **kwargs)

    class Meta:
        abstract = True

class Nginx(ImmutableModel):
    """
        Basis model for Nginx instances
    """
    ip = models.GenericIPAddressField(primary_key=True)
    launch_time = models.DateTimeField()

    def __str__(self):
        return self.ip
    
    def get_fields_as_list(self):
	    return [self.ip, self.launch_time]

class Nginx_AWS(ImmutableModel):
    """
        Specific model for Nginx instances deployed on AWS
    """
    nginx_aws_instance = models.OneToOneField(Nginx, on_delete=models.CASCADE, primary_key=True)
    aws_id = models.CharField(max_length=50)
    dns_public_name = models.CharField(max_length=50)

    def __str__(self):
        return self.aws_id

    def get_fields_as_list(self):
	    return [self.nginx_aws_instance.ip, self.nginx_aws_instance.launch_time, self.aws_id, self.dns_public_name]

class RedELK(ImmutableModel):
    """
        Basis model for RedELK instances
    """
    ip = models.GenericIPAddressField(primary_key=True)
    launch_time = models.DateTimeField()

    def __str__(self):
        return self.ip

    def get_fields_as_list(self):
        return [self.ip, self.launch_time]

class RedELK_AWS(ImmutableModel):
    """
        Specific model for RedELK instances deployed on AWS
    """
    redelk_aws_instance = models.OneToOneField(RedELK, on_delete=models.CASCADE, primary_key=True)
    aws_id = models.CharField(max_length=50)
    dns_public_name = models.CharField(max_length=50)

    def __str__(self):
        return self.aws_id

    def get_fields_as_list(self):
	    return [self.redelk_aws_instance.ip, self.redelk_aws_instance.launch_time, self.aws_id, self.dns_public_name]

class RedELK_Local(ImmutableModel):
    """
        Specific model for RedELK instances deployed on local host
    """
    redelk_local_instance = models.OneToOneField(RedELK, on_delete=models.CASCADE, primary_key=True)
    kibana_access = models.GenericIPAddressField()
    listener_port = models.PositiveIntegerField()
    serveur_ip = models.GenericIPAddressField()

    def __str__(self):
        return "Local RedELK"

    def get_fields_as_list(self):
	    return [self.redelk_local_instance.ip, self.redelk_local_instance.launch_time, self.kibana_access, self.listener_port, self.serveur_ip]

class Infra(ImmutableModel):
    """
        Model for the whole infrastructure (I.E : Nginx + Redelk)
    """
    name = models.CharField(max_length=50, primary_key=True)
    redelk_instance = models.OneToOneField(RedELK, on_delete=models.CASCADE, unique=True)
    nginx_instance = models.OneToOneField(Nginx, on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return self.name

    def get_fields_as_list(self):
	    return [self.name, self.redelk_instance.ip, self.redelk_instance.launch_time, self.nginx_instance.ip, self.nginx_instance.launch_time]
