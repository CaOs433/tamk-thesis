import struct

import bluetooth

from micropython import const


_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)


class BLESimplePeripheral:
    def __init__(self, ble, name="mpy-peripheral"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        self._connections = set()
        self._write_callback = None

        # Randomly generated UUIDs (can be replaced with your own)
        self._service_uuid = bluetooth.UUID("071172ec-47c4-4343-9938-74174242e168")
        self._tx_uuid = bluetooth.UUID("071172ed-47c4-4343-9938-74174242e168")  # Not used here
        self._rx_uuid = bluetooth.UUID("071172ee-47c4-4343-9938-74174242e168")

        self._rx_handle = None

        self._advertise_payload = bluetooth.advertising_payload(name=name, services=[self._service_uuid])

        self._init_service()
        self._advertise()


    def _init_service(self):
        # Only RX is used (client writes to this)
        rx_char = (self._rx_uuid, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE)
        service = (self._service_uuid, (rx_char,))
        ((self._rx_handle,),) = self._ble.gatts_register_services((service,))


    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._advertise_payload)


    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.discard(conn_handle)
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._rx_handle and self._write_callback:
                value = self._ble.gatts_read(self._rx_handle)
                self._write_callback(value)


    def on_write(self, callback):
        self._write_callback = callback
