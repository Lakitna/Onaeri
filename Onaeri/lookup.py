from .timekeeper import TimeKeeper
from . import data
from .helper import scale, sequenceResize, inRange, timecodeRange
from .lamp import Lamp
from .logger import log

from . import settings


class Lookup:
    """
    Calculates and dispenses lookup tables for lamp values
    """
    def __init__(self, config,
                 timekeeper=None, lamp=None, totaldatapoints=None):
        self.time = timekeeper or TimeKeeper()
        self.config = config
        self.lamp = lamp or Lamp()
        self.totalDataPoints = (totaldatapoints
                                or settings.Global.totalDataPoints)

        # Sleep rhythm settings
        self._alarmTime = self.time.code(self.config.alarmTime)
        self._alarmOffset = self.time.code(m=self.config.alarmOffset)

        self._sleepTime = self.time.code(self.config.sleepTime)
        self._windDownTime = self.time.code(m=self.config.windDownTime)

        # Create morning and evening slopes based on sleep rhythm settings
        self.morningSlope = self._calculate_morningSlope_range()
        self.eveningSlope = self._calculate_eveningSlope_range()

        # Build lookup tables
        self.anatomy = self._buildAnatomy()
        self.brightness = self._buildTable(data.brightness)  # pylint: disable
        self.color = self._buildTable(data.color)  # pylint: disable

        # print(self.brightness)
        # print()
        # print(self.color)
        # print()
        # print(self.anatomy)
        # print("\n" * 10)
        # exit()

    def table(self, timeCode):
        """
        Get lamp values associated with timecode. Returns lamp object.
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

        darkrange = timecodeRange(self._sleepTime - self._windDownTime,
                                  self._sleepTime)

        if (self.get_period(timeCode) == 'night'
           or inRange(timeCode, darkrange)):
            self.lamp.mode = 'dark'
        else:
            self.lamp.mode = None

        return self.lamp

    def get_period(self, timecode=None):
        """
        Get period of day, based on latest timecode.
        """
        timeCode = timecode or self.time.latestCode

        # Fix for python v < 3.6
        periods = list(self.anatomy.keys())
        periods.sort()

        for period in periods:
            if inRange(timeCode, self.anatomy[period]):
                return period
    period = property(get_period)

    def _buildAnatomy(self):
        anatomy = {
            "morning": self.morningSlope,
            "day": timecodeRange(self.morningSlope[-1][1],
                                 self.eveningSlope[0][0],
                                 rngeMax=self.totalDataPoints),
            "evening": self.eveningSlope,
            "night": timecodeRange(self.eveningSlope[-1][1],
                                   self.morningSlope[0][0],
                                   rngeMax=self.totalDataPoints)
        }

        if (inRange(anatomy['morning'][-1][1], anatomy['evening'])
           or inRange(anatomy['morning'][0][0], anatomy['evening'])):
            log.error("Morning and evening cycles overlap.")
            log.warn("The program will try to run like normal, but some " +
                     "weird behaviour is inevitable.")
            log.warn("Change your settings to fix this.")

        return anatomy

    def _calculate_morningSlope_range(self):
        return timecodeRange(
            self._alarmTime - self._alarmOffset,
            (self._alarmTime
             - self._alarmOffset
             + self.config.morningSlopeDuration
             )
        )

    def _calculate_eveningSlope_range(self):
        return timecodeRange(
            self._sleepTime - self.config.eveningSlopeDuration,
            self._sleepTime
        )

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
        table = [source['night']] * self.totalDataPoints

        for period in self.anatomy:
            count = 0
            for rnge in self.anatomy[period]:
                if period == 'day' or period == 'night':
                    for timeCode in range(rnge[0], rnge[1]):
                        table[timeCode] = source[period]
                else:
                    for timeCode in range(rnge[0], rnge[1]):
                        table[timeCode] = source[period][count]
                        count += 1
        return table
