import time
from .audio import TextToSpeech
from .evaluator import GoogleGeminiEvaluator
from .memory import SharedMemoryMonitor
from .speech import SpeechToText
from .monitoring import MonitoringSystem

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