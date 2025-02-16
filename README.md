# Study Buddy: AI-Powered Focus and Support Assistant

Study Buddy is an innovative AI assistant developed during the MEXA AI/Mental Health Hackathon that aims to support users in maintaining focus and emotional well-being during work or study sessions. The project combines real-time monitoring with empathetic AI interactions to help users stay aligned with their goals while providing emotional support.

## Project Goals

- **Task Monitoring**: Continuously monitors computer usage to detect potential distractions and gently guide users back to their intended tasks.
- **Emotional Support**: Uses voice interaction and emotion detection to provide timely, empathetic support when users face challenges.
- **Value-Aligned Action**: Helps users persist in activities aligned with their personal values and goals, offering encouragement and practical suggestions.
- **Adaptive Assistance**: Learns from user interactions to provide increasingly personalized and effective support over time.

## Features

- Real-time speech recognition for natural interaction
- Screen activity monitoring for distraction detection
- Text-to-speech feedback for gentle interventions
- Webcam-based emotion detection capabilities
- Memory system for context-aware responses

## Technical Overview

The project is organized into several key components:

- `audio.py`: Handles text-to-speech conversion and audio playback
- `speech.py`: Manages continuous speech recognition
- `memory.py`: Implements the shared memory system for context tracking
- `monitoring.py`: Coordinates system monitoring and user interaction
- `evaluator.py`: Integrates with Google's Gemini AI for content analysis
- `main.py`: Orchestrates all components and manages the application lifecycle

## Getting Started

1. Install the required dependencies:
   ```bash
   pip install pygame gtts SpeechRecognition pyautogui opencv-python pillow google-generativeai
   ```

2. Set up your Google Gemini API key in `main.py`

3. Run the application:
   ```bash
   python -m src.main
   ```

## Development Status

The project represents an initial exploration into AI-assisted focus and emotional support, developed during an intensive week at the MEXA AI/Mental Health Hackathon, with core functionality implemented and ready for further refinement.

## Future Directions

- Enhanced emotion detection algorithms
- More sophisticated distraction analysis
- Expanded personalization capabilities
- Improved context awareness
- Integration with productivity tools
- Privacy-focused data handling

## Contributing

We welcome contributions! Please feel free to submit pull requests or open issues for discussion.

## License

This project is open source and available under the MIT License.