import time
from .lookup import Lookup
from .helper import sequenceResize, inRange, limitTo, scale, timecodeWrap
from . import data
from .observer import Observer
from .lamp import Lamp
from . import settings
from .logger import log


class Cycle:
    """
    Cycle a group of lamps
    """
    def __init__(self, name, devices, timeKeeper):
        log("Setting up cycle named %s: " % name, end="", flush=True)

        if len(devices) == 0:
            log.error("No lamps found with partial name `%s`." % name)
            exit()
        self.devices = devices
        self.name = name
        self.update = False

        self.settings = settings.get(self.name)
        self.lookup = Lookup(self.settings)
        self.time = timeKeeper

        self.observer = {}
        self.deviation = {}
        self.lamp = {}
        self.prevLamp = {}
        for id in self.devices:
            self.observer[id] = Observer(name)
            self.deviation[id] = Deviation(id,
                                           self.lookup.anatomy,
                                           self.settings)
            self.lamp[id] = Lamp()
            self.prevLamp[id] = Lamp()
            settings.dynamic.set(id,
                                 "power",
                                 {'off': self.lookup.anatomy['night'][0][0],
                                  'on': self.lookup.anatomy['morning'][0][0]})

        log.success("Done")

    def tick(self, lampData):
        """
        Progress cycle.
        """
        self.update = False

        for id in self.devices:
            if lampData is not None:
                self.observer[id].look(lampData[id])

            if self.time.update or self.observer[id].update:
                newVals = self.lookup.table(self.time.latestCode)
                newVals.name = id

                if (self.observer[id].update
                   and not self.observer[id].turnedOn
                   and not self.observer[id].turnedOff):
                    if self.lookup.period == 'evening':
                        self.deviation[id].change(newVals,
                                                  self.observer[id].data,
                                                  self.time.latestCode)
                    elif self.lookup.period == 'day':
                        settings.dynamic.set(
                            id,
                            'max',
                            self.observer[id].data(),
                            keys=['brightness', 'color']
                        )
                    elif self.lookup.period == 'night':
                        settings.dynamic.set(
                            id,
                            'min',
                            self.observer[id].data(),
                            keys=['brightness', 'color']
                        )

                newVals = self._applyDynamicSettings(id, newVals)

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
                    self.deviation[id].reset()
                else:
                    newVals = self.deviation[id].apply(newVals)
                    self.lamp[id] = self._compareWithPrevious(newVals, id)

                self.prevLamp[id].copy(newVals)

        return self.update

    def _applyDynamicSettings(self, id, lamp):
        """
        Apply some dynamic settings
        """
        dynamicSettings = settings.dynamic.get(id,
                                               ['max', 'min', 'power'])
        if lamp.brightness is not None:
            lamp.brightness = scale(
                lamp.brightness,
                settings.Global.valRange,
                (dynamicSettings['min']['brightness'],
                 dynamicSettings['max']['brightness'])
            )

        if lamp.color is not None:
            lamp.color = scale(
                lamp.color,
                settings.Global.valRange,
                (dynamicSettings['min']['color'],
                 dynamicSettings['max']['color'])
            )

        lamp.power = None
        if self.time.latestCode == dynamicSettings['power']['off']:
            if self.settings.autoPowerOff:
                lamp.power = False
        elif self.time.latestCode == dynamicSettings['power']['on']:
            if self.settings.autoPowerOn:
                lamp.power = True

        return lamp

    def _compareWithPrevious(self, new, id):
        """
        Update lamp values (brightness & color)
        """
        def update():
            """
            Should the lamps be updated?
            Previously an if-statement that grew too complex.
            """
            # If the lamp should be turned on
            if new.power:
                return True

            # If the lamp is currently on
            if self.observer[id].data.power:
                # If mode changes
                if not new.mode == self.prevLamp[id].mode:
                    return True
                # If the new values are not the same as the old ones
                if not new == self.prevLamp[id]:
                    return True
                # If observer calls for an update
                if self.observer[id].update:
                    return True
            return False

        lamp = Lamp()
        if update():
            if not new.brightness == self.prevLamp[id].brightness:
                lamp.brightness = new.brightness
            if not new.color == self.prevLamp[id].color:
                lamp.color = new.color
            if not new.power == self.prevLamp[id].power:
                lamp.power = new.power

            if lamp.power is True:
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


class Deviation:
    """
    Allow the user to temporary deviate from the given cycle.
    """
    def __init__(self, id, anatomy, settings):
        self.duration = 0
        self.table = []

        self._anatomy = anatomy
        self.id = id
        self.settings = settings

        self.counter = 0
        self.active = False
        self.values = {}
        self.setValues = {}
        self.reset()

    def change(self, dataVals, changeVals, timeCode):
        """
        Apply an observed change to deviation routine
        """
        self.reset()
        self.duration = self._calculateDuration(timeCode)
        self.table = sequenceResize(data.deviation, self.duration)

        if changeVals.power and self.duration > 0:
            if changeVals.color is None:
                self.setValues['color'] = dataVals.color
            else:
                self.setValues['color'] = changeVals.color - dataVals.color

            if changeVals.brightness is None:
                self.setValues['brightness'] = dataVals.brightness
            else:
                self.setValues['brightness'] = (changeVals.brightness
                                                - dataVals.brightness)

            if not inRange(self.setValues['brightness'], (-10, 10)) \
               or not inRange(self.setValues['color'], (-10, 10)):
                self.values = self.setValues.copy()
                self.active = True

    def _calculateDuration(self, timeCode):
        """
        Calcuate the duration of the deviationcycle
        """
        duration = 0
        if inRange(timeCode, self._anatomy['evening']):
            sleeptime = self._anatomy['night'][0][0]
            if sleeptime < timeCode:
                sleeptime += settings.Global.totalDataPoints
            duration = sleeptime - timeCode

        if duration < self.settings.deviationDuration:
            duration = self.settings.deviationDuration
            settings.dynamic.set(self.id,
                                 "power",
                                 {"off": timecodeWrap(timeCode + duration)})

        return duration

    def apply(self, newVals):
        """
        Progress by one tick
        """
        if self.active:
            if self.counter >= self.duration:
                self.reset()

            multiplier = self.table[self.counter] / 1000

            self.values['brightness'] = round(self.setValues['brightness']
                                              * multiplier)
            self.values['color'] = round(self.setValues['color']
                                         * multiplier)

            newVals.brightness = limitTo(
                newVals.brightness + self.values['brightness'],
                settings.Global.valRange
            )
            newVals.color = limitTo(
                newVals.color + self.values['color'],
                settings.Global.valRange
            )
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
