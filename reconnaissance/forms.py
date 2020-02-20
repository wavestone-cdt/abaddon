from django import forms

RECONNG_MODULES = (
    ('google_site_web','google_site_web'),
    ('bing_domain_web','bing_domain_web'),
    ('netcraft','netcraft'),
    ('hackertarget','hackertarget'),
    ('brute_hosts','brute_hosts'),
)

HUNTERIO_SEARCHES = (
    ('domain','domain'),
    ('company','company'),
)

class ReconNgDomain(forms.Form):
    domain = forms.CharField()

class ReconNgModules(forms.Form):
    selected_modules = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        choices = RECONNG_MODULES,
    )

class HunterIOForm(forms.Form):
    """
    selected_modules = forms.ChoiceField(
        widget = forms.RadioSelect,
        choices = HUNTERIO_SEARCHES,
    )"""
    domain = forms.CharField()
    company = forms.CharField(required=False)

class AmassForm(forms.Form):
    domain = forms.CharField()