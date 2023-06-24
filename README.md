# Music Reactive RGB LEDs 
## Real Time Sound Analysis and Visualization using Python and Arduino

> - #### written in Python 3.8 and Arduino
> - #### modules used: PyAudio, NumPy, SciPy, Matplotlib, Plotly, PySide6, PySerial
> - #### real-time sound analysis and processing by separating the complex signal into component frequencies using various processing techniques
> - #### serial link between the program and an LED band that makes it possible to observe the differences in the distribution of sound frequencies in real time
> - #### Demo: https://youtu.be/J8QkFTCnqPo

## Arduino Circuit
- 3x IRF840 MOSFETs , 3x 220 Ω resistors, 12V DC Power, cables and RGB leds
![Circuit Board](/screenshots/arduinocircuit.png)

## Signal processing
- getting audio data from the speakers output using a virtual mixer - Voicemeeter Banana using PyAudio
- storing byte data as a numpy.array
- windowing the data using hanning window and applying FFT transform
- calculate the spectrum of freqencies and their coresponding energies
- calculate the differential spectrum of energy (current - previous spectrum)

## Mapping colors to a sound frequency
- finding the interval with most occurences of a frequency from bass, mids, and highs
- defaulting to that interval and linear maping a color range to that frequency range
- maping the intensity of that color to the maximum energy frequency from the differential spectrum using a non-linear function for smooth transitions
- using adaptive max energy for the spectrum = average maximum energies

## GUI
![Menu](/screenshots/gui1.png)
![Solid Color](/screenshots/gui2.png)
![Reactive Window](/screenshots/gui3.png)
![Config](/screenshots/gui4.png)

## Usage
```
cd /python
pip install -r requirements.txt
py ./main.py
```

## Demo
#### https://youtu.be/J8QkFTCnqPo

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
