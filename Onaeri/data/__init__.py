import json
import os
import sys
from ..logger import log

required = ['brightness', 'color', 'deviation']
blacklist = ['__init__.py']
expectedExtention = "json"

# Brightness evening: y = -(100 / (500^1.7))x^1.7 + 100 for 1 <= x <= 500
# Deviation:          y = -0.0001x^3+100 for 0 <= x <= 99

folderPath = os.path.dirname(os.path.abspath(__file__))
requiredData = list(required)


def retrieve_file_names(path=None):
    """
    Get file names from current folder, excluding invisible and
    blacklisted files.
    """
    folder = path or folderPath
    files = [f for f in os.listdir(folder)
             if os.path.isfile(os.path.join(folder, f))
             and not f.startswith(".") and f not in blacklist]

    ret = []
    for f in files:
        tmp = {}
        tmp['name'] = f.split(".")[0]
        tmp['extention'] = f.split(".")[1]
        tmp['path'] = "%s/%s.%s" % (folderPath, tmp['name'], tmp['extention'])
        ret.append(tmp)

    return ret


def valid_file(file, required=None):
    """
    Check for extention and presence in required data list.
    Gives warning when things aren't ok.
    """
    req = required or requiredData

    if not file['name'] or not file['extention'] or not file['path']:
        return False

    if file['extention'] == expectedExtention:
        try:
            req.remove(file['name'])
            return True
        except ValueError:
            log.warn("[Data] Unexpected file " +
                     "`%s.%s` found." % (file['name'], file['extention']))
            log.warn("[Data] Filetype is compatable. Loading file anyway.")
            return True
    else:
        log.warn("[Data] Unexpected file " +
                 "`%s.%s` found." % (file['name'], file['extention']))
        log.warn("[Data] Skipping file and moving on.")
        return False


def expose_json_file_to_namespace(file):
    """
    Expose json file contents to module namespace
    """
    with open(file['path']) as f:
        setattr(sys.modules[__name__], file['name'], json.load(f))


def validate_required_data(required=None):
    """
    Warn user about missing files marked as required.
    """
    req = required or requiredData

    if len(req) > 0:
        log.error("Couldn't found some required data. " +
                  "Missing the following files:")
        for name in req:
            log("\t- %s/%s.%s" % (folderPath, name, expectedExtention))
        log.warn("Program will probably crash.")
        return False
    return True


def do():
    fileList = retrieve_file_names()
    for f in fileList:
        if valid_file(f):
            expose_json_file_to_namespace(f)

    validate_required_data()


do()
