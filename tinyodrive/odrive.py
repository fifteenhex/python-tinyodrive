#!/usr/bin/env python3

import asyncio

import serial_asyncio


class TinyOdrive:
    PROPERTY_VBUS_VOLTAGE = "vbus_voltage"

    class ASCIIProtocol(asyncio.Protocol):

        def __init__(self):
            super().__init__()
            self.connected = asyncio.Event()
            self.transport = None
            self._result_event = asyncio.Event()

        def connection_made(self, transport):
            print("odrive connected")
            self.transport = transport
            self.connected.set()

        def data_received(self, data):
            print("data in: %s" % data)

        def connection_lost(self, exc):
            print("odrive disconnected")
            self.connected.clear()

    def __init__(self):
        self.__transport: serial_asyncio.SerialTransport = None
        self.__protocol: TinyOdrive.ASCIIProtocol = None

    @staticmethod
    async def create(port='/dev/ttyUSB0'):
        odrive = TinyOdrive()
        odrive._transport, odrive._protocol = await serial_asyncio.create_serial_connection(
            asyncio.get_running_loop(),
            TinyOdrive.ASCIIProtocol,
            port,
            baudrate=115200)
        return odrive

    def _write_cmd(self, cmd):
        self._transport.write(cmd.encode("ascii"))

    async def set_velocity(self, motor, velocity: int):
        if not self._protocol.connected.is_set():
            await self._protocol.connected.wait()
        cmd = "v %d %d\n" % (motor, velocity)
        self._write_cmd(cmd)

    async def set_current(self, motor, current):
        pass

    async def get_feedback(self, motor):
        pass

    async def update_watchdog(self, motor):
        if not self._protocol.connected.is_set():
            await self._protocol.connected.wait()
        cmd = "u %d\n" % motor
        self._write_cmd(cmd)

    async def read_property(self, prop):
        if not self._protocol.connected.is_set():
            await self._protocol.connected.wait()
        cmd = "r %s\n" % prop
        self._write_cmd(cmd)

    async def get_vbus_voltage(self):
        return await self.read_property(TinyOdrive.PROPERTY_VBUS_VOLTAGE)

    async def write_property(self, prop, value):
        pass

    async def save_config(self):
        cmd = "ss\n"
        self._write_cmd(cmd)

    async def erase_config(self):
        cmd = "se\n"
        self._write_cmd(cmd)

    async def reboot(self):
        cmd = "sr\n"
        self._write_cmd(cmd)


async def main():
    odrive = await TinyOdrive.create("/dev/ttyUSB0")
    await odrive.set_velocity(0, 100)
    await odrive.set_velocity(1, 100)
    await asyncio.sleep(10)
    await odrive.set_velocity(0, 0)
    await odrive.set_velocity(1, 0)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
