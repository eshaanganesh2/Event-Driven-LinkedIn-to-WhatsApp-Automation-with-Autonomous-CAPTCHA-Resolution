import os
import time
import random
import urllib.request
import pydub
import speech_recognition
import ssl
from playwright.sync_api import Page

pydub.AudioSegment.converter = "/usr/bin/ffmpeg"
pydub.AudioSegment.ffprobe = "/usr/bin/ffprobe"

class RecaptchaSolver:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.temp_dir = "/tmp"

    def solveCaptcha(self) -> None:
        print(f"Step 1: Locating #captcha-internal...")
        wrapper = self.page.frame_locator("#captcha-internal")
        
        print(f"Step 2: Locating checkbox frame...")
        anchor_frame = wrapper.frame_locator('iframe[title*="reCAPTCHA"]').first
        
        try:
            checkbox = anchor_frame.locator("#recaptcha-anchor")
            checkbox.wait_for(state="visible", timeout=10000)
            
            checkbox.hover()
            time.sleep(random.uniform(0.7, 1.8))
            
            # Clicking slightly away from the exact center (0,0)
            checkbox.click(position={'x': random.randint(10, 20), 'y': random.randint(10, 20)})
            print(f"Checkbox clicked with human offset.")
        except Exception as e:
            print(f"Checkbox interaction failed: {e}")
            raise

        # Wait for the challenge to manifest
        time.sleep(random.uniform(2.0, 3.5))
        
        if self.is_solved(anchor_frame):
            print("Solved immediately by checkbox.")
            return

        print(f"Step 3: Finding Challenge Frame...")
        challenge_frame = wrapper.frame_locator('iframe[title*="challenge"]').first
        
        try:
            audio_btn = challenge_frame.locator("#recaptcha-audio-button")
            # Fallback to global search if frame is shifted
            if audio_btn.count() == 0:
                challenge_frame = self.page.frame_locator('iframe[title*="challenge"]').first
                audio_btn = challenge_frame.locator("#recaptcha-audio-button")

            audio_btn.wait_for(state="visible", timeout=12000)
            
            # mouse jitter before audio click
            self.page.mouse.move(random.randint(100, 300), random.randint(100, 300))
            time.sleep(random.uniform(0.5, 1.2))
            
            print(f"Audio button found. Clicking via JS evaluate...")
            audio_btn.evaluate("node => node.click()") # Bypass overlay detection
            
            self.solve_audio_flow(challenge_frame)
            
        except Exception as e:
            print(f"Step 3 failed: {e}")
            self.page.screenshot(path="/tmp/audio_btn_missing.png")
            raise

    def solve_audio_flow(self, challenge_frame):
        print(f"Step 4: Waiting for audio source...")
        
        if challenge_frame.get_by_text("Try again later").is_visible(timeout=2000):
            print("!!! Google may have detected captcha automation and IP may be flagged for a while !!!")
            raise Exception("Google reCAPTCHA soft-block: Try again later.")

        try:
            audio_source = challenge_frame.locator("#audio-source")
            audio_source.wait_for(state="attached", timeout=20000)
            audio_url = audio_source.get_attribute("src")
            
            text_response = self._process_audio_challenge(audio_url)
            print(f"Recognized: {text_response}")
            
            input_field = challenge_frame.locator("#audio-response")
            input_field.click() # Focus the field first
            time.sleep(random.uniform(0.5, 1.0))
            
            for char in text_response:
                input_field.type(char, delay=random.randint(150, 350))
            
            time.sleep(random.uniform(1.2, 2.5))
            challenge_frame.locator("#recaptcha-verify-button").click()
            print("Verify clicked.")

        except Exception as e:
            print(f"Audio flow failure: {e}")
            self.page.screenshot(path="/tmp/audio_flow_failed.png")
            raise

    def _process_audio_challenge(self, audio_url: str) -> str:
        uid = random.randrange(1, 10000)
        mp3_path = f"{self.temp_dir}/cap_{uid}.mp3"
        wav_path = f"{self.temp_dir}/cap_{uid}.wav"
        
        ssl_context = ssl._create_unverified_context()
        urllib.request.urlretrieve(audio_url, mp3_path)
        
        sound = pydub.AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")

        recognizer = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        
        result = recognizer.recognize_google(audio)
        
        os.remove(mp3_path)
        os.remove(wav_path)
        return result

    def is_solved(self, anchor_frame) -> bool:
        try:
            return anchor_frame.locator('#recaptcha-anchor').get_attribute("aria-checked") == "true"
        except:
            return False