from .timekeeper import TimeKeeper
from . import data
from .helper import scale, sequenceResize, inRange, timecodeRange
from .lamp import Lamp
from .logger import log

from . import settings
import time


class Lookup:
    """
    Calculates and dispenses lookup tables for lamp values
    """
    def __init__(self, config):
        self.time = TimeKeeper()
        self.config = config
        self.lamp = Lamp()

        # Sleep rhythm settings
        self._alarmTime = self.time.code(self.config.alarmTime)
        self._alarmOffset = self.time.code(m=self.config.alarmOffset)

        self._sleepTime = self.time.code(self.config.sleepTime)
        self._windDownTime = self.time.code(m=self.config.windDownTime)

        # Create morning and evening slopes based on sleep rhythm settings
        self.morningSlope = timecodeRange(
            self._alarmTime - self._alarmOffset,
            (self._alarmTime
             - self._alarmOffset
             + self.config.morningSlopeDuration)
        )

        self.eveningSlope = timecodeRange(
            self._sleepTime - self.config.eveningSlopeDuration,
            self._sleepTime
        )

        # Build lookup tables
        self.anatomy = self._buildAnatomy()
        self.brightness = self._buildTable(data.brightness)
        self.color = self._buildTable(data.color)

        # print(self.brightness)
        # print()
        # print(self.color)
        # print()
        # print(self.anatomy)
        # print("\n" * 10)
        # exit()

    def table(self, timeCode):
        """
        Get lamp values associated with timecode. Returns lamp object
        """
        self.lamp.color = scale(
            self.color[timeCode],
            settings.Global.dataRange,
            settings.Global.valRange
        )
        self.lamp.brightness = scale(
            self.brightness[timeCode],
            settings.Global.dataRange,
            settings.Global.valRange
        )

        period = self.period
        darkrange = timecodeRange(self._sleepTime - self._windDownTime,
                                  self._sleepTime)
        if (period == 'night' or inRange(timeCode, darkrange)):
            self.lamp.mode = 'dark'
        else:
            self.lamp.mode = None

        return self.lamp

    @property
    def period(self):
        timeCode = self.time.code()
        for period in self.anatomy:
            if inRange(timeCode, self.anatomy[period]):
                return period

    def _buildAnatomy(self):
        anatomy = {
            "morning": self.morningSlope,
            "day": timecodeRange(self.morningSlope[-1][1],
                                 self.eveningSlope[0][0]),
            "evening": self.eveningSlope,
            "night": timecodeRange(self.eveningSlope[-1][1],
                                   self.morningSlope[0][0])
        }

        if (inRange(anatomy['morning'][-1][1], anatomy['evening'])
           or inRange(anatomy['morning'][0][0], anatomy['evening'])):
            log.error("Morning and evening cycles overlap.")
            log.warn("The program will try to run like normal, but some " +
                     "weird behaviour is inevitable.")
            log.warn("Change your settings to fix this.")

        return anatomy

    def _buildTable(self, source):
        """
        Build a lookup table based on class attributes and a given data source.
        Returns list
        """
        # Resize morningSlope and eveningSlope
        source['morning'] = sequenceResize(source['morning'],
                                           self.config.morningSlopeDuration)
        source['evening'] = sequenceResize(source['evening'],
                                           self.config.eveningSlopeDuration)

        # Create full table and default to nightflat
        table = [source['night']] * settings.Global.totalDataPoints

        for period in self.anatomy:
            c = 0
            for rnge in self.anatomy[period]:
                if period == 'day' or period == 'night':
                    for timeCode in range(rnge[0], rnge[1]):
                        table[timeCode] = source[period]
                else:
                    for timeCode in range(rnge[0], rnge[1]):
                        table[timeCode] = source[period][c]
                        c += 1

        return table
