from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from pprint import pprint
from django.utils import timezone
from helperClasses.simulationClass.getVehicles import Routes
from helperClasses.responseFrame.responseFramework import ResponseSender
from helperClasses.responseFrame.houses.SpawingStation import SpawingStation
from helperClasses.responseFrame.responseClass.responseClasses import *
from control_room.models import PoliceStation, Hospital, FireStation
from control_room.models import Road, Shape, Disaster
from simulation.simulation import CityMap, DisasterSimulation
import logging,json

logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
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
routesPath = 'helperClasses/simulationClass/shapes.txt'
# routesPath = 'shapes.txt'
route = Routes(routesPath)
responseMap = {}
#TODO : initialise : SpawingStation objects from file SpawingStation.py

police_stations_coordinates = [[(p.latitude, p.longitude), p.name, p.capacity, p.vehicles_available] for p in PoliceStation.objects.all()]
hospitals_coordinates = [[(h.latitude, h.longitude), h.name, h.capacity, h.vehicles_available] for h in Hospital.objects.all()]
firestations_coordinates = [[(f.latitude, f.longitude), f.name, f.capacity, f.vehicles_available] for f in FireStation.objects.all()]
locationMap = {}

def getObjectsFromDb(dispatchCenters):
    retSpawningObjects = []
    for objects in dispatchCenters:
        location = objects['location']
        name = objects['name']
        capacity = objects['n_vehicles']
        route = objects['route']
        logger.info("route for location {} is {}".format(location,route))
        if "firestation" in name.lower():
            listOfVehicles = [Firetruck(name="{}:{}".format(location,i),location=None) for i in range(capacity)]
        elif "hospital" in name.lower():
            listOfVehicles = [Ambulance(name="{}:{}".format(location,i),location=None) for i in range(capacity)]
        else:
            listOfVehicles = [PoliceCar(name="{}:{}".format(location,i),location=None) for i in range(capacity)]

        spw = SpawingStation(startingLocation=location,name=name,spawningObjects=listOfVehicles,direction=route)
        retSpawningObjects.append(spw)
    return retSpawningObjects

@login_required(login_url="/accounts/login/")
def StartSimulation(request):
    html_template = "controlroom/controlroom.html"
    context = getDefaultContext("Simulation")

    if (request.POST):
        returnJson = {}
        try:
            pprint('Got the post request for the disaster')
            dataFromFrontEnd = dict(request.POST.items())
            intensity = dataFromFrontEnd['intensityvalue']
            casualities = dataFromFrontEnd['casualtiesvalue']
            lattitude = dataFromFrontEnd['lat']
            longitude = dataFromFrontEnd['long']
            address = dataFromFrontEnd['loc']
            typeofDisaster = dataFromFrontEnd['disaster-type']
            adnnInfo = ''
            logger.info('Starting disaster type {} with intensity {} at {}:{}'.format(typeofDisaster,lattitude,longitude,intensity))
            disasterObject = Disaster(latitude=lattitude,longitude=longitude,intensity=intensity,
                                                     type=typeofDisaster,stAddress=address,additionalInfo=adnnInfo,
                                                     casualities=casualities,isActive=True)
            disasterObject.save()
            returnJson['status'] = 'ok'
            returnJson['error']  = 'None'
        except Exception as e:
            pprint('error {}'.format(e))
            returnJson['status'] = 'error'
            returnJson['error']  = str(e)
        response = json.dumps(returnJson)
        return HttpResponse(response, content_type="application/json")

    elif (request.GET):
        pprint(request.GET)
        if("startSimulation" in request.GET):
            # logger.info('got the vehicle request')
            returnList = []

            disasterObjs = Disaster.objects.filter(isActive=True)
            disasterCoords = []
            for disasterObj in disasterObjs:

                lat = disasterObj.latitude
                long = disasterObj.longitude
                disaster_coordinates = (lat, long)
                disasterCoords.append(disaster_coordinates)
                city_map = CityMap(settings.G, police_stations_coordinates, hospitals_coordinates,
                                   firestations_coordinates)
                if route.getCityMap() is None:
                    route.setCityMap(city_map)
                sim = DisasterSimulation(city_map, disaster_coordinates)
                data = sim.run(policecars=10, firetrucks=10, ambulances=10)
                idOfObj = disasterObj.id
                intensity = disasterObj.intensity
                currentSeverity = "easy"
                if 4 > intensity <= 7 :
                    currentSeverity = "medium"
                elif intensity > 7:
                    currentSeverity = "hard"

                if idOfObj not in responseMap:
                    stationMap = getObjectsFromDb(dispatchCenters=data['dispatch_centers'])
                    logger.info("Adding new disaster")
                    responseMap[idOfObj] = ResponseSender(location=(disasterObj.latitude,disasterObj.longitude),
                                                          type = disasterObj.type,stationMap=stationMap,severity=currentSeverity)

                returnList.extend(responseMap[idOfObj].sendResponse())
                logger.info("monitoring responses now")
                updatedCurrentSeverity = responseMap[idOfObj].monitorSeverity()
                responseObj = responseMap[idOfObj]
                if currentSeverity is None:
                    listOfunits = responseObj.sendBackUnits(currentSeverity, None, None)
                    returnList.extend(listOfunits)
                if updatedCurrentSeverity != currentSeverity:
                    logger.info("****!severity changed!*** from {} to {}".format(currentSeverity,updatedCurrentSeverity))
                    if currentSeverity == "easy":
                        upIntensity = 1
                    elif currentSeverity == "medium":
                        upIntensity = 5
                    else:
                        upIntensity = 8
                    disasterObj.intensity = upIntensity
                    # disasterObj.save()
                    responseObj.setReverseDirection(currentSeverity, None, None)
                    # call back some police cars
                drivingBackList = responseObj.returnToStation()
                returnList.extend(drivingBackList)
            pprint("updating the disaster")
            route.updateTheroutes(disasterCoords)
            pprint(returnList)
            vehicleInfo = route.getVehicleInformation()
            for i in vehicleInfo:
                returnList.append(vehicleInfo[i].toJson())

            response = json.dumps({"status":"ok","routes":returnList})
            # pprint('inside get')
            return HttpResponse(response, content_type="application/json")
        # GET LOGIC GOES HERE
    response = render(request, template_name=html_template, context=context)
    return response
