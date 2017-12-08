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
        self.isNight = False

        # Sleep rhythm settings
        self._alarmTime = self.time.code(self.config.alarmTime)
        self._alarmOffset = self.time.code(m=self.config.alarmOffset)

        self._sleepTime = self.time.code(self.config.sleepTime)
        self._windDownTime = self.time.code(m=self.config.windDownTime)

        # Create morning and evening slopes based on sleep rhythm settings
        self._morningSlope = [0, 0]
        self._morningSlope[0] = (self._alarmTime
                                 - self._alarmOffset)
        self._morningSlope[1] = (self._morningSlope[0]
                                 + self.config.morningSlopeDuration)

        self._eveningSlope = [0, 0, 0, 0]
        self._eveningSlope[0] = (self._sleepTime
                                 - self.config.eveningSlopeDuration)
        self._eveningSlope[1] = self._sleepTime
        self._eveningSlope[2] = self._eveningSlope[0]
        if self._eveningSlope[0] < 0:
            self._eveningSlope[0] = 0
            self._eveningSlope[2] += settings.Global.totalDataPoints
            self._eveningSlope[3] = settings.Global.totalDataPoints

        # Build lookup tables
        self.brightness = self._buildTable(
            data.brightness,
            self.config.brightnessCorrect
        )
        self.color = self._buildTable(
            data.color,
            self.config.colorCorrect
        )

        # print(self.brightness)
        # print()
        # print(self.color)
        # exit()

    def table(self, timeCode):
        """
        Get lamp values associated with timecode. Returns lamp object
        """
        self.lamp.brightness = scale(
            self.brightness[timeCode],
            (0, 100),
            settings.Global.valRange
        )
        self.lamp.color = scale(
            self.color[timeCode],
            (0, 100),
            settings.Global.valRange
        )

        if timeCode == (self._alarmTime - self._alarmOffset):
            self.lamp.power = True
        elif timeCode == self._sleepTime:
            self.lamp.power = False
        else:
            self.lamp.power = None

        self.isNight = self._isNight(timeCode)

        if self.isNight:
            self.lamp.mode = 'dark'
        else:
            self.lamp.mode = None

        return self.lamp

    def _isNight(self, timeCode=None):
        if timeCode is None:
            timeCode = self.time.code()

        if timeCode in range((self._sleepTime - self._windDownTime),
                             settings.Global.totalDataPoints):
            return True
        if timeCode in range(0,
                             (self._alarmTime - self._alarmOffset)):
            return True
        return False

    def _buildTable(self, source, sourceRange):
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
        table = ([source['night'] + sourceRange[0]]
                 * settings.Global.totalDataPoints)

        for timeCode in range(self._morningSlope[0], self._morningSlope[1]):
            table[timeCode] = source['morning'][timeCode
                                                - self._morningSlope[0]]
            table[timeCode] = scale(table[timeCode],
                                    (0, 100),
                                    sourceRange,
                                    decimals=1)

        for timeCode in range(self._eveningSlope[0], self._eveningSlope[1]):
            table[timeCode] = source['evening'][timeCode
                                                - self._eveningSlope[0]]
            table[timeCode] = scale(table[timeCode],
                                    (0, 100),
                                    sourceRange,
                                    decimals=1)

        for timeCode in range(self._eveningSlope[2], self._eveningSlope[3]):
            table[timeCode] = source['evening'][timeCode
                                                - self._eveningSlope[2]]
            table[timeCode] = scale(table[timeCode],
                                    (0, 100),
                                    sourceRange,
                                    decimals=1)

        for timeCode in range(self._morningSlope[1], self._eveningSlope[2]):
            table[timeCode] = scale(source['day'],
                                    (0, 100),
                                    sourceRange)

        return table
