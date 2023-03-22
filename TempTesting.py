import tkinter as tk; from tkinter import ttk
import sys
import time

import numpy as np
import sounddevice as sd

# Default frames per second
DEFAULT_SAMPLE_RATE = 44100

# Frequency of a middle C
MIDDLE_C_FREQUENCY = 261.625565

def direction(start, end):
    '''Returns 1 if end > start, and -1 if end < start.'''
    return 1 if end > start else -1

def bounded_by_end(value, start, end):
    '''Returns value if value is closer to start than end is, otherwise returns end.'''
    if start < end:
        return np.minimum(value, end)
    else:
        return np.maximum(value, end)
    
def frames_to_time(frames, framerate):
    '''Convert frame count to time (using framerate).'''
    return frames / framerate

def frames_to_time_array(start_frame, frames, framerate):
    '''Convert frame information into a time array.'''
    # Convert frame info to time info
    start_time = frames_to_time(start_frame, framerate)
    end_time = frames_to_time(start_frame + frames, framerate)

    # Create time array with one entry for each frame
    time_array = np.linspace(start_time, end_time, frames, endpoint=False)
    return time_array

def interval_to_frequency_ratio(interval):
    '''The frequency of the given pitch (in Hz), relative to middle C'''
    return 2**(interval/12)

def pitch_to_frequency(pitch):
    '''The frequency of the given pitch (in Hz), relative to middle C'''
    return MIDDLE_C_FREQUENCY * 2**(pitch/12)

def decibels_to_amplitude_ratio(decibels):
    '''The ratio between two amplitudes given a decibel change'''
    return 2**(decibels / 10)

class SineWaveGenerator:

    '''Generates continuous sine wave data'''

    def __init__(self, pitch=0, pitch_per_second=12, decibels=1, decibels_per_second=1, samplerate=DEFAULT_SAMPLE_RATE):
        self.frequency = pitch_to_frequency(pitch)
        self.phase = 0
        self.amplitude = decibels_to_amplitude_ratio(decibels)

        self.pitch_per_second = pitch_per_second
        self.decibels_per_second = decibels_per_second
        self.goal_frequency = self.frequency
        self.goal_amplitude = self.amplitude
        self.samplerate = samplerate
    
    # Create the output stream
        self.output_stream = sd.OutputStream(channels=1, callback= lambda *args: self._callback(*args), 
                                samplerate=samplerate)
    def set_pitch(self, value):
        '''Changes the set pitch of oscillator'''
        self.frequency=pitch_to_frequency(value)
        self.goal_frequency=self.frequency
    
    def new_frequency_array(self, time_array):
        '''Calculate the frequency values for the next chunk of data.'''
        dir = direction(self.frequency, self.goal_frequency)
        #new_frequency = self.frequency * interval_to_frequency_ratio(
                            #dir * self.pitch_per_second * time_array)
        new_frequency = self.frequency * interval_to_frequency_ratio(
                            dir * 12 * time_array)
        #print(new_frequency)

        #print(bounded_by_end(new_frequency, self.frequency, self.goal_frequency))
        #return bounded_by_end(new_frequency, self.frequency, self.goal_frequency)
        return new_frequency
        #return np.full(65, 4, self.frequency)

    def new_amplitude_array(self, time_array):
        '''Calculate the amplitude values for the next chunk of data.'''
        dir = direction(self.amplitude, self.goal_amplitude)
        new_amplitude = self.amplitude * decibels_to_amplitude_ratio(
                            dir * self.decibels_per_second * time_array)
        return bounded_by_end(new_amplitude, self.amplitude, self.goal_amplitude)

    def new_phase_array(self, new_frequency_array, delta_time):
        '''Calculate the phase values for the next chunk of data, given frequency values'''
        return self.phase + np.cumsum(new_frequency_array * delta_time)

    def next_data(self, frames):
        '''Get the next pressure array for the given number of frames'''

        # Convert frame information to time information
        time_array = frames_to_time_array(0, frames, self.samplerate)
        delta_time = time_array[1] - time_array[0]

        # Calculate the frequencies of this batch of data
        new_frequency_array = self.new_frequency_array(time_array)

        # Calculate the phases
        new_phase_array = self.new_phase_array(new_frequency_array, delta_time)

        # Calculate the amplitudes
        new_amplitude_array = self.new_amplitude_array(time_array)

        # Create the sinewave array
        sinewave_array = new_amplitude_array * np.sin(2*np.pi*new_phase_array)
        
        # Update frequency and amplitude
        self.frequency = new_frequency_array[-1]
        self.amplitude = new_amplitude_array[-1]

        # Update phase (getting rid of extra cycles, so we don't eventually have an overflow error)
        self.phase = new_phase_array[-1] % 1

        #print('Frequency: {0} Phase: {1} Amplitude: {2}'.format(self.frequency, self.phase, self.amplitude))

        return sinewave_array

    def _callback(self, outdata, frames, time, status):
        '''Callback function for the output stream.'''
        # Print any error messages we receive
        if status:
            print(status, file=sys.stderr)

        # Get and use the sinewave's next batch of data
        data = self.next_data(frames)
        outdata[:] = data.reshape(-1, 1)

    def play(self):
        '''Plays the sinewave (in a separate thread). Changes in frequency or amplitude will transition smoothly.'''
        self.output_stream.start()
    
    def stop(self):
        '''If the sinewave is playing, stops the sinewave.'''
        self.output_stream.stop()
# create the root window
root = tk.Tk()
root.geometry('730x500+10+10')
root.title('Synth Demo')

l = tk.Label(root,text='empty')

var = tk.StringVar()

# Create oscillator object
osc = SineWaveGenerator()

# BUTTON EVENTS

def c(event):
    #global sw
    #global selection
    #sw = SineWave(pitch=0)
    global osc
    osc.set_pitch(0)
    osc.play()

def stop(event):
    osc.stop()

icon1 = tk.PhotoImage(file='assets/leftkey.png')

c_note = tk.Button(
    root,
    image=icon1
)

c_note.place(x=10,y=240)
c_note.bind('<ButtonPress-1>', c)
c_note.bind('<ButtonRelease-1>', stop)

root.mainloop()