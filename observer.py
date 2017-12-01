from .lamp import Lamp
import sys
from .helper import limitTo
from .logger import *
from .settings.Global import valRange


class Observer:
    """
    Observe changes in a lamp
    """
    def __init__(self, cycleName=None):
        self.update = True
        self.data = Lamp()
        self.turnedOn = False
        self.turnedOff = False
        self._cycleName = cycleName
        self._legalChange = True


    def __str__(self):
        """
        Return public vars in dict-string
        """
        ret = {}
        for var in self.__dict__:
            if not "_" in var:
                ret[var] = getattr(self, var)
        return str(ret)


    def look(self, newData):
        """
        Look for changes in lamp values
        """
        self.update = False

        # If observer recieved meaningfull data
        if not newData is None:
            self.turnedOn = False
            self.turnedOff = False
            if self.data.power == False and newData.power == True:
                self.turnedOn = True
            if self.data.power == True and newData.power == False:
                self.turnedOff = True

            newData.color      = limitTo(newData.color, valRange)
            newData.brightness = limitTo(newData.brightness, valRange)

            if not self._legalChange:
                self.data = self._sameData(newData, self.data)
            else:
                self.data = newData

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
        lamp = new

        if not prev == new:
            logHighlight("[Observer] Illegal change detected:")
            logHighlight("\t%s: %s" % (self._cycleName, new))
            self.update = True
        return new
