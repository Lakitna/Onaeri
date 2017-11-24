import os
import importlib
from . import Global
from .. import data
from ..logger import *


blacklist = ["Global", "Template", "__init__"]


def _checkIntegrity(val, rmin=0, rmax=1, *, check=None):
    """
    Check value range and exit() on problems.
    """
    def _ruling(v, rnge):
        if not rnge[0] <= v <= rnge[1]:
            logError("Invalid setting. '%s' is not in allowed range (%s - %s)." % (val, rnge[0], rnge[1]))
            exit()

    if check is None:
        if type(val) is list or type(val) is tuple:
            for v in val:
                _ruling(v, (rmin, rmax))
        else:
            _ruling(val, (rmin, rmax))
    elif check is "unsigned":
        if not val >= 0:
            logError("Invalid setting. '%s' is not in allowed range (%s - ∞)." % (val, rmin))
            exit()
    elif check is "string":
        if not type(val) is str:
            logError("Invalid setting. '%s' is not a string." % (val))
            exit()
    elif check is "boolean":
        if not type(val) is bool:
            logError("Invalid setting. '%s' is not boolean." % (val))
            exit()
    elif check is "time":
        _ruling(val[0], (0, 23))
        _ruling(val[1], (0, 59))
    else:
        logError("Check `%s` could not be performed." % check)
        exit()



_checkIntegrity(Global.minPerTimeCode, check="unsigned")
_checkIntegrity(Global.transitionTime, check="unsigned")
_checkIntegrity(Global.totalDataPoints, check="unsigned")
_checkIntegrity(Global.commandsTries, check="unsigned")
_checkIntegrity(Global.mainLoopDelay, check="unsigned")
_checkIntegrity(Global.settingFileExtention, check="string")

_checkIntegrity(data.brightnessData['day'], 0, 100)
_checkIntegrity(data.brightnessData['night'], 0, 100)
_checkIntegrity(data.brightnessData['morning'], 0, 100)
_checkIntegrity(data.brightnessData['evening'], 0, 100)
_checkIntegrity(data.colorData['day'], 0, 100)
_checkIntegrity(data.colorData['night'], 0, 100)
_checkIntegrity(data.colorData['morning'], 0, 100)
_checkIntegrity(data.colorData['evening'], 0, 100)
_checkIntegrity(data.deviationData, 0, 100)



def _settingFileList():
    """
    Get list of setting files from settings folder.
    """
    ret = []
    files = [f for f in os.listdir(os.path.dirname(__file__)) if os.path.isfile(os.path.join(os.path.dirname(__file__), f))]
    for f in files:
        if f.endswith(Global.settingFileExtention):
            f = f.split(".")[0] # Remove extention
            if f not in blacklist:
                ret.append( f )
    return ret


cycles = _settingFileList();
if len(cycles) == 0:
    logError("No setting files found. Please create a file in the `settings` folder using the Template.py.")
    exit()


def get(settingFile=""):
    """
    Return a setting file
    """
    if not settingFile in cycles:
        logError("Setting file %s not found" % settingFile)
        exit()

    userSettings = importlib.import_module(__name__+"."+settingFile, package=None)

    # Some calculations on settings
    userSettings.eveningSlopeDuration = round(userSettings.eveningSlopeDuration // Global.minPerTimeCode)
    userSettings.morningSlopeDuration = round(userSettings.morningSlopeDuration // Global.minPerTimeCode)
    userSettings.deviationDuration = round(userSettings.deviationDuration // Global.minPerTimeCode)

    userSettingsValidation(userSettings)

    return userSettings


def userSettingsValidation(settings):
    """
    Check integrity of settings
    """
    _checkIntegrity(settings.userAlarmTime, check="time")
    _checkIntegrity(settings.userAlarmOffset, check="unsigned")
    _checkIntegrity(settings.userSleepTime, check="time")
    _checkIntegrity(settings.userWindDownTime, check="unsigned")
    _checkIntegrity(settings.briCorrect, 0, 100)
    _checkIntegrity(settings.colorCorrect, 0, 100)
    _checkIntegrity(settings.morningSlopeDuration, check="unsigned")
    _checkIntegrity(settings.eveningSlopeDuration, check="unsigned")
    _checkIntegrity(settings.deviationDuration, check="unsigned")
    _checkIntegrity(settings.automaticPowerOff, check="boolean")
    _checkIntegrity(settings.automaticPowerOn, check="boolean")
