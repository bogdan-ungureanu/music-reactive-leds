from pyaudio import PyAudio, paFloat32, paContinue
import numpy as np
import scipy, scipy.fftpack
from math import log2
import logging


class AudioStream(PyAudio):
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        chunk,
        channel,
        rate,
        device_index,
        format=paFloat32,
    ):
        super().__init__()
        self._chunk = chunk
        self._format = format
        self._channel = channel
        self._rate = rate
        self._device_index = device_index

        self.data = np.zeros(self._chunk // 2 + 1)
        self.energy_spectrum = np.zeros(self._chunk // 2 + 1)
        self.previous_energy_spectrum = np.zeros(self._chunk // 2 + 1)
        self.diff_energy_spectrum = np.zeros(self._chunk // 2 + 1)
        self.freqs = np.abs(scipy.fftpack.fftfreq(self._chunk, d=1 / self._rate))[
            : self._chunk // 2 + 1
        ]
        self.diff_max_energy = -1
        self.diff_max_freq = -1
        self.lower_freq_index = 0
        self.upper_freq_index = self.freqs[-1]

        self.stream = self.open(
            format=self._format,
            channels=self._channel,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            input_device_index=self._device_index,
            stream_callback=self._procces_stream,
        )
        self.stream.stop_stream()

    def start_stream(self):
        if self.stream.is_stopped():
            AudioStream.logger.info("Audio stream has opened. * Started recording.")
            self.stream.start_stream()

    def _procces_stream(self, in_data, frame_count, time_info, status_flag):
        self.data = np.frombuffer(in_data, dtype=np.float32)
        win = np.hanning(self._chunk)
        data_windowed = self.data * win
        fft = scipy.fft.fft(data_windowed, n=self._chunk)
        fft = np.abs(fft[: self._chunk // 2 + 1])
        self.energy_spectrum = fft**2
        self.diff_energy_spectrum = np.maximum(
            self.energy_spectrum - self.previous_energy_spectrum, 0
        )
        self.previous_energy_spectrum = self.energy_spectrum

        return (in_data, paContinue)

    def get_max_diff_freq_energy(self, freq_bounds: list):
        res = []
        for frange in freq_bounds:
            lower_bound, upper_bound = frange
            inrange_freqs = self.freqs[
                (self.freqs > lower_bound) & (self.freqs < upper_bound)
            ]
            lower_freq_index = np.where(self.freqs == np.min(inrange_freqs))[0][0]
            upper_freq_index = np.where(self.freqs == np.max(inrange_freqs))[0][0]
            diff_energy_argmax = (
                np.argmax(
                    self.diff_energy_spectrum[lower_freq_index : upper_freq_index + 1]
                )
                + lower_freq_index
            )
            diff_max_frequency = self.freqs[diff_energy_argmax]
            diff_max_energy = self.diff_energy_spectrum[diff_energy_argmax]
            res.append((diff_max_frequency, diff_max_energy))
        return res

    def stop_stream(self):
        if self.stream.is_active():
            self.stream.stop_stream()
            AudioStream.logger.info("Audio stream has stopped. * Stopped recording.")

    def close_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        AudioStream.logger.info("Audio stream has closed. * Stopped recording.")

    def enum_devices(self):
        for i in range(self.get_device_count()):
            print(
                i,
                self.get_device_info_by_index(i)["name"],
                self.get_device_info_by_index(i)["maxInputChannels"],
            )

    @staticmethod
    def pitch(freq):
        A4 = 440
        C0 = A4 * pow(2, -4.75)
        name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        h = round(12 * log2(freq / C0))
        octave = h // 12
        n = h % 12
        return (name[n], str(octave))
