import os

import bluetooth
import ujson
import uasyncio as asyncio

from ble_simple_peripheral import BLESimplePeripheral


class BLEReceiverJSON:
    def __init__(
        self, 
        filename='raw-data.json', 
        peripheral_name='PicoW-Receiver'
    ):
        self._filename = filename
        self._peripheral_name = peripheral_name
        
        self._ble = bluetooth.BLE()
        self._new_data_event = asyncio.Event()
        self._idle_event = asyncio.Event()
        self._idle_event.set()  # Initially, we are "idle" (not receiving data)
        self._received_data = None


    def _save_json(self, data_bytes):
        try:
            data_str = data_bytes.decode('utf-8')
            parsed = ujson.loads(data_str)  # Make sure the data is valid JSON
            with open(self._filename, 'w') as f:
                f.write(data_str)

            print(f'File {self._filename} saved.')
            self._received_data = parsed
            self._new_data_event.set()      # Signal that new data is available
            self._idle_event.set()          # Now we are "idle" again

        except Exception as e:
            print('Error with the JSON:', e)
            self._idle_event.set()


    def _on_rx(self, v):
        print('Receiving JSON...')
        self._idle_event.clear()  # Now we are "busy" receiving data
        self._save_json(v)


    async def run(self):
        self._ble.active(True)
        p = BLESimplePeripheral(self._ble, name=self._peripheral_name)
        p.on_write(self._on_rx)
        print("BLE-server running in background...")


    async def wait_for_new_data(self):
        await self._new_data_event.wait()
        self._new_data_event.clear()
        return self._received_data


    async def wait_until_idle(self):
        await self._idle_event.wait()


#    def start(self):
#        self.ble.active(True)
#
#        # Create a BLE peripheral with the specified name
#        p = BLESimplePeripheral(self.ble, name=self.peripheral_name)
#        p.on_write(self._on_rx)
#
#        print('BLE-server running, waiting for the JSON-data...')
#
#        while True:
#            pass
