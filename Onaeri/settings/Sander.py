"""
Basic settings
"""
# Time alarm is set in (hour, minute)
alarmTime = (9, 30)
# Bedtime in (hour, minute)
sleepTime = (23, 30)


# Allow the lamps to automatically go off in the evening.
autoPowerOff = True
# Allow the lamps to automatically go on in the morning.
autoPowerOn = True


# How many minutes before your alarm time should the lamps go on?
alarmOffset = 5
# How many minutes before your bedtime should the lamps notify you?
windDownTime = 29


"""
Advanced settings
"""
# Duration of morningslope in minutes
morningSlopeDuration = 60

# Duration of eveningslope in minutes
eveningSlopeDuration = 400

# Minumum time in minutes a duration cycle should run
deviationDuration = 10
