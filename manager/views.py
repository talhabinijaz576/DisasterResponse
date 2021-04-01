from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from control_room.models import FireStation, PoliceStation, Hospital
from helperClasses.utils.utils import *
from django.utils import timezone
from django.conf import settings
from pprint import pprint
import datetime
import secrets
import pytz
import time


def ManagerView(request):

    page = request.path.replace("developer", "").replace("/", '').lower()
    if('hospitals' in page): 
        context = getDefaultContext("Hospitals")
        CenterModel = Hospital
    elif('policestation' in page): 
        context = getDefaultContext("Police Stations")
        CenterModel = PoliceStation
    elif('firestation' in page): 
        context = getDefaultContext("Fire Stations")
        CenterModel = FireStation


    return DispatchCenterView(request, context, CenterModel)


def DispatchCenterView(request, context, CenterModel):

	html_template = 'manager/manager.html'

	if (request.POST):
		pprint(request.POST)

		if("access_key_form" in request.POST):
			errors, messages = CreateOrSaveDispatchCenter(request)
			return HttpResponseRedirect(request.get_full_path())

		if("delete_access_key" in request.POST):
			errors, messages = DeleteDispatchCenter(request)
			return HttpResponseRedirect(request.get_full_path())

		try:
			context["errors"] = errors
			context["messages"] = messages
		except:
			pass
	
	records = CenterModel.objects.filter().order_by('-date_modified')
	records = [[record.name,
                record.date_modified,
				record.vehicles_available,
                record.capacity 
				] for record in records]
	context['records'] = records
	
	response = render(request, template_name = html_template, context=context)
	return response


def DeleteAccessKey(request):
	errors = []
	messages = []
	key_to_delete = request.POST.get('delete_access_key', "")
	try:
		access_key = AssetAccessKey.objects.get(key = key_to_delete)
		access_key.delete()
		messages.append("Access Key deleted")
	except:
		errors.append("Access Key could not be deleted")

	return errors, messages


