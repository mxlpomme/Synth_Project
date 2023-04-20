import tkinter as tk
from tkinter import ttk
import numpy as np
import sounddevice as sd


# Defined Variables

mid_c_frequency = 261.625565

default_sample_rate = 44100

# Helper Functions


def direction(start, end):
    """Return 1 if end > start, -1 if end < start. (Keeps values consistent instead of sliding up or down)"""
    return 1 if end > start else -1


def pitch_to_frequency(pitch):
    """Frequency of pitch relative to Middle C"""
    return mid_c_frequency * 2 ** (pitch / 12)


def decibels_to_amplitude_ratio(decibels):
    """Ratio between two amplitudes given a decibel change"""
    return 2 ** (decibels / 10)


def interval_to_frequency_ratio(interval):
    return 2 ** (interval / 12)


def frames_to_time(frames, framerate):
    """Convert frame count to time"""
    return frames / framerate


def frames_to_time_array(start_frame, frames, framerate):
    """Convert frame information into time array"""

    # Frame info to time info
    start_time = frames_to_time(start_frame, framerate)
    end_time = frames_to_time(start_frame + frames, framerate)

    # Create time array with one entry for each frame
    time_array = np.linspace(start_time, end_time, frames, endpoint=False)
    return time_array


class SineWaveGenerator:
    """Generates continious sine wave data"""

    def __init__(
        self, pitch=0, decibels=1, decibels_per_second=1, samplerate=default_sample_rate
    ):
        self.frequency = pitch_to_frequency(pitch)
        self.phase = 0
        self.amplitude = decibels_to_amplitude_ratio(decibels)

        self.pitch_per_second = 12
        self.decibels_per_second = 1
        self.goal_frequency = self.frequency
        self.goal_amplitude = self.amplitude
        self.samplerate = samplerate

        # Create the output stream
        self.output_stream = sd.OutputStream(
            channels=1,
            callback=lambda *args: self._callback(*args),
            samplerate=samplerate,
        )

    def set_pitch(self, value):
        """Changes pitch of the oscillator"""
        self.frequency = pitch_to_frequency(value)
        self.goal_frequency = self.frequency

    def new_frequency_array(self, time_array):
        """Calculate the frequency values for the next chunk of data"""
        dir = direction(self.frequency, self.goal_frequency)
        new_frequency = self.frequency * interval_to_frequency_ratio(
            dir * self.pitch_per_second * time_array
        )
        return new_frequency

    def new_amplitude_array(self, time_array):
        """Calculate amiplitude values for next chunck of data"""
        dir = direction(self.amplitude, self.goal_amplitude)
        new_amplitude = self.amplitude * decibels_to_amplitude_ratio(
            dir * self.decibels_per_second * time_array
        )
        return new_amplitude

    def new_phase_array(self, new_frequency_array, delta_time):
        """Calculate phase values for next chunk of data"""
        return self.phase + np.cumsum(new_frequency_array * delta_time)

    def next_data(self, frames):
        """Get the next pressure array for the given number of frames"""

        # Convert frame information to time information
        time_array = frames_to_time_array(0, frames, self.samplerate)
        # delta time = elapsed time
        delta_time = time_array[1] - time_array[0]

        # Calculate the frequencies, phases, and amplitudes of this batch of data
        new_frequency_array = self.new_frequency_array(time_array)
        new_phase_array = self.new_phase_array(new_frequency_array, delta_time)
        new_amplitude_array = self.new_amplitude_array(time_array)

        # Create the sinewave array
        sinewave_array = new_amplitude_array * np.sin(2 * np.pi * new_phase_array)

        # Update phase to prevent overflow error
        self.phase = new_phase_array[-1] % 1

        return sinewave_array

    def _callback(self, outdata, frames, time, status):
        """Callback function for the output stream"""
        if status:
            print(status, file=sys.stderr)

        # Get and use the sinewave's next batch of data
        data = self.next_data(frames)
        outdata[:] = data.reshape(-1, 1)

    def play(self):
        """Plays the sinewave"""
        self.output_stream.start()

    def stop(self):
        """Stops playing wave"""
        self.output_stream.stop()


# create the root window
root = tk.Tk()
root.geometry("730x500+10+10")
root.title("Synth Demo")

l = tk.Label(root, text="empty")

var = tk.StringVar()

# Create oscillator object
osc = SineWaveGenerator()

# BUTTON EVENTS


def c(event):
    osc.set_pitch(0)
    osc.play()


def csharp(event):
    osc.set_pitch(1)
    osc.play()


def d(event):
    osc.set_pitch(2)
    osc.play()


def dsharp(event):
    osc.set_pitch(3)
    osc.play()


def e(event):
    osc.set_pitch(4)
    osc.play()


def f(event):
    osc.set_pitch(5)
    osc.play()


def fsharp(event):
    osc.set_pitch(6)
    osc.play()


def g(event):
    osc.set_pitch(7)
    osc.play()


def gsharp(event):
    osc.set_pitch(8)
    osc.play()


def a(event):
    osc.set_pitch(9)
    osc.play()


def asharp(event):
    osc.set_pitch(10)
    osc.play()


def b(event):
    osc.set_pitch(11)
    osc.play()


def stop(event):
    osc.stop()


icon1 = tk.PhotoImage(file="assets/whitekey2.png")
icon2 = tk.PhotoImage(file="assets/blackkey.png")


c_note = tk.Button(root, image=icon1)

c_note.place(x=10, y=240)
c_note.bind("<ButtonPress-1>", c)
c_note.bind("<ButtonRelease-1>", stop)

d_note = tk.Button(root, image=icon1)

d_note.place(x=110, y=240)
d_note.bind("<ButtonPress-1>", d)
d_note.bind("<ButtonRelease-1>", stop)

csharp_note = tk.Button(root, image=icon2)

csharp_note.place(x=70, y=240)
csharp_note.bind("<ButtonPress-1>", csharp)
csharp_note.bind("<ButtonRelease-1>", stop)

e_note = tk.Button(root, image=icon1)

e_note.place(x=210, y=240)
e_note.bind("<ButtonPress-1>", e)
e_note.bind("<ButtonRelease-1>", stop)

dsharp_note = tk.Button(root, image=icon2)

dsharp_note.place(x=170, y=240)
dsharp_note.bind("<ButtonPress-1>", dsharp)
dsharp_note.bind("<ButtonRelease-1>", stop)

f_note = tk.Button(root, image=icon1)

f_note.place(x=310, y=240)
f_note.bind("<ButtonPress-1>", f)
f_note.bind("<ButtonRelease-1>", stop)

g_note = tk.Button(root, image=icon1)

g_note.place(x=410, y=240)
g_note.bind("<ButtonPress-1>", g)
g_note.bind("<ButtonRelease-1>", stop)

fsharp_note = tk.Button(root, image=icon2)

fsharp_note.place(x=370, y=240)
fsharp_note.bind("<ButtonPress-1>", fsharp)
fsharp_note.bind("<ButtonRelease-1>", stop)

a_note = tk.Button(root, image=icon1)

a_note.place(x=510, y=240)
a_note.bind("<ButtonPress-1>", a)
a_note.bind("<ButtonRelease-1>", stop)

gsharp_note = tk.Button(root, image=icon2)

gsharp_note.place(x=470, y=240)
gsharp_note.bind("<ButtonPress-1>", gsharp)
gsharp_note.bind("<ButtonRelease-1>", stop)

b_note = tk.Button(root, image=icon1)

b_note.place(x=610, y=240)
b_note.bind("<ButtonPress-1>", b)
b_note.bind("<ButtonRelease-1>", stop)

asharp_note = tk.Button(root, image=icon2)

asharp_note.place(x=570, y=240)
asharp_note.bind("<ButtonPress-1>", asharp)
asharp_note.bind("<ButtonRelease-1>", stop)

root.mainloop()


root.mainloop()
