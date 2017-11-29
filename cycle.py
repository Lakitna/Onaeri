import time
from .timekeeper import TimeKeeper
from .lookup import Lookup
from .helper import sequenceResize, inRange, limitTo
from .data import deviationData
from .observer import Observer
from .lamp import Lamp
from . import settings
from .logger import *


class Cycle:
    """
    Cycle a group of lamps
    """
    def __init__(self, name, devices):
        log("Setting up cycle named %s: " % name, end="", flush=True)

        if len(devices) == 0:
            logError("No lamps found with partial name `%s`." % name)
            exit()
        self.devices = devices

        self.name = name
        self.settings = settings.get( self.name )
        self.update = False

        self.lookup = Lookup( self.settings )
        self.observer = Observer( len(self.devices), name, self.lookup )
        self._deviation = Deviation( self.settings )
        self.lamp = Lamp()
        self.prevLamp = Lamp()

        logSuccess("Done")


    def tick(self, timeKeeper, lampData):
        """
        Progress cycle.
        """
        self.update = False
        self.observer.look( lampData )

        if timeKeeper.update or self.observer.update:
            newVals = self.lookup.table( timeKeeper.timeCode )

            if self.observer.update:
                self._deviation.change(newVals, self.observer.data)

            # If observer dictates all lamps to go off
            if self.observer.turnOff:
                self.lamp.power = False
                self.update = True
                self.observer.legalChange
                self._deviation.reset()
            # If observer saw that the lamps where turned on
            elif self.observer.turnedOn:
                self.lamp.copy(newVals)
                if self.lookup.isNight and len(lampData) > 1:
                    self.lamp.mode = 'dark'
                self.lamp.power = None
                self.update = True
                self.observer.legalChange
                self._deviation.reset()
            else:
                newVals = self._deviation.apply( newVals )
                self.lamp = self._compareWithPrevious( newVals )

            self.prevLamp.copy(newVals)

        return self.update


    def _compareWithPrevious(self, vals):
        """
        Update lamp values (brightness & color)
        """
        lamp = Lamp()
        # If the lamp is on and (value is not the same as previous update or observer dictates update) or lamp turns on
        if (self.observer.data.power and (not vals == self.prevLamp or self.observer.update)) or vals.power or vals.mode:
            if not vals.brightness == self.prevLamp.brightness:
                lamp.brightness = vals.brightness
            if not vals.color == self.prevLamp.color:
                lamp.color = vals.color
            if not vals.power == self.prevLamp.power:
                lamp.power = vals.power

            if not lamp.power == None:
                if not self.settings.automaticPowerOff and lamp.power == False:
                    lamp.power = None
                if not self.settings.automaticPowerOn and lamp.power == True:
                    lamp.power = None

            lamp.mode = vals.mode

            self.update = True
            self.observer.legalChange

        return lamp







class Deviation:
    """
    Allow the user to temporary deviate from the given cycle.
    """
    def __init__(self, userSettings):
        self.duration = userSettings.deviationDuration
        self.table = sequenceResize(deviationData, self.duration)

        self.counter = 0
        self.active = False
        self.values = {'brightness': 0, 'color': 0}
        self.setValues = {'brightness': 0, 'color': 0}
        self.reset()


    def change(self, dataVals, changeVals):
        """
        Apply an observed change to deviation routine
        """
        self.reset()

        # log(changeVals)

        if changeVals.power and self.duration > 0:
            if changeVals.color is None:
                self.setValues['color'] = dataVals.color
            else:
                self.setValues['color'] = changeVals.color - dataVals.color

            if changeVals.brightness is None:
                self.setValues['brightness'] = dataVals.brightness
            else:
                self.setValues['brightness'] = changeVals.brightness - dataVals.brightness

            self.values = self.setValues.copy()

            if not inRange(self.setValues['brightness'], (-1,1)) \
               or not inRange(self.setValues['color'], (-10,10)):
                self.active = True


    def apply(self, newVals):
        """
        Progress by one tick
        """
        if self.active:
            if self.counter >= self.duration:
                self.reset()

            multiplier = self.table[self.counter] / 100

            self.values['brightness'] = round(self.setValues['brightness'] * multiplier)
            self.values['color'] = round(self.setValues['color'] * multiplier)

            newVals.brightness = limitTo(
                                    newVals.brightness + self.values['brightness'],
                                    settings.Global.valRange
                                );
            newVals.color = limitTo(
                                    newVals.color + self.values['color'],
                                    settings.Global.valRange
                                );
            self.counter += 1

        return newVals


    def reset(self):
        """
        Reset the deviation routine
        """
        self.counter = 0
        self.active = False
        self.values = {'brightness': 0, 'color': 0}
        self.setValues = {'brightness': 0, 'color': 0}
