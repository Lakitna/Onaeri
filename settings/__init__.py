import os
import importlib
from . import Global
from . import dynamic
from .. import data
from ..logger import log


blacklist = ["Global", "Template", "__init__"]


def _checkIntegrity(val, rmin=0, rmax=1, *, check=None, tag=None):
    """
    Check value range and exit() on problems.
    """
    prefix = ""
    if tag is not None:
        prefix = "[%s] " % tag

    def _ruling(v, rnge):
        if not rnge[0] <= v <= rnge[1]:
            log.error(
                "%sInvalid setting. '%s' is not in allowed range (%s - %s)."
                % (prefix, val, rnge[0], rnge[1])
            )
            exit()

    if check is None:
        if type(val) is list or type(val) is tuple:
            for v in val:
                _ruling(v, (rmin, rmax))
        else:
            _ruling(val, (rmin, rmax))
    elif check is "unsigned":
        if not val >= 0:
            log.error("%sInvalid setting. " +
                      "'%s' is not in allowed range (%s - ∞)."
                      % (prefix, val, rmin))
            exit()
    elif check is "string":
        if not type(val) is str:
            log.error("%sInvalid setting. '%s' is not a string."
                      % (prefix, val))
            exit()
    elif check is "boolean":
        if not type(val) is bool:
            log.error("%sInvalid setting. '%s' is not boolean."
                      % (prefix, val))
            exit()
    elif check is "time":
        _ruling(val[0], (0, 23))
        _ruling(val[1], (0, 59))
    elif check is "lampVal":
        _ruling(val, Global.valRange)
    elif check is "dataVal":
        if type(val) is list or type(val) is tuple:
            for v in val:
                _ruling(v, Global.dataRange)
    else:
        log.error("%sCheck `%s` could not be performed." % (prefix, check))
        exit()


_checkIntegrity(Global.minPerTimeCode, check="unsigned", tag="Global")
_checkIntegrity(Global.transitionTime, check="unsigned", tag="Global")
_checkIntegrity(Global.totalDataPoints, check="unsigned", tag="Global")
_checkIntegrity(Global.commandsTries, check="unsigned", tag="Global")
_checkIntegrity(Global.mainLoopDelay, check="unsigned", tag="Global")
_checkIntegrity(Global.settingFileExtention, check="string", tag="Global")
_checkIntegrity(Global.valRange[0], check="unsigned", tag="Global")
_checkIntegrity(Global.valRange[1], check="unsigned", tag="Global")
_checkIntegrity(Global.dataRange[0], check="unsigned", tag="Global")
_checkIntegrity(Global.dataRange[1], check="unsigned", tag="Global")

_checkIntegrity(data.brightness['day'], check="dataVal", tag="Data")
_checkIntegrity(data.brightness['night'], check="dataVal", tag="Data")
_checkIntegrity(data.brightness['morning'], check="dataVal", tag="Data")
_checkIntegrity(data.brightness['evening'], check="dataVal", tag="Data")
_checkIntegrity(data.color['day'], check="dataVal", tag="Data")
_checkIntegrity(data.color['night'], check="dataVal", tag="Data")
_checkIntegrity(data.color['morning'], check="dataVal", tag="Data")
_checkIntegrity(data.color['evening'], check="dataVal", tag="Data")
_checkIntegrity(data.deviation, check="dataVal", tag="Data")

for id in dynamic.list():
    settings = dynamic.get(id)
    _checkIntegrity(settings['min']['brightness'],
                    check="lampVal", tag="Dynamic|%s" % id)
    _checkIntegrity(settings['min']['color'],
                    check="lampVal", tag="Dynamic|%s" % id)
    _checkIntegrity(settings['max']['brightness'],
                    check="lampVal", tag="Dynamic|%s" % id)
    _checkIntegrity(settings['max']['color'],
                    check="lampVal", tag="Dynamic|%s" % id)


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
