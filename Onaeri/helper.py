from . import settings
import math


def scale(val, inRange, outRange, decimals=0):
    """
    Scale the given value from one range to another
    """
    if val is None:
        return None

    result = (
        ((val - inRange[0]) / (inRange[1] - inRange[0]))
        * (outRange[1] - outRange[0])
        + outRange[0]
    )

    if decimals == 0 or result % 1 == 0:
        return round(result)
    else:
        return round(result, decimals)


def sequenceResize(source, length):
    """
    Resize a data sequence.
    """
    if length <= 1:
        return [source[0]]

    out = []
    step = float(len(source) - 1) / (length - 1)
    for i in range(length):
        key = round(i * step, 5)
        low = source[int(math.floor(key))]
        high = source[int(math.ceil(key))]
        ratio = key % 1
        out.append(round((1 - ratio) * low + ratio * high))

    return out


def limitTo(val, rnge):
    """
    Limit input value to a given absolute range
    """
    if val is None:
        return None
    if val < rnge[0]:
        val = rnge[0]
    if val > rnge[1]:
        val = rnge[1]
    return val


def timecodeRange(min, max, rngeMax=None):
    """
    Get a timecode range. Supports 0 hour rollover.
    """
    if rngeMax is None:
        rngeMax = settings.Global.totalDataPoints

    max = timecodeWrap(max, rngeMax)
    min = timecodeWrap(min, rngeMax)

    rnge = [(min, max)]

    if max < min:
        rnge = [
            (min, rngeMax),
            (0, max)
        ]

    for phase in rnge:
        if phase[0] == phase[1]:
            rnge.remove(phase)

    return rnge


def inRange(val, rnge):
    """
    Is the input value within one or multiple given absolute ranges
    """
    def do(value, rnge):
        if rnge[0] <= value <= rnge[1]:
            return True

    if val is None:
        return False

    for r in rnge:
        if type(r) is tuple or type(r) is list:
            if len(r) == 2:
                if do(val, r):
                    return True
        else:
            if do(val, rnge):
                return True
            break
    return False


def timecodeWrap(val, rngeMax=None):
    """
    Wrap the input so that it's always within timecode range.
    """
    if rngeMax is None:
        rngeMax = settings.Global.totalDataPoints

    if val < 0:
        val += rngeMax
    elif val > rngeMax:
        val -= rngeMax
    return val
