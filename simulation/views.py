from django.conf import settings
from simulation.simulation import CityMap, DisasterSimulation
from control_room.models import PoliceStation, Hospital, FireStation
from pprint import pprint
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import views
import ast


class RunSimulationView(views.APIView):

    police_stations_coordinates = [[(p.latitude, p.longitude), p.name, p.capacity, p.vehicles_available] for p in PoliceStation.objects.all()]
    hospitals_coordinates = [[(h.latitude, h.longitude), h.name, h.capacity, h.vehicles_available] for h in Hospital.objects.all()]
    firestations_coordinates = [[(f.latitude, f.longitude), f.name, f.capacity, f.vehicles_available] for f in FireStation.objects.all()]
    city_map = CityMap(settings.G, police_stations_coordinates, hospitals_coordinates, firestations_coordinates)
    

    def get(self, request):

        #http://127.0.0.1:8000/simulation/run?lat=53.338400&long=-6.246793&policecars=2&ambulances=1&firetrucks=0
        try:
            pprint(request.query_params)
            policecars = int(request.query_params.get("policecars", 0))
            firetrucks = int(request.query_params.get("firetrucks", 0))
            ambulances = int(request.query_params.get("ambulances", 0))
            lat = float(request.query_params["lat"])
            long = float(request.query_params["long"])
            disaster_coordinates = (lat, long)

            sim = DisasterSimulation(self.city_map, disaster_coordinates)
            data = sim.run(policecars=policecars, firetrucks=firetrucks, ambulances=ambulances)
            response = Response(data)
        except Exception as e:
            response = Response({"error": str(e)})
        
        return response

