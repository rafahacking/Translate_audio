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
        self.output_filename = f"gravação_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
    def list_loopback_devices(self):
        print("\n=== Dispositivos de loopback disponíveis (Alto-falantes) ===")
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
            
            print(f"\n🎧 Gravando de: {loopback_device.name}")
            print(f"🔴 Gravando... Press 'q' para parar a gravação\n")
            
            # Use get_microphone with loopback to record system audio
            with sc.get_microphone(id=str(loopback_device.name), include_loopback=True).recorder(samplerate=self.RATE) as mic:
                while self.is_recording:
                    if keyboard.is_pressed('q'):
                        print("\n⏹️  Parando gravação...")
                        self.is_recording = False
                        break
                    
                    try:
                        data = mic.record(numframes=self.RATE // 10)
                        self.recorded_data.append(data)
                    except Exception as e:
                        print(f"❌ Erro ao ler áudio: {e}")
                        continue
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar gravação: {e}")
            print("\nTroubleshooting:")
            print("- Certifique-se de que o áudio está tocando no seu computador")
            print("- Tente executar como Administrador")
            return False
    
    def save_recording(self):
        if not self.recorded_data:
            print("❌ Nenhum áudio gravado!")
            return None
        
        print(f"💾 Salvando gravação para {self.output_filename}...")
        
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
            
            print(f"✅ Gravação salva com sucesso!")
            return self.output_filename
            
        except Exception as e:
            print(f"❌ Erro ao salvar gravação: {e}")
            return None
    
    def transcribe_audio(self, filename):
        if not filename or not os.path.exists(filename):
            print("❌ Arquivo de áudio não encontrado!")
            return None
        
        print(f"\n🎯 Transcrevendo áudio para o inglês...")
        
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(filename) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                print("🔄 Processando reconhecimento de fala...")
                text = recognizer.recognize_google(audio_data, language='en-US')
                print(f"\n{'='*60}")
                print("📝 TRANSCRIÇÃO (English):")
                print(f"{'='*60}")
                print(text)
                print(f"{'='*60}\n")
                return text
                
        except sr.UnknownValueError:
            print("❌ Não foi possível entender o áudio")
            return None
        except sr.RequestError as e:
            print(f"❌ Erro com o serviço de reconhecimento de fala: {e}")
            return None
        except Exception as e:
            print(f"❌ Erro durante a transcrição: {e}")
            return None
    


def main():
    print("=" * 60)
    print("🎙️  GRAVE E TRANSCREVE (English)")
    print("=" * 60)
    
    recorder = SystemAudioRecorder()
    
    loopbacks = recorder.list_loopback_devices()
    
    loopback_device = None
    if loopbacks:
        if len(loopbacks) > 1:
            choice = input(f"\nSelecione o dispositivo (0-{len(loopbacks)-1}) ou press Enter for default: ")
            if choice.strip().isdigit():
                loopback_device = loopbacks[int(choice)]
        
        if loopback_device is None:
            loopback_device = sc.default_speaker()
            print(f"\n✅ Usando o padrão: {loopback_device.name}")
    else:
        print("\n⚠️  Nenhum dispositivo de loopback encontrado. Usando o padrão.")
        loopback_device = sc.default_speaker()
    
    input("\n▶️  Aperte Enter para começar a gravação (Deixe o áudio tocando)...")
    
    if recorder.start_recording(loopback_device):
        filename = recorder.save_recording()
        
        if filename:
            transcription = recorder.transcribe_audio(filename)
            
            if transcription:
                txt_filename = filename.replace('.wav', '_transcription.txt')
                with open(txt_filename, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                print(f"💾 Transcription saved to: {txt_filename}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
