# -*- coding: utf-8 -*-

import os
import time
import fcntl
import subprocess
import shlex
import contextlib


@contextlib.contextmanager
def optional_lock(lockfile, flags=fcntl.LOCK_EX):
    if lockfile is None:
        yield
    else:
        with open(lockfile, "w") as f:
            fcntl.lockf(f, flags)
            yield
            fcntl.lockf(f, fcntl.LOCK_UN)


class SerialDeviceBase(object):
    def __init__(self, encoding, read_delay):
        self.conn = None
        self.encoding = encoding
        self.read_delay = float(read_delay)
        self.lockfile = None

    @staticmethod
    def format_command(cmd, channel, param, ask):
        if channel is None and param is not None:
            channel, param = param, channel

        param = "" if param is None else ":{}".format(param)
        channel = "" if channel is None else channel
        ask = "" if not ask else "?"

        return "{cmd}{channel}{param}{ask}".format(**locals())

    def write(self, cmd, channel=None, param=None, ask=False):
        msg = self.format_command(cmd, channel=channel, param=param,
                                  ask=ask)
        with optional_lock(self.lockfile):
            rv = self.conn.write(msg.encode(self.encoding))
        return rv

    def read_all(self):
        time.sleep(self.read_delay)
        num_to_read = self.conn.inWaiting()

        with optional_lock(self.lockfile):
            value = self.conn.read(num_to_read)

        return value.decode(self.encoding)

    def ask(self, cmd, channel=None, param=None):
        self.write(cmd, channel=channel, param=param, ask=True)
        return self.read_all()


class SerialDevice(SerialDeviceBase):
    def __init__(self, port, timeout=1, encoding="ascii",
                 read_delay=0.1):
        SerialDeviceBase.__init__(self, encoding=encoding,
                                  read_delay=read_delay)

        import serial
        self.port = port
        self.conn = serial.serial_for_url(self.port, baudrate=9600,
                                          timeout=timeout)

        self.lockfile = self.get_lockfile(port)

    def get_lockfile(self):
        serial_num = get_usb_prop_serial(self.port)
        return os.path.join("/tmp", "korad_{}.lock")


class TestSerialDevice(SerialDeviceBase):
    def __init__(self, encoding="ascii", read_delay=0.1):
        SerialDeviceBase.__init__(self, encoding=encoding,
                                  read_delay=read_delay)

        class FakeConn:
            def write(self, msg):
                self.msg = msg
                print("Write: '{}'".format(msg))

            def inWaiting(self):
                return len(self.msg)

            def read(self, size):
                ret = self.msg[:size]
                self.msg = self.msg[size:]
                return ret

        self.conn = FakeConn()

    def write(self, cmd, channel=None, param=None, ask=False):
        SerialDeviceBase.write(self, cmd, channel=channel, param=param,
                               ask=ask)

    def ask(self, cmd, channel=None, param=None):
        a = SerialDeviceBase.ask(self, cmd, channel=channel, param=param)
        return a


def get_usb_prop_serial(port):
    cmd = "udevadm info -q property {}".format(port)
    res = subprocess.check_output(shlex.split(cmd)).decode("ascii").split("\n")
    serial_num = [x for x in res if x.startswith("ID_SERIAL_SHORT")][0].split("=")[1]
    return serial_num
