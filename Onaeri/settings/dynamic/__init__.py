import json
import os
import time
from ...logger import log
from .. import Global

enableLogs = True

blacklist = ['__init__.py']
expectedExtention = "json"
folderPath = os.path.dirname(os.path.abspath(__file__))
fileTemplate = {
    'min': {'brightness': Global.valRange[0], 'color': Global.valRange[0]},
    'max': {'brightness': Global.valRange[1], 'color': Global.valRange[1]},
    'power': {'off': 0, 'on': 0},
    'features': {'color': False, 'temp': False, 'dim': False},
    'meta': {'called': 0, 'created': time.time()}
}


def get(id_, groups=None):
    filePath = "%s/%s.%s" % (folderPath, id_, expectedExtention)
    try:
        content = json.load(open(filePath))
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        _reset(id)
        return fileTemplate

    ret = {}
    if groups is not None:
        if isinstance(groups, (str, int)):
            # Make groups iterable if it isn't
            groups = [groups]

        for group in groups:
            try:
                ret[group] = content[group]
            except KeyError:
                _reset(id_)
    else:
        ret = content

    if len(ret) == 1:
        ret = ret[sorted(ret.keys())[0]]

    set(id_, 'meta', {'called': time.time()})

    return ret


def set(id, group, data, keys=None):
    filePath = "%s/%s.%s" % (folderPath, id, expectedExtention)
    try:
        content = json.load(open(filePath))
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        _reset(id)
        set(id, group, data, keys)
        return

    if isinstance(data, dict):
        if group not in content:
            content[group] = {}
        if keys is None:
            keys = [key for key in data]

        for k in keys:
            if data[k] is not None:
                content[group][k] = data[k]

        with open(filePath, 'w') as f:
            f.write(json.dumps(content))

        if enableLogs:
            log.blind("[time]\t%s\t%s\t%s" % (str(content['min']),
                                              str(content['max']),
                                              str(content['power'])),
                      name="dynamic_%s" % id)
    else:
        log.error("[Settings][Dynamic] Unexpected datatype provided")
        log("Data provided:")
        log("type: %s" % type(data))
        log(data)
        exit()


def list():
    files = [f for f in os.listdir(folderPath)
             if os.path.isfile(os.path.join(folderPath, f))
             and not f.startswith(".") and f not in blacklist]

    ret = []
    for f in files:
        if f.endswith(".%s" % expectedExtention):
            ret.append(f.split(".%s" % expectedExtention)[0])
    return ret


def _reset(id_):
    log.warn("Dynamic settings for `%s` have been reset." % id_)

    filePath = "%s/%s.%s" % (folderPath, id_, expectedExtention)
    with open(filePath, 'w') as f:
        f.write(json.dumps(fileTemplate))


def _cleanup(days=Global.dynamicSettingsKeep):
    """
    Remove old dynamic settings
    """
    for f in list():
        f = "%s.%s" % (f, expectedExtention)
        remove = False
        path = os.path.join(folderPath, f)

        try:
            content = json.load(open(path))
        except json.decoder.JSONDecodeError:
            # Can't parse the file as JSON, so lets toss it.
            remove = True
        else:
            if content['meta']['called'] < (time.time() - (days * 86400)):
                if not content['meta']['called'] == 0:
                    remove = True

        if remove:
            os.remove(path)
            log("[Cleanup] Removed old dynamic settings file `%s`." % f)


_cleanup()
