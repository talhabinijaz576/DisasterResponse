from helperClasses.responseFrame.responseClass.vehicle import Vehicle
from helperClasses.simulationClass.getRoadsInformation import RoadInformation
import pandas as pd
from geopy.geocoders import Nominatim
import logging

logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
class Routes:
    def __init__(self,routes=None,cityMap = None):
        """
        :param routes : route files of the buses
        :param cityMap : city map object from simulation/simulation.py, used to determine different path if their is a disaster
        """
        self.routes = {}
        self.cityMap = cityMap
        if routes is None:
            self.restart = 0
        else:
            dataFrameObj = pd.read_csv(routes,sep=',')
            #dataFrameObj['routeId'] = dataFrameObj['shape_id'].str.split('.',expand=True)[0]
            dataFrameObj['routeId'] = dataFrameObj['shape_id']
            # dataFrameObj = dataFrameObj.assign(routId=lambda x: (x['shape_id'].split('.')[0]))
            self._df = dataFrameObj
            for idx,row in self._df.iterrows():
                routeID = row['routeId']
                lat = row['shape_pt_lat']
                long = row['shape_pt_lon']
                if routeID not in self.routes:
                    self.routes[routeID] = []
                self.routes[routeID].append([lat,long])
            self.restart = len(self.routes[routeID])
            pass
        self.vehicles = {}
        self.idx = 0 # index of start array
        self.roadInformation = RoadInformation()
        self.locationToRoadMap = {}
        self.roadInformation.extractHashMap()
        self._geolocator = Nominatim(user_agent="geoapiExercises")
        self.disasterMap = {} # map used to monitor current disaster

    def isDisasterInaWay(self,disasterLocation,startLocation,endLocation):
        # logger.info("*********Disasterlocation {}, startLocation {}****************".format(disasterLocation,startLocation))
        disasterX, disasterY = disasterLocation
        startX, startY = startLocation
        endX, endY = endLocation
        if startX<= disasterX <= endX or startY <= disasterY <=endY:
            return True
        else:
            return False

    def updateTheroutes(self,disasterLocation):
        for routeKey in self.routes:
            locationToUse = self.routes[routeKey][self.idx]

            if len(disasterLocation) != 0:

                if self.idx+1 >= len(self.routes[routeKey]):
                    continue

                for key in self.disasterMap:
                    if routeKey == self.disasterMap[key][1]:
                        continue

                destination = self.routes[routeKey][self.idx + 1]
                isDisasterPresent = False
                for disasterLocationCoord in disasterLocation:
                    tempRes = self.isDisasterInaWay(disasterLocationCoord, locationToUse, destination)
                    isDisasterPresent = tempRes or isDisasterPresent

                if isDisasterPresent:
                    if self.idx != 0:
                        origin = self.routes[routeKey][self.idx]
                    else:
                        origin = locationToUse
                    roadName = self.getRoadName(locationToUse)

                    self.cityMap.apply_congestion({roadName:100}) # apply congestion to the road
                    route = self.cityMap.get_shortest_path(destination,origin)
                    cordinates = [list(c) for c in route.cordinates]

                    self.disasterMap[(locationToUse[0],locationToUse[1])] = (self.idx,len(cordinates), routeKey)

                    oldList = self.routes[routeKey][:self.idx]
                    newList = oldList+cordinates
                    newList.extend(self.routes[routeKey][self.idx:])
                    self.routes[routeKey] = newList


    def disasterEnded(self,location):
        startIdx,endIdx, routeKey = self.disasterMap[(location[0],location[1])]
        del self.routes[routeKey][startIdx:startIdx+endIdx]

    def getRoadName(self,locationToUse):
        key = (locationToUse[0],locationToUse[1])
        if key not in self.locationToRoadMap:

            positionToQry = "{},{}".format(locationToUse[0], locationToUse[1])
            location = self._geolocator.reverse(positionToQry)
            logger.info("got the roadname {} ofr {}".format(location,locationToUse))
            if 'road' in location.raw['address']:
                roadName = location.raw['address']['road']
            else:
                roadName = location.raw['address']['city_district']
            self.locationToRoadMap[key] = roadName
        return self.locationToRoadMap[key]

    def getVehicleInformation(self):
        """
        :param disasterLocation: list of coordinates points where the disaster has occured, None if no disaster has occured
        """
        for routeKey in self.routes:
            locationToUse = self.routes[routeKey][self.idx]
            if routeKey not in self.vehicles:
                self.vehicles[routeKey] = Vehicle(id=routeKey,typeOfVehicle="bus",currentLocation=locationToUse)
            else:
                self.vehicles[routeKey].setNewLocation(locationToUse)

        self.idx +=1
        if self.idx >=self.restart-2:
            self.idx = 0
        return self.vehicles

    def getRoutes(self):
        return self.routes

    def getStreetCongestion(self):
        """
        get the street name congestion
        to get it first call
        getVehicleInformation()
        then call getStreetCongestion()
        """
        roadDensity = {}
        for routeKey in self.vehicles:
            vehicleObj = self.vehicles[routeKey]
            currentLocation = vehicleObj.getLocation()
            positionToQry = "{},{}".format(currentLocation[0],currentLocation[1])
            location = self._geolocator.reverse(positionToQry)
            if 'road' in location.raw['address']:
                roadName = location.raw['address']['road']
            else:
                roadName = location.raw['address']['city_district']

            if roadName not in roadDensity:
                roadDensity[roadName] =0
            roadDensity[roadName] +=1
        for roadName in roadDensity:
            lanes, length = self.roadInformation.getRoadInformation(roadName)
            oldDensity = roadDensity[roadName]
            if type(lanes) == list:
                lanes = lanes[0]
            newDensity = oldDensity/float(float(lanes)*float(length))
            roadDensity[roadName] = newDensity
        return roadDensity

    def getCityMap(self):
        return self.cityMap

    def setCityMap(self,var):
        self.cityMap = var
if __name__ == '__main__':
    import json
    baseDir = '/home/yoda/ML/DisasterResponse'
    pathofCSv = baseDir+'/helperClasses/simulationClass/shapes.txt'

    r = Routes(pathofCSv)
    _ = r.getVehicleInformation()
    streetCongestion = r.getStreetCongestion()
    with open("sample.json", "w") as outfile:
        json.dump(streetCongestion, outfile)
    pass
