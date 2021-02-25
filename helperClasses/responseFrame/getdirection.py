import osmnx as ox
ox.config(use_cache=True, log_console=True)
import networkx as nx

def getLatAndLong(G,endPointCoord,origin_node):
    destination_node = ox.get_nearest_node(G, endPointCoord)
    route = nx.shortest_path(G, origin_node, destination_node, weight='length')
    long = []
    lat = []
    for i in route:
        point = G.nodes[i]
        long.append(point['x'])
        lat.append(point['y'])
    return lat,long

def getClosetpoint(startPOintCoord):
    return [],[],[]