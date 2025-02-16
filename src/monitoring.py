import threading
import time
import os
import pyautogui
import cv2
from typing import List, Callable
from .memory import SharedMemoryMonitor
from .evaluator import GoogleGeminiEvaluator
from .audio import TextToSpeech

class MonitoringSystem:
    """Monitors user behavior through various inputs and coordinates with the AI evaluator."""
    
    def __init__(self, transcript: SharedMemoryMonitor, evaluator: GoogleGeminiEvaluator, text_to_speech: TextToSpeech) -> None:
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
            time.sleep(3)
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