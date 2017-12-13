from .timekeeper import TimeKeeper
from . import data
from .helper import scale, sequenceResize, inRange
from .lamp import Lamp
from .logger import *

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
        self._morningSlope = [0, 0, 0, 0]
        self._morningSlope[0] = (self._alarmTime - self._alarmOffset)
        self._morningSlope[1] = (self._morningSlope[0]
                                 + self.config.morningSlopeDuration)

        self._eveningSlope = [0, 0, 0, 0]
        self._eveningSlope[0] = (self._sleepTime
                                 - self.config.eveningSlopeDuration)
        self._eveningSlope[1] = self._sleepTime
        if self._eveningSlope[0] < 0:
            self._eveningSlope[2] = 0
            self._eveningSlope[3] = self._sleepTime

            self._eveningSlope[0] = (self._eveningSlope[0]
                                     + settings.Global.totalDataPoints)
            self._eveningSlope[1] = settings.Global.totalDataPoints

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

        if timeCode == (self._alarmTime - self._alarmOffset):
            self.lamp.power = True
        elif timeCode == self._sleepTime:
            self.lamp.power = False
        else:
            self.lamp.power = None

        period = self.period
        if period == 'night':
            self.lamp.mode = 'dark'
        else:
            self.lamp.mode = None

        return self.lamp

    @property
    def period(self, timeCode=None):
        if timeCode is None:
            timeCode = self.time.code()

        for period in self.anatomy:
            for sub in self.anatomy[period]:
                if timeCode in range(sub[0], sub[1]):
                    return period

    def _buildAnatomy(self):
        anatomy = {
            "morning": [(self._morningSlope[0], self._morningSlope[1]),
                        (self._morningSlope[2], self._morningSlope[3])],
            "day": [(self._morningSlope[1], self._eveningSlope[0]),
                    (0, 0)],
            "evening": [(self._eveningSlope[0], self._eveningSlope[1]),
                        (self._eveningSlope[2], self._eveningSlope[3])],
            "night": [(self._eveningSlope[1], settings.Global.totalDataPoints),
                      (self._eveningSlope[3], self._morningSlope[0])]
        }

        for phase in anatomy:
            for partial in anatomy[phase]:
                if partial[0] == partial[1]:
                    anatomy[phase].remove(partial)
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
        table = ([source['night']] * settings.Global.totalDataPoints)

        for timeCode in range(self._morningSlope[0], self._morningSlope[1]):
            table[timeCode] = source['morning'][timeCode
                                                - self._morningSlope[0]]

        for timeCode in range(self._eveningSlope[0], self._eveningSlope[1]):
            table[timeCode] = source['evening'][timeCode
                                                - self._eveningSlope[0]]

        for timeCode in range(self._eveningSlope[2], self._eveningSlope[3]):
            table[timeCode] = source['evening'][timeCode
                                                - self._eveningSlope[2]]

        for timeCode in range(self._morningSlope[1], self._eveningSlope[0]):
            table[timeCode] = source['day']

        return table
