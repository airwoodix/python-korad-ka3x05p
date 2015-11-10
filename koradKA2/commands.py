# -*- coding: utf-8 -*-

import re
import collections


class Command:
    pass


class ReadCommand(Command):
    @classmethod
    def _getter(cls):
        def getter(self):
            channel = getattr(self, "ch_num", None)
            a = self.ask(cls.cmd, channel=channel)
            return cls.to_python(a)
        return getter


class WriteCommand(Command):
    @classmethod
    def _setter(cls):
        def setter(self, value):
            channel = getattr(self, "ch_num", None)
            value = cls.to_bus(value)
            self.write(cls.cmd, channel=channel, param=value)
        return setter


# ====================

class Current(ReadCommand, WriteCommand):
    """Current set point"""
    cmd = "ISET"

    @classmethod
    def to_python(cls, value):
        return float(value)

    @classmethod
    def to_bus(cls, value):
        # enforce float
        value = float(value)
        return str(value)


class Voltage(ReadCommand, WriteCommand):
    """Voltage set point"""
    cmd = "VSET"

    @classmethod
    def to_python(cls, value):
        return float(value)

    @classmethod
    def to_bus(cls, value):
        value = float(value)
        return str(value)


class CurrentOut(ReadCommand):
    """Actual output current"""
    cmd = "IOUT"

    @classmethod
    def to_python(cls, value):
        return float(value)


class VoltageOut(ReadCommand):
    """Actual output voltage"""
    cmd = "VOUT"

    @classmethod
    def to_python(cls, value):
        return Float(value)


class Track(WriteCommand):
    """Set tracking mode: independent, series or parallel"""
    cmd = "TRACK"

    values = {"independent": 0,
              "series": 1,
              "parallel": 2}

    @classmethod
    def to_bus(cls, value):
        value = Track.values[int(value)]
        return value


class Beep(WriteCommand):
    """Enable/disable beep"""
    cmd = "BEEP"

    @classmethod
    def to_bus(cls, value):
        val = 0 if not value else 1
        return val


class EnableOutput(WriteCommand):
    """Enable/disable output"""
    cmd = "OUT"

    @classmethod
    def to_bus(cls, value):
        val = 0 if not value else 1
        return val


class Status(ReadCommand):
    """Power supply status"""
    cmd = "STATUS"

    python_type = collections.namedtuple("Status",
                                         ["ch1_mode",
                                          "ch2_mode",
                                          "tracking",
                                          "OVP", "OCP",
                                          "ch1_enabled",
                                          "ch2_enabled"])

    @classmethod
    def to_python(cls, value):
        value = int.from_bytes(value.encode("ascii"), "big")

        dct = {}
        dct["ch1_mode"] = "CV" if value >> 0 else "CC"
        dct["ch2_mode"] = "CV" if value >> 1 else "CC"

        if (value >> 2) & 3 == 0:
            dct["tracking"] = "independent"
        elif (value >> 2) & 3 == 1:
            dct["tracking"] = "series"
        else:
            dct["tracking"] = "parallel"

        dct["OVP"] = True if value >> 4 else False
        dct["OCP"] = True if value >> 5 else False
        dct["ch1_enabled"] = True if value >> 6 else False
        dct["ch2_enabled"] = True if value >> 7 else False
        return Status.python_type(**dct)


class IDN(ReadCommand):
    """Identification"""
    cmd = "*IDN"

    @classmethod
    def to_python(cls, value):
        return str(value)
