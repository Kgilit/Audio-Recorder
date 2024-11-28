import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import customtkinter as ctk
from tkinter import filedialog, messagebox


is_recording = False
recorded_audio = []
sample_rate = 44100
stream = None
selected_microphone = None


def list_microphones():

    devices = sd.query_devices()
    input_devices = [
        device['name']
        for device in devices
        if device['max_input_channels'] > 0 and device['hostapi'] == 0
    ]
    return input_devices




def set_microphone(selection):

    global selected_microphone
    try:
        devices = sd.query_devices()
        device_names = [device['name'] for device in devices if device['max_input_channels'] > 0]
        selected_microphone = devices[device_names.index(selection)]["name"]
        status_label.configure(text=f"Selected Microphone: {selected_microphone}", text_color="blue")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to set microphone: {e}")


def start_recording():
    global is_recording, recorded_audio, stream
    try:
        if not selected_microphone:
            messagebox.showwarning("No Microphone Selected", "Please select a microphone before recording.")
            return

        is_recording = True
        recorded_audio = []
        device_index = sd.query_devices(selected_microphone)['index']
        sd.default.device = device_index
        sd.default.samplerate = sample_rate
        sd.default.channels = 2  # Stereo
        stream = sd.InputStream(callback=callback)
        stream.start()  # Start recording
        start_button.configure(state="disabled")
        stop_button.configure(state="normal")
        status_label.configure(text="Recording... 🎙️", text_color="green")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start recording: {e}")
        is_recording = False


def callback(indata,status):
    global recorded_audio
    if is_recording:
        if status:
            print(f"Warning: {status}")
        recorded_audio.append(indata.copy())


def stop_recording():
    global is_recording, stream
    try:
        is_recording = False
        start_button.configure(state="normal")
        stop_button.configure(state="disabled")
        save_button.configure(state="normal")
        status_label.configure(text="Recording Stopped.", text_color="orange")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop recording: {e}")


def save_recording():
    global recorded_audio
    try:
        audio_data = np.concatenate(recorded_audio, axis=0)
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            write(file_path, sample_rate, audio_data)
            status_label.configure(text=f"Saved: {file_path}", text_color="blue")
        recorded_audio = []  # Clear buffer
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save recording: {e}")


# GUI
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Audio Recorder")
app.geometry("600x350")
app.resizable(False, False)

# Title Label
title_label = ctk.CTkLabel(app, text="Voice Recorder", font=("Arial", 24, "bold"))
title_label.pack(pady=20)

# Microphone Selection
mic_label = ctk.CTkLabel(app, text="Select Microphone:", font=("Arial", 14))
mic_label.pack(pady=5)

mic_list = list_microphones()
mic_dropdown = ctk.CTkComboBox(app, values=mic_list, command=set_microphone, width=300)
mic_dropdown.pack(pady=10)

# Status Label
status_label = ctk.CTkLabel(app, text="Ready to record", font=("Arial", 14))
status_label.pack(pady=10)

# Button Frame
button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=30)

# Buttons with adjusted sizes and padding
start_button = ctk.CTkButton(button_frame, text="Start Recording", command=start_recording, fg_color="green", width=150)
start_button.grid(row=0, column=0, padx=20, pady=10)

stop_button = ctk.CTkButton(button_frame, text="Stop Recording", command=stop_recording, fg_color="red", width=150, state="disabled")
stop_button.grid(row=0, column=1, padx=20, pady=10)

save_button = ctk.CTkButton(button_frame, text="Save Recording", command=save_recording, fg_color="blue", width=150, state="disabled")
save_button.grid(row=0, column=2, padx=20, pady=10)


footer_label = ctk.CTkLabel(app, text="© 2024 Kush Gilitwala", font=("Arial", 10))
footer_label.pack(side="bottom", pady=10)


app.mainloop()
