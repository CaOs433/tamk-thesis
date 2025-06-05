import ujson as json


class LEDCommandParser:
    def __init__(self, filename='raw-data.json', NUM_LEDS=50):
        self.filename = filename
        self.NUM_LEDS = NUM_LEDS

        self.start_time = 0
        self.schedule = {}


    def _load_schedule(self):
        with open(self.filename) as f:
            raw = json.load(f)

        start_time = raw['start']
        data = raw['data']

        schedule = {}
        for relative_ts_str, commands in data.items():
            relative_ts = int(relative_ts_str)
            schedule[relative_ts] = commands

        return start_time, schedule


    def _expand_led_ids(self, led_ids):
        expanded = set()
        for item in led_ids:
            if item == '*':
                expanded.update(i for i in range(1, self.NUM_LEDS))
            elif '*' in item:
                start, end = map(int, item.split('*'))
                expanded.update(range(start, min(end + 1, self.NUM_LEDS)))
            else:
                expanded.add(int(item))
        return sorted(expanded)


    def _parse_cmd_type(self, cmd) -> int:
        if cmd == 'instant':
            return 0
        if cmd == 'fast_fade':
            return 250
        if cmd == 'slow_fade':
            return 1000
    
        print(f"[WARN] Unknown command type '{cmd}', defaulting to instant")
        return 0


    def _process_led_patch(self, patch):
        parsed = []
        for id_patch in patch:
            led_ids = self._expand_led_ids(id_patch['led_ids'])
            hsv = id_patch['hsv']
            cmd_type = id_patch.get('type', 'instant')

            parsed.append({
                'led_ids': led_ids,
                'hsv': hsv,
                'delay': self._parse_cmd_type(cmd_type)
            })

        return parsed

    def parse(self):
        start_time, raw_data = self._load_schedule()
        parsed = {}

        for ts, patch in raw_data.items():
            parsed[ts] = self._process_led_patch(patch)

        print('Parsed LED commands:', parsed)
        return start_time, parsed
