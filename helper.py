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
    if val is not None:
        if val < rnge[0]:
            return rnge[0]
        if val > rnge[1]:
            return rnge[1]
    return val


def timecodeRange(min, max):
    """
    Get a timecode range. Supports 0 hour rollover.
    """
    max = timecodeWrap(max)
    min = timecodeWrap(min)

    if max < min:
        rnge = [
            (min, settings.Global.totalDataPoints),
            (0, max)
        ]

        # Remove range phases where min == max
        for phase in rnge:
            if phase[0] == phase[1]:
                rnge.remove(phase)

        return rnge
    else:
        return [(min, max)]


def inRange(val, rnge):
    """
    Is the input value within one or multiple given absolute ranges
    """
    if val is None:
        return False

    if type(rnge[0]) is int:
        if rnge[0] > rnge[1]:
            rnge = (rnge[1], rnge[0])
        if rnge[0] <= val <= rnge[1]:
            return True
    else:
        for r in rnge:
            if r[0] > r[1]:
                r = (r[1], r[0])
            if r[0] <= val <= r[1]:
                return True
    return False


def timecodeWrap(val):
    """
    Wrap the input so that it's always within timecode range.
    """
    if val < 0:
        return val + settings.Global.totalDataPoints
    if val > settings.Global.totalDataPoints:
        return val - settings.Global.totalDataPoints
    return val
