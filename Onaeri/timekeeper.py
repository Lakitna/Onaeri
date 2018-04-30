import time
import math
from . import settings


class TimeKeeper:
    """
    Handles timekeeping in timecodes
    """
    def __init__(self, minpertimecode=None,
                 runtime=0, update=True, latestcode=None):
        self._minPerTimeCode = minpertimecode or settings.Global.minPerTimeCode
        self.latestCode = latestcode or self.code()
        self.update = update
        self.runtime = runtime

    def tick(self):
        """
        Progress the timekeeper and set update flag on timeCode change.
        """
        if self.latestCode == self.code():
            self.update = False
        else:
            self.update = True
            self.runtime += 1

    def code(self, h=None, m=None, s=None, dry=False):
        """
        Calculate a new timecode
        """
        if h is None and m is None and s is None:
            h = time.localtime().tm_hour
            m = time.localtime().tm_min
            s = time.localtime().tm_sec

        if h is None:
            h = 0
        if m is None:
            m = 0
        if s is None:
            s = 0

        if type(h) is tuple:
            if len(h) > 2:
                s = h[2]
            m = h[1]
            h = h[0]

        ret = math.floor(((h * 60) + m + (s / 60)) / self._minPerTimeCode)
        if not dry:
            self.latestCode = ret
        return ret

    @property
    def timestamp(self):
        """
        Return the timestring of a timecode
        """
        minutes = self.latestCode * self._minPerTimeCode
        h = math.floor(minutes / 60)
        m = math.floor(minutes % 60)
        s = math.floor((minutes % 1) * 60)

        return "%02d:%02d:%02d" % (h, m, s)
