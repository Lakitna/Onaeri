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
        self._valList = ['brightness', 'color', 'power', 'hue', 'sat']

    def __str__(self):
        """
        Return public vars in dict-string
        """
        ret = {}
        for var in self.__dict__:
            if "_" not in var:
                ret[var] = getattr(self, var)
        return str(ret)

    def look(self, newData):
        """
        Look for changes in lamp values
        """
        self.update = False

        # If observer recieved meaningfull data
        if newData is not None:
            self.turnedOn = False
            self.turnedOff = False
            if self.data.power is False and newData.power is True:
                self.turnedOn = True
            if self.data.power is True and newData.power is False:
                self.turnedOff = True

            for v in self._valList:
                if not v == 'power':
                    setattr(newData, v, limitTo(getattr(newData, v), valRange))

            if not self._legalChange:
                self._detectChange(newData, self.data)
                self.data = newData
            else:
                self.data = newData

            self._legalChange = False

    @property
    def legalChange(self):
        """
        Prevent observer from overwriting next detected change.
        """
        self._legalChange = True

    def _detectChange(self, new, prev):
        """
        Compare new to previous lamp values.
        Returns lamp object and sets update flag.
        """
        change = False
        lamp = Lamp()

        for val in self._valList:
            if getattr(new, val) != getattr(prev, val):
                setattr(lamp, val, getattr(new, val))
                change = True

        if change:
            log.highlight("[[time]] Change detected in %s: %s"
                          % (new.name, lamp))
            self.update = True
