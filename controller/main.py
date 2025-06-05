import uasyncio as asyncio

from ble_json_receiver import BLEReceiverJSON
from led_processor import LEDProcessor


# Set how many LEDs you have
NUM_LEDS = 50


async def ble_listener(receiver):
    await receiver.run()


async def main_task(receiver):
    led_p = LEDProcessor()

    while True:
        led_p.all_lights_off()  # Turn off all LEDs before processing new commands
        led_p.process()

        await asyncio.sleep(1)

        # Waiting for BLE data to be received
        if not receiver._idle_event.is_set():
            print("Receiving data...")
            await receiver.wait_until_idle()

        # Check if new data is available
        if receiver._new_data_event.is_set():
            json_data = await receiver.wait_for_new_data()
            print("Received JSON data:", json_data)


async def main():
    receiver = BLEReceiverJSON()
    asyncio.create_task(ble_listener(receiver))  # BLE listening in the background
    await main_task(receiver)  # Other tasks in the main loop


asyncio.run(main())
