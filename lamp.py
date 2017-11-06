from .helper import printWarning, inRange
from .data import briRange, colorRange


class Lamp:
    """
    Data structure for a lamp
    """
    def __init__(self, brightness=None, color=None, power=None, name=None):
        self._brightness = brightness
        self._color = color
        self._power = power

        self._name = name


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
        Return all values as string
        """
        return str(self.__call__())

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
        for var in self.__dict__:
            exec("self.%s = obj.%s" % (var, var))

    def empty(self):
        for var in self.__dict__:
            var = None

    def isEmpty(self):
        empty = True
        for var in self.__dict__:
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
            printWarning("[Lamp] Power input value error. Allowed values 'True', 'False' or 'None'.")


    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if inRange(value, briRange):
            self._brightness = value
        else:
            printWarning("[Lamp] Brightness input value error. %d given, allowed range %s" % (value, str(briRange)))


    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if inRange(value, colorRange):
            self._color = value
        else:
            printWarning("[Lamp] Color input value error. %d given, allowed range %s" % (value, str(colorRange)))


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
