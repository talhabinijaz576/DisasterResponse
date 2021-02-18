import osmnx as ox
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import pandas as pd

class RoadInformation:
    def __init__(self,north=53.363870,west=-6.303802,south=53.333346,east=-6.240316):
        self._north = north
        self._west = west
        self._east = east
        self._south = south

        self._G = ox.graph_from_bbox(north, south, east, west, network_type='drive')

    def extractHashMap(self):
        edges = list(self._G.edges(data=True))
        edges = pd.DataFrame(np.array(edges), columns=["Node1", "Node2", "Data"])
        hashMap = {}
        for idx, row in edges.iterrows():
            if 'name' in row['Data']:
                name = row['Data']['name']
                if 'lanes' in row['Data']:
                    lane = row['Data']['lanes']
                else:
                    lane = 1
                length = row['Data']['length']
                # print(name, lane, length)
                if type(name) == list:
                    for newName in name:
                        hashMap[newName] = {'lanes': lane, 'length': length}
                else:
                    hashMap[name] = {'lanes': lane, 'length': length}
        self._hashMap = hashMap

    def getRoadInformation(self,nameOfRoad):
        if nameOfRoad in self._hashMap:
            return self._hashMap[nameOfRoad]['lanes'],self._hashMap[nameOfRoad]['length']
        else:
            return 1,1