"""
Onaeri API
https://github.com/Lakitna/Onaeri
"""

__version__ = '0.3.0'


from .logger import *

log("Onaeri API v%s" % __version__)

from .cycle import Cycle
from .timekeeper import TimeKeeper
from . import settings



class Onaeri:
    """
    Onaeri API wrapper
    """
    def __init__(self, devices):
        self.time = TimeKeeper()
        self.cycles = []
        self.update = False
        self.logIt = {}
        self.devices = devices

        for cycleName in settings.cycles:
            lamps = {}
            for l in self.devices:
                if cycleName.lower() in l.name.lower():
                    lamps[l.name] = l
                    self.logIt[l.name] = 1
            self.cycles.append( Cycle(cycleName, lamps) )


    def tick(self, lampDataList=None):
        """
        Progress everything by one tick
        """
        self.update = False

        for cycle in self.cycles:
            if lampDataList == None:
                lampData = None
            else:
                lampData = {}
                for lamp in lampDataList:
                    if cycle.name.lower() in lamp.name.lower():
                        lampData[lamp.name] = lamp

            if cycle.tick( self.time, lampData ):
                self.update = True
                for id in cycle.lamp:
                    self.logIt[id] = 3

            # Log state of lamps
            for id in cycle.lamp:
                if self.logIt[id] == 1 or cycle.observer[id].update:
                    log.blind("[time]\t%s\t%s\t%s\t%s\t%s" % (
                            cycle.observer[id].data.brightness,
                            cycle.observer[id].data.color,
                            cycle.observer[id].data.power,
                            cycle.observer[id].update,
                            cycle.deviation[id].active
                        ), id)
                if self.logIt[id] > 0:
                    self.logIt[id] -= 1

        self.time.tick()
