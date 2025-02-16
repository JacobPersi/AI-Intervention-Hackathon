import threading
import speech_recognition as sr
from .memory import SharedMemoryMonitor

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