import ujson as json


def read_settings(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        name = str(data.get('name', ''))
        description = str(data.get('description', ''))
        num_leds = int(data.get('number_of_leds', -1))

        return name, description, num_leds

# Example usage:
# name, description, num_leds = read_settings('settings.json')
