from . import settings
import math


def scale(val, inRange, outRange, decimals=0):
    """
    Scale the given value from one scale to another
    """
    if val is None:
        return None

    ret = (
        ((val - inRange[0]) / (inRange[1] - inRange[0]))
        * (outRange[1] - outRange[0])
        + outRange[0]
    )

    if ret % 1 == 0:
        ret = round(ret)
    elif decimals == 0:
        ret = round(ret)
    else:
        ret = round(ret, decimals)

    return ret


def sequenceResize(source, length):
    """
    Resize a data sequence.
    """
    out = []
    step = float(len(source) - 1) / (length - 1)
    for i in range(length):
        key = i * step
        if key > len(source) - 1:
            key = len(source) - 1

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


def timecodeRange(min, max):
    """
    Get a timecode range. Supports 0 hour rollover.
    """
    max = timecodeWrap(max)
    min = timecodeWrap(min)

    rnge = [(min, max)]

    if max < min:
        rnge = [
            (min, settings.Global.totalDataPoints),
            (0, max)
        ]

    for phase in rnge:
        if phase[0] == phase[1]:
            rnge.remove(phase)

    return rnge


def inRange(val, rnge):
    """
    Find out if input value is within a given absolute range
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


def timecodeWrap(val):
    """
    Wrap the input so that it's always within timecode range.
    Not foolproof, but good enough.
    """
    if val < 0:
        val += settings.Global.totalDataPoints
    elif val > settings.Global.totalDataPoints:
        val -= settings.Global.totalDataPoints
    return val
