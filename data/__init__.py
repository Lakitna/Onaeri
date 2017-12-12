import json
import os
import sys
from ..logger import log

requiredData = ['brightness', 'color', 'deviation']
blacklist = ['__init__.py']
expectedExtention = "json"

# Brightness evening: y = -(100 / (500^1.7))x^1.7 + 100 for 1 <= x <= 500
# Deviation:          y = -0.0001x^3+100 for 0 <= x <= 99


path = os.path.dirname(os.path.abspath(__file__))
files = [f for f in os.listdir(path)
         if os.path.isfile(os.path.join(path, f))]

for f in files:
    if f not in blacklist:
        name = f.split(".")[0]
        extention = f.split(".")[1]
        if extention == expectedExtention:
            try:
                requiredData.remove(name)
            except ValueError:
                log.warn("[Data] Unexpected file " +
                         "`%s.%s` found." % (name, extention))
                log.warn("[Data] Filetype is compatable. Loading file anyway.")

            filePath = "%s/%s" % (path, f)
            setattr(sys.modules[__name__],
                    name,
                    json.load(open(filePath)))
        else:
            log.warn("[Data] Unexpected file " +
                     "`%s.%s` found." % (name, extention))
            log.warn("[Data] Skipping file and moving on.")


if len(requiredData) > 0:
    log.error("Couldn't found some required data. " +
              "Missing the following files:")
    log(str(requiredData))
    log.warn("Program will probably crash.")
