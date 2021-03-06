"""
Basic settings
"""
# Duration of lamp transition in seconds, unsigned float.
transitionTime = 1

# Time the program rests between ticks in seconds, unsigned float.
mainLoopDelay = 1

# Minutes per timecode, unsigned float.
minPerTimeCode = .5


"""
Advanced settings
"""
# Amount of times to try sending a command before giving up, unsigned int.
commandsTries = 3

# Extention of settings file, String.
settingFileExtention = '.py'

# Total amount of timecodes in a day, calculated unsigned int.
totalDataPoints = round((24 * 60) // minPerTimeCode)

# Days to keep dynamic setting files without it being used, unsigned int.
dynamicSettingsKeep = 30

# Range of lamp values, int.
valRange = (0, 1000)

# Range of data values, int.
dataRange = (0, 1000)

# Time offset in minutes for scheduler, unsigned int.
# [lamp on time] - [offset] = [scheduled time]
schedulerLampOffset = round(10 // minPerTimeCode)
