import io
import sounddevice as sd
import soundfile as sf
from openai import OpenAI
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os
import re
import time
import tempfile
import numpy as np

load_dotenv()

class VoiceAgent:
    def __init__(self):
        self.client = OpenAI()
        self.voice_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.voice_id = "JBFqnCBsd6RMkjVDRZzb"  # Rachel voice
        self.sample_rate = 44100
        
    def speak(self, text):
        """Convert text to speech using ElevenLabs"""
        try:
            audio = self.voice_client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            play(audio)
            # Add a small delay to ensure the message is heard
            time.sleep(len(text.split()) * 0.3)
        except Exception as e:
            print(f"Speech synthesis failed: {e}")
            print(f"Fallback to text: {text}")  # Fallback to printing
            
    def record_audio(self, duration=5):
        """Record audio from microphone"""
        self.speak("Recording...")
        
        # Record audio
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_file.name, recording, self.sample_rate)
        
        return temp_file.name
        
    def transcribe_audio(self, audio_file):
        """Transcribe audio using Whisper API"""
        try:
            with open(audio_file, "rb") as f:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            return transcript.text
        except Exception as e:
            print(f"Transcription failed: {e}")
            return None
            
    def listen_for_input(self, prompt):
        """Listen for voice input with a specific prompt"""
        self.speak(prompt)
        
        time.sleep(3)
        
        # Record audio
        audio_file = self.record_audio()
        
        # Transcribe
        text = self.transcribe_audio(audio_file)
        
        # Cleanup
        os.unlink(audio_file)
        
        if text:
            self.speak(f"I heard: {text}")
            return text
        else:
            self.speak("I could not understand what you said. Please try again.")
            return None
            
    def extract_url(self, text):
        """Extract URL from text using regex and validation"""
        # Basic URL pattern
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        urls = re.findall(url_pattern, text)
        
        if urls:
            return urls[0]
            
        # If no URL found, use OpenAI to try to understand the URL
        response = self.client.chat.completions.create(
            model="o1-mini",
            messages=[
                {"role": "user", "content": f"Extract a website URL from this {text}. If no valid URL is found, try to construct one from the domain name. Return just the URL with https:// prefix or 'invalid' if no URL can be constructed."}
            ]
        )
        
        extracted_url = response.choices[0].message.content.strip()
        return None if extracted_url == "invalid" else extracted_url
            
    def get_reference_url(self):
        """Get reference URL from voice input with validation"""
        url = None
        while not url:
            text = self.listen_for_input(
                "Please provide a URL for the reference design you'd like to use. "
                "You can say the full URL or just the website name."
            )
            if not text:
                return None
                
            url = self.extract_url(text)
            if not url:
                self.speak("I couldn't understand the URL. Please try again.")
            else:
                self.speak(f"Great! I'll use {url} as the reference design.")
                
        return url
            
    def process_design_feedback(self, screenshot_analysis):
        """Process feedback about the design based on screenshot analysis"""
        self.speak("I've analyzed the design. What changes would you like to make?")
        feedback = self.listen_for_input("Please provide your feedback.")
        if not feedback:
            return None
            
        response = self.client.chat.completions.create(
            model="o1-mini",
            messages=[
                {"role": "user", "content": f"You are a UI/UX expert. Based on the screenshot analysis and user feedback, provide specific UI component requirements.\nScreenshot Analysis: {screenshot_analysis}\nUser Feedback: {feedback}"}
            ]
        )
        
        return response.choices[0].message.content

if __name__ == "__main__":
    agent = VoiceAgent()
    url = agent.get_reference_url()
    print("Reference URL:", url)
