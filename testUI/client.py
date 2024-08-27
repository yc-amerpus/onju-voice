import tkinter as tk
from tkinter import ttk
import pyaudio
import sounddevice as sd
import socket
import numpy as np
import threading

# Global variables to handle mute state and selected devices
mic_muted = False
speaker_muted = False
selected_mic = None
selected_speaker = None

# Initialize PyAudio
p = pyaudio.PyAudio()

# Function to update LED representation
def update_led(color):
    led_canvas.config(bg=color)

# Function to mute/unmute the microphone
def toggle_mic():
    global mic_muted
    mic_muted = not mic_muted
    mic_button.config(text="Unmute Mic" if mic_muted else "Mute Mic")
    update_led("red" if mic_muted else "green")

# Function to mute/unmute the speaker
def toggle_speaker():
    global speaker_muted
    speaker_muted = not speaker_muted
    speaker_button.config(text="Unmute Speaker" if speaker_muted else "Mute Speaker")

# Function to start the audio processing
def start_audio():
    # Initialize PyAudio and start processing
    # Simulate audio processing with a basic function
    pass

# Function to stop the audio processing
def stop_audio():
    # Stop audio processing
    pass

# Function to exit the application
def exit_app():
    p.terminate()
    root.quit()  # Alternatively, use root.destroy() to terminate the application
    root.destroy()

# Function to get microphone devices
def get_microphone_devices():
    #p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            devices.append((device_info["index"], f"{device_info['name']} (API: {device_info['hostApi']})"))
    return devices

# Function to get speaker devices
def get_speaker_devices():
    devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxOutputChannels"] > 0:  # Only consider devices with output channels
            devices.append((device_info["index"], device_info["name"]))
    return devices

def get_microphone_devicesOLD():
    devices = sd.query_devices()
    input_devices = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append((i, device['name']))
    return input_devices

# Function to populate the dropdown
def populate_microphone_dropdown():
    devices = get_microphone_devices()
    mic_dropdown["values"] = [name for index, name in devices]
    if devices:
        mic_dropdown.current(0)  # Set the first device as the default selection

# Function to populate the speaker dropdown
def populate_speaker_dropdown():
    devices = get_speaker_devices()
    speaker_dropdown["values"] = [name for index, name in devices]
    if devices:
        speaker_dropdown.current(0)  # Set the first device as the default selection

# Function to get the selected microphone index
def get_selected_microphone_index():
    selected_name = mic_dropdown.get()
    for index, name in get_microphone_devices():
        if name == selected_name:
            return index
    return None    

# Function to get the selected speaker index
def get_selected_speaker_index():
    selected_name = speaker_dropdown.get()
    for index, name in get_speaker_devices():
        if name == selected_name:
            return index
    return None

# Function to update the microphone level meter
def update_mic_level(mic_index):
    def callback(in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        peak = np.abs(audio_data).max() / 32768  # Normalize to 0.0 to 1.0
        meter_level = int(peak * 100)  # Scale to 0-100 for the progress bar
        level_meter["value"] = meter_level
        return (in_data, pyaudio.paContinue)

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    input_device_index=mic_index,
                    frames_per_buffer=1024,
                    stream_callback=callback)

    stream.start_stream()

    # Keep the stream alive
    while stream.is_active():
        root.update_idletasks()
        root.update()

    stream.stop_stream()
    stream.close()

# Function to start monitoring the microphone
def start_monitoring():
    mic_index = get_selected_microphone_index()
    if mic_index is not None:
        thread = threading.Thread(target=update_mic_level, args=(mic_index,))
        thread.start()

# Function to play a two-tone noise for 5 seconds
def play_test_tone(speaker_index):
    def generate_tone(frequency, duration, rate=44100):
        t = np.linspace(0, duration, int(rate * duration), False)
        tone = 0.5 * np.sin(2 * np.pi * frequency * t)
        return tone.astype(np.float32)

    tone1 = generate_tone(440, 2.5)  # 440 Hz for 2.5 seconds
    tone2 = generate_tone(880, 2.5)  # 880 Hz for 2.5 seconds
    tones = np.concatenate([tone1, tone2])

    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    output=True,
                    output_device_index=speaker_index)

    stream.write(tones.tobytes())
    stream.stop_stream()
    stream.close()

# Function to start playing the test tone
def start_test_tone():
    speaker_index = get_selected_speaker_index()
    if speaker_index is not None:
        thread = threading.Thread(target=play_test_tone, args=(speaker_index,))
        thread.start()

# Setup GUI
root = tk.Tk()
root.title("OnjuVoice Test Application")

# LED representation (using a Canvas)
led_canvas = tk.Canvas(root, width=50, height=50, bg="green")
led_canvas.grid(row=0, column=0, padx=20, pady=20)

# Microphone dropdown
mic_label = tk.Label(root, text="Select Microphone:")
mic_label.grid(row=1, column=0, padx=20, pady=10)
mic_dropdown = ttk.Combobox(root)
mic_dropdown.grid(row=1, column=1, padx=20, pady=10)

# Speaker dropdown
speaker_label = tk.Label(root, text="Select Speaker:")
speaker_label.grid(row=2, column=0, padx=20, pady=10)
speaker_dropdown = ttk.Combobox(root)
speaker_dropdown.grid(row=2, column=1, padx=20, pady=10)

# Mute buttons
mic_button = tk.Button(root, text="Mute Mic", command=toggle_mic)
mic_button.grid(row=3, column=0, padx=20, pady=10)
speaker_button = tk.Button(root, text="Mute Speaker", command=toggle_speaker)
speaker_button.grid(row=3, column=1, padx=20, pady=10)

# Audio control buttons
start_button = tk.Button(root, text="Start Audio", command=start_audio)
start_button.grid(row=4, column=0, padx=20, pady=10)
stop_button = tk.Button(root, text="Stop Audio", command=stop_audio)
stop_button.grid(row=4, column=1, padx=20, pady=10)
test_tone_button = tk.Button(root, text="Test Speaker", command=start_test_tone)
test_tone_button.grid(row=4, column=2, padx=20, pady=10)

# Microphone level meter (using a Progressbar)
level_meter_label = tk.Label(root, text="Mic Level:")
level_meter_label.grid(row=5, column=0, padx=20, pady=10)
level_meter = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
level_meter.grid(row=5, column=1, padx=20, pady=10)

# Button to start monitoring the microphone level
monitor_button = tk.Button(root, text="Start Monitoring", command=start_monitoring)
monitor_button.grid(row=6, column=0, columnspan=2, padx=20, pady=10)


# Exit button
exit_button = tk.Button(root, text="Exit", command=exit_app)
exit_button.grid(row=7, column=0, columnspan=2, padx=20, pady=10)

# Populate the dropdown with available microphones
populate_microphone_dropdown()

# Populate the dropdown with available speakers
populate_speaker_dropdown()

# Button to print the selected microphone index
def print_selected_microphone():
    mic_index = get_selected_microphone_index()
    print(f"Selected Microphone Index: {mic_index}")

select_button = tk.Button(root, text="Select Microphone", command=print_selected_microphone)
select_button.grid(row=8, column=0, columnspan=2, padx=20, pady=10)

# Handle the window close event
root.protocol("WM_DELETE_WINDOW", exit_app)  

# Main loop
root.mainloop()
