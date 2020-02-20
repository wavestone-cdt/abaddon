from django.views.generic import TemplateView
from django.shortcuts import render
from .forms import ReconNgDomain, ReconNgModules, HunterIOForm, AmassForm
#from reconnaissance.back import ReconNgManager
from .reconngmanager import ReconNgManager
from .passive_scans.hunteriomanager import HunterioManager
from .passive_scans.amassmanager import AmassManager

"""
Several POSTs on same page:
https://rock-it.pl/multiple-forms-on-one-page-in-django/ <=> https://gist.github.com/Valian/1fbca0783df7149a328877fef1013954
"""

class ReconView(TemplateView):
    #template_name = 'recon/login.html'
    template_name = 'passive_scans.html'

    def get(self, request):
        reconngdomainform = ReconNgDomain()
        reconngform = ReconNgModules()

        hunterioform = HunterIOForm()

        amassform = AmassForm()

        status = False
        args  = {'reconngdomainform': reconngdomainform, 'reconngform': reconngform, 'hunterioform': hunterioform, 'amassform': amassform, 'status': status}
        return render(request, self.template_name, args)


class ReconNgView(TemplateView):
    #template_name = 'recon/login.html'
    template_name = 'passive_scans.html'

    def post(self, request):
        reconngdomainform = ReconNgDomain(request.POST)
        reconngform = ReconNgModules(request.POST)
        selected_modules = request.POST.getlist('selected_modules')
        print(selected_modules)
        reconm = ReconNgManager()

        if reconngdomainform.is_valid():
            if len(selected_modules) != 0:
                url = reconngdomainform.cleaned_data['domain']
                listurl = url.split()
                length = len(listurl) == 1
                print(length)
                if " " in url:
                    #print(type(url))
                    lbdd = []
                    for x in listurl:
                        #print(type(lbdd))
                        bdd = reconm.globalProcess(x, selected_modules)
                        print("global process")
                        lbdd.append(bdd)
                        reconngdomainform = ReconNgDomain()
                        reconngform = ReconNgModules()
                        print(lbdd)
                    status = True
                    length = len(listurl)  == 1
                    print(length)
                    args = {'reconngdomainform': reconngdomainform,'length': length, 'url': listurl,'raws': lbdd,'reconngform':reconngform,'status': status}

                else:
                    raws = reconm.globalProcess(url, selected_modules)
                    reconngdomainform = ReconNgDomain()
                    reconngform = ReconNgModules()
                    status = True
                    args = {'reconngdomainform': reconngdomainform, 'length': length,'url': url,'raws': raws,'reconngform':reconngform,'status': status}
            else:
                reconngdomainform = ReconNgDomain()
                reconngform = ReconNgModules()
                msg = 'Please choose at least one module !'
                args = {'reconngdomainform': reconngdomainform, 'msg': msg, 'reconngform': reconngform}

        return render(request, self.template_name, args)

class HunterioView(TemplateView):
    
    template_name = 'passive_scans.html'

    def post(self, request):
        hunterioform = HunterIOForm(request.POST)
        hunteriom = HunterioManager()

        if hunterioform.is_valid():
            domain = hunterioform.cleaned_data['domain']
            company = hunterioform.cleaned_data['company']
            res = hunteriom.get_mails(domain, company)
            status = True
            #print(res)
            args = {'hunterioform': hunterioform, 'hunterio_results': res, 'status': status}
        else:
            msg = 'Please do not mess around !'
            args = {'hunterioform': hunterioform, 'msg': msg}

        return render(request, self.template_name, args)

class AmassView(TemplateView):
    
    template_name = 'passive_scans.html'

    def post(self, request):
        amassform = AmassForm(request.POST)
        amassm = AmassManager()

        if amassform.is_valid():
            domain = amassform.cleaned_data['domain']
            res = amassm.get_results(domain)
            status = True
            #print(res)
            args = {'amassform': amassform, 'amass_results': res, 'status': status}
        else:
            msg = 'Please do not mess around !'
            args = {'amassform': amassform, 'msg': msg}

        return render(request, self.template_name, args)