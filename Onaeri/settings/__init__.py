import os
import importlib
from . import Global
from . import dynamic
from .. import data
from ..logger import log


blacklist = ["Global", "Template", "__init__"]


def _checkIntegrity(val, rnge=(0, 1), *, check=None, tag=None):
    """
    Check value range and exit() on problems.
    """
    prefix = ""
    if tag is not None:
        prefix = "[%s] " % tag

    def _ruling(v, rnge):
        if not rnge[0] <= v <= rnge[1]:
            log.error("%sInvalid setting. " % prefix +
                      "'%s' is not in allowed range (%s - %s)."
                      % (v, rnge[0], rnge[1]))
            exit()

    if not isinstance(val, (list, tuple)):
        if check is "string":
            if not isinstance(val, str):
                log.error("%sInvalid setting. '%s' is not a string."
                          % (prefix, val))
                exit()
        elif check is "boolean":
            if not isinstance(val, bool):
                log.error("%sInvalid setting. '%s' is not boolean."
                          % (prefix, val))
                exit()
        elif check is "time":
            _ruling(val[0], (0, 23))
            _ruling(val[1], (0, 59))

        val = [val]

    for v in val:
        if check is None:
            _ruling(v, rnge)
        elif check is "unsigned":
            if not v >= 0:
                log.error("%sInvalid setting. " % prefix +
                          "'%s' is not in allowed range (0 - ∞)."
                          % v)
                exit()


_checkIntegrity(Global.minPerTimeCode, check="unsigned", tag="Global")
_checkIntegrity(Global.transitionTime, check="unsigned", tag="Global")
_checkIntegrity(Global.totalDataPoints, check="unsigned", tag="Global")
_checkIntegrity(Global.commandsTries, check="unsigned", tag="Global")
_checkIntegrity(Global.mainLoopDelay, check="unsigned", tag="Global")
_checkIntegrity(Global.settingFileExtention, check="string", tag="Global")
_checkIntegrity(Global.valRange, check="unsigned", tag="Global")
_checkIntegrity(Global.dataRange, check="unsigned", tag="Global")
_checkIntegrity(Global.schedulerLampOffset, check="unsigned", tag="Global")

_checkIntegrity(data.brightness['day'], Global.dataRange, tag="Data")
_checkIntegrity(data.brightness['night'], Global.dataRange, tag="Data")
_checkIntegrity(data.brightness['morning'], Global.dataRange, tag="Data")
_checkIntegrity(data.brightness['evening'], Global.dataRange, tag="Data")
_checkIntegrity(data.color['day'], Global.dataRange, tag="Data")
_checkIntegrity(data.color['night'], Global.dataRange, tag="Data")
_checkIntegrity(data.color['morning'], Global.dataRange, tag="Data")
_checkIntegrity(data.color['evening'], Global.dataRange, tag="Data")
_checkIntegrity(data.deviation, Global.dataRange, tag="Data")

for id_ in dynamic.list():
    settings = dynamic.get(id_)
    _checkIntegrity(settings['min']['brightness'], Global.valRange,
                    tag="Dynamic|%s" % id_)
    _checkIntegrity(settings['min']['color'], Global.valRange,
                    tag="Dynamic|%s" % id_)
    _checkIntegrity(settings['max']['brightness'], Global.valRange,
                    tag="Dynamic|%s" % id_)
    _checkIntegrity(settings['max']['color'], Global.valRange,
                    tag="Dynamic|%s" % id_)


def _settingFileList():
    """
    Get list of setting files from settings folder.
    """
    ret = []
    files = [f for f in os.listdir(os.path.dirname(__file__))
             if os.path.isfile(os.path.join(os.path.dirname(__file__), f))]
    for f in files:
        if f.endswith(Global.settingFileExtention):
            f = f.split(".")[0]  # Remove extention
            if f not in blacklist:
                ret.append(f)
    return ret


cycles = _settingFileList()
if len(cycles) == 0:
    log.error("No setting files found. Please create a file " +
              "in the `settings` folder using the Template.py.")


def get(settingFile=""):
    """
    Return a setting file
    """
    if settingFile not in cycles:
        log.error("Setting file %s not found" % settingFile)
        exit()

    userSettings = importlib.import_module(
        __name__ + "." + settingFile, package=None)

    # Some calculations on settings
    userSettings.eveningSlopeDuration = round(
        userSettings.eveningSlopeDuration // Global.minPerTimeCode
    )
    userSettings.morningSlopeDuration = round(
        userSettings.morningSlopeDuration // Global.minPerTimeCode
    )
    userSettings.deviationDuration = round(
        userSettings.deviationDuration // Global.minPerTimeCode
    )

    userSettingsValidation(userSettings)

    return userSettings


def userSettingsValidation(settings):
    """
    Check integrity of settings
    """
    name = settings.__name__.split(".")
    name = name[len(name) - 1]
    _checkIntegrity(settings.alarmTime, check="time", tag=name)
    _checkIntegrity(settings.alarmOffset, check="unsigned", tag=name)
    _checkIntegrity(settings.sleepTime, check="time", tag=name)
    _checkIntegrity(settings.windDownTime, check="unsigned", tag=name)
    _checkIntegrity(settings.morningSlopeDuration, check="unsigned", tag=name)
    _checkIntegrity(settings.eveningSlopeDuration, check="unsigned", tag=name)
    _checkIntegrity(settings.deviationDuration, check="unsigned", tag=name)
    _checkIntegrity(settings.autoPowerOff, check="boolean", tag=name)
    _checkIntegrity(settings.autoPowerOn, check="boolean", tag=name)
