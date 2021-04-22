from helperClasses.responseFrame.responseClass.vehicle import Vehicle
from helperClasses.simulationClass.getRoadsInformation import RoadInformation
import pandas as pd
import reverse_geocoder as rg
# from geopy.geocoders import Nominatim
import logging

logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Routes:
    def __init__(self,routes=None,cityMap = None):
        """
        :param routes : route files of the buses
        :param cityMap : city map object from simulation/simulation.py, used to determine different path if their is a disaster
        >>> routesPath = 'shapes.txt'
        >>> disasterLocation = [53.3480407862403,-6.25937461853027]
        >>> startLocation = [53.3480407862309,-6.25937461853027]
        >>> endLocation = [53.3480407862406,-6.25937461853028]
        >>> route = Routes(routesPath)
        >>> route.updateTheroutes(disasterLocation)
        >>> route.isDisasterInaWay(disasterLocation,startLocation,endLocation,None)
        True
        """
        self.routes = {}
        self.cityMap = cityMap
        self.vehicles = {}
        if routes is None:
            self.restart = 0
        else:
            #dataFrameObj = pd.read_csv(routes,sep=',')
            #dataFrameObj['routeId'] = dataFrameObj['shape_id'].str.split('.',expand=True)[0]
            #dataFrameObj['routeId'] = dataFrameObj['shape_id']
            # dataFrameObj = dataFrameObj.assign(routId=lambda x: (x['shape_id'].split('.')[0]))

            dataFrameObj = pd.read_csv(routes, sep=',')
            dataFrameObj = dataFrameObj[['shape_id', 'shape_pt_lat', 'shape_pt_lon']]
            dataFrameObj['routeId'] = dataFrameObj['shape_id']

            self._df = dataFrameObj

            unique_routes = set(dataFrameObj['shape_id'])

            for shape in unique_routes:
                self.routes[shape] = dataFrameObj[dataFrameObj['shape_id'] == shape][['shape_pt_lat', 'shape_pt_lon']].values.tolist()

            self.routes_length = {}
            for key in self.routes.keys():
                self.routes_length[key] = len(self.routes[key])

            self.restart = len(self.routes[shape])


        self.idx = 0 # index of start array
        self.roadInformation = RoadInformation()
        self.locationToRoadMap = {}
        self.roadInformation.extractHashMap()
        # self._geolocator = Nominatim(user_agent="geoapiExercises")
        self.disasterMap = {} # map used to monitor current disaster

    def isDisasterInaWay(self,disasterLocation,startLocation,endLocation,routeKey):
        # logger.info("*********Disasterlocation {}, startLocation {}****************".format(disasterLocation,startLocation))
        # disasterX, disasterY = disasterLocation
        # disasterKey = (disasterLocation[0], disasterLocation[1])
        # circleObjDisaster = Circle(disasterX, disasterY)
        # if circleObjDisaster.isInside(endLocation[0], endLocation[1]):
        #     if disasterKey not in self.disasterMap:
        #         self.disasterMap[disasterKey] = (Circle(disasterX, disasterY), disasterLocation, routeKey)
        #
        # return circleObjDisaster.isInside(endLocation[0], endLocation[1])
        disasterX, disasterY = disasterLocation
        startX, startY = startLocation
        endX, endY = endLocation
        if startX<= disasterX <= endX or startY <= disasterY <=endY:
            return True
        else:
            return False

    def findDestination(self,disasterLocation,locationOfPoints, routeKey):
        for idx in range(1,len(locationOfPoints)):
            startLocation = locationOfPoints[idx-1]
            endLocation = locationOfPoints[idx]
            temp = self.isDisasterInaWay(disasterLocation,startLocation,endLocation,routeKey)
            if not temp:
                return endLocation,idx
        return locationOfPoints[1],1

    def updateTheroutes(self,disasterLocation):
        logger.info("in update the routes")
        for routeKey in self.routes:

            if len(disasterLocation) != 0 and self.idx > 0:

                if self.idx+1 >= len(self.routes[routeKey]):
                    continue

                for key in self.disasterMap:
                    if routeKey == self.disasterMap[key][2]:
                        logger.info("Route already Present hence not touching this.")
                        continue
                destination = self.routes[routeKey][self.idx]
                locationToUse = self.routes[routeKey][self.idx-1]
                isDisasterPresent = False
                disasterLocationPresent = None
                for disasterLocationCoord in disasterLocation:
                    tempRes = self.isDisasterInaWay(disasterLocationCoord, locationToUse, destination, routeKey)

                    if tempRes:
                        isDisasterPresent = True
                        disasterLocationPresent = disasterLocationCoord
                        break


                if isDisasterPresent:
                    logger.info("found the disaster at location {}".format(disasterLocationPresent))
                    destinationNew,idxTillRoute = self.findDestination(disasterLocationPresent,self.routes[routeKey][self.idx:],routeKey)
                    roadName = self.getRoadName(locationToUse)

                    self.cityMap.apply_congestion({roadName:20}) # apply congestion to the road
                    route = self.cityMap.get_shortest_path(destinationNew,locationToUse)
                    cordinates = [list(c) for c in route.cordinates]

                    self.disasterMap[(locationToUse[0],locationToUse[1])] = (self.idx,len(cordinates), routeKey)

                    oldList = self.routes[routeKey][:idxTillRoute]
                    # logger.info("#### len {}".format(len(oldList)))
                    if len(oldList) >0:
                        logger.info("#### Prev Cordirnates {}".format(oldList[-1]))
                        logger.info("#### New coordinates {}".format(cordinates))
                    newList = oldList+cordinates
                    newList.extend(self.routes[routeKey][idxTillRoute:])
                    self.routes[routeKey] = newList


    def disasterEnded(self,location):
        startIdx,endIdx, routeKey = self.disasterMap[(location[0],location[1])]
        del self.routes[routeKey][startIdx:startIdx+endIdx]

    def getRoadName(self,locationToUse):
        key = (locationToUse[0],locationToUse[1])
        if key not in self.locationToRoadMap:

            # positionToQry = "{},{}".format(locationToUse[0], locationToUse[1])
            location = rg.search(key)
            # logger.info("got the roadname {} ofr {}".format(location,locationToUse))
            roadName = location[0]['name']
            # if 'road' in location.raw['address']:
            #     roadName = location.raw['address']['road']
            # else:
            #     roadName = location.raw['address']['city_district']
            self.locationToRoadMap[key] = roadName
        return self.locationToRoadMap[key]

    def getVehicleInformation(self):
        """
        :param disasterLocation: list of coordinates points where the disaster has occured, None if no disaster has occured
        """
        #for routeKey in self.routes:
        #    locationToUse = self.routes[routeKey][self.idx]
        #    if routeKey not in self.vehicles:
        #        self.vehicles[routeKey] = Vehicle(id=routeKey,typeOfVehicle="bus",currentLocation=locationToUse)
        #    else:
        #        self.vehicles[routeKey].setNewLocation(locationToUse)

        for routeKey in self.routes.keys():
            if (self.idx // self.routes_length[routeKey]) % 2 == 0:
                index = self.idx - self.routes_length[routeKey] * (self.idx // self.routes_length[routeKey])
            else:
                index = self.routes_length[routeKey] - (self.idx - self.routes_length[routeKey] * (self.idx // self.routes_length[routeKey])) - 1

            locationToUse = self.routes[routeKey][index]

            if routeKey not in self.vehicles:
                self.vehicles[routeKey] = Vehicle(id=routeKey, typeOfVehicle="bus", currentLocation=locationToUse)
            else:
                self.vehicles[routeKey].setNewLocation(locationToUse)

        self.idx +=1
        #if self.idx >=self.restart-2:
        #    self.idx = 0
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

class Circle:
    def __init__(self,centerX,centerY,radius=0.001):
        self._x = centerX
        self._y = centerY
        self.radius = radius

    def isInside(self,x,y):
        d  = self.radius**2 - ((self._x-x)**2 + (self._y-y)**2)
        if d>=0:
            return True
        else:
            return False

if __name__ == '__main__':
    # import json
    # baseDir = '/home/yoda/ML/DisasterResponse'
    # pathofCSv = baseDir+'/helperClasses/simulationClass/shapes.txt'
    #
    # r = Routes(pathofCSv)
    # _ = r.getVehicleInformation()
    # streetCongestion = r.getStreetCongestion()
    # with open("sample.json", "w") as outfile:
    #     json.dump(streetCongestion, outfile)
    import doctest
    doctest.testmod(verbose=True)
    pass
