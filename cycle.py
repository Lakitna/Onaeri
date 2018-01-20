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
    def __init__(self, name, devices, timeKeeper, scheduler):
        log("Setting up cycle named %s: " % name, end="", flush=True)

        if len(devices) == 0:
            log.error("No lamps found with partial name `%s`." % name)

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

            # Set some dynamic settings for lamp
            data = {'off': self.lookup.anatomy['night'][0][0],
                    'on': self.lookup.anatomy['morning'][0][0]}
            settings.dynamic.set(id, "power", data)

            # Schedule resetting the lamps dynamic power settings
            scheduler.add(
                timecodeWrap(data['on'] - settings.Global.schedulerLampOffset),
                settings.dynamic.set,
                "Reset dynamic settings for %s" % id,
                args={"id": id, "group": "power", "data": data}
            )

        log.success("Done")

    def tick(self, lampData):
        """
        Progress cycle by an arbitrary time unit.
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
        dynamicSettings = settings.dynamic.get(id)
        vals = [
            {'val': 'brightness', 'feature': ['dim'], 'setting': 'brightness'},
            {'val': 'color', 'feature': ['temp', 'color'], 'setting': 'color'},
            {'val': 'sat', 'feature': ['color'], 'setting': 'color'},
        ]

        for v in vals:
            def canDo():
                for f in v['feature']:
                    if dynamicSettings['features'][f]:
                        return True
                return False

            if getattr(lamp, v['val']) is not None and canDo():
                setattr(lamp, v['val'], scale(
                    getattr(lamp, v['val']),
                    settings.Global.valRange,
                    (dynamicSettings['min'][v['setting']],
                     dynamicSettings['max'][v['setting']])
                ))
            else:
                setattr(lamp, v['val'], None)

        lamp.features = dynamicSettings['features']
        if dynamicSettings['features']['color'] and lamp.mode == 'alert':
            lamp.color = None
            lamp.hue = 333
            lamp.sat = 1000

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
            vals = ['brightness', 'color', 'hue', 'sat', 'power']
            for v in vals:
                if not getattr(new, v) == getattr(self.prevLamp[id], v):
                    setattr(lamp, v, getattr(new, v))

            if lamp.power is True:
                for v in vals:
                    if not v == 'power':
                        setattr(lamp, v, getattr(new, v))

            lamp.mode = new.mode
            if lamp.mode == 'dark' and len(self.devices) > 1:
                if 'dark' in id.lower():
                    lamp.brightness = None
                    lamp.power = False

            lamp.features = new.features
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
