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
        self.update = False

        self.settings = settings.get( self.name )
        self.lookup = Lookup( self.settings )

        self.observer = {}
        self._deviation = {}
        self.lamp = {}
        self.prevLamp = {}
        for id in self.devices:
            self.observer[id] = Observer( name )
            self._deviation[id] = Deviation( self.settings )
            self.lamp[id] = Lamp()
            self.prevLamp[id] = Lamp()

        logSuccess("Done")


    def tick(self, timeKeeper, lampData):
        """
        Progress cycle.
        """
        self.update = False

        for id in self.devices:
            if not lampData is None:
                self.observer[id].look( lampData[id] )

            if timeKeeper.update or self.observer[id].update:
                newVals = self.lookup.table( timeKeeper.timeCode )
                newVals.name = id

                if self.observer[id].update:
                    self._deviation[id].change(newVals, self.observer[id].data)


                if self.observer[id].turnedOff:
                    self.lamp[id].power = False
                elif self.observer[id].turnedOn:
                    if newVals.mode == 'dark' and 'dark' in id.lower():
                        self.lamp[id].power = False
                        self.lamp[id].brightness = None
                    else:
                        self.lamp[id].copy(newVals)
                        self.lamp[id].power = None
                    self.update = True
                    self.observer[id].legalChange
                    self._deviation[id].reset()
                else:
                    newVals = self._deviation[id].apply( newVals )
                    self.lamp[id] = self._compareWithPrevious( newVals, id )

                self.prevLamp[id].copy(newVals)

        return self.update


    def _compareWithPrevious(self, new, id):
        """
        Update lamp values (brightness & color)
        """
        lamp = Lamp()
        if self._lampUpdate(new, id):
            if not new.brightness == self.prevLamp[id].brightness:
                lamp.brightness = new.brightness
            if not new.color == self.prevLamp[id].color:
                lamp.color = new.color
            if not new.power == self.prevLamp[id].power:
                lamp.power = new.power

            if not lamp.power == None:
                if not self.settings.automaticPowerOff and lamp.power == False:
                    lamp.power = None
                if not self.settings.automaticPowerOn and lamp.power == True:
                    lamp.power = None

                if lamp.power == True:
                    lamp.brightness = new.brightness
                    lamp.color = new.color

            lamp.mode = new.mode

            if lamp.mode == 'dark' and len(self.devices) > 1:
                if 'dark' in id.lower():
                    lamp.brightness = None
                    lamp.power = False

            lamp.name = id
            self.update = True
            self.observer[id].legalChange

        return lamp


    def _lampUpdate(self, new, id):
        """
        Define if the lamps should be updated.
        Previously a very complex if statement.
        """
        # If the lamp should be turned on according to Lookup
        if new.power:  return True

        # If mode changes
        if not new.mode == self.prevLamp[id].mode:  return True

        # If the lamp is currently on
        if self.observer[id].data.power:
            # If the new values are not the same as the old ones
            if not new == self.prevLamp[id]:  return True
            # If observer calls for an update
            if self.observer[id].update:  return True

        return False






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
