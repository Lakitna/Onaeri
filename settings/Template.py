"""
Basic settings
"""
# Time alarm is set in (hour, minute)
userAlarmTime = (9, 0)
# Bedtime in (hour, minute)
userSleepTime = (23, 30)


# Allow the lamps to automatically go off in the evening.
automaticPowerOff = True
# Allow the lamps to automatically go on in the morning.
automaticPowerOn  = True


# Lamp brightness adjust in percentages.
briCorrect   = (0, 100)
# Lamp color adjust in percentages.
colorCorrect = (0, 100)


# How many minutes before your alarm time should the lamps go on?
userAlarmOffset  = 30
# How many minutes before your bedtime should the lamps notify you?
userWindDownTime = 30



"""
Advanced settings
"""
# Duration of morningslope in minutes
morningSlopeDuration = 60

# Duration of eveningslope in minutes
eveningSlopeDuration = 500

# Temporary cycle deviation duration in minutes
deviationDuration = 45
