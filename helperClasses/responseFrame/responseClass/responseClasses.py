from helperClasses.responseFrame.responseClass.vehicle import Vehicle

class PoliceCar(Vehicle,):
    def __init__(self,name,location):
        super().__init__(name,"Policecar",location)

    def actionAtSite(self):
        return 'block'

class Firetruck(Vehicle,):
    def __init__(self,name,location):
        super().__init__(name,"FireTruck",location)

    def actionAtSite(self):
        return 'Reduce Fire'

class Ambulance(Vehicle,):
    def __init__(self,name,location):
        super().__init__(name,"Ambulance",location)

    def actionAtSite(self):
        return 'Pick and go'
