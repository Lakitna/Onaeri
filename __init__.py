"""
Onaeri API
https://github.com/Lakitna/Onaeri
"""

__version__ = '0.4.0'


from .logger import log

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
        self.devices = devices

        for cycleName in settings.cycles:
            lamps = {}
            for l in self.devices:
                if cycleName.lower() in l.name.lower():
                    lamps[l.name] = l
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

            if self.time.update:
                for id in cycle.lamp:
                    log.blind("[time]\t%s\t%s\t%s\t%s\t%s" % (
                            cycle.observer[id].data.brightness,
                            cycle.observer[id].data.color,
                            cycle.observer[id].data.power,
                            cycle.observer[id].update,
                            cycle.deviation[id].active
                        ), id)

        self.time.tick()
