# -*- coding: utf-8 -*-

import re
import inspect
import itertools
import six

from . import commands
from .serial_device import SerialDevice


# http://stackoverflow.com/a/1176023
def convert_name(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# from P. Cladé's RigolD5000 code
# https://pypi.python.org/pypi/RigolDG5000
class ChannelProperty(object):
    def __init__(self, cls):
        self.klass = cls

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.klass
        return self.klass(obj)


class ControllerMeta(type):
    def __new__(cls, name, bases, dct):
        out = dct.copy()
        for key, klass in dct.items():
            if not inspect.isclass(klass):
                continue

            if type(klass) == ControllerMeta:
                out.update({convert_name(key): ChannelProperty(klass)})

            else:
                getter, setter = None, None

                if issubclass(klass, commands.ReadCommand):
                    getter = klass._getter()
                if issubclass(klass, commands.WriteCommand):
                    setter = klass._setter()

                out.update({convert_name(key): property(
                    getter, setter, doc=klass.__doc__)})

        return type.__new__(cls, name, bases, out)


@six.add_metaclass(ControllerMeta)
class Channel(object):
    def __init__(self, parent):
        self.parent = parent

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            return object.__getattribute__(self.parent, key)

    from .commands import Current, Voltage, CurrentOut, VoltageOut


class Channel1(Channel):
    """Output channel 1"""
    ch_num = 1


class Channel2(Channel):
    """Output channel 2"""
    ch_num = 2


@six.add_metaclass(ControllerMeta)
class KoradKA_DualChannel(SerialDevice):
    from .commands import Output, Status, IDN, Beep, Track, OCP, OVP
    ch1 = Channel1
    ch2 = Channel2


@six.add_metaclass(ControllerMeta)
class KoradKA_SingleChannel(SerialDevice):
    from .commands import Output, Status, IDN, Beep, OCP, OVP
    ch1 = Channel1
