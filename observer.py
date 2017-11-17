from .lamp import Lamp
import sys
from .helper import limitTo
from .data import briRange, colorRange
from .logger import *


class Observer:
    """
    Observe changes in a lamp
    """
    def __init__(self, lampIds=[0], cycleName=None):
        self.update = True
        self.data = Lamp()
        self.turnedOn = False
        self._cycleName = cycleName
        self._container = self.data
        self._lampIds = lampIds
        self._legalChange = True

    def look(self, newData):
        """
        Look for changes in lamp values
        """
        self.update = False

        # If observer recieved meaningfull data
        if not newData == None:
            self.turnedOn = False
            for i in range(len(newData)):
                if self.data.power == False and newData[i].power == True:
                    self.turnedOn = True

                newData[i].color = limitTo(newData[i].color, colorRange)
                newData[i].brightness = limitTo(newData[i].brightness, briRange)

            if not self._legalChange:
                self.data = self._sameData(newData, self.data)
            else:
                self.data = newData[0]

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
            if not prev == lamp:
                logHighlight("[Observer] Illegal change detected:")
                logHighlight("\t%s: %s" % (self._cycleName, lamp))
                self.update = True
                return lamp
        return new[0]
