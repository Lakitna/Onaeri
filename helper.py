import os, sys

def programRestart(self):
    """
    Restart entire program
    """
    os.execl(sys.executable, sys.executable, *sys.argv)


def scale(val, inRange, outRange, decimals=1):
    """
    Scale the given value from one scale to another
    """
    ret = ( (val - inRange[0]) \
            / (inRange[1] - inRange[0]) ) \
            * (outRange[1] - outRange[0]) \
            + outRange[0]

    if ret % 1 == 0:
        ret = round(ret)
    elif decimals > 0:
        ret = round(ret * (10*decimals)) / (10*decimals)
    else:
        ret = round(ret)

    return ret


def sequenceResize(source, length):
    """
    Crude way of resizing a data sequence. Shrinking is here more accurate than expanding.
    """
    sourceLen = len(source)
    out = []
    for i in range(length):
        key = round(i * (sourceLen/length))
        if key >= sourceLen:
            key = sourceLen-1

        out.append(source[key])
    return out


def limitTo(val, rnge):
    """
    Limit input value to a given absolute range
    """
    if val < rnge[0]:  val = rnge[0]
    if val > rnge[1]:  val = rnge[1]
    return val


def inRange(val, rnge):
    """
    Find out if input value is within a given absolute range
    """
    if rnge[0] <= val <= rnge[1]:
        return True
    return False
