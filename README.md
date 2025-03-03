# Hinglish Cold Call Agent

A voice-based conversational AI agent that conducts cold calls in Hinglish (a mix of Hindi and English) for various business scenarios using Google's Gemini AI.

## Overview

This project creates an interactive voice assistant that can conduct realistic cold calls in Hinglish for three different business scenarios:
- **Demo Scheduling**: Sales representative pitching an ERP software product
- **Candidate Interviewing**: HR representative conducting initial job screening
- **Payment Follow-up**: Accounts department representative requesting overdue payment

The agent uses speech recognition to understand voice input, processes it through Google's Gemini AI model to generate contextually appropriate responses, and delivers them using text-to-speech.

## Features

- 🎙️ **Voice Recognition**: Captures and transcribes user speech
- 🤖 **AI-Powered Responses**: Generates contextually relevant responses using Gemini 1.5 Pro
- 🗣️ **Text-to-Speech**: Converts AI responses to natural-sounding voice output
- 💬 **Bilingual Support**: Handles Hinglish conversations (Hindi-English mix)
- 🧠 **Conversation Memory**: Maintains context throughout the interaction
- 📝 **Scenario Templates**: Pre-configured prompts for different business use cases

## Requirements

- Python 3.7+
- Google API key for Gemini AI
- Internet connection for speech API and Gemini services

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hinglish-cold-call-agent.git
cd hinglish-cold-call-agent
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/)
   - Replace `GEMINI_API_KEY` in the code with your actual key

## Usage

Run the main script:
```bash
python cold_call_agent.py
```

Follow the on-screen instructions to select a scenario. The agent will:
1. Greet you with an introduction specific to the chosen scenario
2. Listen for your voice input
3. Respond appropriately in Hinglish
4. Continue the conversation until you say "bye", "goodbye", or "end call"

## Project Structure

```
hinglish-cold-call-agent/
├── cold_call_agent.py      # Main application file
├── requirements.txt        # Required Python packages
└── README.md               # Project documentation
```

## How It Works

The application has three main components:

1. **SpeechHandler**: Manages voice input and output using speech recognition and text-to-speech services
2. **ConversationMemory**: Maintains the conversation history and context
3. **GeminiAgent**: Processes the conversation using structured prompts and the Gemini AI model

Each conversation follows a three-phase structure:
- **Greeting**: Introduces the agent and purpose of the call
- **Conversation**: Handles the main dialogue
- **Farewell**: Concludes the call with a summary and next steps

## Scenarios

### Demo Scheduling
Simulates a sales representative calling to schedule a product demo for an ERP system, highlighting features relevant to the customer's interests.

### Candidate Interviewing
Simulates an HR representative conducting an initial screening interview for a software engineering position, assessing candidate qualifications.

### Payment Follow-up
Simulates an accounts department representative following up on an overdue invoice, aiming to secure a payment commitment.

## Dependencies

- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/): For voice recognition
- [gTTS](https://pypi.org/project/gTTS/): For text-to-speech conversion
- [pygame](https://pypi.org/project/pygame/): For audio playback
- [Google Generative AI](https://pypi.org/project/google-generativeai/): For AI response generation

## Future Improvements

- Add support for more languages and regional accents
- Implement more business scenarios
- Enhance conversation memory with long-term retention
- Add sentiment analysis to adapt tone based on customer mood
- Implement call recording and analytics

## License

[MIT License](LICENSE)

## Acknowledgments

- Google for providing the Gemini AI API
- Open source speech recognition and text-to-speech libraries

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
