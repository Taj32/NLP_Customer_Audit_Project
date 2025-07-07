"""
Audio Recorder Module

This module provides functionality to record audio, detect silence, apply automatic gain control (AGC),
and save the recorded audio to a WAV file. It includes a class `AudioRecorder` and a main entry point
for direct script execution.
"""

import pyaudio
import numpy as np
import wave
import os
from datetime import datetime


class AudioRecorder:
    """
    A class for recording audio with silence detection and automatic gain control (AGC).

    Attributes:
        output_folder (str): Directory to save recordings.
        silence_threshold (int): RMS threshold to detect silence.
        silence_duration (float): Duration of silence to trigger auto-stop.
        target_rms (int): Target RMS for AGC.
        format (int): Audio format (default: pyaudio.paInt16).
        channels (int): Number of audio channels (default: 1).
        rate (int): Sampling rate (default: 44100 Hz).
        chunk (int): Buffer size for audio frames (default: 1024).
    """

    def __init__(
        self,
        output_folder="recordings",
        silence_threshold=100,
        silence_duration=5.0,
        target_rms=3000,
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        chunk=1024
    ):
        """
        Initializes the AudioRecorder instance with default or user-provided settings.

        Args:
            output_folder (str): Directory to save recordings.
            silence_threshold (int): RMS threshold to detect silence.
            silence_duration (float): Duration of silence to trigger auto-stop.
            target_rms (int): Target RMS for AGC.
            format (int): Audio format.
            channels (int): Number of audio channels.
            rate (int): Sampling rate.
            chunk (int): Buffer size for audio frames.
        """
        self.output_folder = output_folder
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.target_rms = target_rms
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.frames = []
        self.current_gain = 1.0
        self.is_recording = False
        self.stream = None
        self.audio = None

        # Ensure the output folder exists
        os.makedirs(self.output_folder, exist_ok=True)

    def start_recording(self, auto_stop=True):
        """
        Starts recording audio. Optionally stops after a duration of silence.

        Args:
            auto_stop (bool): If True, stops recording after silence_duration seconds of silence.
        """
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.frames = []
        self.is_recording = True
        print(f"Recording started (Auto-stop: {auto_stop})...")
        print(f"Press Ctrl+C to stop manually.\n")

        silence_counter = 0
        silence_chunks = int(self.silence_duration * self.rate / self.chunk)

        try:
            while self.is_recording:
                # Read raw audio data from the stream
                raw_data = self.stream.read(self.chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(raw_data, dtype=np.int16)

                # Calculate RMS for silence detection
                raw_rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2)) if len(audio_data) > 0 else 0
                if auto_stop:
                    if raw_rms < self.silence_threshold:
                        silence_counter += 1
                    else:
                        silence_counter = 0

                    # Stop recording if silence duration is exceeded
                    if silence_counter >= silence_chunks:
                        print(f"\nStopped due to {self.silence_duration}s of silence.")
                        self.stop_recording()
                        break

                # Apply Automatic Gain Control (AGC)
                if raw_rms > 0:
                    desired_gain = self.target_rms / raw_rms
                    self.current_gain = 0.2 * self.current_gain + 0.8 * desired_gain
                adjusted_data = np.clip(audio_data * self.current_gain, -32768, 32767).astype(np.int16)
                self.frames.append(adjusted_data.tobytes())

        except KeyboardInterrupt:
            # Handle manual stop
            self.stop_recording()
            print("\nRecording stopped manually.")

    def stop_recording(self):
        """
        Stops recording and cleans up resources.
        """
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
            print("Recording stopped.")

    def save_recording(self, filename=None):
        """
        Saves the recorded audio to a WAV file.

        Args:
            filename (str): Name of the output file. If None, generates a timestamp-based name.

        Returns:
            str: Path to the saved file, or None if no audio was recorded.
        """
        if not self.frames:
            print("No audio to save.")
            return None

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(self.output_folder, filename)

        # Write audio data to a WAV file
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))

        print(f"Saved to: {os.path.abspath(filepath)}")
        return filepath

    def record_until_silence(self):
        """
        Convenience method to start recording, auto-stop on silence, and save the recording.

        Returns:
            str: Path to the saved file, or None if no audio was recorded.
        """
        self.start_recording(auto_stop=True)
        return self.save_recording()


def main():
    """
    Entry point for direct script execution.
    """
    recorder = AudioRecorder()
    try:
        recorder.record_until_silence()  # Auto-stop on silence
    except Exception as e:
        print(f"Error: {e}")
    finally:
        recorder.stop_recording()


if __name__ == "__main__":
    main()