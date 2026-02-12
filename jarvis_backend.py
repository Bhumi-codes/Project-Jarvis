
import asyncio
import json
import websockets
import logging
from datetime import datetime
import threading
import pyttsx3
import speech_recognition as sr
import webbrowser
import os
import pywhatkit as kit
from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class JarvisBackend:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        # self.microphone = sr.Microphone()
        # Set a more patient pause threshold
        self.recognizer.pause_threshold = 2.0

        # Initialize text-to-speech
        
        # Store connected clients
        self.connected_clients = set()

        # Initialize the client to use OpenRouter
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENAI_API_KEY"),
        )


        logger.info("Jarvis Backend initialized successfully!")

    async def register_client(self, websocket):
        self.connected_clients.add(websocket)
        await self.send_phase_update(websocket, 'initializing', 'Connecting to Jarvis backend...')
        await asyncio.sleep(1)
        await self.send_phase_update(websocket, 'ready', 'Connected to Jarvis backend!')
        await self.send_message(websocket, {
            'type': 'jarvis_message',
            'content': 'Hello! I\'m now connected and ready to assist.'
        })
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

    async def unregister_client(self, websocket):
        self.connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")

    async def send_message(self, websocket, data):
        try:
            await websocket.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def send_phase_update(self, websocket, phase, message):
        await self.send_message(websocket, {
            'type': 'phase_update',
            'phase': phase,
            'message': message
        })

    async def speak(self, text):
        """Converts text to speech in a background thread using an isolated engine to prevent deadlocks."""
        if not text:
            return

        loop = asyncio.get_event_loop()

        def speak_in_thread():
            """This function runs in a separate thread."""
            logger.info("TTS background thread started.")
            try:
                # Create a new, isolated TTS engine for this thread only
                engine = pyttsx3.init()
                engine.setProperty('rate', 180)
                engine.setProperty('volume', 0.8)
                
                # Set the desired female voice on the new engine
                voices = engine.getProperty('voices')
                if len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)

                engine.say(text)
                engine.runAndWait()
                logger.info("TTS runAndWait() completed.")
            except Exception as e:
                logger.error(f"Error during TTS playback in thread: {e}")

        logger.info(f"Attempting to speak: '{text}'")
        await loop.run_in_executor(None, speak_in_thread)
        logger.info("TTS thread has finished execution.")


    async def listen_for_audio(self, websocket):
        """Listen for audio input and return the recognized text."""
        await self.send_phase_update(websocket, 'listening', 'Listening...')
        try:
            def listen_sync():
                logger.info("Creating microphone instance...")
                with sr.Microphone() as source:
                    logger.info("Calibrating for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    logger.info("Listening for command...")
                    audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=20)
                    logger.info("Finished listening.")
                return audio_data

            # def listen_sync():
            #     with self.microphone as source:
            #         logger.info("Calibrating for ambient noise...")
            #         self.recognizer.adjust_for_ambient_noise(source, duration=1)
            #         logger.info("Listening for command...")
            #         audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=20)
            #         logger.info("Finished listening.")
            #     return audio_data

            def recognize_sync(audio_data):
                logger.info("Sending audio for recognition...")
                return self.recognizer.recognize_google(audio_data)

            loop = asyncio.get_event_loop()
            audio = await loop.run_in_executor(None, listen_sync)
            text = await loop.run_in_executor(None, recognize_sync, audio)
            
            logger.info(f"DEBUG: Recognized text from audio -> '{text}'")
            return text.lower().strip()

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            logger.warning("No speech detected or understood.")
            await self.send_phase_update(websocket, 'ready', 'Ready to help')
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred in audio listening: {e}")
            await self.send_phase_update(websocket, 'ready', 'Ready to help')
            return None

    async def process_command(self, websocket, command_text, is_voice=False):
        """Processes a command, gets a response, and speaks it."""
        await self.send_phase_update(websocket, 'processing', 'Thinking...')
        if is_voice:
            await self.send_message(websocket, {'type': 'voice_user_message', 'content': command_text})

        response = await self.handle_command(command_text)

        await self.send_message(websocket, {'type': 'jarvis_response', 'content': response})
        await self.send_phase_update(websocket, 'speaking', 'Speaking...')
        await self.speak(response)
        await self.send_phase_update(websocket, 'ready', 'Ready to help')

  
    async def get_openai_response(self, query, system_prompt=None):
        """Get response from OpenRouter, with a dynamic system prompt and enhanced error handling."""
        logger.info(f"Sending query to OpenRouter: '{query}'")
        
        # Use the provided system_prompt, or a default one if none is given.
        if system_prompt is None:
            system_prompt = "You are Jarvis, a helpful and concise AI assistant."

        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=150,
                timeout=20.0,
            )
            return response.choices[0].message.content.strip()

        except self.openai_client.APIConnectionError as e:
            logger.error(f"OpenRouter Connection Error: {e.__cause__}")
            return "I'm having trouble connecting to the AI network. Please check your connection."
        except self.openai_client.RateLimitError as e:
            logger.error(f"OpenRouter Rate Limit Exceeded: {e.status_code} - {e.response}")
            return "The AI network is currently busy. Please try again in a moment."
        except self.openai_client.APIStatusError as e:
            logger.error(f"OpenRouter API Status Error: {e.status_code} - {e.response}")
            return "The AI network reported an error. Please try again."
        except Exception as e:
            logger.error(f"An unexpected error occurred with the AI call: {e}")
            return "I'm having trouble connecting to my advanced knowledge base right now."

    
    
    async def handle_command(self, command):
        """Handle commands with a flexible approach to AI prompts."""
        command_lower = command.lower().strip()
        system_prompt = None  # Start with no special instructions

        # --- 1. Intent Detection for AI Behavior ---
        # If the user mentions "hindi," we prepare a special instruction for the AI.
        if "in hindi" in command_lower:
            system_prompt = "You are a helpful female AI assistant named Jarvis. You MUST respond in Hindi."
        
        # --- 2. Simple, Keyword-Based Rules (No AI needed) ---
        # These are checked first for instant responses.
        if "open google" in command_lower:
            webbrowser.open("https://www.google.com")
            return "Opening Google for you."

        elif "open youtube" in command_lower:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube for you."
        
        elif "open instagram" in command_lower:
            webbrowser.open("https://www.instagram.com")
            return "Opening Instagram for you."
        
        elif "open linkedin" in command_lower:
            webbrowser.open("https://www.linkedin.com")
            return "Opening Linkedin for you."
            
        elif command_lower.startswith("play "):
            song = command.replace("play ", "", 1).strip()
            try:
                kit.playonyt(song)
                return f"Playing {song} on YouTube."
            except Exception as e:
                logger.error(f"Error playing song: {e}")
                return f"Sorry, I had trouble playing {song} on YouTube."

        elif "time" in command_lower:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}."
        
        elif "date" in command_lower or "today" in command_lower:
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
            
        elif "news" in command_lower and not "in hindi" in command_lower:
             webbrowser.open("https://news.google.com")
             return "Opening Google News for the latest updates."

        # --- 3. Fallback to AI ---
        # If no simple rule was triggered, it's a question for the AI.
        # We pass the user's original command and any special system_prompt we detected.
        else:
            logger.info(f"No specific rule for '{command}'. Forwarding to AI with prompt: {system_prompt}")
            return await self.get_openai_response(command, system_prompt=system_prompt)

    async def handle_voice_request(self, websocket):
        """A simple handler for a single voice command."""
        audio_text = await self.listen_for_audio(websocket)
        if audio_text:
            await self.process_command(websocket, audio_text, is_voice=True)

    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections."""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')

                    if message_type == 'text_command':
                        command = data.get('message', '').strip()
                        if command:
                            await self.process_command(websocket, command)
                    elif message_type == 'voice_request':
                        await self.handle_voice_request(websocket)
                    elif message_type == 'speak_request':
                        text = data.get('text', '')
                        if text:
                            await self.speak(text)
                    elif message_type == 'ping':
                        await self.send_message(websocket, {'type': 'pong'})
                    else:
                        logger.warning(f"Unknown message type: {message_type}")

                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed normally")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.unregister_client(websocket)

# Main execution
async def main():
    jarvis = JarvisBackend()
    print("\n" + "="*60)
    print("🤖 JARVIS BACKEND SERVER (STABLE VERSION)")
    print("="*60)
    print("📡 WebSocket server starting on localhost:8765")
    print("🌐 Frontend should connect to: ws://localhost:8765")
    print("🎤 Voice recognition: ENABLED")
    print("🔊 Text-to-speech: ENABLED")
    print("🎵 Music playback: ENABLED")
    print("🌍 Website controls: ENABLED")
    print("🧠 AI responses: ENABLED (OpenRouter)")
    print("✨ Jarvis is ready to assist!")
    print("="*60)
    print("\n💡 Instructions:")
    print("1. Keep this terminal open")
    print("2. Open your HTML file in a browser")
    print("3. Use voice commands or type messages")
    print("4. Press Ctrl+C to stop the server")
    print("\n📝 Logs:")
    
    try:
        async with websockets.serve(jarvis.handle_websocket, "localhost", 8765):
            logger.info("Server started successfully")
            await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n👋 Shutting down Jarvis backend server...")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    # Install required packages reminder
    try:
        import pywhatkit
        import pyttsx3
        import speech_recognition
        import websockets
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\n📦 Please install required packages:")
        print("pip install websockets pywhatkit pyttsx3 SpeechRecognition pyaudio")
        exit(1)

    # Run the server
    asyncio.run(main())


