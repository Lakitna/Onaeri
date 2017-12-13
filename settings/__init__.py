import os
import importlib
from . import Global
from . import dynamic
from .. import data
from ..logger import log


blacklist = ["Global", "Template", "__init__"]


def _checkIntegrity(val, rmin=0, rmax=1, *, check=None):
    """
    Check value range and exit() on problems.
    """
    def _ruling(v, rnge):
        if not rnge[0] <= v <= rnge[1]:
            log.error(
                "Invalid setting. '%s' is not in allowed range (%s - %s)."
                % (val, rnge[0], rnge[1])
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
            log.error("Invalid setting. '%s' is not in allowed range (%s - ∞)."
                      % (val, rmin))
            exit()
    elif check is "string":
        if not type(val) is str:
            log.error("Invalid setting. '%s' is not a string." % (val))
            exit()
    elif check is "boolean":
        if not type(val) is bool:
            log.error("Invalid setting. '%s' is not boolean." % (val))
            exit()
    elif check is "time":
        _ruling(val[0], (0, 23))
        _ruling(val[1], (0, 59))
    else:
        log.error("Check `%s` could not be performed." % check)
        exit()


_checkIntegrity(Global.minPerTimeCode, check="unsigned")
_checkIntegrity(Global.transitionTime, check="unsigned")
_checkIntegrity(Global.totalDataPoints, check="unsigned")
_checkIntegrity(Global.commandsTries, check="unsigned")
_checkIntegrity(Global.mainLoopDelay, check="unsigned")
_checkIntegrity(Global.settingFileExtention, check="string")

_checkIntegrity(data.brightness['day'], 0, 1000)
_checkIntegrity(data.brightness['night'], 0, 1000)
_checkIntegrity(data.brightness['morning'], 0, 1000)
_checkIntegrity(data.brightness['evening'], 0, 1000)
_checkIntegrity(data.color['day'], 0, 1000)
_checkIntegrity(data.color['night'], 0, 1000)
_checkIntegrity(data.color['morning'], 0, 1000)
_checkIntegrity(data.color['evening'], 0, 1000)
_checkIntegrity(data.deviation, 0, 1000)


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
    _checkIntegrity(settings.alarmTime, check="time")
    _checkIntegrity(settings.alarmOffset, check="unsigned")
    _checkIntegrity(settings.sleepTime, check="time")
    _checkIntegrity(settings.windDownTime, check="unsigned")
    _checkIntegrity(settings.morningSlopeDuration, check="unsigned")
    _checkIntegrity(settings.eveningSlopeDuration, check="unsigned")
    _checkIntegrity(settings.deviationDuration, check="unsigned")
    _checkIntegrity(settings.autoPowerOff, check="boolean")
    _checkIntegrity(settings.autoPowerOn, check="boolean")
