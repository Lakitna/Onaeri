from . import settings


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
    Crude way of resizing a data sequence.
    Shrinking is here more accurate than expanding.
    """
    sourceLen = len(source)
    out = []
    for i in range(length):
        key = int(i * (sourceLen / length))
        if key >= sourceLen:
            key = sourceLen - 1

        out.append(source[key])
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
    rnge = [(min, max)]
    if max < 0:
        max += settings.Global.totalDataPoints
    if max > settings.Global.totalDataPoints:
        max -= settings.Global.totalDataPoints

    if min < 0:
        min += settings.Global.totalDataPoints
    if min > settings.Global.totalDataPoints:
        min -= settings.Global.totalDataPoints

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
