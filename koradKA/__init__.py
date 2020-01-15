# -*- coding: utf-8 -*-

from .controller import KoradKA_DualChannel, KoradKA_SingleChannel
from .commands import TrackingMode


def identify(port, **kwds):
    import serial, time, re
    from contextlib import closing

    with closing(serial.serial_for_url(port, **kwds)) as bus:
        bus.reset_input_buffer()

        bus.write(b"*IDN?\r\n")
        time.sleep(0.1)
        idn = bus.readline().decode("ascii").strip()

    match = re.search(r"KORAD\s?K[A|D](\d{4})", idn)
    return match.group(1) if match else None


def get_psu(port):
    model = identify(port)
    if model == "3005":
        return KoradKA_SingleChannel(port)
    elif model == "3305":
        return KoradKA_DualChannel(port)
    else:
        raise RuntimeError("Device identification failed")
