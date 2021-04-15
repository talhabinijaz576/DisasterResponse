import osmnx as ox
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from pprint import pprint
import copy
from control_room.models import PoliceStation, Hospital, FireStation, EvacuationPoint


class DispatchCenter:
    capacity = None
    vehicles_available = None
    lat = None
    long = None
    name = ""
    dispatch_type = ""
    vehicle_type = ""
    center = None
    
    def __init__(self, model):
        self.lat = model.latitude 
        self.long = model.longitude
        self.name = model.name
        self.capacity = model.capacity
        self.model = model
        self.vehicles_available = model.vehicles_available
        print("Model Set")


    def reset(self):
        self.vehicles_available = self.capacity
        self.center.vehicles_available =  self.capacity 
        self.center.save()
        
    def dispatchVehicles(self, n):
        if(self.vehicles_available < n ):
            raise Exception("Not enough vehicles")
        self.vehicles_available -= n 
        self.model.vehicles_available -= n 
        self.model.save()
        
    def returnVehicles(self, n):
        if(self.vehicles_available + n > self.capacity):
            raise Exception("Cannot exceed total capacity")
        self.vehicles_available += n 
        self.model.vehicles_available += n 
        self.model.save()
        
    def isPoliceStation(self):
        return self.dispatch_type=="p"
    
    def isFirestation(self):
        return self.dispatch_type=="f"
    
    def isHospital(self):
        return self.dispatch_type=="h"
        
    
class PoliceStationInterface(DispatchCenter):
    
    def __init__(self, model):
        super().__init__(model)
        self.type = "p"
        self.vehicle_type = "police car"
        
class HospitalInterface(DispatchCenter):
    
    def __init__(self, model):
        super().__init__(model)
        self.type = "h"
        self.vehicle_type = "ambulance"

class FireStationInterface(DispatchCenter):
    
    def __init__(self, model):
        super().__init__(model)
        self.type = "f"
        self.vehicle_type = "firetruck"


class EvacuationPointInterface(DispatchCenter):
    
    def __init__(self, model):
        super().__init__(model)
        self.type = "e"
        
        
class Route:
    
    def __init__(self, origin, destination, cordinates, length, route, dispatch_center=None):
        self.origin = origin
        self.destination = destination
        self.cordinates = cordinates
        self.length = length
        self.route = route
        self.dispatch_center = dispatch_center


class CityMap:
    
    def __init__(self, G, policestation_info=None, hospital_info=None, firestation_info=None):
        self.G = copy.deepcopy(G)
        self.apply_congestion({})
        
        #if(policestation_info!=None):
        #    self.policestations = [PoliceStationInterface(x[1], x[2], x[0], (x[3] if len(x)>3 else None)) for x in policestation_info]
        #else:
        #    self.policestations = [PoliceStationInterface(point.name, point.capacity (point.latitude, point.longitude)) for point in PoliceStation.objects.all()]
        #if(policestation_info!=None):
        #    self.hospitals = [HospitalInterface(x[1], x[2], x[0], (x[3] if len(x)>3 else None)) for x in hospital_info]
        #else:
        #    self.hospitals = [HospitalInterface(point.name, point.capacity (point.latitude, point.longitude)) for point in Hospital.objects.all()]
        #if(firestation_info!=None):
        #    self.firestations = [FireStationInterface(x[1], x[2], x[0], (x[3] if len(x)>3 else None)) for x in firestation_info]
        #else:
        #    self.firestations = [FireStationInterface(point.name, point.capacity (point.latitude, point.longitude)) for point in FireStation.objects.all()]


        self.policestations = [PoliceStationInterface(point) for point in PoliceStation.objects.all()]
        self.hospitals = [HospitalInterface(point) for point in Hospital.objects.all()]
        self.firestations = [FireStationInterface(point) for point in FireStation.objects.all()]
        self.evacuation_points = [EvacuationPointInterface(point) for point in EvacuationPoint.objects.all()]


        edges = list(G.edges(data=True))
        self.all_roads = [x[2].get('name') for x in edges]
        self.edges = pd.DataFrame(np.array(edges), columns = ["Node1", "Node2", "Data"])
    
    def normalize_congestion_values(self, congestion):
        return congestion
        
    def apply_congestion(self, congestion):
        congestion = self.normalize_congestion_values(congestion)
        for source, target in self.G.edges():
            edge =  self.G[source][target][0]
            road_name = edge.get("name", "NONE")
            road_name = road_name[0] if type(road_name)==list else road_name 
            traffic_indicator = congestion.get(road_name, 1.0)
            edge["weight"] = edge["length"] * traffic_indicator
        
    def reset_map(self):
        self.apply_congestion({})
        return self.G
        
    def plot_path(self, lat, long, origin_point, destination_point):
        
        fig = go.Figure(go.Scattermapbox(name = "Path", mode = "lines", lon = long, lat = lat, marker = {'size': 10}, line = dict(width = 4.5, color = 'blue')))
        
        for policestation in self.policestations:
            fig.add_trace(go.Scattermapbox(name = policestation.name, mode = "markers", lon = [policestation.long], lat = [policestation.lat], marker = {'size': 12, 'color':"blue"}))
            
        for hospital in self.hospitals:
            fig.add_trace(go.Scattermapbox(name = hospital.name, mode = "markers", lon = [hospital.long], lat = [hospital.lat], marker = {'size': 12, 'color':"pink"}))
            
        for firestation in self.firestations:
            fig.add_trace(go.Scattermapbox(name = firestation.name, mode = "markers", lon = [firestation.long], lat = [firestation.lat], marker = {'size': 12, 'color':"red"}))
        
        fig.add_trace(go.Scattermapbox(name = "Source", mode = "markers", lon = [origin_point[1]], lat = [origin_point[0]], marker = {'size': 12, 'color':"black"}))
        fig.add_trace(go.Scattermapbox(name = "Destination", mode = "markers", lon = [destination_point[1]], lat = [destination_point[0]], marker = {'size': 12, 'color':'black'}))
        
        lat_center = np.mean(lat)
        long_center = np.mean(long)
        
        fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lat = 30, mapbox_center_lon=-80)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, mapbox = { 'center': {'lat': lat_center, 'lon': long_center}, 'zoom': 13})
        fig.show()

    def find_edge(self, node1, node2):
        edges_required = self.edges[np.bitwise_and(
                                    np.bitwise_or(self.edges["Node1"]==node1, self.edges["Node2"]==node1),
                                    np.bitwise_or(self.edges["Node1"]==node2, self.edges["Node2"]==node2),
                                   )]
        if(edges_required.shape[0]!=0):
            data = edges_required.values[0, 2]
        else:
            data = None

        return data

    def getRoads(self, route):
        roads = []
        for i in range(len(route)-1):
            node1 = route[i]
            node2 = route[i+1]
            data = self.find_edge(node1, node2)
            if(data!=None):
                road = data.get("name", "")
                roads.append(road)

        cordinates = []
        for node_id in route:
            node = self.G.nodes[node_id]
            cordinates.append((node["y"], node["x"]))
        return roads, cordinates
    
    def get_shortest_path(self, destination_point, origin_point=None, weight = "weight", dispatch_center=None, plot_map=False):
        if(dispatch_center!=None):
            origin_point = (dispatch_center.lat, dispatch_center.long)
        assert origin_point!=None 
        origin_node = ox.get_nearest_node(self.G, origin_point) 
        destination_node = ox.get_nearest_node(self.G, destination_point)
        route = nx.shortest_path(self.G, origin_node, destination_node, weight=weight)
        length = nx.shortest_path_length(self.G, source=origin_node, target=destination_node , weight=weight)
        cordinates = self.get_route(route, plot_map=plot_map)
        route = Route(origin_point, destination_point, cordinates, length, route, dispatch_center=dispatch_center)
        
        return route
        
    def get_route(self, route, plot_map=False):
        long = [] 
        lat = []  
        for i in route:
            point = self.G.nodes[i]
            long.append(point['x'])
            lat.append(point['y'])
            
        roads, cordinates = self.getRoads(route)
        
        if(plot_map):
            self.plot_path(lat, long, origin_point, destination_point)
            
        return cordinates
    

class DisasterSimulation:
    
    def __init__(self, city_map, disaster_coordinates):
        self.city_map = city_map
        self.disaster_cordinates = disaster_coordinates


    def GetSimulationImage(self, data):
        
        lat = float(self.disaster_cordinates[0])
        long = float(self.disaster_cordinates[1])

        fig = go.Figure(go.Scattermapbox(name="Disaster", mode = "markers", lon = [long], lat = [lat], marker = {'size': 24, 'color':"black"}))
        #go.Scattermapbox(name = "Path", mode = "lines", lon = long, lat = lat, marker = {'size': 10}, line = dict(width = 4.5, color = 'blue'))
        #fig.add_trace(go.Scattermapbox(name = policestation.name, mode = "markers", lon = [policestation.long], lat = [policestation.lat], marker = {'size': 12, 'color':"blue"}))
        #   
        
        colors = ["red", "blue", "orange", "purple", "green", "yellow"]
        i = 0
        for record in data:
            interface = record["interface"]
            #print("Record: ", interface.name, interface.vehicles_available, record["n_vehicles"])
            route = record["route"]
            lats = [x[0] for x in route]
            longs = [x[1] for x in route]
            fig.add_trace(go.Scattermapbox(name="Route ("+interface.name+")" , mode = "lines", lon = longs, lat = lats, marker = {'size': 10}, line = dict(width = 4.5, color = colors[i])))
            fig.add_trace(go.Scattermapbox(name=interface.name, mode = "markers", lon = [interface.long], lat = [interface.lat], marker = {'size': 20}, line = dict(width = 4.5, color = colors[i])))

            i = i+1 if (i+1) < len(colors) else 0
        #fig.add_trace(go.Scattermapbox(name = "Disaster", mode = "markers", lon = self.disaster_cordinates[1], lat = self.disaster_cordinates[0], marker = {'size': 14, 'color':"black"}))
        
        fig.add_trace(go.Scattermapbox(name = "Disaster", mode = "markers", lon = [long], lat = [lat], marker = {'size': 24, 'color':"black"}))
        fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lat = 30, mapbox_center_lon=-80)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, mapbox = { 'center': {'lat': lat, 'lon': long}, 'zoom': 13})
        
        return fig

    def ApplyEvents(self, data):
        events = []
        for record in data:
            interface = record["interface"]
            interface.dispatchVehicles(int(record["n_vehicles"]))
            if(interface.type == "e"):
                event = "Evacuated {} people to evaucation center at {}".format(record["n_vehicles"], interface.name)
            else:
                plural = "s" if int(record["n_vehicles"]) > 1 else ""
                event = "Dispatched {} {}{} from {}".format(record["n_vehicles"], interface.vehicle_type, plural, interface.name)
            events.append(event)

        return events
        
    def GetVehicleData(self, dispatch_centers, vehicles_needed = 10):
        vehicle_i = 1
        routes = []
        for dispatch_center in dispatch_centers:
            route = self.city_map.get_shortest_path(destination_point=self.disaster_cordinates, dispatch_center=dispatch_center, plot_map=False)
            routes.append(route)
            
        data = []
        dispatch_centers = []
        closest_centers_inds = np.argsort(np.array([route.length for route in routes]))
        #print([route.length for route in routes])
        #print(closest_centers_inds)
        for i in closest_centers_inds:
            route = routes[i]
            dispatch_center = route.dispatch_center
            vehicle_type = dispatch_center.vehicle_type
            n_vehicles = min(dispatch_center.vehicles_available, vehicles_needed)
            #dispatch_center.dispatchVehicles(n_vehicles)
            cordinates = [list(c) for c in route.cordinates]
            for _ in range(n_vehicles):
                vehicle_data = {"name": vehicle_type+" "+str(vehicle_i),
                                "type": vehicle_type,
                                "dispatch_center": dispatch_center.name,
                                "origin": list(route.origin),
                                "destination": list(route.destination),
                                "route": cordinates}
                vehicle_i = vehicle_i+1
                data.append(vehicle_data)
            vehicles_needed = vehicles_needed - n_vehicles
            if(n_vehicles>0):
                dispatch_centers.append({"name": dispatch_center.name,
                                         "interface": dispatch_center,
                                         "location": [dispatch_center.lat, dispatch_center.long],
                                         "n_vehicles": n_vehicles,
                                         "distance": route.length,
                                         "route": cordinates,})
            if(vehicles_needed<=0):
                break

        data = {"dispatch_centers": dispatch_centers, 
                "vehicles": data}
        
        return data
    
    
    def run(self, policecars=0, firetrucks=0, ambulances=0, evacuations=0):
        print("*******************")
        print("Running Simulation")
        print("*******************")
        print()
        hospital_dispatch = self.GetVehicleData(self.city_map.hospitals, vehicles_needed = ambulances)
        police_dispatch = self.GetVehicleData(self.city_map.policestations, vehicles_needed = policecars)
        firestation_dispatch = self.GetVehicleData(self.city_map.firestations, vehicles_needed = firetrucks)
        evacuations = self.GetVehicleData(self.city_map.evacuation_points, vehicles_needed = evacuations)
        
        data = {"disaster_cordinates": self.disaster_cordinates,
                "dispatch_centers": police_dispatch["dispatch_centers"] + hospital_dispatch["dispatch_centers"] + firestation_dispatch["dispatch_centers"] + evacuations["dispatch_centers"], 
                "vehicles": police_dispatch["vehicles"] + hospital_dispatch["vehicles"] + firestation_dispatch["vehicles"] + evacuations["vehicles"]}
        

        return data