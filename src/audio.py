import pygame
import os
import time
import queue
import threading
from gtts import gTTS

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