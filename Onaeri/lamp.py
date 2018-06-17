from .helper import inRange
from .logger import log
from .settings.Global import valRange


class Lamp:
    """
    Data structure for a lamp
    """
    def __init__(self, brightness=None, color=None,
                 power=None, name=None, mode=None,
                 features=None, hue=None, sat=None):
        self._brightness = brightness
        self._color = color
        self._hue = hue
        self._sat = sat
        self._power = power
        self._name = name
        self._mode = mode
        self._features = features

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
        blacklist = ['_features', '_name']
        ret = {}
        for var in self.__dict__:
            if var not in blacklist:
                val = getattr(self, var)
                if val is not None:
                    ret[var.lstrip("_")] = val
        return str(ret)

    def __eq__(self, other):
        """
        Compare with other object of same type
        """
        vals = ['brightness', 'color', 'power', 'hue', 'sat']
        for v in vals:
            if not getattr(self, "_%s" % v) == getattr(other, "_%s" % v):
                return False
        return True

    def copy(self, obj):
        """
        Copy an object of same type
        """
        for var in self.__dict__:
            setattr(self, var, getattr(obj, var))

    def empty(self):
        """
        Set all values to None
        """
        for var in self.__dict__:
            setattr(self, var, None)

    def isEmpty(self, varList=None):
        """
        Check if values in object are all None
        """
        if varList is None:
            varList = self.__dict__

        empty = True
        for var in varList:
            if getattr(self, var) is not None:
                empty = False
        return empty

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, value):
        if value is None or value is True or value is False:
            self._power = value
        else:
            log.warn("[Lamp] Power input value error. " +
                     "Allowed values 'True', 'False' or 'None'.")

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
        elif type(value) is int:
            if inRange(value, valRange):
                self._brightness = value
            else:
                log.warn("[Lamp] Brightness input value error. " +
                         "%d given, allowed range %s" % (value, str(valRange)))
        else:
            log.error("[Lamp] Brightness requires a integer, not a %s"
                      % type(value))

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value is None:
            self._color = None
        elif type(value) is int:
            if inRange(value, valRange):
                self._color = value
            else:
                log.warn("[Lamp] Color input value error. " +
                         "%d given, allowed range %s" % (value, str(valRange)))
        else:
            log.error("[Lamp] Color requires a integer, not a %s"
                      % type(value))

    @property
    def hue(self):
        return self._hue

    @hue.setter
    def hue(self, value):
        if value is None:
            self._hue = None
        elif type(value) is int:
            if inRange(value, valRange):
                self._hue = value
            else:
                log.warn("[Lamp] Hue input value error. " +
                         "%d given, allowed range %s" % (value, str(valRange)))
        else:
            log.error("[Lamp] Hue requires a integer, not a %s"
                      % type(value))

    @property
    def sat(self):
        return self._sat

    @sat.setter
    def sat(self, value):
        if value is None:
            self._sat = None
        elif type(value) is int:
            if inRange(value, valRange):
                self._sat = value
            else:
                log.warn("[Lamp] Saturation input value error. " +
                         "%d given, allowed range %s" % (value, str(valRange)))
        else:
            log.error("[Lamp] Saturation requires a integer, not a %s"
                      % type(value))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, value):
        self._features = value
