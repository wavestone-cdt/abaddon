from django import forms
from django.contrib.admin import widgets

class Ec2Form(forms.Form):
    """docstring for HomeForm"""
    post = forms.CharField()

class GophishForm(forms.Form):
    """docstring for HomeForm"""
    instance_id = forms.CharField()