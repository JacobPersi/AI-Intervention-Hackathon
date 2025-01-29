from typing import Optional, List, Tuple, Callable
import pygame
import os
from gtts import gTTS
import threading
import time
import queue
import speech_recognition as sr
from time import sleep
import pyautogui
import cv2
from PIL import Image
import google.generativeai as gemini
import base64
import re
from dataclasses import dataclass
from typing import Optional, List, Tuple, Callable
import json

@dataclass
class AudioJob:
    """Represents a text-to-speech job in the queue."""
    text: str
    audio_file: str

class TextToSpeech:
    """Handles text-to-speech conversion and audio playback with queue management."""
    
    def __init__(self) -> None:
        self.audio_queue: queue.Queue = queue.Queue()
        self.thread: threading.Thread = threading.Thread(target=self._process_queue)
        self.lock: threading.Lock = threading.Lock()
        self.running: bool = False
        pygame.mixer.init()

    def _process_queue(self) -> None:
        """Process audio jobs from the queue continuously while running."""
        while self.running:
            try:
                text, audio_file = self.audio_queue.get(timeout=1)
                self._play_audio(text, audio_file)
            except queue.Empty:
                continue

    def _play_audio(self, text: str, audio_file: str = "tts.mp3") -> None:
        """Convert text to speech and play the resulting audio."""
        try:
            with self.lock:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                timestamp = int(time.time() * 1000)
                audio_file_name = f'{timestamp}_{audio_file}'
                audio_path = os.path.join(script_dir, audio_file_name)

                tts = gTTS(text=text, lang="en")
                tts.save(audio_path)
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

        except (pygame.error, Exception) as e:
            print(f"Error in audio playback: {e}")

    def add_to_queue(self, text: str, audio_file: str = "tts.mp3") -> None:
        """Add a new text-to-speech job to the queue."""
        self.audio_queue.put((text, audio_file))

    def start(self) -> None:
        """Start the audio processing thread."""
        self.running = True
        self.thread.start()

    def stop(self) -> None:
        """Stop the audio processing thread and cleanup resources."""
        self.running = False
        self.thread.join()
        pygame.mixer.quit()

class SharedMemoryMonitor:
    """Manages shared memory for storing and processing transcribed text."""
    
    def __init__(self) -> None:
        self.shared_memory: Optional[str] = ""
        self.long_term_memory: str = ""
        self.last_update_time: float = time.time()
        self.running: bool = False
        self.check_every: int = 4

    def update_memory(self, new_value: str) -> None:
        """Update shared memory with new transcribed text."""
        if self.shared_memory is None:
            self.shared_memory = ""
        self.shared_memory += new_value + " "
        self.last_update_time = time.time()

    def _monitor(self) -> None:
        """Monitor shared memory for updates and execute processing when needed."""
        while self.running:
            time_since_update = time.time() - self.last_update_time
            if time_since_update > self.check_every:
                self.execute()
                self.last_update_time = time.time()
            time.sleep(1)

    def execute(self) -> None:
        """Process shared memory content based on triggers and timing."""
        if self.shared_memory is None:
            return

        if "study buddy" in self.shared_memory:
            print(f"IMMEDIATE: {self.shared_memory}")
        else:
            self.long_term_memory += self.shared_memory

        self.shared_memory = None

    def start(self) -> None:
        """Start the memory monitoring thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor)
            self.thread.daemon = True
            self.thread.start()

    def stop(self) -> None:
        """Stop the memory monitoring thread."""
        if self.running:
            self.running = False
            self.thread.join()

class SpeechToText:
    """Handles continuous speech recognition and transcription."""
    
    def __init__(self, transcript: SharedMemoryMonitor) -> None:
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running: bool = False
        self.transcript = transcript

    def _transcription_loop(self) -> None:
        """Continuously listen for and transcribe speech."""
        print("Adjusting for ambient noise... please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Ready! Start speaking.")

        while self.running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=15)
                    transcription = self.recognizer.recognize_google(audio)
                    self.transcript.update_memory(transcription)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass
            except sr.RequestError as e:
                print(f"Request error from Google Speech Recognition: {e}")
                self.running = False

    def start(self) -> None:
        """Start the speech recognition thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._transcription_loop)
            self.thread.daemon = True
            self.thread.start()
            print("Transcription started in the background.")

    def stop(self) -> None:
        """Stop the speech recognition thread."""
        if self.running:
            self.running = False
            self.thread.join()
            print("Transcription stopped.")

class MonitoringSystem:
    """Monitors user behavior through various inputs and coordinates with the AI evaluator."""
    
    def __init__(self, transcript: SharedMemoryMonitor, evaluator: 'GoogleGeminiEvaluator', text_to_speech) -> None:
        self.transcript = transcript
        self.evaluator = evaluator
        self.text_to_speech = text_to_speech
        self.running: bool = False
        self.actions: List[Callable[[], None]] = [
            self.check_computer_use,
            self.check_emotion,
            self.check_transcript
        ]
        self.current_action_index: int = 0
        self.interval: int = 15

    def check_computer_use(self) -> None:
        """Capture and analyze screenshot for potential distractions."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "screenshot.png")
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            analysis = self.evaluator.analyze_screenshot(filename)
            
            if analysis:
                if analysis.is_distracted:
                    print(f"Distraction detected: {analysis.rationale}")
                    # Add the response to the text-to-speech queue
                    self.text_to_speech.add_to_queue(analysis.response)
                else: 
                    print("No distraction")
            else:
                print("Failed to analyze screenshot")
        except Exception as e:
            print(f"Error in screenshot analysis: {e}")

    def check_emotion(self) -> None:
        """Capture and analyze webcam image for emotion detection."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "photo.jpg")
        try:
            video_capture = cv2.VideoCapture(0)
            if not video_capture.isOpened():
                raise IOError("Cannot open webcam")

            ret, frame = video_capture.read()
            if ret:
                cv2.imwrite(filename, frame)
            
            video_capture.release()
        except Exception as e:
            print(f"Error in emotion detection: {e}")

    def check_transcript(self) -> None:
        """Analyze accumulated transcripts for patterns or concerns."""
        print(f"Checking Vocalizations: {self.transcript.long_term_memory}")

    def _monitor_loop(self) -> None:
        """Cycle through monitoring actions at regular intervals."""
        while self.running:
            self.actions[self.current_action_index]()
            self.current_action_index = (self.current_action_index + 1) % len(self.actions)
            time.sleep(self.interval)

    def start(self) -> None:
        """Start the monitoring system."""
        if not self.running:
            sleep(3)
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            print("Started monitoring behaviour.")

    def stop(self) -> None:
        """Stop the monitoring system."""
        if self.running:
            self.running = False
            self.thread.join()

@dataclass
class DistractionAnalysis:
    """Structured response for distraction analysis."""
    is_distracted: bool
    rationale: str
    response: str

class GoogleGeminiEvaluator:
    """Handles interactions with Google's Gemini API for content analysis."""
    
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        gemini.configure(api_key=api_key)
        self.model = gemini.GenerativeModel('gemini-1.5-flash')

    def analyze_screenshot(self, screenshot_path: str) -> Optional[DistractionAnalysis]:
        """Analyze a screenshot using Gemini vision capabilities."""
        try:
            with open(screenshot_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

            structured_prompt = """
            Analyze this screenshot and provide a structured response in the following JSON format:
            {
                "is_distracted": boolean indicating if non-work activities are present,
                "rationale": detailed explanation of why this assessment was made,
                "response": encouraging and concise first-person message to help user stay focused
            }

            Focus on identifying:
            - Social media usage
            - Entertainment websites
            - Video streaming
            - Gaming applications
            - Other non-work applications

            Your response must be valid JSON with these exact keys and appropriate value types.
            The 'response' should be written in first person, as if speaking directly to the user.
            """

            contents = [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    },
                    {"text": structured_prompt}
                ]
            }]

            response = self.model.generate_content(contents)
            
            # Extract the JSON response
            try:
                # Find JSON within the response using regex
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    analysis_dict = json.loads(json_str)
                    
                    return DistractionAnalysis(
                        is_distracted=analysis_dict['is_distracted'],
                        rationale=analysis_dict['rationale'],
                        response=analysis_dict['response']
                    )
                else:
                    print("No valid JSON found in response")
                    return None
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                return None

        except FileNotFoundError:
            print("Error: Image not found.")
        except Exception as e:
            print(f"Error in Gemini analysis: {e}")
        
        return None

def main() -> None:
    """Initialize and run the Study Buddy application."""
    try:
        # Initialize components
        text_to_speech = TextToSpeech()
        text_to_speech.start()

        evaluator = GoogleGeminiEvaluator("AIzaSyB2haGEeWLiv1cDWMMw_MpBFFU0ThTcNAo")

        # Initial greeting
        text_to_speech.add_to_queue("Hey there! I'm Study Buddy and I'm here to help you stay on track and support you in your work... Let's make today productive and stress-free!")
        text_to_speech.add_to_queue("How would you like to start?")

        # Start monitoring systems
        transcript = SharedMemoryMonitor()
        transcript.start()

        speech_to_text = SpeechToText(transcript)
        speech_to_text.start()

        monitoring_system = MonitoringSystem(transcript, evaluator, text_to_speech)
        monitoring_system.start()

        # Keep main thread alive
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting program...")
        text_to_speech.add_to_queue("Good bye!")
        
        # Cleanup
        text_to_speech.stop()
        speech_to_text.stop()
        transcript.stop()
        monitoring_system.stop()

if __name__ == "__main__":
    main()
