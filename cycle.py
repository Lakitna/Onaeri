import time
from .timekeeper import TimeKeeper
from .lookup import Lookup
from .helper import sequenceResize, inRange, limitTo, programRestart
from .data import deviationData, briRange, colorRange
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

        self.name = name
        self._devices = devices
        self.settings = settings.get( self.name )
        self.group = self._lampNameToIds( self.name )
        self.update = False

        self._runTime = 0
        self._resetTime = TimeKeeper().makeCode(settings.Global.restartTime)

        self.lookup = Lookup( self.settings )
        self.observer = Observer( self.group, name )
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

            if self.observer.turnedOn:
                self.lamp.copy(newVals)
                self.lamp.power = None
                self.update = True
                self.observer.legalChange
                self._deviation.reset()
            else:
                newVals = self._deviation.apply( newVals )
                self.lamp = self._compareWithPrevious( newVals )

            self.prevLamp.copy(newVals)


            if timeKeeper.timeCode == self._resetTime and self._runTime > 10:
                programRestart()
            if timeKeeper.update:  self._runTime += 1

        return self.update


    def _compareWithPrevious(self, vals):
        """
        Update lamp values (brightness & color)
        """
        lamp = Lamp()
        # If the lamp is on and (value is not the same as previous update or observer dictates update) or lamp turns on
        if self.observer.data.power and (not vals == self.prevLamp or self.observer.update) or vals.power:
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

            self.update = True
            self.observer.legalChange

        return lamp



    def _lampNameToIds(self, name):
        """
        Get lamp ids (plural) based on a partial device name.
        """
        ret = []
        for i in range(len(self._devices)):
            if name.lower() in self._devices[i].name.lower():
                ret.append(i)

        if len(ret) == 0:
            ret = [0] # Default to lamp 0
            logError("[Cycle] No lamps found with partial name `%s`. Use the Ikea Tradfri app to change the name of a lamp." % name)
        return ret







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
            self.setValues['brightness'] = changeVals.brightness - dataVals.brightness
            self.setValues['color'] = changeVals.color - dataVals.color

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
                                    briRange
                                );
            newVals.color = limitTo(
                                    newVals.color + self.values['color'],
                                    colorRange
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
