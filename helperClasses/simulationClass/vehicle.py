import json
import logging.config
logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Vehicle:

    def __init__(self,id,typeOfVehicle,currentLocation=None):
        self._type = typeOfVehicle
        self._id = id
        self._currentLocation = currentLocation
        self._previousLocation = None

    def setNewLocation(self,location):
        """
        set the new location of the vehicle
        Args:
            location: new location of vehicle

        Returns:

        """
        self._previousLocation = self._currentLocation
        self._currentLocation = location

    def toJson(self):
        """
        return the json format of the class.
        Returns:
        """
        return {
            "id":self._id,"type":self._type,"currentLocation":self._currentLocation,
            "previousLocation":self._previousLocation
        }

    def jsonify(self):
        """
        return the string json which can be sent to the front end
        Returns:

        """
        return json.dumps(self.toJson())

    def __str__(self):
        return self._id

    def getLocation(self):
        return self._currentLocation