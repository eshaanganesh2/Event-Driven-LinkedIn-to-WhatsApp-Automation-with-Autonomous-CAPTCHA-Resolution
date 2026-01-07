# from selenium_recaptcha_solver import RecaptchaSolver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.remote.webelement import WebElement
# from selenium.common.exceptions import TimeoutException
# import time
# from selenium.common.exceptions import NoSuchElementException
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support import expected_conditions as ec
# import os

# class Test:
#     def drill_down_to_iframe_containing_element(self,driver, target_id):
#         # 1. Check if the element is in the CURRENT context
#         if len(driver.find_elements(By.ID, target_id)) > 0:
#             # We found the element! Now we need to return the 'frame' we are currently in.
#             # But Selenium doesn't have a 'driver.get_current_frame_element()' easily.
#             # So we return True to signal to the parent that THIS is the correct frame.
#             return True

#         # 2. Look for nested iframes
#         iframes = driver.find_elements(By.TAG_NAME, "iframe")
#         for i in range(len(iframes)):
#             current_iframes = driver.find_elements(By.TAG_NAME, "iframe")
#             try:
#                 target_frame = current_iframes[i]
#                 driver.switch_to.frame(target_frame)
                
#                 # Recursive call
#                 found = self.drill_down_to_iframe_containing_element(driver, target_id)
                
#                 if found is True:
#                     # If the child found it, the 'target_frame' from this level is the one!
#                     return target_frame
#                 elif found is not None and not isinstance(found, bool):
#                     # If we are deeper than 2 levels, keep bubbling the element up
#                     return found
                    
#                 driver.switch_to.parent_frame()
#             except:
#                 continue
                
#         return None

#     def solve_recaptcha(self,driver,solver):
#        # try:
#                 #recaptcha_iframe = driver.find_elements(By.XPATH, '//iframe[contains(@title, "reCAPTCHA")]')
#                 # The *= means "contains"
#                 recaptcha_iframe = driver.find_elements(By.CSS_SELECTOR, 'iframe[id*="captcha-internal"]') 
#                 driver.switch_to.frame(recaptcha_iframe)

#                 # If the captcha image audio is available, locate it. Otherwise, skip to the next line of code.
#                 frame2=WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '//iframe[contains(@title, "reCAPTCHA")]')))
#                 driver.switch_to.frame(frame2)
#                 checkbox = self._wait_for_element(
#                     by='id',
#                     locator='recaptcha-anchor',
#                     timeout=10,
#                 )
#                 self._wait_for_element(
#                         by=By.XPATH,
#                         locator='//*[@id="recaptcha-audio-button"]',
#                         timeout=1,
#                     ).click()    
#                 # wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "captcha-internal")))
#                 for idx, iframe in enumerate(recaptcha_iframe):
#                     iframe_id = iframe.get_attribute("id")
#                     iframe_name = iframe.get_attribute("name")
#                     iframe_class = iframe.get_attribute("class")

#                     print(f"Iframe {idx}:")
#                     print(f"  id    = {iframe_id}")
#                     print(f"  name  = {iframe_name}")
#                     print(f"  class = {iframe_class}")
#             # iframes = driver.find_elements(By.XPATH, '//iframe[contains(@src,"recaptcha")]')
#             # iframes = driver.find_elements(By.TAG_NAME, "iframe")
#             # Usage:
#             # driver.switch_to.default_content() # Start from the very top
#             # target_iframe = self.drill_down_to_iframe_containing_element(driver, "recaptcha-anchor")
#                 # The driver is now focused on the correct nested frame!
#                 # checkbox = driver.find_element(By.ID, "recaptcha-anchor")
#                 # driver.execute_script("arguments[0].click();", checkbox)
#             # if target_iframe:
#                 try:
#                     solver.click_recaptcha_v2(iframe=recaptcha_iframe,by_selector=By.XPATH)
#                 except NoSuchElementException:
#                     print("checkbox element not found")
#                 print("reCAPTCHA solved successfully.")
#         # except NoSuchElementException:
#         #     print("reCAPTCHA iframe NOT found")
#         # except Exception as e:
#         #     print(f"Error solving reCAPTCHA: {e}")
    
#     # Check if a reCaptcha challenge is presented
#     def checkSecurityChallenge(self,driver):
#         if "recaptcha" in driver.page_source.lower():
#             print("reCAPTCHA detected. Attempting to solve...")
#             return True
#         else:
#             return False

#     # Check if pin-based verification is required
#     def is_pin_verification_page(self,driver, timeout=3):
#         try:
#             WebDriverWait(driver, timeout).until(
#                 EC.visibility_of_element_located(
#                     (By.ID, "input__email_verification_pin")
#                 )
#             )
#             return True
#         except TimeoutException:
#             return False
    
#     # def login(self,session,email, password):
#     def login(self,driver,username,password):
#         try:
#             solver = RecaptchaSolver(driver=driver)

#             # Navigating to the LinkedIn login page
#             # print("Performing automated login with passed credentials")
#             # driver.get("https://www.google.com/recaptcha/api2/demo")

#             driver.get("https://linkedin.com/uas/login")

#             # Locating the username and password fields
#             username_element = driver.find_element(By.ID, "username")
#             password_element = driver.find_element(By.ID, "password")

#             # Filling the username and password fields
#             username_element.send_keys(username)
#             password_element.send_keys(password)

#             # Clicking the login button
#             login = driver.find_element(By.XPATH, "//button[@aria-label='Sign in']")
#             login.click()

#             # Locating the username and password fields
#             # username_element = driver.find_element(By.ID, "username")
#             # password_element = driver.find_element(By.ID, "password")

#             # # Filling the username and password fields
#             # username_element.send_keys(username)
#             # password_element.send_keys(password)

#             # # Clicking the login button
#             # login = driver.find_element(By.XPATH, "//button[@aria-label='Sign in']")
#             # login.click()
#             # # driver.get(url)
#             # print("Logged in successfully")

#             # Wait for the page to load
#             time.sleep(15)
#             if self.checkSecurityChallenge(driver):
#                 print("Security challenge detected")
#                 # iframe_inner = WebDriverWait(driver, 10).until(
#                 #     EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@title, 'reCAPTCHA')]"))
#                 # )
                
#                 # # Click on the CAPTCHA box
#                 # WebDriverWait(driver, 10).until(
#                 #     EC.element_to_be_clickable((By.ID, 'recaptcha-anchor'))
#                 # ).click()
#                 self.solve_recaptcha(driver,solver)

#         except Exception as e:
#             print("Error Encountered during login  ",e)

#     # Method for pin-based verification
#     def verify_pin(self,driver,verification_code):
#         try:  
#             print("Performing PIN based verification")
#             pin_verification_input_box = driver.find_element(By.ID, "input__email_verification_pin")

#             # Filling the pin verification field
#             pin_verification_input_box.send_keys(verification_code)

#             # Clicking the submit button
#             submit = driver.find_element(By.ID, "email-pin-submit-button")
#             submit.click()
#             # driver.get(url)
#             print("PIN-based verification completed successfully")
#         except Exception as e:
#             print("Error encountered during PIN verification ",e)


# test_ua = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
# chrome_options = Options()
# chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# # chrome_options.add_argument("--headless=new")  
# # chrome_options.add_argument("--no-sandbox")    
# # chrome_options.add_argument("--disable-dev-shm-usage")
# # # chrome_options.add_argument(f'--user-agent={test_ua}')
# # chrome_options.add_argument("--disable-gpu")
# # chrome_options.add_argument("--window-size=1280x1696")
# # chrome_options.add_argument("--single-process")
# # # --- STRIP PAGE WEIGHT ---
# # chrome_options.add_argument("--blink-settings=imagesEnabled=false") # Don't load images
# # chrome_options.add_argument("--disable-extensions")
# # chrome_options.add_argument("--disable-notifications")
# # chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# # ChromeDriver path provided by the layer
# service = Service("/Users/eshaanamin/development/chromedriver-mac-arm64/chromedriver")

# # Return Selenium Chrome WebDriver
# driver = webdriver.Chrome(service=service, options=chrome_options)
# test = Test()
# username = os.environ.get('LINKEDIN_EMAIL')
# password = os.environ.get('LINKEDIN_PASSWORD')
# test.login(driver,username,password)


























# import os
# import time
# import random
# import urllib.request
# import pydub
# import speech_recognition
# from DrissionPage import ChromiumPage
# from typing import Optional
# from dotenv import load_dotenv
# import ssl

# load_dotenv()

# class RecaptchaSolver:
#     """A class to solve reCAPTCHA challenges using audio recognition for DrissionPage."""

#     TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
#     TIMEOUT_STANDARD = 15 # Increased for slower network/Lambda environments
#     TIMEOUT_SHORT = 2
#     TIMEOUT_DETECTION = 0.5

#     def __init__(self, driver: ChromiumPage) -> None:
#         self.driver = driver

#     def solveCaptcha(self) -> None:
#         """Robustly navigates nested frames by searching for reCAPTCHA keywords."""
        
#         # 1. Find and Enter the LinkedIn Wrapper
#         print("Searching for LinkedIn Security Wrapper...")
#         self.driver.wait.ele_displayed('#captcha-internal', timeout=15)
#         wrapper = self.driver.get_frame('#captcha-internal')
        
#         if not wrapper:
#             raise Exception("Could not find the LinkedIn Security Wrapper.")

#         # 2. Find the Anchor Iframe (Wait for it to exist)
#         print("Waiting for Google reCAPTCHA frame to be injected...")
#         # We search for an iframe whose 'src' contains 'api2/anchor'
#         anchor_locator = 'xpath://iframe[contains(@src, "api2/anchor") or contains(@title, "reCAPTCHA")]'
        
#         # We must wait for the element to exist inside the wrapper first
#         if not wrapper.wait.ele_displayed(anchor_locator, timeout=15):
#             raise Exception("Google reCAPTCHA iframe never appeared inside the wrapper.")

#         anchor_frame = wrapper.get_frame(anchor_locator)
        
#         print("Checkpoint: Clicking Checkbox")
#         # reCAPTCHA often uses a div with id 'recaptcha-anchor' or the class 'rc-anchor-center-item'
#         anchor_frame.ele('#recaptcha-anchor').click(by_js=True)
        
#         time.sleep(2)

#         # 3. Check if solved immediately
#         if self.is_solved(anchor_frame):
#             print("Solved by checkbox click!")
#             return

#         # 4. Handle Challenge Frame (Audio Popup)
#         print("Locating Challenge Frame...")
#         challenge_locator = 'xpath://iframe[contains(@src, "api2/bframe") or contains(@title, "challenge")]'
        
#         # This frame often appears ONLY after clicking the checkbox
#         if not wrapper.wait.ele_displayed(challenge_locator, timeout=10):
#             # Try searching the whole page if wrapper fails (sometimes it breaks out)
#             challenge_frame = self.driver.get_frame(challenge_locator)
#         else:
#             challenge_frame = wrapper.get_frame(challenge_locator)

#         if not challenge_frame:
#             raise Exception("Challenge frame (bframe) not found.")

#         challenge_frame.wait.ele_displayed("#recaptcha-audio-button", timeout=10)
#         print("Checkpoint: Clicking Audio Button")
#         challenge_frame.ele("#recaptcha-audio-button").click()
        
#         # ... proceed with audio download using 'challenge_frame'

#         # ... continuation of solveCaptcha inside the 'challenge_frame' context

#         # 5. Check for Bot Detection
#         if self.is_detected(challenge_frame):
#             raise Exception("reCAPTCHA blocked us: 'Try again later' detected.")

#         # 6. Process Audio Challenge
#         try:
#             # Wait for the audio source element to be injected into the bframe
#             challenge_frame.wait.ele_displayed("#audio-source", timeout=self.TIMEOUT_STANDARD)
            
#             # Use .link to get the absolute URL of the mp3 file
#             audio_url = challenge_frame.ele("#audio-source").link
#             if not audio_url:
#                 raise Exception("Audio source URL is empty.")
            
#             print(f"Checkpoint 6: Audio URL found. Processing...")
            
#             # Download and Transcribe
#             text_response = self._process_audio_challenge(audio_url)
#             print(f"Recognized Text: {text_response}")
            
#             # Input the recognized text into the response box
#             response_input = challenge_frame.ele("#audio-response")
#             response_input.input(text_response.lower(), clear=True)
            
#             # Click the 'Verify' button
#             verify_button = challenge_frame.ele("#recaptcha-verify-button")
#             verify_button.click(by_js=True)
            
#             # Small wait for the result to register
#             time.sleep(2)

#             # 7. Final Verification
#             # We check the anchor_frame (the checkbox) again to see if it's now 'true'
#             if not self.is_solved(anchor_frame):
#                 # Check if Google asked for a second audio challenge (happens if first was low confidence)
#                 if challenge_frame.ele("#audio-source"):
#                     print("Google requested a second verification. Retrying audio process...")
#                     return self.solveCaptcha() # Recursive retry
#                 raise Exception("Verification failed: Checkbox is still not checked.")
            
#             print("Captcha Solved Successfully!")

#         except Exception as e:
#             raise Exception(f"Audio challenge failed: {str(e)}")

    

#     def _process_audio_challenge(self, audio_url: str) -> str:
#         uid = random.randrange(1, 10000)
#         mp3_path = os.path.join(self.TEMP_DIR, f"cap_{uid}.mp3")
#         wav_path = os.path.join(self.TEMP_DIR, f"cap_{uid}.wav")

#         # --- SSL BYPASS START ---
#         context = ssl._create_unverified_context()
#         # ------------------------

#         try:
#             # Download using the unverified context
#             print(f"Downloading audio from: {audio_url}")
#             with urllib.request.urlopen(audio_url, context=context) as response, open(mp3_path, 'wb') as out_file:
#                 out_file.write(response.read())
            
#             # Convert MP3 to WAV
#             sound = pydub.AudioSegment.from_mp3(mp3_path)
#             sound.export(wav_path, format="wav")

#             # Recognize speech
#             recognizer = speech_recognition.Recognizer()
#             with speech_recognition.AudioFile(wav_path) as source:
#                 audio = recognizer.record(source)
            
#             return recognizer.recognize_google(audio)

#         finally:
#             # Cleanup
#             for path in (mp3_path, wav_path):
#                 if os.path.exists(path):
#                     try: os.remove(path)
#                     except: pass

#     def is_solved(self, anchor_frame) -> bool:
#         try:
#             # Check the aria-checked attribute on the checkbox element
#             status = anchor_frame.ele('#recaptcha-anchor').attrs.get('aria-checked')
#             return status == "true"
#         except:
#             return False

#     def is_detected(self, challenge_frame) -> bool:
#         # Check if the "Try again later" message is visible
#         try:
#             return challenge_frame.ele("text:Try again later", timeout=0.5).states.is_displayed
#         except:
#             return False

# # --- Main Execution ---

# page = ChromiumPage()
# solver = RecaptchaSolver(driver=page)
# page.get('https://linkedin.com/uas/login')

# username = os.environ.get('LINKEDIN_EMAIL')
# password = os.environ.get('LINKEDIN_PASSWORD')

# # 1. Fill username
# page.ele('@id:username').input(username, clear=True)

# # 2. Press "TAB" to move to password field (Avoids NoRectError/Focus issues)
# page.actions.key_down('TAB').key_up('TAB')

# # 3. Type into the now-focused password field
# page.actions.type(password)

# # 4. Press Enter to login (Bypasses the ElementLostError on the 'Sign in' button)
# page.actions.key_down('ENTER').key_up('ENTER')

# time.sleep(3)
# # 5. Wait for the URL to change to see if we hit a checkpoint
# page.wait.url_change('uas/login', timeout=10)
# # Check if a challenge appeared
# if 'checkpoint' in page.url:
#     print("Challenge detected. Proceeding to solve...")
#     try:
#         solver.solveCaptcha()
#         # After solving, wait to see if it redirects you to the feed
#         time.sleep(3)
#         if 'checkpoint' in page.url:
#             # Sometimes you need to click 'Submit' on the page AFTER the captcha is green
#             submit_btn = page.ele('text:Submit', timeout=3)
#             if submit_btn:
#                 submit_btn.click(by_js=True)
#     except Exception as e:
#         print(f"Solver Error: {e}")
# else:
#     print("No challenge detected, successfully logged in.")
    















# import os
# import time
# import random
# import urllib.request
# import pydub
# import speech_recognition
# import ssl
# from DrissionPage import ChromiumPage
# from typing import Optional
# from dotenv import load_dotenv

# load_dotenv()

# class RecaptchaSolver:
#     """A stealthy reCAPTCHA solver using Action Chains for human-like movement."""

#     TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
#     TIMEOUT_STANDARD = 15 

#     def __init__(self, driver: ChromiumPage) -> None:
#         self.driver = driver

#     def solveCaptcha(self) -> None:
#         print("Searching for LinkedIn Security Wrapper...")
#         self.driver.wait.ele_displayed('#captcha-internal', timeout=self.TIMEOUT_STANDARD)
#         wrapper = self.driver.get_frame('#captcha-internal')
        
#         if not wrapper:
#             raise Exception("Could not find the LinkedIn Security Wrapper.")

#         print("Waiting for Google reCAPTCHA frame...")
#         anchor_locator = 'xpath://iframe[contains(@src, "api2/anchor") or contains(@title, "reCAPTCHA")]'
#         wrapper.wait.ele_displayed(anchor_locator, timeout=self.TIMEOUT_STANDARD)
#         anchor_frame = wrapper.get_frame(anchor_locator)
        
#         time.sleep(random.uniform(1.5, 3.0))
#         print("Checkpoint: Clicking Checkbox")
        
#         # FIXED: Using ActionChains for randomized click location
#         anchor_frame.actions.move_to('#recaptcha-anchor', 
#                                     offset_x=random.randint(-10, 10), 
#                                     offset_y=random.randint(-10, 10)).click()
        
#         time.sleep(random.uniform(2, 3.5))

#         if self.is_solved(anchor_frame):
#             print("Solved by checkbox click!")
#             return

#         print("Locating Challenge Frame...")
#         challenge_locator = 'xpath://iframe[contains(@src, "api2/bframe") or contains(@title, "challenge")]'
#         wrapper.wait.ele_displayed(challenge_locator, timeout=10)
#         challenge_frame = wrapper.get_frame(challenge_locator)

#         if not challenge_frame:
#             raise Exception("Challenge frame (bframe) not found.")

#         print("Checkpoint: Clicking Audio Button")
#         challenge_frame.wait.ele_displayed("#recaptcha-audio-button", timeout=5)
#         time.sleep(random.uniform(0.8, 1.8))
        
#         # Using actions for the audio button too
#         challenge_frame.actions.move_to("#recaptcha-audio-button").click()
        
#         self.solve_audio_flow(challenge_frame, anchor_frame)

#     def solve_audio_flow(self, challenge_frame, anchor_frame, attempts=0) -> None:
#         if attempts > 3:
#             raise Exception("Too many attempts. Blocked by Google.")

#         if self.is_detected(challenge_frame):
#             raise Exception("reCAPTCHA blocked us: 'Try again later' detected.")

#         time.sleep(random.uniform(2.0, 4.0))
#         print(f"Attempt {attempts + 1}: Extracting Audio URL")
#         challenge_frame.wait.ele_displayed("#audio-source", timeout=self.TIMEOUT_STANDARD)
#         audio_url = challenge_frame.ele("#audio-source").link
        
#         try:
#             text_response = self._process_audio_challenge(audio_url)
#             print(f"Recognized Text: {text_response}")
            
#             time.sleep(random.uniform(3.0, 6.0)) # Thinking time
            
#             response_input = challenge_frame.ele("#audio-response")
#             response_input.click() 
            
#             for char in text_response.lower():
#                 response_input.input(char)
#                 time.sleep(random.uniform(0.1, 0.3)) 
            
#             time.sleep(random.uniform(1.5, 3.0))
#             challenge_frame.actions.move_to("#recaptcha-verify-button").click()
            
#             time.sleep(4)

#             if self.is_solved(anchor_frame):
#                 print("Captcha Solved Successfully!")
#                 return
#             else:
#                 print("Response not accepted. Reloading...")
#                 reload_btn = challenge_frame.ele("#recaptcha-reload-button")
#                 if reload_btn:
#                     challenge_frame.actions.move_to("#recaptcha-reload-button").click()
#                     time.sleep(2)
#                 return self.solve_audio_flow(challenge_frame, anchor_frame, attempts + 1)

#         except Exception as e:
#             raise Exception(f"Audio flow error: {str(e)}")

#     def _process_audio_challenge(self, audio_url: str) -> str:
#         uid = random.randrange(1, 10000)
#         mp3_path = os.path.join(self.TEMP_DIR, f"cap_{uid}.mp3")
#         wav_path = os.path.join(self.TEMP_DIR, f"cap_{uid}.wav")
#         context = ssl._create_unverified_context()

#         try:
#             with urllib.request.urlopen(audio_url, context=context) as response, open(mp3_path, 'wb') as out_file:
#                 out_file.write(response.read())
            
#             sound = pydub.AudioSegment.from_mp3(mp3_path)
#             sound.export(wav_path, format="wav")

#             recognizer = speech_recognition.Recognizer()
#             with speech_recognition.AudioFile(wav_path) as source:
#                 audio = recognizer.record(source)
            
#             return recognizer.recognize_google(audio)
#         finally:
#             for path in (mp3_path, wav_path):
#                 if os.path.exists(path):
#                     try: os.remove(path)
#                     except: pass

#     def is_solved(self, anchor_frame) -> bool:
#         try:
#             return anchor_frame.ele('#recaptcha-anchor').attrs.get('aria-checked') == "true"
#         except:
#             return False

#     def is_detected(self, challenge_frame) -> bool:
#         try:
#             return challenge_frame.ele("text:Try again later", timeout=0.5).states.is_displayed
#         except:
#             return False

# # --- Main ---
# page = ChromiumPage()
# solver = RecaptchaSolver(driver=page)

# page.set.user_agent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
# page.get('https://linkedin.com/uas/login')

# username = os.environ.get('LINKEDIN_EMAIL')
# password = os.environ.get('LINKEDIN_PASSWORD')

# print("Filling credentials...")
# page.ele('@id:username').input(username, clear=True)
# time.sleep(random.uniform(1, 2))

# page.actions.key_down('TAB').key_up('TAB')
# time.sleep(random.uniform(0.5, 1.5))

# for char in password:
#     page.actions.type(char)
#     time.sleep(random.uniform(0.1, 0.2))

# time.sleep(random.uniform(1, 2))
# page.actions.key_down('ENTER').key_up('ENTER')

# try:
#     page.wait.url_change('uas/login', timeout=10)
# except:
#     pass

# time.sleep(5)

# if 'checkpoint' in page.url:
#     print("Challenge detected. Proceeding...")
#     try:
#         solver.solveCaptcha()
#         page.wait.url_change('checkpoint', timeout=15)
#         if 'checkpoint' in page.url:
#             submit = page.ele('text:Submit', timeout=3)
#             if submit: 
#                 time.sleep(2)
#                 submit.click()
#     except Exception as e:
#         print(f"Solver Error: {e}")

# if 'feed' in page.url or 'mynetwork' in page.url:
#     print("Logged in successfully!")
# else:
#     print(f"Final URL: {page.url}")











import os
import time
import random
import urllib.request
import pydub
import speech_recognition
import ssl
from DrissionPage import ChromiumPage
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class RecaptchaSolver:
    """A stealthy reCAPTCHA solver with improved race-condition handling."""

    TEMP_DIR = os.getenv("TEMP") if os.name == "nt" else "/tmp"
    TIMEOUT_STANDARD = 15 

    def __init__(self, driver: ChromiumPage) -> None:
        self.driver = driver

    def solveCaptcha(self) -> None:
        print("refreshCookies.py -> Searching for LinkedIn Security Wrapper...")
        self.driver.wait.ele_displayed('#captcha-internal', timeout=self.TIMEOUT_STANDARD)
        wrapper = self.driver.get_frame('#captcha-internal')
        
        if not wrapper:
            raise Exception("Could not find the LinkedIn Security Wrapper.")

        print("refreshCookies.py -> Waiting for Google reCAPTCHA frame...")
        anchor_locator = 'xpath://iframe[contains(@src, "api2/anchor") or contains(@title, "reCAPTCHA")]'
        wrapper.wait.ele_displayed(anchor_locator, timeout=self.TIMEOUT_STANDARD)
        anchor_frame = wrapper.get_frame(anchor_locator)
        
        time.sleep(random.uniform(1.5, 3.0))
        print("refreshCookies.py -> Checkpoint: Clicking Checkbox")
        
        anchor_frame.actions.move_to('#recaptcha-anchor', 
                                    offset_x=random.randint(-10, 10), 
                                    offset_y=random.randint(-10, 10)).click()
        
        time.sleep(random.uniform(2, 3.5))

        if self.is_solved(anchor_frame):
            print("Solved by checkbox click!")
            return

        print("refreshCookies.py -> Locating Challenge Frame...")
        challenge_locator = 'xpath://iframe[contains(@src, "api2/bframe") or contains(@title, "challenge")]'
        wrapper.wait.ele_displayed(challenge_locator, timeout=10)
        challenge_frame = wrapper.get_frame(challenge_locator)

        if not challenge_frame:
            raise Exception("Challenge frame (bframe) not found.")

        print("refreshCookies.py -> Checkpoint: Clicking Audio Button")
        challenge_frame.wait.ele_displayed("#recaptcha-audio-button", timeout=5)
        time.sleep(random.uniform(0.8, 1.8))
        
        challenge_frame.actions.move_to("#recaptcha-audio-button").click()
        
        self.solve_audio_flow(challenge_frame, anchor_frame)

    def solve_audio_flow(self, challenge_frame, anchor_frame, attempts=0) -> None:
        if attempts > 3:
            raise Exception("Too many attempts. Blocked by Google.")

        if self.is_detected(challenge_frame):
            raise Exception("reCAPTCHA blocked us: 'Try again later' detected.")

        time.sleep(random.uniform(2.0, 4.0))
        print(f"refreshCookies.py -> Attempt {attempts + 1}: Extracting Audio URL")
        challenge_frame.wait.ele_displayed("#audio-source", timeout=self.TIMEOUT_STANDARD)
        audio_url = challenge_frame.ele("#audio-source").link
        
        try:
            text_response = self._process_audio_challenge(audio_url)
            print(f"refreshCookies.py -> Recognized Text: {text_response}")
            
            time.sleep(random.uniform(3.0, 6.0))
            
            response_input = challenge_frame.ele("#audio-response")
            response_input.click() 
            
            for char in text_response.lower():
                response_input.input(char)
                time.sleep(random.uniform(0.1, 0.3)) 
            
            time.sleep(random.uniform(1.5, 3.0))
            challenge_frame.actions.move_to("#recaptcha-verify-button").click()
            
            # --- Race condition fix start ---
            print("refreshCookies.py -> Verification submitted. Waiting for state change...")
            time.sleep(3)
            
            solved = False
            for i in range(3):  # Check 5 times over 5 seconds
                if self.is_solved(anchor_frame):
                    solved = True
                    break
                print(f"refreshCookies.py -> Checking solve status... attempt {i+1}")
                time.sleep(1)

            if solved:
                print("refreshCookies.py -> Captcha Solved Successfully!")
                return
            
            # If the audio button is still there, it failed. 
            if not challenge_frame.ele("#audio-source", timeout=1):
                print("Challenge UI disappeared. Assuming successful redirection.")
                return

            print("Response not accepted by Google. Reloading challenge...")
            reload_btn = challenge_frame.ele("#recaptcha-reload-button")
            if reload_btn:
                challenge_frame.actions.move_to("#recaptcha-reload-button").click()
                time.sleep(2)
            return self.solve_audio_flow(challenge_frame, anchor_frame, attempts + 1)

        except Exception as e:
            raise Exception(f"Audio flow error: {str(e)}")

    def _process_audio_challenge(self, audio_url: str) -> str:
        uid = random.randrange(1, 10000)
        mp3_path = os.path.join(self.TEMP_DIR, f"cap_{uid}.mp3")
        wav_path = os.path.join(self.TEMP_DIR, f"cap_{uid}.wav")
        context = ssl._create_unverified_context()

        try:
            with urllib.request.urlopen(audio_url, context=context) as response, open(mp3_path, 'wb') as out_file:
                out_file.write(response.read())
            
            sound = pydub.AudioSegment.from_mp3(mp3_path)
            sound.export(wav_path, format="wav")

            recognizer = speech_recognition.Recognizer()
            with speech_recognition.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
            
            return recognizer.recognize_google(audio)
        finally:
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    try: os.remove(path)
                    except: pass

    def is_solved(self, anchor_frame) -> bool:
        try:
            # Check the aria-checked attribute on the checkbox element
            return anchor_frame.ele('#recaptcha-anchor').attrs.get('aria-checked') == "true"
        except:
            return False

    def is_detected(self, challenge_frame) -> bool:
        try:
            return challenge_frame.ele("text:Try again later", timeout=0.5).states.is_displayed
        except:
            return False


page = ChromiumPage()
solver = RecaptchaSolver(driver=page)

# Set Stealth User Agent
page.set.user_agent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
page.get('https://linkedin.com/uas/login')

username = os.environ.get('LINKEDIN_EMAIL')
password = os.environ.get('LINKEDIN_PASSWORD')

print("refreshCookies.py -> Filling credentials...")
page.ele('@id:username').input(username, clear=True)
time.sleep(random.uniform(1, 2))

page.actions.key_down('TAB').key_up('TAB')
time.sleep(random.uniform(0.5, 1.5))

for char in password:
    page.actions.type(char)
    time.sleep(random.uniform(0.1, 0.2))

time.sleep(random.uniform(1, 2))
page.actions.key_down('ENTER').key_up('ENTER')

# Wait for navigation away from login
try:
    page.wait.url_change('uas/login', timeout=10)
except:
    pass

time.sleep(5)

# If challenged, solve it
if 'checkpoint' in page.url:
    print("refreshCookies.py -> Challenge detected. Proceeding...")
    try:
        solver.solveCaptcha()
        
        # Give the page time to transition to feed after solving
        page.wait.url_change('checkpoint', timeout=15)
        
        if 'checkpoint' in page.url:
            submit = page.ele('text:Submit', timeout=3)
            if submit: 
                time.sleep(2)
                submit.click()
    except Exception as e:
        print(f"refreshCookies.py -> Solver Error: {e}")

# Verification of Success
if 'feed' in page.url or 'mynetwork' in page.url:
    print("refreshCookies.py -> Logged in successfully!")
else:
    print(f"refreshCookies.py -> Final URL: {page.url} - Check if login was successful.")