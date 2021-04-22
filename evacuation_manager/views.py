from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from control_room.models import EvacuationPoint
from evacuation_manager.models import EvacuationEvent, DisasterEvent
from helperClasses.utils.utils import *
from simulation.simulation import DisasterSimulation, CityMap
from django.utils import timezone
from django.conf import settings
from pprint import pprint
import datetime
import secrets
import base64
import pytz
import time



def StartEvacuationView(request):

	html_template = 'evacuations/start.html'
	context = getDefaultContext(["Evacuations", "Start"])
	

	if (request.POST):
		#pprint(request.POST)

		if("start_evacuation" in request.POST):

			lat = float(request.POST["lat"])
			long = float(request.POST["long"])
			size = int(request.POST["size"])

			city_map = CityMap(settings.G)
			sim = DisasterSimulation(city_map, (lat, long))
			data = sim.run(policecars=0, firetrucks=0, ambulances=0, evacuations=size)

			events = sim.ApplyEvents(data["dispatch_centers"])
			events_str = ";".join(events)
			event = EvacuationEvent.objects.create(latitude = lat, longitude = long, events=events_str, size=size)
			event.name = "EvacuationEvent"+str(event.id)
			event.save()
			fig = sim.GetSimulationImage(data["dispatch_centers"])
			fig.write_image(event.image())

			#context = ShowEvent(event.name, context, EvacuationEvent)

			return HttpResponseRedirect("/evacuations/view?view_event="+event.name)
        #return HttpResponse({})
	
	response = render(request, template_name = html_template, context=context)
	return response


def ShowEvent(event_name, context, model):
	try:
		print("In show event")
		event = model.objects.get(name = event_name)
		context["event_name"] = event.name
		context["event"] = event
		context["events"] = event.events.split(";")
		context["show_event"] = True
		print("Showing Image")
	except Exception as e:
		print(e)
	return context

def ShowImage(event_name, model):
	
	print("Displaying image for ", event_name)

	image_path = model.objects.get(name=event_name).image()
	print(image_path)
	with open(image_path, "rb") as f:
		image_data = base64.b64encode(f.read())
		return HttpResponse(image_data, content_type="image/png")

	response =  HttpResponse("Hello, successful call for "+event_name)

	return response


def EvacuationHistoryView(request):
	context = getDefaultContext(["Evacuations", "View Evacuations"])
	context["heading"] = "Evacuations"
	model = EvacuationEvent

	return EventViewerView(request, context, model)


def DisasterHistoryView(request):
	context = getDefaultContext("Disasters")
	context["heading"] = "Disasters"
	model = DisasterEvent

	return EventViewerView(request, context, model)


def EventViewerView(request, context, model):

	html_template = 'evacuations/view.html'
	if (request.POST):
		pprint(request.POST)

		if("delete_event" in request.POST):
			DeleteEvent(request, model)
			return HttpResponse({})

		if("view_image" in request.POST):
			event_name = request.POST["view_image"]
			return ShowImage(event_name, model)

		if("stop_event" in request.POST):
			event_name = request.POST["stop_event"]
			StopEvent(event_name, model)


	if (request.GET):

		if("view_event" in request.GET):
			event_name = request.GET["view_event"]
			context = ShowEvent(event_name, context, model)
		
		if("stop_event" in request.GET):
			event_name = request.GET["stop_event"]
			StopEvent(event_name, model)

		

		#return HttpResponseRedirect(request.get_full_path())
        #return HttpResponse({})

	
	records = model.objects.filter().order_by('-date_created')
	records = [ [record.name,
				 (record.latitude, record.longitude),
				 record.date_created,
				 record.date_ended if record.date_ended!=None else "",
				 record.size,
	  			 record.is_running]  for record in records]
	context['records'] = records
	
	response = render(request, template_name = html_template, context=context)
	return response


def StopEvent(event_name, model):
	errors = []
	messages = []
	try:
		event = model.objects.get(name = event_name)
		if(event.is_running):
			event.is_running = False
			event.date_ended = timezone.now()
			event.save()
			messages.append(event_name+" ended")
	except:
		pass

	return errors, messages


def DeleteEvent(request, model):
	errors = []
	messages = []
	center = request.POST.get('center', "")
	try:
		model.objects.get(name = center).delete()
	except:
		pass

	return errors, messages

