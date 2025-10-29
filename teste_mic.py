import soundcard as sc
import numpy as np
import wave
import speech_recognition as sr
import keyboard
import os
from datetime import datetime
import struct

class SystemAudioRecorder:
    def __init__(self):
        self.RATE = 48000
        self.recorded_data = []
        self.is_recording = False
        self.output_filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
    def list_loopback_devices(self):
        print("\n=== Available Loopback Devices (Speakers) ===")
        loopbacks = sc.all_speakers()
        
        for i, speaker in enumerate(loopbacks):
            print(f"{i}: {speaker.name}")
        
        print("=" * 50)
        return loopbacks
    
    def start_recording(self, loopback_device=None):
        self.recorded_data = []
        self.is_recording = True
        
        try:
            if loopback_device is None:
                loopback_device = sc.default_speaker()
            
            print(f"\n🎧 Recording from: {loopback_device.name}")
            print(f"🔴 RECORDING... Press 'q' to stop recording\n")
            
            # Use get_microphone with loopback to record system audio
            with sc.get_microphone(id=str(loopback_device.name), include_loopback=True).recorder(samplerate=self.RATE) as mic:
                while self.is_recording:
                    if keyboard.is_pressed('q'):
                        print("\n⏹️  Stopping recording...")
                        self.is_recording = False
                        break
                    
                    try:
                        data = mic.record(numframes=self.RATE // 10)
                        self.recorded_data.append(data)
                    except Exception as e:
                        print(f"Error reading audio: {e}")
                        continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting recording: {e}")
            print("\nTroubleshooting:")
            print("- Make sure audio is playing on your computer")
            print("- Try running as Administrator")
            return False
    
    def save_recording(self):
        if not self.recorded_data:
            print("❌ No audio data recorded!")
            return None
        
        print(f"💾 Saving recording to {self.output_filename}...")
        
        try:
            audio_data = np.concatenate(self.recorded_data, axis=0)
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            audio_data = np.int16(audio_data * 32767)
            with wave.open(self.output_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.RATE)
                wf.writeframes(audio_data.tobytes())
            
            print(f"✅ Recording saved successfully!")
            return self.output_filename
            
        except Exception as e:
            print(f"❌ Error saving recording: {e}")
            return None
    
    def transcribe_audio(self, filename):
        if not filename or not os.path.exists(filename):
            print("❌ Audio file not found!")
            return None
        
        print(f"\n🎯 Transcribing audio to English...")
        
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(filename) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                print("🔄 Processing speech recognition...")
                text = recognizer.recognize_google(audio_data, language='en-US')
                print(f"\n{'='*60}")
                print("📝 TRANSCRIPTION (English):")
                print(f"{'='*60}")
                print(text)
                print(f"{'='*60}\n")
                return text
                
        except sr.UnknownValueError:
            print("❌ Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return None
    


def main():
    print("=" * 60)
    print("🎙️  SYSTEM AUDIO RECORDER & TRANSCRIBER (English)")
    print("=" * 60)
    
    recorder = SystemAudioRecorder()
    
    # List available loopback devices
    loopbacks = recorder.list_loopback_devices()
    
    loopback_device = None
    if loopbacks:
        if len(loopbacks) > 1:
            choice = input(f"\nSelect device (0-{len(loopbacks)-1}) or press Enter for default: ")
            if choice.strip().isdigit():
                loopback_device = loopbacks[int(choice)]
        
        if loopback_device is None:
            loopback_device = sc.default_speaker()
            print(f"\n✅ Using default speaker: {loopback_device.name}")
    else:
        print("\n⚠️  No loopback devices found. Using default.")
        loopback_device = sc.default_speaker()
    
    input("\n▶️  Press Enter to start recording (make sure audio is playing)...")
    
    # Start recording
    if recorder.start_recording(loopback_device):
        # Save the recording
        filename = recorder.save_recording()
        
        if filename:
            # Transcribe the audio
            transcription = recorder.transcribe_audio(filename)
            
            if transcription:
                # Save transcription to file
                txt_filename = filename.replace('.wav', '_transcription.txt')
                with open(txt_filename, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                print(f"💾 Transcription saved to: {txt_filename}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
