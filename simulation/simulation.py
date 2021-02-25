import osmnx as ox
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import copy


class DispatchCenter:
    capacity = None
    vehicles_available = None
    lat = None
    long = None
    name = ""
    dispatch_type = ""
    vehicle_type = ""
    
    def reset(self):
        self.vehicles_available = self.capacity
        
    def dispatchVehicles(self, n):
        if(self.vehicles_available < n ):
            raise Exception("Not enough vehicles")
        self.vehicles_available -= n 
        
    def returnVehicles(self, n):
        if(self.vehicles_available + n > self.capacity):
            raise Exception("Cannot exceed total capacity")
        self.vehicles_available += n 
        
    def isPoliceStation(self):
        return self.dispatch_type=="p"
    
    def isFirestation(self):
        return self.dispatch_type=="f"
    
    def isHospital(self):
        return self.dispatch_type=="h"
        
    
class PoliceStation(DispatchCenter):
    
    def __init__(self, name, capacity, coordinates, vehicles_available=None):
        self.lat, self.long = coordinates
        self.name = name
        self.type = "p"
        self.vehicle_type = "PoliceCar"
        self.capacity = capacity
        if(vehicles_available==None):
            self.vehicles_available = capacity
        else:
            self.vehicles_available = vehicles_available

class Hospital(DispatchCenter):
    
    def __init__(self, name, capacity, coordinates, vehicles_available=None):
        self.lat, self.long = coordinates
        self.name = name
        self.type = "h"
        self.vehicle_type = "Ambulance"
        self.capacity = capacity
        if(vehicles_available==None):
            self.vehicles_available = capacity
        else:
            self.vehicles_available = vehicles_available

class FireStation(DispatchCenter):
    
    def __init__(self, name, capacity, coordinates, vehicles_available=None):
        self.lat, self.long = coordinates
        self.name = name
        self.type = "f"
        self.vehicle_type = "Firetruck"
        self.capacity = capacity
        if(vehicles_available==None):
            self.vehicles_available = capacity
        else:
            self.vehicles_available = vehicles_available
        
        
class Route:
    
    def __init__(self, origin, destination, cordinates, length, route, dispatch_center=None):
        self.origin = origin
        self.destination = destination
        self.cordinates = cordinates
        self.length = length
        self.route = route
        self.dispatch_center = dispatch_center


class CityMap:
    
    def __init__(self, G, policestation_info, hospital_info, firestation_info):
        self.G = copy.deepcopy(G)
        self.apply_congestion({})
        
        self.policestations = [PoliceStation(x[1], x[2], x[0], (x[3] if len(x)>3 else None)) for x in policestation_info]
        self.hospitals = [Hospital(x[1], x[2], x[0], (x[3] if len(x)>3 else None)) for x in hospital_info]
        self.firestations = [FireStation(x[1], x[2], x[0], (x[3] if len(x)>3 else None)) for x in firestation_info]
        
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
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},mapbox = { 'center': {'lat': lat_center, 'lon': long_center}, 'zoom': 13})
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
                                         "location": [dispatch_center.lat, dispatch_center.long],
                                         "n_vehicles": n_vehicles,
                                         "distance": route.length,
                                         "route": cordinates,})
            if(vehicles_needed<=0):
                break

        data = {"dispatch_centers": dispatch_centers, 
                "vehicles": data}
        
        return data
    
    
    def run(self, policecars=0, firetrucks=0, ambulances=0):

        hospital_dispatch = self.GetVehicleData(self.city_map.hospitals, vehicles_needed = ambulances)
        police_dispatch = self.GetVehicleData(self.city_map.policestations, vehicles_needed = policecars)
        firestation_dispatch = self.GetVehicleData(self.city_map.firestations, vehicles_needed = firetrucks)
        
        data = {"disaster_cordinates": self.disaster_cordinates,
                "dispatch_centers": police_dispatch["dispatch_centers"] + hospital_dispatch["dispatch_centers"] + firestation_dispatch["dispatch_centers"], 
                "vehicles": police_dispatch["vehicles"] + hospital_dispatch["vehicles"] + firestation_dispatch["vehicles"]}
        
        return data