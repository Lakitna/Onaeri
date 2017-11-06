"""
Onaeri API
"""

__version__ = '0.0.1a'
__author__ = 'Sander van Beek'


print("Onaeri API v%s" % __version__)
print()


# from . import settings

from .cycle import Cycle
from .timekeeper import TimeKeeper
from . import settings



class Onaeri:
    """
    Onaeri API wrapper
    """
    def __init__(self, settings, devices):
        self.time = TimeKeeper()
        self.cycles = []
        self.update = False
        self.devices = devices

        for cycleName in settings.cycles:
            self.cycles.append( Cycle(cycleName, self.devices) )


    def tick(self, lampDataList=None):
        """
        Progress everything by one tick
        """
        self.update = False

        for cycle in self.cycles:
            if lampDataList == None:
                lampData=None
            else:
                lampData = []
                for lamp in lampDataList:
                    if cycle.name.lower() in lamp.name.lower():
                        lampData.append(lamp)

            if cycle.tick( self.time, lampData ):
                self.update = True

        self.time.tick()
