from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from pprint import pprint
from django.utils import timezone
from helperClasses.simulationClass.getVehicles import Routes
from helperClasses.responseFrame.responseFramework import ResponseSender
from control_room.models import Road, Shape, Disaster
import logging,json

def getDefaultContext(request):
    context = {}
    return context


@login_required(login_url="/accounts/login/")
def ControlRoomHomeView(request):

    html_template = "controlroom/controlroom.html"
    context = getDefaultContext(request)
    
    if(request.POST):
        pprint(request.POST)
        # POST LOGIC GOES HERE

        if("GET_CURRENT_DATE" in request.POST):
            response = str(timezone.now())
            print("Response : ", response)
            return HttpResponse(response)


    if(request.GET):
        pprint(request.GET)
        
        # GET LOGIC GOES HERE


    response = render(request, template_name = html_template, context=context)
    return response

#logger = logging.getLogger(__name__)
routesPath = '/home/yoda/Downloads/google_transit_dublinbus/shapes.txt'
# routesPath = 'shapes.txt'
#routesPath = 'C:/Users/Kaushik/Desktop/DisasterResponse/helperClasses/simulationClass/shapes.txt'
route = Routes(routesPath)
responseMap = {}
#TODO : initialise : SpawingStation objects from file SpawingStation.py

@login_required(login_url="/accounts/login/")
def StartSimulation(request):
    html_template = "controlroom/controlroom.html"
    context = getDefaultContext(request)

    # add responseFramework object
    if (request.GET):
        pprint(request.GET)
        if("startSimulation" in request.GET):
            # logger.info('got the vehicle request')
            disasterObjs = Disaster.objects.filter(isActive=True)
            returnList = []

            for disasterObj in disasterObjs:
                idOfObj = disasterObj['id']
                stationMap = None #TODO ask talha for this
                if idOfObj not in responseMap:
                    responseMap[idOfObj] = ResponseSender(location=(disasterObj['latitude'],disasterObj['longitude']),
                                                          type = disasterObj['type'],stationMap=stationMap,severity=
                                                          disasterObj['intensity'])
                returnList.extend(responseMap[idOfObj].sendResponse())
                currentSeverity = responseMap[idOfObj].monitorSeverity()
                responseObj = responseMap[idOfObj]
                if currentSeverity is None:
                    listOfunits = responseObj.sendBackUnits(currentSeverity, None, None)
                    returnList.extend(listOfunits)
                if currentSeverity != disasterObj['intensity']:
                    disasterObj.intensity = currentSeverity
                    listOfunits = responseObj.sendBackUnits(currentSeverity, None, None)
                    # call back some police cars
                    returnList.extend(listOfunits)

            vehicleInfo = route.getVehicleInformation()
            for i in vehicleInfo:
                returnList.append(vehicleInfo[i].toJson())
            response = json.dumps({"status":"ok","routes":returnList})
            pprint('inside get')
            return HttpResponse(response, content_type="application/json")
        # GET LOGIC GOES HERE
    response = render(request, template_name=html_template, context=context)
    return response