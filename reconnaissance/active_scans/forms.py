from django import forms
from django.contrib.admin import widgets
#from .models import Scan, ScanCampaign, ScanDefinition
#from engines.models import Engine, EnginePolicy
#from assets.models import Asset, AssetGroup
from datetimewidget.widgets import DateTimeWidget
from datetime import datetime
from django.core.validators import RegexValidator

engines = []
policies = []
assets = []
scans = []
asset_groups = []

PERIOD_CHOICES = (
    ('days', 'Days'),
    ('hours', 'Hours'),
    ('minutes', 'Minutes'),
    ('seconds', 'Seconds'),
    #('microseconds', 'Microseconds'),
)

SCAN_TYPES = (
    ('nmap', 'nmap'),
    ('nessus', 'nessus'),
)

dateTimeOptions = {
    'format': 'dd/mm/yyyy HH:ii P',
    'autoclose': True,
    'showMeridian': False,
    #'todayBtn': True
    'todayHighlight': True,
    'minuteStep': 5,
    'pickerPosition': 'bottom-right',
    'clearBtn': True
}

nmapOptions_validator = RegexValidator(r"(-[0-9A-Za-oq-z]*)?( -[0-9A-Za-oq-z]*)*( *-p [0-9]*)( -[0-9A-Za-oq-z]*)*", "(-XX)* uniquement. Exception pour -p qui est obligatoire.")

class HomeForm(forms.Form):
    """docstring for HomeForm"""
    post = forms.CharField()

class ScanForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, max_length=1000)
    targets = forms.CharField(widget=forms.Textarea,required=False)
    file = forms.FileField(required=False)
    scanFrequency = forms.SplitDateTimeField(initial=datetime.now(),required=False,widget=widgets.AdminSplitDateTime)
    scanengine = forms.ChoiceField(choices =SCAN_TYPES, widget=forms.Select(), required=False)
    nmapOptions = forms.CharField(initial="-p - -sV", required=False, validators=[nmapOptions_validator])