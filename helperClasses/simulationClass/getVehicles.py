from helperClasses.responseFrame.responseClass.vehicle import Vehicle
from helperClasses.simulationClass.getRoadsInformation import RoadInformation
import pandas as pd
from geopy.geocoders import Nominatim

class Routes:
    def __init__(self,routes=None):
        self.routes = {}
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
        self.roadInformation.extractHashMap()
        self._geolocator = Nominatim(user_agent="geoapiExercises")
    def getVehicleInformation(self):
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

if __name__ == '__main__':
    baseDir = '/home/yoda/ML/DisasterResponse'
    pathofCSv = baseDir+'/helperClasses/simulationClass/shapes.txt'

    r = Routes(pathofCSv)
    _ = r.getVehicleInformation()
    streetCongestion = r.getStreetCongestion()
    pass
