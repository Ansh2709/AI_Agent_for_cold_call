import os
import re
import time
import json
import uuid
import logging
from typing import Dict, List, Any

# Speech recognition and text-to-speech
import speech_recognition as sr
from gtts import gTTS
import pygame

# Gemini AI
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = 'AIzaSyBMnolhA145-dLMXZkE8PQVXNxwLNDxAXY'  # Replace with your actual key
genai.configure(api_key=GEMINI_API_KEY)


class SpeechHandler:
    """Handles speech recognition and text-to-speech functionality."""
    
    def __init__(self, language: str = "en-IN", tld: str = "co.in"):
        """Initialize speech handler.
        
        Args:
            language: Language code for speech recognition and TTS
            tld: Top-level domain for Google TTS service
        """
        self.language = language
        self.tld = tld
        self.recognizer = sr.Recognizer()
        
        # Configure speech recognition settings
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        logger.info("Speech handler initialized")
    
    def recognize_speech(self) -> str:
        """Capture voice input and convert to text.
        
        Returns:
            Transcribed text from speech input
        """
        with sr.Microphone() as source:
            logger.info("Listening...")
            print("Listening...")
            
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen for audio input
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                logger.info("Processing speech...")
                
                # Convert speech to text
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"User: {text}")
                print(f"User: {text}")
                
                return text.lower()
                
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                print("Sorry, I didn't catch that.")
            except sr.RequestError as e:
                logger.error(f"Speech service error: {e}")
                print("Speech service error. Please try again.")
            except sr.WaitTimeoutError:
                logger.warning("No speech detected within timeout period")
                print("I didn't hear anything. Please try again.")
                
        return ""
    
    def speak(self, text: str, slow: bool = False) -> None:
        """Convert text to speech and play it.
        
        Args:
            text: Text to be converted to speech
            slow: Whether to speak slowly
        """
        # Clean text for TTS
        cleaned_text = re.sub(r'[^\w\s.,!?-]', '', text)
        logger.info(f"AI: {cleaned_text}")
        print(f"AI: {cleaned_text}")
        
        # Generate TTS audio
        filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
        try:
            tts = gTTS(text=cleaned_text, lang=self.language.split('-')[0], 
                      slow=slow, tld=self.tld)
            tts.save(filename)
            
            # Play audio
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"Error generating speech: {e}")
        finally:
            # Cleanup
            pygame.mixer.music.unload()
            if os.path.exists(filename):
                os.remove(filename)


class ConversationMemory:
    """Manages conversation state and history."""
    
    def __init__(self):
        """Initialize conversation memory."""
        self.context = {
            "profile": {},
            "knowledge": {}
        }
        self.messages = []
        
    def add_user_message(self, message: str) -> None:
        """Add user message to conversation history.
        
        Args:
            message: User's message
        """
        self.messages.append({"role": "user", "content": message})
        
    def add_agent_message(self, message: str) -> None:
        """Add agent message to conversation history.
        
        Args:
            message: Agent's message
        """
        self.messages.append({"role": "agent", "content": message})
        
    def get_conversation_history(self) -> str:
        """Get formatted conversation history.
        
        Returns:
            Formatted conversation history string
        """
        history = ""
        for msg in self.messages:
            prefix = "Customer" if msg["role"] == "user" else "AI"
            history += f"{prefix}: {msg['content']}\n"
        return history
    
    def set_context(self, key: str, data: Dict[str, Any]) -> None:
        """Set context information.
        
        Args:
            key: Context key
            data: Context data dictionary
        """
        self.context[key] = data
        
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context information.
        
        Args:
            key: Context key
            default: Default value if key doesn't exist
            
        Returns:
            Context data for the key
        """
        return self.context.get(key, default)


class GeminiAgent:
    """AI agent for conducting cold calls in Hinglish using Gemini API."""
    
    def __init__(self, scenario: str, model_name: str = "gemini-1.5-pro"):
        """Initialize the Gemini agent.
        
        Args:
            scenario: Call scenario ("demo", "interview", or "payment")
            model_name: Name of the Gemini model to use
        """
        self.scenario = scenario
        self.memory = ConversationMemory()
        self.speech_handler = SpeechHandler()
        self.running = False
        
        # Set up Gemini model
        self.model = genai.GenerativeModel(model_name)
        
        # Load scenario data
        self._load_scenario_data()
        
        logger.info(f"Gemini agent initialized for {scenario} scenario")
        
    def _load_scenario_data(self) -> None:
        """Load scenario-specific data."""
        # Demo scenario data
        if self.scenario == "demo":
            self.memory.set_context("profile", {
                "name": "Ansh Aggarwal",
                "company": "Tech Solutions Ltd",
                "role": "IT Manager",
                "interest_area": "Inventory Management and HR modules",
                "company_size": "150 employees"
            })
            
        # Interview scenario data
        elif self.scenario == "interview":
            self.memory.set_context("profile", {
                "name": "Ansh Aggarwal",
                "experience": "3 years",
                "current_role": "Junior Developer",
                "applied_for": "Software Engineer"
            })
            self.memory.set_context("knowledge", {
                "position": "Software Engineer",
                "skills": "Python, React, SQL, Cloud platforms",
                "experience_required": "2-5 years",
                "company_domain": "FinTech"
            })
            
        # Payment scenario data
        elif self.scenario == "payment":
            self.memory.set_context("profile", {
                "name": "Customer",
                "company": "Global Enterprises",
                "role": "Procurement Manager"
            })
            self.memory.set_context("knowledge", {
                "invoice_number": "INV-2024-1075",
                "due_amount": "₹4,85,000",
                "days_late": "45",
                "payment_history": "Generally good, but occasional delays"
            })
    
    def _get_prompt_template(self, phase: str) -> str:
        """Get the appropriate prompt template based on scenario and conversation phase.
        
        Args:
            phase: Conversation phase ("greeting", "conversation", or "farewell")
            
        Returns:
            Template string for the specified phase
        """
        templates = {
            "demo": {
                "greeting": """
                You are an AI assistant conducting a cold call in Hinglish (mix of Hindi and English).
                
                You're a sales representative for an ERP software company.
                Your goal is to schedule a product demo.
                
                Customer profile:
                Name: {name}
                Company: {company}
                Role: {role}
                Interest area: {interest_area}
                Company size: {company_size}
                
                Start with a friendly greeting in Hinglish.
                Introduce yourself, mention your company, and state the purpose of your call.
                Keep your response concise (2-3 sentences) and end with an open question.
                """,
                
                "conversation": """
                You are an AI assistant conducting a cold call in Hinglish (mix of Hindi and English).
                
                You're a sales representative for an ERP software company.
                Your goal is to schedule a product demo.
                Highlight benefits relevant to the customer's interests.
                Try to get a specific date and time for the demo.
                
                Customer profile:
                Name: {name}
                Company: {company}
                Role: {role}
                Interest area: {interest_area}
                Company size: {company_size}
                
                Conversation history:
                {conversation_history}
                
                Customer's most recent message: {user_input}
                
                Respond in Hinglish with a friendly, professional tone.
                Address customer concerns empathetically and move the conversation toward scheduling a demo.
                Keep your response concise (2-4 sentences).
                """,
                
                "farewell": """
                You are an AI assistant concluding a cold call in Hinglish (mix of Hindi and English).
                
                You're a sales representative for an ERP software company.
                
                Customer profile:
                Name: {name}
                Company: {company}
                
                Conversation history:
                {conversation_history}
                
                Create a polite and warm closing statement in Hinglish that:
                1. Thanks the customer for their time
                2. Summarizes any demo scheduling details
                3. Mentions that you'll send a confirmation email
                4. Ends on a positive note
                
                Keep your response concise (2-3 sentences).
                """
            },
            
            "interview": {
                "greeting": """
                You are an AI assistant conducting an interview in Hinglish (mix of Hindi and English).
                
                You're an HR representative conducting an initial screening interview.
                Your goal is to assess the candidate's fit for the position.
                
                Candidate profile:
                Name: {name}
                Experience: {experience}
                Current role: {current_role}
                Applied for: {applied_for}
                
                Position details:
                Position: {position}
                Skills required: {skills}
                Experience required: {experience_required}
                Company domain: {company_domain}
                
                Start with a friendly greeting in Hinglish.
                Introduce yourself, mention your company, and explain the interview process.
                Keep your response concise (2-3 sentences) and end with an open question about their background.
                """,
                
                "conversation": """
                You are an AI assistant conducting an interview in Hinglish (mix of Hindi and English).
                
                You're an HR representative conducting an initial screening interview.
                Your goal is to assess the candidate's fit for the position.
                Ask about relevant skills, experiences, and interest in the role.
                Evaluate communication skills and cultural fit.
                
                Candidate profile:
                Name: {name}
                Experience: {experience}
                Current role: {current_role}
                Applied for: {applied_for}
                
                Position details:
                Position: {position}
                Skills required: {skills}
                Experience required: {experience_required}
                Company domain: {company_domain}
                
                Interview history:
                {conversation_history}
                
                Candidate's most recent response: {user_input}
                
                Respond in Hinglish with a professional tone.
                Ask follow-up questions that help assess the candidate's suitability.
                Keep your response concise (2-3 sentences).
                """,
                
                "farewell": """
                You are an AI assistant concluding an interview in Hinglish (mix of Hindi and English).
                
                You're an HR representative who has just completed an initial screening interview.
                
                Candidate profile:
                Name: {name}
                Applied for: {applied_for}
                
                Interview history:
                {conversation_history}
                
                Create a polite and professional closing statement in Hinglish that:
                1. Thanks the candidate for their time
                2. Explains the next steps in the interview process
                3. Mentions when they can expect to hear back
                4. Ends on an encouraging note
                
                Keep your response concise (2-3 sentences).
                """
            },
            
            "payment": {
                "greeting": """
                You are an AI assistant conducting a payment follow-up call in Hinglish (mix of Hindi and English).
                
                You're from the accounts department following up on an overdue payment.
                Your goal is to secure a commitment for payment.
                
                Customer profile:
                Name: {name}
                Company: {company}
                Role: {role}
                
                Invoice details:
                Invoice number: {invoice_number}
                Due amount: {due_amount}
                Days late: {days_late}
                Payment history: {payment_history}
                
                Start with a polite greeting in Hinglish.
                Introduce yourself, mention your company's accounts department, and state the purpose of your call.
                Keep your response concise (2-3 sentences) and be respectful but direct about the overdue payment.
                """,
                
                "conversation": """
                You are an AI assistant conducting a payment follow-up call in Hinglish (mix of Hindi and English).
                
                You're from the accounts department following up on an overdue payment.
                Your goal is to secure a commitment for payment.
                Be polite but firm about the urgency.
                Try to get a specific date for when the payment will be made.
                
                Customer profile:
                Name: {name}
                Company: {company}
                Role: {role}
                
                Invoice details:
                Invoice number: {invoice_number}
                Due amount: {due_amount}
                Days late: {days_late}
                Payment history: {payment_history}
                
                Conversation history:
                {conversation_history}
                
                Customer's most recent message: {user_input}
                
                Respond in Hinglish with a professional tone.
                Be understanding but firm about the need for payment.
                Keep your response concise (2-3 sentences).
                """,
                
                "farewell": """
                You are an AI assistant concluding a payment follow-up call in Hinglish (mix of Hindi and English).
                
                You're from the accounts department following up on an overdue payment.
                
                Customer profile:
                Name: {name}
                Company: {company}
                
                Invoice details:
                Invoice number: {invoice_number}
                Due amount: {due_amount}
                
                Conversation history:
                {conversation_history}
                
                Create a polite and professional closing statement in Hinglish that:
                1. Thanks the customer for their time
                2. Summarizes any payment commitments made
                3. Confirms any next steps
                4. Ends on a positive note
                
                Keep your response concise (2-3 sentences).
                """
            }
        }
        
        return templates.get(self.scenario, {}).get(phase, "")
    
    def _format_prompt(self, template: str, user_input: str = "") -> str:
        """Format prompt template with context variables.
        
        Args:
            template: Prompt template string
            user_input: User's input message
            
        Returns:
            Formatted prompt string
        """
        profile = self.memory.get_context("profile", {})
        knowledge = self.memory.get_context("knowledge", {})
        
        return template.format(
            name=profile.get("name", ""),
            company=profile.get("company", ""),
            role=profile.get("role", ""),
            interest_area=profile.get("interest_area", ""),
            company_size=profile.get("company_size", ""),
            experience=profile.get("experience", ""),
            current_role=profile.get("current_role", ""),
            applied_for=profile.get("applied_for", ""),
            position=knowledge.get("position", ""),
            skills=knowledge.get("skills", ""),
            experience_required=knowledge.get("experience_required", ""),
            company_domain=knowledge.get("company_domain", ""),
            invoice_number=knowledge.get("invoice_number", ""),
            due_amount=knowledge.get("due_amount", ""),
            days_late=knowledge.get("days_late", ""),
            payment_history=knowledge.get("payment_history", ""),
            conversation_history=self.memory.get_conversation_history(),
            user_input=user_input
        )
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini API.
        
        Args:
            prompt: Formatted prompt for the model
            
        Returns:
            Generated response text
        """
        logger.info("Generating response...")
        try:
            response = self.model.generate_content(prompt)
            result = response.text if hasattr(response, 'text') else str(response)
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "Sorry, I'm having trouble generating a response. Let me try again."
    
    def run_greeting_chain(self) -> str:
        """Generate greeting message to start the conversation.
        
        Returns:
            Greeting message
        """
        template = self._get_prompt_template("greeting")
        prompt = self._format_prompt(template)
        
        result = self.generate_response(prompt)
        
        # Add to conversation history
        self.memory.add_agent_message(result)
        return result
    
    def run_conversation_chain(self, user_input: str) -> str:
        """Generate response to user input during the conversation.
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response
        """
        # Add user input to memory
        self.memory.add_user_message(user_input)
        
        template = self._get_prompt_template("conversation")
        prompt = self._format_prompt(template, user_input)
        
        result = self.generate_response(prompt)
        
        # Add response to memory
        self.memory.add_agent_message(result)
        
        return result
    
    def run_farewell_chain(self) -> str:
        """Generate farewell message to end the conversation.
        
        Returns:
            Farewell message
        """
        template = self._get_prompt_template("farewell")
        prompt = self._format_prompt(template)
        
        result = self.generate_response(prompt)
        
        # Add to conversation history
        self.memory.add_agent_message(result)
        return result
    
    def start_call(self) -> None:
        """Start the cold call conversation."""
        self.running = True
        logger.info(f"Starting cold call for {self.scenario} scenario")
        
        try:
            # Greeting
            greeting = self.run_greeting_chain()
            self.speech_handler.speak(greeting)
            
            # Main conversation loop
            while self.running:
                user_input = self.speech_handler.recognize_speech()
                
                # Check for exit commands
                if user_input.lower() in ["bye", "goodbye", "end call", "quit", "exit", "bye-bye"]:
                    break
                
                # Process non-empty input
                if user_input:
                    response = self.run_conversation_chain(user_input)
                    self.speech_handler.speak(response)
            
            # Farewell
            farewell = self.run_farewell_chain()
            self.speech_handler.speak(farewell)
            
        except Exception as e:
            logger.error(f"Error during call: {e}")
            print(f"An error occurred: {e}")
        finally:
            self.end_call()
    
    def end_call(self) -> None:
        """End the cold call conversation."""
        self.running = False
        logger.info("Call ended")
        print("Call ended. Thank you!")


def main():
    """Main function to run the cold call agent."""
    print("Hinglish Cold Call Agent")
    print("=======================")
    print("Available scenarios:")
    print("1. Demo Scheduling (ERP System)")
    print("2. Candidate Interviewing")
    print("3. Payment/Order Follow-up")
    
    choice = input("Select a scenario (1-3): ").strip()
    
    scenario_map = {
        "1": "demo",
        "2": "interview",
        "3": "payment"
    }
    
    scenario = scenario_map.get(choice)
    
    if not scenario:
        print("Invalid choice. Please select 1, 2, or 3.")
        return
    
    print(f"\nInitializing {scenario.title()} scenario...")
    print("Say 'bye', 'goodbye', or 'end call' to finish the conversation.\n")
    
    agent = GeminiAgent(scenario)
    agent.start_call()


if __name__ == "__main__":
    main()
