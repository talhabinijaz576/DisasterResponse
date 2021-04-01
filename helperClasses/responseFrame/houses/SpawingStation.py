import logging
import logging.config
from helperClasses.responseFrame.getdirection import getLatAndLong
logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SpawingStation:
    """
    This class can be used as a sole entity which can act as a hospital or as a police station.
    Below are the test cases for the class which should pass without fail !
    >>> from helperClasses.responseFrame.responseClass.responseClasses import Firetruck
    >>> location = (53.345863, -6.254423)
    >>> capacity = 5
    >>> listOfVehicles = [Firetruck(name="{}:{}".format(location,i),location=None) for i in range(capacity)]
    >>> sStn = SpawingStation("Firestation1",startingLocation=location,spawningObjects=listOfVehicles)
    >>> sStn.unitLeft()
    5
    >>> sStn.recieveInfo(8)
    {'status': False, 'units': [], 'numUnitsLeft': 8}
    >>> sStn.recieveInfo(4)
    {'status': True, 'units': {'(53.345863, -6.254423):0': {'id': '(53.345863, -6.254423):0', 'type': 'FireTruck', 'currentLocation': (53.345863, -6.254423), 'previousLocation': None}, '(53.345863, -6.254423):1': {'id': '(53.345863, -6.254423):1', 'type': 'FireTruck', 'currentLocation': (53.345863, -6.254423), 'previousLocation': None}, '(53.345863, -6.254423):2': {'id': '(53.345863, -6.254423):2', 'type': 'FireTruck', 'currentLocation': (53.345863, -6.254423), 'previousLocation': None}, '(53.345863, -6.254423):3': {'id': '(53.345863, -6.254423):3', 'type': 'FireTruck', 'currentLocation': (53.345863, -6.254423), 'previousLocation': None}}, 'numUnitsLeft': -1}
    """
    def __init__(self,name,startingLocation,spawningObjects,direction=None):
        """
        initialise the spawing station,
        Args:
            name: type of spawing station
            startingLocation: coords of the spawing station
            spawningObjects: list of objects from the class responseClasses which are the actual responses sent
        """
        self._type = name
        self._locationpoint = startingLocation
        self._spawningObjs = spawningObjects
        self._numberOfspawns = len(spawningObjects)
        self._direction = direction
        logger.info("initialising the spawning station for type {}".format(name))

    def recieveInfo(self,numberofUnitsRequired,direction=None,**kwargs):
        """
        function which should be called by the simulation software to send the responses to the location
        Args:
            severity: how bad is the disaster
            location: location coords of the disaster
            direction: list of points which our vehicle can use to navigate throught the city.
            **kwargs:

        Returns:

        """
        if direction is not None:
            self._direction = direction

        direction = self._direction
        logger.info("In station {} having {} units required units {}".format(
            self._type,self.unitLeft(),numberofUnitsRequired
        ))
        if self.unitLeft() > numberofUnitsRequired:
            #TODO : update lat long according to new trafic simulation
            # lat,long = getLatAndLong('',location,self._locationpoint)
            unitsToSend = {}
            for idx in range(0,numberofUnitsRequired):
                unitToSend = self._spawningObjs.pop(0) # always removing the first element
                logger.info("unit to send {}".format(unitsToSend))
                unitToSend.setNewLocation(self._locationpoint)
                unitToSend.setDirection(direction)
                unitsToSend[str(unitToSend)]= unitToSend.toJson()

            retJson = {'status':True,'units':unitsToSend,'numUnitsLeft':numberofUnitsRequired-self._numberOfspawns}
        else:
            retJson = {'status':False,'units':[],'numUnitsLeft':numberofUnitsRequired}
        return retJson

    def unitBack(self,vehicleObj):
        """
        when we get back a unit just increase the amount
        Returns:

        """
        self._spawningObjs.append(vehicleObj)

    def unitLeft(self):
        """
        returns the number of unit left in the station
        Returns:

        """
        return len(self._spawningObjs)

    def __str__(self):
        return self._type

    def locStr(self):
        return '{}:{}'.format(self._locationpoint[0],self._locationpoint[1])

    def setDirection(self, direction):
        self._direction = direction
    # def recieveUnitsBack(self,numUnits,direction):
    #     for

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)