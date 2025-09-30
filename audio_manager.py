"""
Audio manager for playing sound effects using I2S audio output
"""

import os
import random
import wave
import numpy as np
import alsaaudio
import threading
import queue
from config import *

class AudioManager:
    """Manages audio playback for sound effects"""
    
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.current_volume = AUDIO_VOLUME
        self.playback_thread = None
        self.stop_playback = False
        
        # Initialize ALSA audio output
        try:
            self.device = alsaaudio.PCM(
                type=alsaaudio.PCM_PLAYBACK,
                mode=alsaaudio.PCM_NORMAL,
                device='default'
            )
            
            # Set audio parameters
            self.device.setchannels(AUDIO_CHANNELS)
            self.device.setrate(AUDIO_SAMPLE_RATE)
            self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            self.device.setperiodsize(1024)
            
            print("Audio manager initialized successfully")
        except alsaaudio.ALSAAudioError as e:
            print(f"Error initializing audio: {e}")
            self.device = None
        
        # Verify sound files exist
        self.available_sounds = self._scan_sound_files()
        
        # Start playback thread
        self._start_playback_thread()
    
    def _scan_sound_files(self):
        """Scan and catalog available sound files"""
        sounds = {}
        
        for category, files in SOUND_EFFECTS.items():
            sounds[category] = []
            for filename in files:
                filepath = os.path.join(AUDIO_BASE_PATH, filename)
                if os.path.exists(filepath):
                    sounds[category].append(filepath)
                    if DEBUG_MODE:
                        print(f"Found sound: {category}/{filename}")
                else:
                    print(f"Warning: Sound file not found: {filepath}")
        
        return sounds
    
    def _start_playback_thread(self):
        """Start background thread for audio playback"""
        self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self.playback_thread.start()
    
    def _playback_worker(self):
        """Background worker that processes audio queue"""
        while not self.stop_playback:
            try:
                # Get next audio file from queue (with timeout)
                audio_file = self.audio_queue.get(timeout=0.1)
                
                if audio_file and self.device:
                    self._play_wav_file(audio_file)
                
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in playback worker: {e}")
    
    def _play_wav_file(self, filepath):
        """Play a WAV file"""
        if not self.device:
            return
        
        try:
            self.is_playing = True
            
            with wave.open(filepath, 'rb') as wf:
                # Verify format
                if wf.getnchannels() != AUDIO_CHANNELS:
                    print(f"Warning: Audio file has {wf.getnchannels()} channels, expected {AUDIO_CHANNELS}")
                
                if wf.getframerate() != AUDIO_SAMPLE_RATE:
                    print(f"Warning: Audio file sample rate is {wf.getframerate()}Hz, expected {AUDIO_SAMPLE_RATE}Hz")
                
                # Read and play audio data
                data = wf.readframes(1024)
                
                while data and not self.stop_playback:
                    # Apply volume
                    if self.current_volume != 1.0:
                        audio_array = np.frombuffer(data, dtype=np.int16)
                        audio_array = (audio_array * self.current_volume).astype(np.int16)
                        data = audio_array.tobytes()
                    
                    # Write to audio device
                    self.device.write(data)
                    data = wf.readframes(1024)
            
            if DEBUG_MODE:
                print(f"Finished playing: {os.path.basename(filepath)}")
                
        except Exception as e:
            print(f"Error playing audio file {filepath}: {e}")
        finally:
            self.is_playing = False
    
    def play_sound(self, category, specific_file=None):
        """
        Play a sound effect from the specified category
        
        Args:
            category: Sound category ('ambient', 'detection', 'scare')
            specific_file: Optional specific filename to play, otherwise random
        """
        if category not in self.available_sounds:
            print(f"Unknown sound category: {category}")
            return
        
        available_files = self.available_sounds[category]
        
        if not available_files:
            print(f"No sounds available in category: {category}")
            return
        
        if specific_file:
            # Play specific file if it exists
            filepath = os.path.join(AUDIO_BASE_PATH, specific_file)
            if filepath in available_files:
                self.audio_queue.put(filepath)
            else:
                print(f"Specific file not found: {specific_file}")
        else:
            # Play random file from category
            filepath = random.choice(available_files)
            self.audio_queue.put(filepath)
            
            if DEBUG_MODE:
                print(f"Queued sound: {category}/{os.path.basename(filepath)}")
    
    def play_random_ambient(self):
        """Play a random ambient sound"""
        self.play_sound('ambient')
    
    def play_detection_sound(self):
        """Play a sound when face is detected"""
        self.play_sound('detection')
    
    def play_scare_sound(self):
        """Play a scare sound effect"""
        self.play_sound('scare')
    
    def set_volume(self, volume):
        """
        Set playback volume
        
        Args:
            volume: Float between 0.0 (silent) and 1.0 (full volume)
        """
        self.current_volume = max(0.0, min(1.0, volume))
        if DEBUG_MODE:
            print(f"Volume set to: {self.current_volume * 100:.0f}%")
    
    def stop_all(self):
        """Stop all audio playback"""
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self.stop_playback = True
        self.is_playing = False
    
    def is_currently_playing(self):
        """Check if audio is currently playing"""
        return self.is_playing
    
    def get_queue_size(self):
        """Get number of sounds waiting to play"""
        return self.audio_queue.qsize()
    
    def cleanup(self):
        """Cleanup audio resources"""
        self.stop_all()
        
        if self.playback_thread:
            self.playback_thread.join(timeout=2.0)
        
        if self.device:
            self.device.close()
        
        print("Audio manager stopped")