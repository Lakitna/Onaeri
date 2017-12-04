from os import path, makedirs
import time

setting_logFolder = "log"
setting_logExtention = ".tsv"
setting_programLogName = "main.log"


def log(string="", name=None, end="\n", flush=False):
    """
    Log and print a message
    """
    string = _stringReplace(string)
    print(string, end=end, flush=flush)

    string = "%s%s" % (string, end)
    _writeToFile(string, name)

def logBlind(string="", name=None, end="\n"):
    """
    Log in the background
    """
    string = _stringReplace(string)
    string = "%s%s" % (string, end)
    _writeToFile(string, name)

def logError(string="", name=None, end="\n", flush=False):
    """
    Log and print an error
    """
    string = _stringReplace(string)
    print("\033[7;31m %s \033[0;0m" % string, end=end, flush=flush)

    string = "[ERROR] %s [/ERROR]%s" % (string, end)
    _writeToFile(string, name)

def logWarn(string="", name=None, end="\n", flush=False):
    """
    Log and print a warning
    """
    string = _stringReplace(string)
    print("\033[1;34m%s\033[0;0m" % string, end=end, flush=flush)

    string = "!!! %s !!!%s" % (string, end)
    _writeToFile(string, name)

def logSuccess(string="", name=None, end="\n", flush=False):
    """
    Log and print a success message
    """
    string = _stringReplace(string)
    print("\033[7;32m %s \033[0;0m" % string, end=end, flush=flush)

    string = "[%s]%s" % (string, end)
    _writeToFile(string, name)

def logHighlight(string="", name=None, end="\n", flush=False):
    """
    Log and print a highlighted message
    """
    string = _stringReplace(string)
    print("\033[1;36m%s\033[0;0m" % string, end=end, flush=flush)

    string = "%s%s" % (string, end)
    _writeToFile(string, name)


def _writeToFile(string, name=None):
    """
    Add a log entry to logfile
    """
    extention = setting_logExtention
    if name is None:
        name = setting_programLogName
        extention = ""

    with open("%s/%s%s" % (folderPath, name, extention), 'a') as f:
        f.write(string)


def _stringReplace(string):
    string = string.replace("[time]", time.strftime("%H:%M:%S"))

    return string


def summary(values):
    log("\n")
    log("--------------------------------------------------")
    log("RUNTIME SUMMARY")
    log("Generated on %s" % time.strftime("%d-%m-%Y @ %H:%M"))
    log("--------------------------------------------------")
    for key in values:
        if type(values[key]) is dict:
            log("%s:" % key)
            for subkey in values[key]:
                log("\t%s:\t\t%s" % (subkey, values[key][subkey]))
        else:
            log("%s:\t\t%s" % (key, values[key]))
    log()
    _writeToFile("\n\n\n\n\n")


def logHeaders(name):
    if not path.exists("%s/%s%s" % (folderPath, name, setting_logExtention)):
        _writeToFile("%s\t%s\t%s\t%s\t%s\t%s\n" % (
            "Timestamp",
            "Brightness",
            "Color",
            "Power",
            "Observer update",
            "Deviation active"
        ), name)



# Check if main logging folder exists and create if it doesn't
folderPath = '%s/%s' % (path.dirname(path.abspath(__file__)), setting_logFolder)
if not path.exists(folderPath):
    makedirs(folderPath)

# Check if daily logging folder exists and create if it doesn't
folderPath = '%s/%s' % (folderPath, time.strftime("%d-%m-%Y"))
if not path.exists(folderPath):
    makedirs(folderPath)


# Check if program log file exists and create if it doesn't
filePath = "%s/%s" % (folderPath, setting_programLogName)
if not path.isfile(filePath) or not path.getsize(filePath) > 0:
    with open(filePath, 'w') as f:
        f.write("Log opened on %s\n" % time.strftime("%d-%m-%Y @ %H:%M"))

_writeToFile("\nProgram started\n")
_writeToFile("--------------------------------------------------\n")
