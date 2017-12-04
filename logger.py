from os import path, makedirs
import time

setting_logFolder = "log"
setting_logExtention = ".log"


def log(string="", end="\n", flush=False):
    """
    Log and print a message
    """
    print(string, end=end, flush=flush)

    string = "%s%s" % (string, end)
    _writeToFile(string)

def logError(string="", end="\n", flush=False):
    """
    Log and print an error
    """
    print("\033[7;31m %s \033[0;0m" % string, end=end, flush=flush)

    string = "[ERROR] %s [/ERROR]%s" % (string, end)
    _writeToFile(string)

def logWarn(string="", end="\n", flush=False):
    """
    Log and print a warning
    """
    print("\033[1;34m%s\033[0;0m" % string, end=end, flush=flush)

    string = "!!! %s !!!%s" % (string, end)
    _writeToFile(string)

def logSuccess(string="", end="\n", flush=False):
    """
    Log and print a success message
    """
    print("\033[7;32m %s \033[0;0m" % string, end=end, flush=flush)

    string = "[%s]%s" % (string, end)
    _writeToFile(string)

def logHighlight(string="", end="\n", flush=False):
    """
    Log and print a highlighted message
    """
    print("\033[1;36m%s\033[0;0m" % string, end=end, flush=flush)

    string = "%s%s" % (string, end)
    _writeToFile(string)


def _writeToFile(string):
    """
    Add a log entry to logfile
    """
    with open(filePath, 'a') as f:
        f.write(string)


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


# Check if logging folder exists and create if it doesn't
folderPath = '%s/%s' % (path.dirname(path.abspath(__file__)), setting_logFolder)
if not path.exists(folderPath):
    makedirs(folderPath)

# Check if log file exists and create if it doesn't
filePath = "%s/%s%s" % (folderPath, time.strftime("%d-%m-%Y"), setting_logExtention)
if not path.isfile(filePath) or not path.getsize(filePath) > 0:
    with open(filePath, 'w') as f:
        f.write("Log opened on %s\n" % time.strftime("%d-%m-%Y @ %H:%M"))

_writeToFile("\nProgram started\n")
_writeToFile("--------------------------------------------------\n")
