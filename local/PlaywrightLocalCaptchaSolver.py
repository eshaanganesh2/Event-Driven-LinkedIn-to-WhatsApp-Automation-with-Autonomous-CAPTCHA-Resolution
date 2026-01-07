import os
import time
import random
import urllib.request
import pydub
import speech_recognition
import ssl
from playwright.sync_api import Page, sync_playwright
from dotenv import load_dotenv

load_dotenv()
# --- LOCAL CONFIGURATION ---
pydub.AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
pydub.AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"

class RecaptchaSolver:
    def __init__(self, page: Page) -> None:
        self.page = page
        # Use current working directory for local debugging of audio files
        self.temp_dir = os.getcwd()

    def solveCaptcha(self) -> None:
        print(f"Step 1: Locating #captcha-internal...")
        wrapper = self.page.frame_locator("#captcha-internal")
        
        print(f"Step 2: Locating checkbox frame...")
        anchor_frame = wrapper.frame_locator('iframe[title*="reCAPTCHA"]').first
        
        try:
            checkbox = anchor_frame.locator("#recaptcha-anchor")
            checkbox.wait_for(state="visible", timeout=10000)
            
            # Human-like interaction
            checkbox.hover()
            time.sleep(random.uniform(0.7, 1.8))
            checkbox.click(position={'x': random.randint(10, 20), 'y': random.randint(10, 20)})
            print(f"Checkbox clicked.")
        except Exception as e:
            print(f"Checkbox interaction failed: {e}")
            return

        time.sleep(random.uniform(2.0, 3.5))
        
        if self.is_solved(anchor_frame):
            print("Solved immediately by checkbox.")
            return

        print(f"Step 3: Finding Challenge Frame...")
        challenge_frame = wrapper.frame_locator('iframe[title*="challenge"]').first
        
        try:
            audio_btn = challenge_frame.locator("#recaptcha-audio-button")
            audio_btn.wait_for(state="visible", timeout=12000)
            
            # Mouse jitter to simulate human movement
            self.page.mouse.move(random.randint(100, 300), random.randint(100, 300))
            time.sleep(random.uniform(0.5, 1.2))
            
            print(f"Audio button found. Clicking...")
            audio_btn.evaluate("node => node.click()") 
            
            self.solve_audio_flow(challenge_frame)
            
        except Exception as e:
            print(f"Step 3 failed: {e}")
            self.page.screenshot(path="error_challenge_frame.png")

    def solve_audio_flow(self, challenge_frame):
        print(f"Step 4: Waiting for audio source...")
        
        if challenge_frame.get_by_text("Try again later").is_visible(timeout=2000):
            print("!!! Google may have detected captcha automation and IP may be flagged for a while !!!")
            return

        try:
            audio_source = challenge_frame.locator("#audio-source")
            audio_source.wait_for(state="attached", timeout=20000)
            audio_url = audio_source.get_attribute("src")
            
            text_response = self._process_audio_challenge(audio_url)
            print(f"Recognized: {text_response}")
            
            input_field = challenge_frame.locator("#audio-response")
            input_field.click() 
            time.sleep(random.uniform(0.5, 1.0))
            
            # Natural typing speed
            for char in text_response:
                input_field.type(char, delay=random.randint(100, 250))
            
            time.sleep(random.uniform(1.2, 2.5))
            challenge_frame.locator("#recaptcha-verify-button").click()
            print("Verify clicked.")

        except Exception as e:
            print(f"Audio flow failure: {e}")
            self.page.screenshot(path="error_audio_flow.png")

    def _process_audio_challenge(self, audio_url: str) -> str:
        uid = random.randrange(1, 10000)
        mp3_path = os.path.join(self.temp_dir, f"cap_{uid}.mp3")
        wav_path = os.path.join(self.temp_dir, f"cap_{uid}.wav")
        
        # --- SSL BYPASS FOR LOCAL TESTING ---
        import ssl
        context = ssl._create_unverified_context()
        
        # Open the URL using the unverified context
        with urllib.request.urlopen(audio_url, context=context) as response, \
             open(mp3_path, 'wb') as out_file:
            out_file.write(response.read())

        # Convert
        sound = pydub.AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")

        # Recognize
        recognizer = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        
        result = recognizer.recognize_google(audio)
        
        # Cleanup
        if os.path.exists(mp3_path): os.remove(mp3_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        return result

    def is_solved(self, anchor_frame) -> bool:
        try:
            return anchor_frame.locator('#recaptcha-anchor').get_attribute("aria-checked") == "true"
        except:
            return False

def run_local_test():
    with sync_playwright() as p:
        print("Launching browser...")
        # Use args to prevent the crash we discussed earlier
        browser = p.chromium.launch(
            headless=False, 
            args=["--no-sandbox", "--disable-gpu"]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("Navigating to LinkedIn Login...")
        page.goto("https://www.linkedin.com/uas/login")

        username = os.environ.get('LINKEDIN_EMAIL')
        password = os.environ.get('LINKEDIN_PASSWORD')+"abc"

        if not username or not password:
            print(" WARNING: Environment variables LINKEDIN_EMAIL or PASSWORD not found!")
            # Fallback for local testing if env vars aren't set
            username = "your-email@example.com"
            password = "your-password"

        print("Filling credentials...")
        # Fill email
        page.locator("#username").fill(username)
        time.sleep(random.uniform(1, 2))

        # Human-like password entry
        page.locator("#password").click()
        for char in password:
            page.keyboard.type(char, delay=random.randint(100, 200))
            
        time.sleep(random.uniform(1, 2))
        print("Pressing Enter...")
        page.keyboard.press("Enter")

        # WAIT FOR CAPTCHA TO APPEAR
        print("Waiting to see if reCAPTCHA appears...")
        try:
            # Check if the captcha container exists within 10 seconds
            page.wait_for_selector("#captcha-internal", timeout=10000)
            print(" reCAPTCHA detected! Starting solver...")
            
            solver = RecaptchaSolver(page)
            solver.solveCaptcha()
            
        except Exception as e:
            print(f"No captcha detected or error occurred: {e}")
            # Take a screenshot to see where we landed
            page.screenshot(path="login_result.png")

        print("\n" + "="*30)
        print("LOCAL TEST FINISHED")
        print("Check the browser window to see if it worked.")
        input("Press ENTER to close the browser and exit...")
        browser.close()

if __name__ == "__main__":
    run_local_test()