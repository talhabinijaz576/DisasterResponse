from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from control_room.models import FireStation, PoliceStation, Hospital, EvacuationPoint
from helperClasses.utils.utils import *
from django.utils import timezone
from django.conf import settings
from pprint import pprint
import datetime
import secrets
import pytz
import time


def ManagerView(request):

    page = request.path.lower()
    if('hospitals' in page): 
        context = getDefaultContext("Hospitals")
        CenterModel = Hospital
    elif('policestation' in page): 
        context = getDefaultContext("Police Stations")
        CenterModel = PoliceStation
    elif('firestation' in page): 
        context = getDefaultContext("Fire Stations")
        CenterModel = FireStation
    elif('evacuationpoints' in page): 
        context = getDefaultContext(["Evacuations", "Evacuation Points"])
        CenterModel = EvacuationPoint


    return DispatchCenterView(request, context, CenterModel)


def DispatchCenterView(request, context, CenterModel):

	html_template = 'manager/manager.html'

	errors = []
	messages = []
	if (request.POST):
		pprint(request.POST)

		if("save_center" in request.POST):
			context = SaveCenter(request, context, CenterModel)
			#return HttpResponseRedirect(request.get_full_path())

		if("view_center" in request.POST):
			context = ViewCenter(request, context, CenterModel)
			#return HttpResponse({})

		if("return_center" in request.POST):
			context = ReturnToCenter(request, context, CenterModel)

		if("reset_center" in request.POST):
			context = ResetCenter(request, context, CenterModel)

		if("delete_center" in request.POST):
			DeleteDispatchCenter(request)
			return HttpResponse({})
			
		context["errors"] = errors
		context["messages"] = messages
	
	records = CenterModel.objects.filter().order_by('-date_modified')
	records = [[record.name,
                record.date_modified,
				record.vehicles_available,
                record.capacity 
				] for record in records]
	context['records'] = records

	context['all_centers'] = ";".join([center.name for center in CenterModel.objects.all()])
	
	response = render(request, template_name = html_template, context=context)
	return response


def DeleteCenter(request, CenterModel):
	errors = []
	messages = []
	center = request.POST.get('center', "")
	try:
		center = CenterModel.objects.get(name = center)
		center.delete()
	except:
		pass

	return errors, messages


def SaveCenter(request, context, CenterModel):
	sent = request.POST.get("center_sent", "")
	name = request.POST.get("center_name", "")
	is_new_center = len(sent) == 0
	original_center_name = name if is_new_center else sent
	all_centers = [center.name for center in CenterModel.objects.all()]

	if(is_new_center and name in all_centers):
			context["show_popup"] = True
			context["popup_message"] = name + " already exists"
			context["popup_type"] = "error"
			return context

	try:
		center = CenterModel.objects.get(name = original_center_name)
	except:
		if(not is_new_center):
			context["show_popup"] = True
			context["popup_message"] = "Center not found"
			context["popup_type"] = "error"
			return context
		
		center = CenterModel(name = original_center_name)
	
	
	center.name = name
	try:
		center.latitude = float(request.POST.get("latitude", ""))
		center.longitude = float(request.POST.get("longitude", ""))
		center.capacity = int(request.POST.get("capacity", ""))
		center.vehicles_available = int(request.POST.get("available", ""))
	except:
		context["show_popup"] = True
		context["popup_message"] =  "Invalid input"
		context["popup_type"] = "error"
		return context
	
	center.date_modified = timezone.now()
	
	if(center.vehicles_available <= center.capacity):
		center.save()
		context["show_popup"] = True
		context["popup_message"] =  name + (" successfully created" if  is_new_center else " successfully modified")
		context["popup_type"] = "success"
	
	else:
		context["show_popup"] = True
		context["popup_message"] =  "Availability cannot exceed capacity"
		context["popup_type"] = "error"
	
	return context


def ReturnToCenter(request, context, CenterModel):
	center = request.POST.get('center_name', "")
	try:
		n_return = int(request.POST.get('n_return', "None"))
		try:
			center = CenterModel.objects.get(name = center)
			if(center.capacity >= (center.vehicles_available + n_return)):
				center.vehicles_available += n_return
				center.date_modified = timezone.now()
				center.save()
				context["show_popup"] = True
				context["popup_message"] =  "Capacity returned successfully"
				context["popup_type"] = "success"
			else:
				context["show_popup"] = True
				context["popup_message"] =  "Availability cannot exceed capacity"
				context["popup_type"] = "error"
		except:
			context["show_popup"] = True
			context["popup_message"] =  "Center not found"
			context["popup_type"] = "error"
	except:
		context["show_popup"] = True
		context["popup_message"] =  "Invalid input"
		context["popup_type"] = "error"
	

	return context

def ResetCenter(request, context, CenterModel):
	center = request.POST.get('reset_center', "")
	try:
		center = CenterModel.objects.get(name = center)
		center.vehicles_available = center.capacity
		center.date_modified = timezone.now()
		center.save()
		context["show_popup"] = True
		context["popup_message"] =  "Capacity reset successfully"
		context["popup_type"] = "success"

	except:
		context["show_popup"] = True
		context["popup_message"] =  "Center not found"
		context["popup_type"] = "error"

	

	return context



def ViewCenter(request, context, CenterModel):
	center = request.POST.get('view_center', "")
	try:
		center = CenterModel.objects.get(name = center)
		context["show_center"] = True
		context["center"] = center
	except:
		pass

	return context


