# -*- coding: utf-8 -*-

import time


class SerialDeviceBase:
    def __init__(self, *, encoding, read_delay):
        self.conn = None
        self.encoding = encoding
        self.read_delay = float(read_delay)

    @staticmethod
    def format_command(cmd, *, channel, param, ask):
        if channel is None and param is not None:
            channel, param = param, channel

        param = "" if param is None else ":{}".format(param)
        channel = "" if channel is None else channel
        ask = "" if not ask else "?"

        return "{cmd}{channel}{param}{ask}".format(**locals())

    def write(self, cmd, *, channel=None, param=None, ask=False):
        msg = self.format_command(cmd, channel=channel, param=param,
                                  ask=ask)
        return self.conn.write(msg.encode(self.encoding))

    def read_all(self):
        time.sleep(self.read_delay)
        num_to_read = self.conn.inWaiting()
        return self.conn.read(num_to_read).decode(self.encoding)

    def ask(self, cmd, *, channel=None, param=None):
        self.write(cmd, channel=channel, param=param, ask=True)
        return self.read_all()


class SerialDevice(SerialDeviceBase):
    def __init__(self, port, *, timeout=1, encoding="ascii",
                 read_delay=0.1):
        SerialDeviceBase.__init__(self, encoding=encoding,
                                  read_delay=read_delay)

        import serial
        self.conn = serial.Serial(port, baudrate=9600,
                                  timeout=timeout)


class TestSerialDevice(SerialDeviceBase):
    def __init__(self):
        SerialDeviceBase.__init__(self)

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

    def write(self, cmd, *, channel=None, param=None, ask=False):
        SerialDeviceBase.write(self, cmd, channel=channel, param=param,
                               ask=ask)

    def ask(self, cmd, *, channel=None, param=None):
        a = SerialDeviceBase.ask(self, cmd, channel=channel, param=param)
        return a
