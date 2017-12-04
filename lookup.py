from .timekeeper import TimeKeeper
from .data import brightnessData, colorData
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
        self.timeKeeper = TimeKeeper();
        self.config = config
        self.lamp = Lamp()
        self.isNight = False

        # Sleep rhythm settings
        self._userAlarmTime =    self.timeKeeper.makeCode(self.config.userAlarmTime)
        self._userAlarmOffset =  self.timeKeeper.makeCode(m=self.config.userAlarmOffset)

        self._userSleepTime =    self.timeKeeper.makeCode(self.config.userSleepTime)
        self._userWindDownTime = self.timeKeeper.makeCode(m=self.config.userWindDownTime)

        # Create morning and evening slopes based on sleep rhythm settings
        self._userMorningSlope = [0,0]
        self._userMorningSlope[0] = self._userAlarmTime - self._userAlarmOffset
        self._userMorningSlope[1] = self._userMorningSlope[0] + self.config.morningSlopeDuration

        self._userEveningSlope = [0,0,0,0]
        self._userEveningSlope[0] = self._userSleepTime - self.config.eveningSlopeDuration
        self._userEveningSlope[1] = self._userSleepTime
        self._userEveningSlope[2] = self._userEveningSlope[0]
        if self._userEveningSlope[0] < 0:
            self._userEveningSlope[0] = 0
            self._userEveningSlope[2] += settings.Global.totalDataPoints
            self._userEveningSlope[3] = settings.Global.totalDataPoints

        # Build lookup tables
        self.brightness = self._buildTable(brightnessData, self.config.briCorrect)
        self.color = self._buildTable(colorData, self.config.colorCorrect)

        # print(self.brightness)
        # print()
        # print(self.color)
        # exit()


    def table(self, timeCode):
        """
        Get lamp values associated with timecode. Returns lamp object
        """
        self.lamp.brightness = scale(self.brightness[timeCode], (0,100), settings.Global.valRange)
        self.lamp.color      = scale(self.color[timeCode], (0,100), settings.Global.valRange)

        if timeCode == (self._userAlarmTime - self._userAlarmOffset):
            self.lamp.power = True
        elif timeCode == self._userSleepTime:
            self.lamp.power = False
        else:
            self.lamp.power = None

        if timeCode in range((self._userSleepTime - self._userWindDownTime), settings.Global.totalDataPoints) or \
           timeCode in range(0, (self._userAlarmTime - self._userAlarmOffset)):
           self.lamp.mode = 'dark'
        else:
            self.lamp.mode = None

        self.isNight = self._isNight(timeCode)

        return self.lamp


    def _isNight(self, timeCode=None):
        if timeCode is None:
            timeCode = self.timeKeeper.makeCode()

        if timeCode in range((self._userSleepTime - self._userWindDownTime), settings.Global.totalDataPoints):
            return True
        if timeCode in range(0, (self._userAlarmTime - self._userAlarmOffset)):
            return True
        return False


    def _buildTable(self, source, sourceRange):
        """
        Build a lookup table based on class attributes and a given data source. Returns list
        """
        # Resize morningSlope and eveningSlope
        source['morning'] = sequenceResize(source['morning'], self.config.morningSlopeDuration)
        source['evening'] = sequenceResize(source['evening'], self.config.eveningSlopeDuration)

        # Create full table and default to nightflat
        table = [source['night']+sourceRange[0]] * settings.Global.totalDataPoints

        for timeCode in range(self._userMorningSlope[0], self._userMorningSlope[1]):
            table[timeCode] = source['morning'][timeCode - self._userMorningSlope[0]]
            table[timeCode] = scale(table[timeCode], (0,100), sourceRange, decimals=1)

        for timeCode in range(self._userEveningSlope[0], self._userEveningSlope[1]):
            table[timeCode] = source['evening'][timeCode - self._userEveningSlope[0]]
            table[timeCode] = scale(table[timeCode], (0,100), sourceRange, decimals=1)
        for timeCode in range(self._userEveningSlope[2], self._userEveningSlope[3]):
            table[timeCode] = source['evening'][timeCode - self._userEveningSlope[2]]
            table[timeCode] = scale(table[timeCode], (0,100), sourceRange, decimals=1)

        for timeCode in range(self._userMorningSlope[1], self._userEveningSlope[2]):
            table[timeCode] = scale(source['day'], (0,100), sourceRange)

        return table
