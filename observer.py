from .lamp import Lamp
import sys
# from .lookup import isNight
from .helper import limitTo
from .logger import *
from .settings.Global import valRange


class Observer:
    """
    Observe changes in a lamp
    """
    def __init__(self, lampCount, cycleName=None, lookup=None):
        self.update = True
        self.data = Lamp()
        self.turnedOn = False
        self.turnOff = False
        self.lookup = lookup
        self._unpoweredLamps = []
        self._unpoweredLampsPrev = []
        self._cycleName = cycleName
        self._lampCount = lampCount
        self._legalChange = True

    def look(self, newData):
        """
        Look for changes in lamp values
        """
        self.update = False


        # If observer recieved meaningfull data
        if not newData == None:
            self.turnedOn = False
            self.turnOff = False
            self._unpoweredLamps = []
            for i in range(len(newData)):
                if self.data.power == False and newData[i].power == True:
                    self.turnedOn = True
                if not newData[i].power:
                    self._unpoweredLamps.append(i)
                    newData[i] = self.data
                    if len(self._unpoweredLamps) == self._lampCount:
                        self.data.power = False


                newData[i].color = limitTo(newData[i].color, valRange)
                newData[i].brightness = limitTo(newData[i].brightness, valRange)


            if not self._legalChange:
                if not self._unpoweredLamps == self._unpoweredLampsPrev and self.lookup.isNight:
                    # If user tried to turn off the lamps while in dark mode
                    if len(self._unpoweredLamps) - len(self._unpoweredLampsPrev) in range(-1,1):
                        self.update = True
                        self.turnOff = True

                self.data = self._sameData(newData, self.data)
            else:
                self.data = newData[0]


            self._unpoweredLampsPrev = self._unpoweredLamps
            self._legalChange = False


    @property
    def legalChange(self):
        """
        Prevent observer from overwriting next detected change.
        """
        self._legalChange = True


    def _sameData(self, new, prev):
        """
        Compare new to previous lamp values. Returns lamp object and sets update flag.
        """
        for i in range(len(new)):
            lamp = new[i]

            if not prev == lamp \
              and (len(self._unpoweredLamps) == self._lampCount or len(self._unpoweredLamps) == 0):
                logHighlight("[Observer] Illegal change detected:")
                logHighlight("\t%s: %s" % (self._cycleName, lamp))
                self.update = True
                return lamp
        return new[0]
