from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from control_room.models import EvacuationPoint
from evacuation_manager.models import Evacuation
from helperClasses.utils.utils import *
from django.utils import timezone
from django.conf import settings
from pprint import pprint
import datetime
import secrets
import pytz
import time



def StartEvacuationView(request):

	html_template = 'evacuations/start.html'
	context = getDefaultContext(["Evacuations", "Start"])


	if (request.POST):
		pprint(request.POST)

		#return HttpResponseRedirect(request.get_full_path())
        #return HttpResponse({})
	
	response = render(request, template_name = html_template, context=context)
	return response





def EvacuationHistoryView(request):

	html_template = 'evacuations/view.html'
	context = getDefaultContext(["Evacuations", "View Evacuations"])


	if (request.POST):
		pprint(request.POST)

		#return HttpResponseRedirect(request.get_full_path())
        #return HttpResponse({})

	
	records = Evacuation.objects.filter().order_by('-date_created')
	records = [record for record in records]
	context['records'] = records
	
	response = render(request, template_name = html_template, context=context)
	return response


