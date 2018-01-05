from .settings import dynamic
from .logger import log
from .helper import timecodeWrap


class Scheduler:
    def __init__(self, TimeKeeper):
        self.time = TimeKeeper
        self.events = {}

        self.add((0, 0), log.fileManagement, "Log file management")
        self.add((3, 0), dynamic.cleanup, "Dynamic settings file cleanup")

    def add(self, time, function, description=None, args={}):
        """
        Add an event to the schedule
        """
        def keyExists(key):
            key = timecodeWrap(key)
            if key in self.events:
                return keyExists(key + 1)
            return key

        if type(time) is not int:
            if len(time) < 2:
                time = (time, 0)
            time = self.time.code(h=time[0], m=time[1], dry=True)

        time = keyExists(time)
        self.events[time] = (function, description, args)

        log.blind("\nScheduled an event for %s:" % self.time.timestamp(time))
        log.blind("\tDescription: %s" % description)
        log.blind("\tFunction: %s" % function)
        log.blind("\tArguments: %s" % args)

    def tick(self):
        """
        Advance the schedule by one tick
        """
        if self.time.update:
            if self.time.latestCode in self.events:
                try:
                    event = self.events[self.time.latestCode]
                    event[0](**event[2])
                except TypeError:
                    log.error("[Scheduler] Timed event could not be " +
                              "triggered at [time]: %s"
                              % self.events[self.time.latestCode][1])
                else:
                    log("[Scheduler] Timed event triggered at [time]: %s"
                        % self.events[self.time.latestCode][1])
