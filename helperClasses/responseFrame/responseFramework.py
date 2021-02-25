import logging
import logging.config
import time
from helperClasses.responseFrame.getdirection import getClosetpoint
from helperClasses.responseFrame.houses import SpawingStation

logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ResponseSender:

    def __init__(self,location,type,stationMap,severity='medium'):
        """
        initialise the response sender for a disaster at the location
        Args:
            severity: severity of the disaster default is medium
            location: location coords of the disaster
            type: type of disaster
        """

        #TODO : remove the severity map to some outer file
        self.severitymap = {'easy':3,'medium':6,'hard':10}
        self._severityList = {0:'easy',1:'medium',2:'hard'}
        self._location = location
        self._type = type
        self._severity = severity
        self._stationMap = stationMap # it is also sorted by the distance
        # actual minutes required to reduce the severity of the disaster if working at full capacity
        self._fullTimeEfficiency = 5
        self._numResponsereached = 0
        self._prevCurrentTime = None
        self._timeElapsed = None
        self._startTime = None
        self.startTime()
        self.unitsSend = None
        self._spawingRecorder = {}
        self._direction = None

    def sendResponse(self,direction):
        if self._startTime is None:
            self.startTime()

        numResponseRequired = self.severitymap[self._severity]
        logger.info('Sending the units')
        unitsSend = []
        for responseObj in self._stationMap:
            if responseObj.unitLeft() >0:
                retJson = responseObj.recieveInfo(direction,numResponseRequired) # dictionary of vehicles with there path
                self._direction = direction
                type, locationStr = responseObj._type ,responseObj.locStr()
                if type not in self._spawingRecorder:
                    self._spawingRecorder[type] = {}
                if locationStr not in self._spawingRecorder[type]:
                    self._spawingRecorder[type] = {locationStr:{'working':[]}}

                self._spawingRecorder[type][locationStr]['working'].append(retJson['units'])
                logger.info('sent {} units from {}'.format(numResponseRequired-retJson['numUnitsLeft'],responseObj))
                if retJson['status']:
                    unitsSend.extend(retJson['units'])
                    if retJson['numUnitsLeft'] == 0:
                        break
                    else:
                        numResponseRequired = retJson['numUnitsLeft']
        logger.info('sent all units now monitoring the disaster and waiting for it to end,')
        self.unitsSend = unitsSend
        return unitsSend

    def sendBackUnits(self,severity=None,spawningObjs=None,direction=None):
        """
        this function is called when the severity of the disaster is reduced or its is being completly mitigated
        severity : new severity of the disaster
        spawningObjs: new sorted list of police station, if None previously used list is used.
        direction: way back to stn
        """
        if direction is None:
            direction = self._direction

        if severity is not None:
            oldNumResponseRequired = self.severitymap[self._severity]
            newNumresponseRequired = self.severitymap[severity]
            numUnitsToSendBack = oldNumResponseRequired-newNumresponseRequired
        else:
            numUnitsToSendBack = self.severitymap[severity]

        if spawningObjs is None:
            spawingStnObjs = self._stationMap
        else:
            spawingStnObjs = spawningObjs

        unitsSentBack = 0
        sentAllUnits = False
        listOfUnits = []
        for responseObj in spawingStnObjs:
            if sentAllUnits:
                break
            type, locationStr = responseObj._type, responseObj.locStr()
            if type in self._spawingRecorder and locationStr in self._spawingRecorder[type]:
                units = self._spawingRecorder[type][locationStr]['working']
                if 'workdone' not in self._spawingRecorder[type][locationStr]:
                    self._spawingRecorder[type][locationStr]['workdone'] = []
                for unit in units:
                    if sentAllUnits:
                        break
                    unit.setDirection(direction) # sending the unit back
                    self._spawingRecorder[type][locationStr]['workdone'].append(unit)
                    unitsSentBack +=1
                    if unitsSentBack == numUnitsToSendBack:
                        sentAllUnits = True
                    listOfUnits.append(unit)

        return listOfUnits
    def continousMonitoring(self):
        #TODO : update this function later.
        currentSeverity = self.monitorSeverity()
        if currentSeverity is None:
            # disaster ended send back all units
            logger.info('reduced the severity below easy now returing')
        else:
            if currentSeverity != self._severity:
                logger.info('helping worked now severity has reduced')
                self._severity = currentSeverity
        return

    def resetAfterDisaster(self):
        self._numResponsereached = 0

    def startTime(self):
        self._startTime = time.time()

    def responseReached(self):
        self._numResponsereached +=1

    def getKey(self,val):
        for key, value in self._severityList.items():
            if val == value:
                return key

    def monitorSeverity(self):
        """
        on the basis of time and the number of response vehical this function will return the updated severity of the
        disaster at the given location
        Returns: the current severity of the disaster

        """
        logger.info('monitoring the effect of severity')
        currentTime = time.time()
        if self._timeElapsed is None:
            self._timeElapsed = currentTime - self._startTime
        else:
            self._timeElapsed += currentTime - self._prevCurrentTime
        self._prevCurrentTime = currentTime
        timeElapsedMins = self._timeElapsed/60
        currentSeverity = self._severity
        numReachedResponses = self._numResponsereached
        numResponseRequired = self.severitymap[self._severity]
        percResponseReached = (numReachedResponses/numResponseRequired)*100 # this is the efficiency of the system
        extraMinsRequired = ((100-percResponseReached)*self._fullTimeEfficiency)/100
        timeRequiredToReduceSeverity = self._fullTimeEfficiency+extraMinsRequired
        timeRemaining = timeRequiredToReduceSeverity-timeElapsedMins
        logger.info('Got {} % of responses hence the time to reduce the severity is {}'
                    .format(percResponseReached,timeRemaining))
        if timeRemaining <=0:
            # time to reduce severity
            keyOfSev = self.getKey(currentSeverity)
            keyOfnewSev = keyOfSev -1
            if keyOfnewSev >0:
                currentSeverity = self._severityList[keyOfnewSev]
            else:
                currentSeverity = None

        return currentSeverity