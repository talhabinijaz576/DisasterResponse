import logging
import logging.config
logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Response:

    def __init__(self,name,location,direction=None):

        self._type = name
        self._point = location
        self._direction = direction
        logger.info("initialising the response for type {}".format(name))

    def actionAtSite(self):
        raise NotImplemented

    def getCurrentLocation(self):
        return self._point

    def setCurrentLocation(self,location):
        self._point = location

    def setDirection(self,location):
        self._direction = location

    def __str__(self):
        self._type