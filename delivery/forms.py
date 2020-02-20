from django import forms
from .utils import get_available_instances

class ELKProject(forms.Form):
    name = forms.CharField(max_length=50)

class ServerForm(forms.Form):
    """
        Form allowing the user to choose 2 integers
        Respectively the port used for http connection
        and the port used for https connection
    """
    http_port = forms.IntegerField()
    ssl_port = forms.IntegerField()
    listener_port = forms.IntegerField()
    C2_ip = forms.GenericIPAddressField()

class ChooseEC2Instance(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst_list = get_available_instances(self.validate_ami)
        self.fields['instance_id'] = forms.ChoiceField(choices=inst_list)

    def validate_ami(self, description):
        return True

class ChooseEC2InstanceNGINX(ChooseEC2Instance):
    def validate_ami(self, description):
        return "Amazon Linux 2" in description

class ChooseInstanceC2ELK(ChooseEC2Instance):
    def validate_ami(self, description):
        return "Ubuntu" in description or description == "Local Deployment"
