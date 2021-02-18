from helperClasses.simulationClass.vehicle import Vehicle
import pandas as pd
class Routes:
    def __init__(self,routes=None):
        self.routes = {}
        if routes is None:
            pass
        else:
            dataFrameObj = pd.read_csv(routes,sep=',')
            dataFrameObj['routeId'] = dataFrameObj['shape_id'].str.split('.',expand=True)[0]
            # dataFrameObj = dataFrameObj.assign(routId=lambda x: (x['shape_id'].split('.')[0]))
            self._df = dataFrameObj
            for idx,row in self._df.iterrows():
                routeID = row['routeId']
                lat = row['shape_pt_lat']
                long = row['shape_pt_lon']
                if routeID not in self.routes:
                    self.routes[routeID] = []
                self.routes[routeID].append([lat,long])
            pass
        self.vehicles = {}
        self.idx = 0 # index of start array
        self.restart = len(self.routes[routeID])
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

if __name__ == '__main__':
    pathofCSv = '/home/yoda/Downloads/google_transit_dublinbus/shapes.txt'
    r = Routes(pathofCSv)