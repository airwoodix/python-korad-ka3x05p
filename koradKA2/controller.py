# -*- coding: utf-8 -*-

import re
import inspect
import itertools
from . import commands
from .serial_device import SerialDevice


# http://stackoverflow.com/a/1176023
def convert_name(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class ControllerMeta(type):
    def __new__(cls, name, bases, dct):
        out = dct.copy()
        for key, klass in dct.items():
            if not inspect.isclass(klass):
                continue

            if hasattr(klass, "channels"):
                getters, setters = [], []

                if issubclass(klass, commands.ReadCommand):
                    getters = (klass._getter(chan)
                               for chan in klass.channels)
                if issubclass(klass, commands.WriteCommand):
                    setters = (klass._setter(chan)
                               for chan in klass.channels)

                names = ("{}{}".format(convert_name(key), chan)
                         for chan in klass.channels)

                for name, getter, setter in itertools.zip_longest(
                        names, getters, setters):
                    out.update({name: property(
                        getter, setter, doc=klass.__doc__)})
            else:
                getter, setter = None, None

                if issubclass(klass, commands.ReadCommand):
                    getter = klass._getter()
                if issubclass(klass, commands.WriteCommand):
                    setter = klass._setter()

                out.update({convert_name(key): property(
                    getter, setter, doc=klass.__doc__)})

        print(out)

        return type.__new__(cls, name, bases, out)


class KoradKA2(SerialDevice, metaclass=ControllerMeta):
    from .commands import Current, Voltage, CurrentOut, VoltageOut, \
        EnableOutput, Status, IDN


if __name__ == "__FAKE__":
    # actually wanted
    psu = KoradKA2(port)
    psu.ch1.voltage = 12.5
    print(psu.ch1.voltage_out)  # actual voltage
    print(psu.idn)  # identification
