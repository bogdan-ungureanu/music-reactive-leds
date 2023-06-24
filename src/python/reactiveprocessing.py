from arduinoserial import ArduinoSerial
from audiostream import AudioStream
from rgbcolor import RgbColor
import numpy as np
import math
import time
import logging


class ReactiveProcessing:
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        arduino_port: str,
        arduino_on: bool,
        chunk: int,
        channel: int,
        rate: int,
        device_index: int,
        energy_range: list,
        reactive: bool,
        reactive_count: int,
        colors: list,
        **kwargs
    ) -> None:
        self.serial = ArduinoSerial(port=arduino_port, arduino=arduino_on)
        self.audio = AudioStream(
            chunk=chunk,
            channel=channel,
            rate=rate,
            device_index=device_index,
        )

        self.freq_range = (0, 400)
        self.energy_range = energy_range
        self.reactive = reactive
        self.reactive_count = reactive_count
        self.colors = colors
        self.default_energy = self.energy_range[1]
        self.energy_sum = self.energy_range[1]
        self.energy_samples = 1
        self.running = False

    def start(self):
        ReactiveProcessing.logger.info("Main logic for reactive leds started.")
        self.running = True
        self.serial.start_serial()
        self.audio.start_stream()
        freq_categories = {
            "bass": {"range": (80, 400), "count": 0},
            "mid": {"range": (400, 1000), "count": 0},
            "high": {"range": (1000, 1600), "count": 0},
        }

        prev_time = time.time()
        freq_ranges = [freq_categories[cat]["range"] for cat in freq_categories.keys()]

        while self.running:
            freq_energy_list = self.audio.get_max_diff_freq_energy(freq_ranges)
            dfmax, demax = max(freq_energy_list, key=lambda x: x[1])
            index_max = freq_energy_list.index((dfmax, demax))
            category = list(freq_categories.keys())[index_max]
            freq_categories[category]["count"] += 1 if demax > 0 else 0
            max_range = max(freq_categories.items(), key=lambda x: x[1]["count"])[1][
                "range"
            ]
            dfmax, demax = freq_energy_list[freq_ranges.index(max_range)]
            self.freq_range = max_range
            self.energy_sum += demax
            self.energy_samples += 1
            self.energy_range[1] = self.energy_sum / self.energy_samples
            power = self.generate_power(demax)
            if power == 0:
                self.energy_sum = self.default_energy
                self.energy_samples = 1
            if time.time() - prev_time > 5:
                max_cat = "bass"
                maxi = -1
                for cat in freq_categories.keys():
                    if freq_categories[cat]["count"] > maxi:
                        maxi = freq_categories[cat]["count"]
                        max_cat = cat
                    freq_categories[cat]["count"] = 0

                freq_categories[max_cat]["count"] += 1
                prev_time = time.time()
            frange, color = self.search_range(dfmax, self.generate_color_range())
            color = color.power(power)
            self.serial.communicate(color.rgb)
            time.sleep(self.audio._chunk / self.audio._rate)
        else:
            try:
                self.audio.stop_stream()
                self.serial.close_serial()
                self.serial.communicate((0, 0, 0))
            except:
                pass

    def close(self):
        ReactiveProcessing.logger.info("Main logic for reactive leds closed.")
        self.running = False
        del self.audio
        del self.serial

    def stop(self):
        if self.running:
            ReactiveProcessing.logger.info("Main logic for reactive leds stopped.")
            self.serial.communicate((0, 0, 0))
            self.running = False

    def search_range(self, freq, color_ranges: list):
        for i, x in list(enumerate(color_ranges))[::-1]:
            if freq > x[0]:
                return x
        return color_ranges[0]

    def generate_colors(self, **kwargs: dict):
        if self.reactive:
            hue_min = kwargs.get("hue_min", 0)
            hue_max = kwargs.get("hue_max", 280)

            return [
                RgbColor(hsv=(hue, 1, 1))
                for hue in np.linspace(hue_min, hue_max, self.reactive_count)
            ][::-1]
        else:
            return [RgbColor(rgb=color) for color in self.colors]

    def generate_color_range(self, **kwargs: dict):
        colors = self.generate_colors(kwargs=kwargs)
        ranges = list(
            range(
                *self.freq_range,
                (self.freq_range[1] - self.freq_range[0]) // len(colors)
            )
        )
        return [(ranges[i], colors[i]) for i in range(len(colors))]

    @staticmethod
    def map_range(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def generate_power(self, energy):
        power = (
            math.tanh(
                ReactiveProcessing.map_range(
                    energy, self.energy_range[0], self.energy_range[1], 0, 1
                )
            )
            * 100
        )
        return power
