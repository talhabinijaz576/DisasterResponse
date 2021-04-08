import logging
import logging.config
import time
from helperClasses.responseFrame.getdirection import getClosetpoint
from helperClasses.responseFrame.houses import SpawingStation

logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ResponseSender:
    """
    This class is the heart of our application, as this class mangaes how the vehicles move around the city, montiors if
    there is a disaster, if there is send the relevant support and diverge traffic, and also monitor the severity of the disaster
    """

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
        self._fullTimeEfficiency = 2
        self._numResponsereached = 0
        self._prevCurrentTime = None
        self._timeElapsed = None
        self._startTime = None
        self.startTime()
        self.unitsSend = None
        self._spawingRecorder = {}
        self._direction = None

    def sendResponse(self):
        if self._startTime is None:
            self.startTime()

        numResponseRequired = self.severitymap[self._severity]
        logger.info('Sending the units')
        unitsSend = []
        for responseObj in self._stationMap:
            direction = responseObj._direction
            type, locationStr = responseObj._type, responseObj.locStr()
            if self.unitsSend is None:
                if responseObj.unitLeft() >0 and numResponseRequired > 0:
                    retJson = responseObj.recieveInfo(numResponseRequired,direction) # dictionary of vehicles with there path

                    if type not in self._spawingRecorder:
                        self._spawingRecorder[type] = {}
                    if locationStr not in self._spawingRecorder[type]:
                        self._spawingRecorder[type] = {locationStr:{'driving':[]}}
                    # logger.info('units in objecets {}'.format(retJson['units']))
                    for unitObj in retJson['units']:
                        self._spawingRecorder[type][locationStr]['driving'].append(retJson['units'][unitObj])
                    self._spawingRecorder[type][locationStr]['prevLocationPtr'] = 0
                    logger.info('sent {} units from {}'.format(len(self._spawingRecorder[type][locationStr]['driving']),responseObj))
                    if retJson['status']:
                        for unitObj in retJson['units']:
                            unitsSend.append(retJson['units'][unitObj])
                        if retJson['numUnitsLeft'] == 0:
                            break
                        else:
                            numResponseRequired = retJson['numUnitsLeft']
            else:
                useThisStation = self.isStationWorking(type,locationStr)
                if useThisStation:
                    drivingunits = self._spawingRecorder[type][locationStr]['driving']
                    self._spawingRecorder[type][locationStr]['prevLocationPtr'] +=1

                    currentLocationPtr = self._spawingRecorder[type][locationStr]['prevLocationPtr']
                    logger.info("Current location Ptr is {} and length of direction is {} for location {}".format(currentLocationPtr,
                                                                                            len(direction),locationStr))
                    if currentLocationPtr >= len(direction):
                        # logger.info("units reached !")
                        self._spawingRecorder[type][locationStr]['prevLocationPtr'] = len(direction)
                        # vehicle has reached the destination
                        if len(self._spawingRecorder[type][locationStr]['driving']) >0:
                            self._spawingRecorder[type][locationStr]["working"] = self._spawingRecorder[type][locationStr]['driving']
                            self._spawingRecorder[type][locationStr]["driving"] = []

                        for reachedUnit in self._spawingRecorder[type][locationStr]["working"]:
                            logger.info("Units reached")
                            reachedUnit["previousLocation"] = reachedUnit["currentLocation"]
                            unitsSend.append(reachedUnit)
                        pass
                    else:
                        # unitsSend = []
                        logger.info("Number of driving unit for location {} are {}".format(locationStr,len(drivingunits)))
                        for drivingunit in drivingunits:
                            # unitInformation = workingunits[workingunit]
                            logger.info("updating information for unit {}".format(drivingunit))
                            currentLoc = direction[currentLocationPtr]
                            drivingunit['previousLocation'] = drivingunit['currentLocation']
                            drivingunit['currentLocation'] = currentLoc
                            unitsSend.append(drivingunit)

                    # logger.info(self._spawingRecorder[type])
                    # logger.info("length of the direction given is {}".format(len(direction)))
                    # logger.info("units send {}".format(unitsSend))
        # logger.info('sent all units now monitoring the disaster and waiting for it to end,')
        self.unitsSend = unitsSend
        # logger.info(unitsSend)
        return unitsSend

    def isStationWorking(self,type,locationStr):
        useThisStation = False
        if type in self._spawingRecorder:
            if locationStr in self._spawingRecorder[type]:
                useThisStation = True
        return useThisStation

    def setReverseDirection(self,severity,spawningObjs=None,direction=None):
        """
        this function is called when the severity of the disaster is reduced or its is being completly mitigated
        severity : new severity of the disaster
        spawningObjs: new sorted list of police station, if None previously used list is used.
        direction: way back to stn
        """
        if severity is not None:
            oldNumResponseRequired = self.severitymap[self._severity]
            newNumresponseRequired = self.severitymap[severity]
            numUnitsToSendBack = oldNumResponseRequired - newNumresponseRequired
        else:
            numUnitsToSendBack = self.severitymap[severity]

        if spawningObjs is None:
            spawingStnObjs = self._stationMap
        else:
            spawingStnObjs = spawningObjs
        sentAllUnits = False
        for responseObj in spawingStnObjs:
            if sentAllUnits:
                break
            type, locationStr = responseObj._type, responseObj.locStr()
            stnWorking = self.isStationWorking(type,locationStr)
            if stnWorking:
                if direction is None:
                    directiontoWork = responseObj._direction[::-1]
                else:
                    directiontoWork = direction
                responseObj.setDirection(directiontoWork)
                self._spawingRecorder[type][locationStr]['drivingBackPtr'] = 0
                if 'drivingBack' not in self._spawingRecorder[type][locationStr]:
                    self._spawingRecorder[type][locationStr]['drivingBack'] = []
                    self._spawingRecorder[type][locationStr]['drivingBack'] = self._spawingRecorder[type][locationStr]['working'][:numUnitsToSendBack]
                    self._spawingRecorder[type][locationStr]['working'] = self._spawingRecorder[type][locationStr]['working'][:numUnitsToSendBack]
                if len(self._spawingRecorder[type][locationStr]['drivingBack']) < numUnitsToSendBack:
                    self._spawingRecorder[type][locationStr]['drivingBack'].extend(self._spawingRecorder[type][locationStr][
                                                                                  'working'][:numUnitsToSendBack])
                    self._spawingRecorder[type][locationStr]['working'] = self._spawingRecorder[type][locationStr][
                                                                              'working'][:numUnitsToSendBack]
    def returnToStation(self):

        unitsSend = []
        for responseObj in self._stationMap:
            type,locationStr = responseObj._type, responseObj.locStr()
            isUsingStn = self.isStationWorking(type,locationStr)

            if isUsingStn:
                if "drivingBack" in self._spawingRecorder[type][locationStr]:
                    drivingunits = self._spawingRecorder[type][locationStr]['drivingBack']
                    direction = responseObj._direction
                    currentLocationPtr = self._spawingRecorder[type][locationStr]['drivingBackPtr']
                    logger.info("Number of driving unit for location {} are {}".format(locationStr, len(drivingunits)))
                    for drivingunit in drivingunits:
                        # print(unit)
                        # unitInformation = workingunits[workingunit]
                        logger.info("updating information for unit {}".format(drivingunit))
                        currentLoc = direction[currentLocationPtr]
                        drivingunit['previousLocation'] = drivingunit['currentLocation']
                        drivingunit['currentLocation'] = currentLoc
                        unitsSend.append(drivingunit)
                    self._spawingRecorder[type][locationStr]['drivingBackPtr'] +=1
        return unitsSend
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
        for responseObj in self._stationMap:
            type, locationStr = responseObj._type, responseObj.locStr()
            useThisStation = self.isStationWorking(type, locationStr)
            if not useThisStation:
                continue
            responseWorkerState = self._spawingRecorder[type][locationStr]
            if "working" in responseWorkerState:
                numReachedResponses += len(responseWorkerState["working"])
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

        return currentSeverity,timeRemaining