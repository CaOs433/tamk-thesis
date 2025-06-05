import utime

from led_command_parser import LEDCommandParser

import plasma


class LEDProcessor:
    def __init__(self, filename='raw-data.json', NUM_LEDS=50):
        self._filename = filename
        self._NUM_LEDS = NUM_LEDS

        self.led_command_parser = LEDCommandParser(filename, NUM_LEDS)
        self.start_time = 0
        self.commands = {}

        self._load_schedule()

        # set up the WS2812 / NeoPixel™ LEDs
        self._led_strip = plasma.WS2812(NUM_LEDS, color_order=plasma.COLOR_ORDER_RGB)
        self._led_strip.start()

        # Initialize all LED HSVs to off
        self._current_led_hsvs = {
            i: {'hue': 0.0, 'saturation': 0.0, 'value': 0.0}
            for i in range(1, NUM_LEDS + 1)
        }


    def _load_schedule(self):
        self.start_time, self.commands = self.led_command_parser.parse()


    def _current_unix_time_ms(self):
        return utime.time() * 1000


    def _wait_until(self, target_ts_ms):
        while True:
            now = self._current_unix_time_ms()
            diff = target_ts_ms - now
            if diff <= 0:
                break
            utime.sleep_ms(min(diff, 100))


    def _get_fade_hsv_steps(self, led_ids, target_hsv, num_steps):
        steps = {}
        for led_id in led_ids:
            current = self._current_led_hsvs[led_id]
            steps[led_id] = {
                'hue': (target_hsv['hue'] - current['hue']) / num_steps,
                'saturation': (target_hsv['saturation'] - current['saturation']) / num_steps,
                'value': (target_hsv['value'] - current['value']) / num_steps
            }
        return steps


    def _fade_leds(self, led_ids, target_hsv, duration_ms):
        num_steps = max(1, int(duration_ms / 10))
        steps = self._get_fade_hsv_steps(led_ids, target_hsv, num_steps)

        for _ in range(num_steps):
            for led_id in led_ids:
                current = self._current_led_hsvs[led_id]
                step = steps[led_id]

                new_hue = (current['hue'] + step['hue']) % 360
                new_saturation = min(max(current['saturation'] + step['saturation'], 0), 1)
                new_value = min(max(current['value'] + step['value'], 0), 1)

                self._led_strip.set_hsv(led_id, new_hue, new_saturation, new_value)

                self._current_led_hsvs[led_id] = {
                    'hue': new_hue,
                    'saturation': new_saturation,
                    'value': new_value
                }

            utime.sleep_ms(10)


    def _execute_commands(self, commands):
        for command in commands:
            hsv = command['hsv']
            led_ids = command['led_ids']

            if command['delay'] == 0:
                for led_id in led_ids:
                    self._led_strip.set_hsv(led_id, hsv['hue'], hsv['saturation'], hsv['value'])
                    self._current_led_hsvs[led_id] = {
                        'hue': hsv['hue'],
                        'saturation': hsv['saturation'],
                        'value': hsv['value']
                    }
            else:
                self._fade_leds(led_ids, hsv, command['delay'])


    def process(self):
        current_time = self._current_unix_time_ms()
        if self.start_time < current_time:
            self.start_time = current_time + 10

        print(f"[INFO] Waiting for start time: {self.start_time} ms")
        self._wait_until(self.start_time)

        for offset_ms in sorted(self.commands.keys()):
            self._wait_until(self.start_time + offset_ms)
            self._execute_commands(self.commands[offset_ms])


    def all_lights_off(self):
        for i in range(self._NUM_LEDS):
            self._led_strip.set_rgb(i, 0, 0, 0)
