#!/usr/bin/env python3

import asyncio

import serial_asyncio


class TinyOdrive:
    class ASCIIProtocol(asyncio.Protocol):

        def __init__(self):
            super().__init__()
            self.connected = asyncio.Event()
            self.transport = None

        def connection_made(self, transport):
            print("odrive connected")
            self.transport = transport
            self.connected.set()

        def data_received(self, data):
            pass

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

    async def set_velocity(self, motor, velocity):
        if not self._protocol.connected.is_set():
            await self._protocol.connected.wait()
        cmd = "v %d %d\n" % (motor, velocity)
        self._transport.write(cmd.encode("ascii"))


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
