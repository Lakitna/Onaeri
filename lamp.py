from .helper import inRange
from .logger import *
from .settings.Global import valRange


class Lamp:
    """
    Data structure for a lamp
    """
    def __init__(self, brightness=None, color=None, power=None, name=None, mode=None):
        self._brightness = brightness
        self._color = color
        self._power = power
        self._name = name
        self._mode = mode


    def __call__(self):
        """
        Return all values in dict
        """
        ret = {}
        for var in self.__dict__:
            ret[var.lstrip("_")] = getattr(self, var)
        return ret

    def __str__(self):
        """
        Return all values that aren't None as string
        """
        ret = {}
        for var in self.__dict__:
            val = getattr(self, var)
            if not val is None:
                ret[var.lstrip("_")] = val
        return str(ret)

    def __eq__(self, other):
        """
        Compare with other object of same type
        """
        ret = True
        if not self._brightness == other._brightness:  ret = False
        if not self._color == other._color:  ret = False
        if not self._power == other._power:  ret = False
        return ret


    def copy(self, obj):
        """
        Copy an object of same type
        """
        for var in self.__dict__:
            exec("self.%s = obj.%s" % (var, var))

    def empty(self):
        """
        Set all values to None
        """
        for var in self.__dict__:
            var = None

    def isEmpty(self, varList=None):
        """
        Check if values in object are all None
        """
        if varList is None:  varList = self.__dict__

        empty = True
        for var in varList:
            if not getattr(self, var) == None:
                empty = False
        return empty


    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        if value == None or value == True or value == False:
            self._power = value
        else:
            log.warn("[Lamp] Power input value error. Allowed values 'True', 'False' or 'None'.")


    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value


    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if value is None:
            self._brightness = None
        elif inRange(value, valRange):
            self._brightness = value
        else:
            log.warn("[Lamp] Brightness input value error. %d given, allowed range %s" % (value, str(valRange)))


    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value is None:
            self._color = None
        elif inRange(value, valRange):
            self._color = value
        else:
            log.warn("[Lamp] Color input value error. %d given, allowed range %s" % (value, str(valRange)))


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
