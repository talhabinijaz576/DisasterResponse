from helperClasses.responseFrame.responseClass.responseBase import Response

class PoliceCar(Response,):
    def __init__(self,name,location):
        super().__init__(name,location)

    def actionAtSite(self):
        return 'block'

class Firetruck(Response,):
    def __init__(self,name,location):
        super().__init__(name,location)

    def actionAtSite(self):
        return 'Reduce Fire'

class Ambulance(Response,):
    def __init__(self,name,location):
        super().__init__(name,location)

    def actionAtSite(self):
        return 'Pick and go'
