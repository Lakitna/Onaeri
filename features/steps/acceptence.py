from behave import given, then, when
from Onaeri import lamp
from Onaeri import cycle
from Onaeri import timekeeper


def setup_cycle(context, name, lampCount):
    """
    Create a cycle with a certain amount of lamps in it.
    """
    lamps = {}
    for i in range(lampCount):
        lampName = "%s-%d" % (name, i)
        lamps[lampName] = lamp.Lamp(name=lampName)

    cycleObj = cycle.Cycle(name,
                           lamps,
                           timekeeper.TimeKeeper(update=False))
    set_cycle_lamps(cycleObj, {'brightness': None,
                               'color': None,
                               'power': None})
    return cycleObj


def set_cycle_lamps(cycle, kwargs):
    """
    Update the lamps in a cycle
    """
    lamps = {}
    for id in cycle.devices:
        lamps[id] = lamp.Lamp(**kwargs)
        lamps[id].name = id


@given('there are {count:d} lamp groups')
def step_impl(context, count):
    """ Setup N cycles with 1 lamp """
    context.cycles = []
    for i in range(count):
        context.cycles.append(
            setup_cycle(context, context.cycleNames[i], 1)
        )


@given('there are {cCount:d} lamp groups with {lCount:d} lamps each')
def step_impl(context, cCount, lCount):
    """ Setup N cycles with N lamp """
    context.cycles = []
    for i in range(cCount):
        context.cycles.append(
            setup_cycle(context, context.cycleNames[i], lCount)
        )


@given('there are {count:d} lamps')
def step_impl(context, count):
    """ Setup a cycle with N lamps """
    context.cycles = [setup_cycle(context, context.cycleNames[0], count)]


@given('there is a lamp')
def step_impl(context):
    """ Setup a cycle with one lamp """
    context.cycles = [setup_cycle(context, context.cycleNames[0], 1)]


@given('the lamps are turned on')
@given('the lamp is turned on')
def step_impl(context):
    """
    Turn on the lamps and make sure the observer doesn't think the cycle
    should be updated.
    """
    for c in context.cycles:
        for _ in range(2):
            set_cycle_lamps(c, {'brightness': 100,
                                'color': 100,
                                'power': True})


@when('the {attr} of the lamps are changed')
@when('the {attr} of the lamp is changed')
def step_impl(context, attr):
    for c in context.cycles:
        devices = c.devices
        observer = c.observer
        currentVal = getattr(observer[next(iter(devices))].data, attr)
        if currentVal is None:
            newVal = 50
        elif currentVal > 50:
            newVal = currentVal // 2
        else:
            newVal = currentVal * 2

        set_cycle_lamps(c, {attr: newVal})


@then('the change will be detected')
def step_impl(context):
    """ The observer detects changes in the lamps """
    for c in context.cycles:
        devices = c.devices
        observer = c.observer

        for id in devices:
            assert observer[id].update is True
