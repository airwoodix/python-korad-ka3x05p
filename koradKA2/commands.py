# -*- coding: utf-8 -*-


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
        return float(value)


class EnableOutput(WriteCommand):
    """Enable/disable output"""
    cmd = "OUT"

    @classmethod
    def to_bus(cls, value):
        val = 0 if not value else 1
        return val


class Status(ReadCommand):
    """Raw power supply status"""
    cmd = "STATUS"

    @classmethod
    def to_python(cls, value):
        return int(value)


class IDN(ReadCommand):
    """Identification"""
    cmd = "*IDN"

    @classmethod
    def to_python(cls, value):
        return str(value)
