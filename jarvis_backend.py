# import asyncio
# import json
# import websockets
# import logging
# from datetime import datetime
# import threading
# import pyttsx3
# import speech_recognition as sr
# import requests
# import webbrowser
# import os
# import pywhatkit as kit
# from openai import OpenAI

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class JarvisBackend:
#     def __init__(self):
#         # Initialize speech recognition
#         self.recognizer = sr.Recognizer()
#         self.microphone = sr.Microphone()
#         self.recognizer.pause_threshold = 2.0 

#         # Initialize text-to-speech
#         self.tts_engine = pyttsx3.init()
#         self.tts_engine.setProperty('rate', 180)
#         self.tts_engine.setProperty('volume', 0.8)

#         # Set female voice if available
#         voices = self.tts_engine.getProperty('voices')
#         if len(voices) > 1:
#             # voices[0] is typically male, voices[1] is typically female on Windows
#             self.tts_engine.setProperty('voice', voices[1].id) 
#         # Store connected clients
#         self.connected_clients = set()

#         # Initialize the client to use OpenRouter
#         self.openai_client = OpenAI(
#             base_url="https://openrouter.ai/api/v1",
#             api_key="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",
#         )


#         # Current states
#         self.is_listening = False
#         self.is_processing = False
#         self.is_speaking = False

#         logger.info("Jarvis Backend initialized successfully!")

#     async def register_client(self, websocket):
#         """Register a new client connection"""
#         self.connected_clients.add(websocket)
#         await self.send_phase_update(websocket, 'initializing', 'Connecting to Jarvis backend...')

#         # Simulate initialization
#         await asyncio.sleep(1)
#         await self.send_phase_update(websocket, 'ready', 'Connected to Jarvis backend!')

#         # Send welcome message
#         await self.send_message(websocket, {
#             'type': 'jarvis_message',
#             'content': 'Hello! I\'m now connected to the Python backend. You can use voice commands and all advanced features are now available!'
#         })

#         logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

#     async def unregister_client(self, websocket):
#         """Remove client connection"""
#         self.connected_clients.discard(websocket)
#         logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")

#     async def send_message(self, websocket, data):
#         """Send data to specific client"""
#         try:
#             await websocket.send(json.dumps(data))
#         except websockets.exceptions.ConnectionClosed:
#             await self.unregister_client(websocket)
#         except Exception as e:
#             logger.error(f"Error sending message: {e}")

#     async def send_phase_update(self, websocket, phase, message):
#         """Send phase update to frontend"""
#         await self.send_message(websocket, {
#             'type': 'phase_update',
#             'phase': phase,
#             'message': message
#         })

#     async def broadcast_to_all(self, data):
#         """Send data to all connected clients"""
#         if self.connected_clients:
#             disconnected = []
#             for websocket in self.connected_clients:
#                 try:
#                     await websocket.send(json.dumps(data))
#                 except websockets.exceptions.ConnectionClosed:
#                     disconnected.append(websocket)
#                 except Exception as e:
#                     logger.error(f"Error broadcasting: {e}")
#                     disconnected.append(websocket)

#             # Remove disconnected clients
#             for websocket in disconnected:
#                 await self.unregister_client(websocket)

#     def speak_sync(self, text):
#         """Convert text to speech synchronously"""
#         try:
#             self.tts_engine.say(text)
#             self.tts_engine.runAndWait()
#         except Exception as e:
#             logger.error(f"TTS Error: {e}")

#     # async def speak(self, text):
#     #     """A simplified function that only handles text-to-speech conversion."""
#     #     if not text:
#     #         logger.warning("Speak function called with empty text.")
#     #         return

#     #     loop = asyncio.get_event_loop()

#     #     def speak_sync_wrapper():
#     #         logger.info("TTS background thread started.")
#     #         try:
#     #             self.tts_engine.say(text)
#     #             self.tts_engine.runAndWait()
#     #             logger.info("TTS runAndWait() completed.")
#     #         except Exception as e:
#     #             logger.error(f"Error within TTS thread: {e}")

#     #     logger.info(f"Attempting to speak: '{text}'")
#     #     await loop.run_in_executor(None, speak_sync_wrapper)
#     #     logger.info("TTS thread has finished execution.")
#     async def speak(self, websocket, text):
#         """Convert text to speech and update phases"""
#         if not text:
#             logger.warning("Speak function called with empty text.")
#             return

#         self.is_speaking = True
#         await self.send_phase_update(websocket, 'speaking', 'Speaking response...')
#         logger.info(f"Attempting to speak: '{text}'")

#         loop = asyncio.get_event_loop()

#         def speak_sync_wrapper():
#             logger.info("TTS background thread started.")
#             try:
#                 # Use the engine configured in __init__
#                 self.tts_engine.say(text)
#                 self.tts_engine.runAndWait()
#                 logger.info("TTS runAndWait() completed.")
#             except Exception as e:
#                 logger.error(f"Error within TTS thread: {e}")

#         try:
#             await loop.run_in_executor(None, speak_sync_wrapper)
#             logger.info("TTS thread has finished execution.")
#         except Exception as e:
#             logger.error(f"Error running TTS in executor: {e}")
#         finally:
#             # Crucially, resets its own state flag when done
#             self.is_speaking = False
#             await self.send_phase_update(websocket, 'ready', 'Ready to help')
#             logger.info("Speaking process finished, phase set back to ready.")



#     async def listen_for_audio(self, websocket):
#         """Listen for audio input"""
#         self.is_listening = True
#         await self.send_phase_update(websocket, 'listening', 'Listening...')

#         try:
#             # Define the synchronous function for listening
#             def listen_sync():
#                 with self.microphone as source:
#                     logger.info("Calibrating for ambient noise...")
#                     self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
#                     logger.info(f"Ambient noise energy threshold set to: {self.recognizer.energy_threshold:.2f}")

#                     logger.info("Listening for command...")
#                     audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
#                     logger.info("Finished listening.")
#                 return audio_data

#             # Define the synchronous function for recognition
#             def recognize_sync(audio_data):
#                 logger.info("Sending audio for recognition...")
#                 recognized_text = self.recognizer.recognize_google(audio_data)
#                 return recognized_text

#             # Get the current event loop
#             loop = asyncio.get_event_loop()

#             # Step 1: Run the listening function in a separate thread to get the audio data
#             audio = await loop.run_in_executor(None, listen_sync)
            
#             # Step 2: Run the recognition function in a separate thread to get the text
#             text = await loop.run_in_executor(None, recognize_sync, audio)

#             # Step 3: Log the final result for debugging
#             logger.info(f"DEBUG: Recognized text from audio -> '{text}'")

#             self.is_listening = False
#             return text.lower().strip()

#         except sr.WaitTimeoutError:
#             self.is_listening = False
#             logger.warning("Listening timed out. No speech detected.")
#             await self.send_phase_update(websocket, 'ready', 'Ready to help')
#             return None
#         except sr.UnknownValueError:
#             self.is_listening = False
#             logger.warning("Google Speech Recognition could not understand audio.")
#             await self.send_phase_update(websocket, 'ready', 'Ready to help')
#             return None
#         except sr.RequestError as e:
#             self.is_listening = False
#             logger.error(f"Speech recognition service error: {e}")
#             await self.send_phase_update(websocket, 'ready', 'Ready to help')
#             return None
#         except Exception as e:
#             self.is_listening = False
#             logger.error(f"An unexpected error occurred in audio listening: {e}")
#             await self.send_phase_update(websocket, 'ready', 'Ready to help')
#             return None



#     # async def process_command(self, websocket, command_text, is_voice=False):
#     #     """Process command and return response"""
#     #     self.is_processing = True
#     #     await self.send_phase_update(websocket, 'processing', 'Processing your command...')

#     #     try:
#     #         # If it's a voice command, send it as user message to frontend
#     #         if is_voice:
#     #             await self.send_message(websocket, {
#     #                 'type': 'voice_user_message',
#     #                 'content': command_text
#     #             })

#     #         response = await self.handle_command(command_text)

#     #         # Send response back to frontend
#     #         await self.send_message(websocket, {
#     #             'type': 'jarvis_response',
#     #             'content': response,
#     #             'original_command': command_text
#     #         })

#     #         # Speak the response
#     #         await self.speak(websocket, response)

#     #     except Exception as e:
#     #         logger.error(f"Error processing command: {e}")
#     #         error_response = "I'm sorry, I encountered an error processing your request."
#     #         await self.send_message(websocket, {
#     #             'type': 'jarvis_response',
#     #             'content': error_response
#     #         })
#     #         await self.speak(websocket, error_response)

#     #     finally:
#     #         self.is_processing = False

#     # async def process_command(self, websocket, command_text, is_voice=False):
#     #     """
#     #     Process command, get response, and speak it, managing all states.
#     #     This function now controls the entire processing and speaking lifecycle.
#     #     """
#     #     try:
#     #         # === START of the entire busy period ===
#     #         self.is_processing = True
#     #         await self.send_phase_update(websocket, 'processing', 'Thinking...')
#     #         logger.info("State set: is_processing=True")

#     #         if is_voice:
#     #             await self.send_message(websocket, {
#     #                 'type': 'voice_user_message',
#     #                 'content': command_text
#     #             })

#     #         # Get the response from the rule-based or AI handler
#     #         response = await self.handle_command(command_text)

#     #         # Now, transition state from "processing" to "speaking"
#     #         self.is_processing = False
#     #         self.is_speaking = True
#     #         logger.info("State set: is_processing=False, is_speaking=True")
            
#     #         # Send the text response to the frontend first
#     #         await self.send_message(websocket, {
#     #             'type': 'jarvis_response',
#     #             'content': response,
#     #             'original_command': command_text
#     #         })
            
#     #         await self.send_phase_update(websocket, 'speaking', 'Speaking...')

#     #         # Speak the response using our simplified speak function
#     #         await self.speak(response)

#     #     except Exception as e:
#     #         logger.error(f"Error processing command: {e}")
#     #         error_response = "I'm sorry, I encountered an error. Please try again."
#     #         # Try to send and speak an error message
#     #         try:
#     #             await self.send_message(websocket, {'type': 'jarvis_response', 'content': error_response})
#     #             await self.speak(error_response)
#     #         except Exception as speak_error:
#     #             logger.error(f"Failed to even speak the error message: {speak_error}")
                
#     #     finally:
#     #         # === END of the entire busy period ===
#     #         # This block guarantees that the assistant becomes ready again,
#     #         # no matter what happened in the try block.
#     #         self.is_processing = False
#     #         self.is_speaking = False
#     #         await self.send_phase_update(websocket, 'ready', 'Ready to help')
#     #         logger.info("process_command finished. Final state: is_processing=False, is_speaking=False. Assistant is ready.")
#     async def process_command(self, websocket, command_text, is_voice=False):
#         """Process command and return response"""
#         self.is_processing = True
#         await self.send_phase_update(websocket, 'processing', 'Processing your command...')

#         try:
#             if is_voice:
#                 await self.send_message(websocket, {
#                     'type': 'voice_user_message',
#                     'content': command_text
#                 })

#             response = await self.handle_command(command_text)

#             await self.send_message(websocket, {
#                 'type': 'jarvis_response',
#                 'content': response,
#                 'original_command': command_text
#             })

#             # Speak the response
#             await self.speak(websocket, response)

#         except Exception as e:
#             logger.error(f"Error processing command: {e}")
#             error_response = "I'm sorry, I encountered an error processing your request."
#             await self.send_message(websocket, {
#                 'type': 'jarvis_response',
#                 'content': error_response
#             })
#             await self.speak(websocket, error_response)

#         finally:
#             # Resets its own state flag when done
#             self.is_processing = False



#     async def handle_command(self, command):
#             """Handle different commands - enhanced version of your existing logic"""
#             command = command.lower().strip()

#             # Website opening commands
#             if "open google" in command or "google" in command:
#                 webbrowser.open("https://www.google.com")
#                 return "Opening Google for you."

#             elif "open youtube" in command or "youtube" in command:
#                 webbrowser.open("https://www.youtube.com")
#                 return "Opening YouTube for you."

#             elif "open instagram" in command or "instagram" in command:
#                 webbrowser.open("https://www.instagram.com")
#                 return "Opening Instagram for you."

#             elif "open linkedin" in command or "linkedin" in command:
#                 webbrowser.open("https://www.linkedin.com")
#                 return "Opening LinkedIn for you."

#             # Music commands
#             elif command.startswith("play "):
#                 song = command.replace("play ", "").strip()
#                 try:
#                     # Use pywhatkit to play on YouTube
#                     kit.playonyt(song)
#                     return f"Playing {song} on YouTube."
#                 except Exception as e:
#                     logger.error(f"Error playing song: {e}")
#                     # Fallback to search
#                     search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
#                     webbrowser.open(search_url)
#                     return f"Searching for {song} on YouTube."

#             elif "music" in command:
#                 song_match = None
#                 if "play" in command:
#                     # Extract song name after "play"
#                     parts = command.split("play")
#                     if len(parts) > 1:
#                         song_match = parts[1].strip()

#                 if song_match:
#                     try:
#                         kit.playonyt(song_match)
#                         return f"Playing {song_match} on YouTube."
#                     except:
#                         webbrowser.open(f"https://www.youtube.com/results?search_query={song_match.replace(' ', '+')}")
#                         return f"Searching for {song_match} on YouTube."
#                 else:
#                     webbrowser.open("https://www.youtube.com/results?search_query=music")
#                     return "Opening YouTube music for you."

#             # News command
#             elif "news" in command:
#                 webbrowser.open("https://news.google.com")
#                 return "Opening Google News for the latest updates."

#             # Time query
#             elif "time" in command:
#                 current_time = datetime.now().strftime("%I:%M %p")
#                 return f"The current time is {current_time}."

#             # Date query
#             elif "date" in command or "today" in command:
#                 current_date = datetime.now().strftime("%A, %B %d, %Y")
#                 return f"Today is {current_date}."

#             # Weather query
#             elif "weather" in command:
#                 webbrowser.open("https://weather.com")
#                 return "I don't have access to real-time weather data, but I've opened Weather.com for you."

#             # Greetings
#             elif any(word in command for word in ["hello", "hi", "hey", "jarvis"]):
#                 return "Hello! How can I assist you today? I can help you open websites, play music, get news, or answer questions."

#             # Thank you
#             elif "thank" in command:
#                 return "You're welcome! Is there anything else I can help you with?"

#             # Help command
#             elif "help" in command:
#                 return "I can help you with: Opening websites (Google, YouTube, Instagram, LinkedIn), Playing music on YouTube, Getting news updates, Telling you the time and date, Managing your chat history, and much more! Try saying 'play some music' or 'open Google'."
            
#             # elif "capital of india" in command:
#             #     return "The capital of India is New Delhi."

#             # Advanced queries - you can integrate OpenAI here
#             else:
#                 # You can uncomment this section if you have OpenAI API key
#                 # return await self.get_openai_response(command)

#                 # For now, return a helpful default response
#                 return f"I heard you say '{command}'. I can help you with opening websites, playing music, getting news, or telling you the time. What would you like me to do?"

#     async def get_openai_response(self, query):
#             """Get response from OpenRouter using an OpenAI-compatible API call."""
#             logger.info(f"Sending query to OpenRouter: '{query}'")
#             try:
#                 # Use asyncio.to_thread to run the synchronous API call in a separate thread
#                 # This prevents blocking the main event loop.
#                 response = await asyncio.to_thread(
#                     self.openai_client.chat.completions.create,
#                     model="openai/gpt-3.5-turbo",  # Correct model name for OpenRouter
#                     messages=[
#                         {"role": "system", "content": "You are Jarvis, a helpful and concise AI assistant."},
#                         {"role": "user", "content": query}
#                     ],
#                     max_tokens=150
#                 )
#                 result = response.choices[0].message.content.strip()
#                 logger.info(f"Received response from OpenRouter: '{result}'")
#                 return result
                
#             except Exception as e:
#                 logger.error(f"OpenRouter API error: {e}")
#                 return "I'm having trouble connecting to my advanced knowledge base right now. Please try again in a moment."

#     #634
#     # async def handle_voice_request(self, websocket):
#     #     """Handle voice input from frontend request, now with more robust state logging."""
#     #     logger.info("Voice request received from frontend.")
        
#     #     # Log the current state before checking
#     #     logger.info(f"Current state: is_listening={self.is_listening}, is_processing={self.is_processing}, is_speaking={self.is_speaking}")
        
#     #     if self.is_listening or self.is_processing or self.is_speaking:
#     #         logger.warning("Assistant is busy. Ignoring new voice request.")
#     #         await self.send_message(websocket, {
#     #             'type': 'status_update',
#     #             'message': 'I am currently busy. Please wait a moment.'
#     #         })
#     #         return

#     #     try:
#     #         # Listen for audio
#     #         audio_text = await self.listen_for_audio(websocket)

#     #         if audio_text:
#     #             logger.info(f"Recognized text: '{audio_text}'. Processing command.")
#     #             # Process the recognized text as a voice command
#     #             await self.process_command(websocket, audio_text, is_voice=True)
#     #         else:
#     #             # No audio detected or error occurred
#     #             logger.warning("No audio text was recognized.")
#     #             await self.send_message(websocket, {
#     #                 'type': 'jarvis_response',
#     #                 'content': "I didn't catch that clearly. Please try again or type your message."
#     #             })
#     #             # Explicitly set phase back to ready if listening fails
#     #             await self.send_phase_update(websocket, 'ready', 'Ready to help')
                
#     #     except Exception as e:
#     #         logger.error(f"An unhandled error occurred in handle_voice_request: {e}")
#     #     finally:
#     #         # This block ensures that no matter what happens, we log the final state.
#     #         # The individual functions are already supposed to reset their flags,
#     #         # but this gives us a final check.
#     #         logger.info(f"handle_voice_request finished. Final state: is_listening={self.is_listening}, is_processing={self.is_processing}, is_speaking={self.is_speaking}")

#     async def handle_voice_request(self, websocket):
#         """Handle voice input from frontend, checking if the assistant is busy."""
#         logger.info("Voice request received from frontend.")
        
#         # Log the current state before checking
#         logger.info(f"Current state: is_listening={self.is_listening}, is_processing={self.is_processing}, is_speaking={self.is_speaking}")
        
#         # This is the important check. If busy, log it and do nothing else.
#         if self.is_listening or self.is_processing or self.is_speaking:
#             logger.warning("Assistant is busy. Ignoring new voice request.")
#             return

#         try:
#             # Listen for audio
#             audio_text = await self.listen_for_audio(websocket)

#             if audio_text:
#                 logger.info(f"Recognized text: '{audio_text}'. Processing command.")
#                 await self.process_command(websocket, audio_text, is_voice=True)
#             else:
#                 logger.warning("No audio text was recognized.")
#                 await self.send_message(websocket, {
#                     'type': 'jarvis_response',
#                     'content': "I didn't catch that clearly. Please try again or type your message."
#                 })
#                 await self.send_phase_update(websocket, 'ready', 'Ready to help')
                
#         except Exception as e:
#             logger.error(f"An unhandled error occurred in handle_voice_request: {e}")
#         finally:
#             logger.info(f"handle_voice_request finished.")

#     # async def handle_voice_request(self, websocket):
#         # """Handle voice input from frontend, checking if the assistant is busy."""
#         # logger.info("Voice request received from frontend.")
        
#         # # Log the current state
#         # logger.info(f"Current state: is_listening={self.is_listening}, is_processing={self.is_processing}, is_speaking={self.is_speaking}")
        
#         # # This is the most important check. If busy, do nothing.
#         # if self.is_listening or self.is_processing or self.is_speaking:
#         #     logger.warning("Assistant is busy. Ignoring new voice request.")
#         #     return # Simply exit the function if busy

#         # try:
#         #     # Listen for audio
#         #     audio_text = await self.listen_for_audio(websocket)

#         #     if audio_text:
#         #         logger.info(f"Recognized text: '{audio_text}'. Processing command.")
#         #         await self.process_command(websocket, audio_text, is_voice=True)
#         #     else:
#         #         # This handles cases where listening timed out or no speech was heard
#         #         logger.warning("No audio text was recognized.")
#         #         await self.send_message(websocket, {
#         #             'type': 'jarvis_response',
#         #             'content': "I didn't quite catch that. Could you please try again?"
#         #         })
#         #         await self.send_phase_update(websocket, 'ready', 'Ready to help')
                
#         # except Exception as e:
#         #     logger.error(f"An unhandled error occurred in handle_voice_request: {e}")
#         #     # Ensure states are reset even if an error happens
#         #     self.is_listening = False
#         #     self.is_processing = False
#         #     await self.send_phase_update(websocket, 'ready', 'Ready to help')
#         # finally:
#         #     logger.info("handle_voice_request finished.")


#     async def handle_websocket(self, websocket, path):
#         """Handle WebSocket connections."""
#         await self.register_client(websocket)
#         try:
#             async for message in websocket:
#                 try:
#                     data = json.loads(message)
#                     message_type = data.get('type')

#                     if message_type == 'text_command':
#                         command = data.get('message', '').strip()
#                         if command:
#                             await self.process_command(websocket, command)

#                     elif message_type == 'voice_request':
#                         await self.handle_voice_request(websocket)

#                     elif message_type == 'speak_request':
#                         text = data.get('text', '')
#                         if text:
#                                 # Pass the websocket to speak
#                             await self.speak(websocket, text) 

#                     elif message_type == 'ping':
#                         await self.send_message(websocket, {'type': 'pong'})

#                     else:
#                         logger.warning(f"Unknown message type: {message_type}")

#                 except json.JSONDecodeError:
#                     logger.error(f"Invalid JSON received: {message}")
#                 except Exception as e:
#                     logger.error(f"Error handling message: {e}")

#         except websockets.exceptions.ConnectionClosed:
#                 logger.info("Client connection closed normally")
#         except Exception as e:
#                 logger.error(f"WebSocket error: {e}")
#         finally:
#                 await self.unregister_client(websocket)


# # Main execution
# async def main():
#     jarvis = JarvisBackend()

#     print("\n" + "="*60)
#     print("🤖 JARVIS BACKEND SERVER")
#     print("="*60)
#     print("📡 WebSocket server starting on localhost:8765")
#     print("🌐 Frontend should connect to: ws://localhost:8765")
#     print("🎤 Voice recognition: ENABLED")
#     print("🔊 Text-to-speech: ENABLED")
#     print("🎵 Music playback: ENABLED")
#     print("🌍 Website controls: ENABLED")
#     print("✨ Jarvis is ready to assist!")
#     print("="*60)
#     print("\n💡 Instructions:")
#     print("1. Keep this terminal open")
#     print("2. Open your HTML file in a browser")
#     print("3. Use voice commands or type messages")
#     print("4. Press Ctrl+C to stop the server")
#     print("\n📝 Logs:")

#     # Start WebSocket server
#     try:
#         async with websockets.serve(jarvis.handle_websocket, "localhost", 8765):
#             logger.info("Server started successfully")
#             await asyncio.Future()  # Run forever
#     except KeyboardInterrupt:
#         print("\n👋 Shutting down Jarvis backend server...")
#     except Exception as e:
#         logger.error(f"Server error: {e}")

# if __name__ == "__main__":
#     # Install required packages reminder
#     try:
#         import pywhatkit
#         import pyttsx3
#         import speech_recognition
#         import websockets
#     except ImportError as e:
#         print(f"❌ Missing required package: {e}")
#         print("\n📦 Please install required packages:")
#         print("pip install websockets pywhatkit pyttsx3 SpeechRecognition pyaudio")
#         exit(1)

#     # Run the server
#     asyncio.run(main())









# # import asyncio
# # import json
# # import websockets
# # import logging
# # from datetime import datetime
# # import threading
# # import pyttsx3
# # import speech_recognition as sr
# # import webbrowser
# # import os
# # import pywhatkit as kit
# # from openai import OpenAI

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)


# # class JarvisBackend:
# #     def __init__(self):
# #         # Initialize speech recognition
# #         self.recognizer = sr.Recognizer()
# #         self.microphone = sr.Microphone()
# #         # Set a more patient pause threshold
# #         self.recognizer.pause_threshold = 2.0

# #         # Initialize text-to-speech
# #         self.tts_engine = pyttsx3.init()
# #         self.tts_engine.setProperty('rate', 180)
# #         self.tts_engine.setProperty('volume', 0.8)

# #         # Set female voice (Zira on Windows)
# #         voices = self.tts_engine.getProperty('voices')
# #         if len(voices) > 1:
# #             self.tts_engine.setProperty('voice', voices[1].id)

# #         # Store connected clients
# #         self.connected_clients = set()

# #         # Initialize the client to use OpenRouter
# #         self.openai_client = OpenAI(
# #             base_url="https://openrouter.ai/api/v1",
# #             api_key="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",
# #         )

# #         logger.info("Jarvis Backend initialized successfully!")

# #     async def register_client(self, websocket):
# #         self.connected_clients.add(websocket)
# #         await self.send_phase_update(websocket, 'initializing', 'Connecting to Jarvis backend...')
# #         await asyncio.sleep(1)
# #         await self.send_phase_update(websocket, 'ready', 'Connected to Jarvis backend!')
# #         await self.send_message(websocket, {
# #             'type': 'jarvis_message',
# #             'content': 'Hello! I\'m now connected and ready to assist.'
# #         })
# #         logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

# #     async def unregister_client(self, websocket):
# #         self.connected_clients.discard(websocket)
# #         logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")

# #     async def send_message(self, websocket, data):
# #         try:
# #             await websocket.send(json.dumps(data))
# #         except websockets.exceptions.ConnectionClosed:
# #             await self.unregister_client(websocket)
# #         except Exception as e:
# #             logger.error(f"Error sending message: {e}")

# #     async def send_phase_update(self, websocket, phase, message):
# #         await self.send_message(websocket, {
# #             'type': 'phase_update',
# #             'phase': phase,
# #             'message': message
# #         })

# #     async def speak(self, text):
# #         """A simple, stable function to speak text in a background thread."""
# #         if not text:
# #             return
        
# #         loop = asyncio.get_event_loop()
# #         def speak_sync_wrapper():
# #             try:
# #                 self.tts_engine.say(text)
# #                 self.tts_engine.runAndWait()
# #             except Exception as e:
# #                 logger.error(f"Error in TTS thread: {e}")

# #         await loop.run_in_executor(None, speak_sync_wrapper)

# #     async def listen_for_audio(self, websocket):
# #         """Listen for audio input and return the recognized text."""
# #         await self.send_phase_update(websocket, 'listening', 'Listening...')
# #         try:
# #             def listen_sync():
# #                 with self.microphone as source:
# #                     logger.info("Calibrating for ambient noise...")
# #                     self.recognizer.adjust_for_ambient_noise(source, duration=1)
# #                     logger.info("Listening for command...")
# #                     audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
# #                     logger.info("Finished listening.")
# #                 return audio_data

# #             def recognize_sync(audio_data):
# #                 logger.info("Sending audio for recognition...")
# #                 return self.recognizer.recognize_google(audio_data)

# #             loop = asyncio.get_event_loop()
# #             audio = await loop.run_in_executor(None, listen_sync)
# #             text = await loop.run_in_executor(None, recognize_sync, audio)
            
# #             logger.info(f"DEBUG: Recognized text from audio -> '{text}'")
# #             return text.lower().strip()

# #         except (sr.WaitTimeoutError, sr.UnknownValueError):
# #             logger.warning("No speech detected or understood.")
# #             await self.send_phase_update(websocket, 'ready', 'Ready to help')
# #             return None
# #         except Exception as e:
# #             logger.error(f"An unexpected error occurred in audio listening: {e}")
# #             await self.send_phase_update(websocket, 'ready', 'Ready to help')
# #             return None

# #     async def process_command(self, websocket, command_text, is_voice=False):
# #         """Processes a command, gets a response, and speaks it."""
# #         await self.send_phase_update(websocket, 'processing', 'Thinking...')
# #         if is_voice:
# #             await self.send_message(websocket, {'type': 'voice_user_message', 'content': command_text})

# #         response = await self.handle_command(command_text)

# #         await self.send_message(websocket, {'type': 'jarvis_response', 'content': response})
# #         await self.send_phase_update(websocket, 'speaking', 'Speaking...')
# #         await self.speak(response)
# #         await self.send_phase_update(websocket, 'ready', 'Ready to help')

# #     async def get_openai_response(self, query):
# #         """Get response from OpenRouter."""
# #         logger.info(f"Sending query to OpenRouter: '{query}'")
# #         try:
# #             response = await asyncio.to_thread(
# #                 self.openai_client.chat.completions.create,
# #                 model="openai/gpt-3.5-turbo",
# #                 messages=[
# #                     {"role": "system", "content": "You are Jarvis, a helpful and concise AI assistant."},
# #                     {"role": "user", "content": query}
# #                 ],
# #                 max_tokens=150
# #             )
# #             return response.choices[0].message.content.strip()
# #         except Exception as e:
# #             logger.error(f"OpenRouter API error: {e}")
# #             return "I'm having trouble connecting to my AI brain right now."

# #     async def handle_command(self, command):
# #         """Handle different commands."""
# #         command = command.lower().strip()
        
# #         # Website opening commands
# #         if "open google" in command or "google" in command:
# #             webbrowser.open("https://www.google.com")
# #             return "Opening Google for you."
# #         elif "open youtube" in command or "youtube" in command:
# #             webbrowser.open("https://www.youtube.com")
# #             return "Opening YouTube for you."
# #         elif "open instagram" in command or "instagram" in command:
# #             webbrowser.open("https://www.instagram.com")
# #             return "Opening Instagram for you."
# #         elif "open linkedin" in command or "linkedin" in command:
# #             webbrowser.open("https://www.linkedin.com")
# #             return "Opening LinkedIn for you."
        
# #         # Music commands
# #         elif command.startswith("play "):
# #             song = command.replace("play ", "").strip()
# #             try:
# #                 kit.playonyt(song)
# #                 return f"Playing {song} on YouTube."
# #             except Exception as e:
# #                 logger.error(f"Error playing song: {e}")
# #                 search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
# #                 webbrowser.open(search_url)
# #                 return f"Searching for {song} on YouTube."
        
# #         elif "music" in command:
# #             song_match = None
# #             if "play" in command:
# #                 parts = command.split("play")
# #                 if len(parts) > 1:
# #                     song_match = parts[1].strip()

# #             if song_match:
# #                 try:
# #                     kit.playonyt(song_match)
# #                     return f"Playing {song_match} on YouTube."
# #                 except:
# #                     webbrowser.open(f"https://www.youtube.com/results?search_query={song_match.replace(' ', '+')}")
# #                     return f"Searching for {song_match} on YouTube."
# #             else:
# #                 webbrowser.open("https://www.youtube.com/results?search_query=music")
# #                 return "Opening YouTube music for you."
        
# #         # News command
# #         elif "news" in command:
# #             webbrowser.open("https://news.google.com")
# #             return "Opening Google News for the latest updates."
        
# #         # Time query
# #         elif "time" in command:
# #             current_time = datetime.now().strftime("%I:%M %p")
# #             return f"The current time is {current_time}."
        
# #         # Date query
# #         elif "date" in command or "today" in command:
# #             current_date = datetime.now().strftime("%A, %B %d, %Y")
# #             return f"Today is {current_date}."
        
# #         # Weather query
# #         elif "weather" in command:
# #             webbrowser.open("https://weather.com")
# #             return "I don't have access to real-time weather data, but I've opened Weather.com for you."
        
# #         # Greetings
# #         elif any(word in command for word in ["hello", "hi", "hey", "jarvis"]):
# #             return "Hello! How can I assist you today? I can help you open websites, play music, get news, or answer questions."
        
# #         # Thank you
# #         elif "thank" in command:
# #             return "You're welcome! Is there anything else I can help you with?"
        
# #         # Help command
# #         elif "help" in command:
# #             return "I can help you with: Opening websites (Google, YouTube, Instagram, LinkedIn), Playing music on YouTube, Getting news updates, Telling you the time and date, Managing your chat history, and much more! Try saying 'play some music' or 'open Google'."
        
# #         # AI Fallback for any other query
# #         else:
# #             logger.info(f"No specific rule for '{command}'. Forwarding to AI.")
# #             return await self.get_openai_response(command)

# #     async def handle_voice_request(self, websocket):
# #         """A simple handler for a single voice command."""
# #         audio_text = await self.listen_for_audio(websocket)
# #         if audio_text:
# #             await self.process_command(websocket, audio_text, is_voice=True)

# #     async def handle_websocket(self, websocket, path):
# #         """Handle WebSocket connections."""
# #         await self.register_client(websocket)
# #         try:
# #             async for message in websocket:
# #                 try:
# #                     data = json.loads(message)
# #                     message_type = data.get('type')

# #                     if message_type == 'text_command':
# #                         command = data.get('message', '').strip()
# #                         if command:
# #                             await self.process_command(websocket, command)
# #                     elif message_type == 'voice_request':
# #                         await self.handle_voice_request(websocket)
# #                     elif message_type == 'speak_request':
# #                         text = data.get('text', '')
# #                         if text:
# #                             await self.speak(text)
# #                     elif message_type == 'ping':
# #                         await self.send_message(websocket, {'type': 'pong'})
# #                     else:
# #                         logger.warning(f"Unknown message type: {message_type}")

# #                 except json.JSONDecodeError:
# #                     logger.error(f"Invalid JSON received: {message}")
# #                 except Exception as e:
# #                     logger.error(f"Error handling message: {e}")

# #         except websockets.exceptions.ConnectionClosed:
# #             logger.info("Client connection closed normally")
# #         except Exception as e:
# #             logger.error(f"WebSocket error: {e}")
# #         finally:
# #             await self.unregister_client(websocket)

# # # Main execution
# # async def main():
# #     jarvis = JarvisBackend()
# #     print("\n" + "="*60)
# #     print("🤖 JARVIS BACKEND SERVER (STABLE VERSION)")
# #     print("="*60)
# #     print("📡 WebSocket server starting on localhost:8765")
# #     print("🌐 Frontend should connect to: ws://localhost:8765")
# #     print("🎤 Voice recognition: ENABLED")
# #     print("🔊 Text-to-speech: ENABLED")
# #     print("🎵 Music playback: ENABLED")
# #     print("🌍 Website controls: ENABLED")
# #     print("🧠 AI responses: ENABLED (OpenRouter)")
# #     print("✨ Jarvis is ready to assist!")
# #     print("="*60)
# #     print("\n💡 Instructions:")
# #     print("1. Keep this terminal open")
# #     print("2. Open your HTML file in a browser")
# #     print("3. Use voice commands or type messages")
# #     print("4. Press Ctrl+C to stop the server")
# #     print("\n📝 Logs:")
    
# #     try:
# #         async with websockets.serve(jarvis.handle_websocket, "localhost", 8765):
# #             logger.info("Server started successfully")
# #             await asyncio.Future()  # Run forever
# #     except KeyboardInterrupt:
# #         print("\n👋 Shutting down Jarvis backend server...")
# #     except Exception as e:
# #         logger.error(f"Server error: {e}")

# # if __name__ == "__main__":
# #     # Install required packages reminder
# #     try:
# #         import pywhatkit
# #         import pyttsx3
# #         import speech_recognition
# #         import websockets
# #     except ImportError as e:
# #         print(f"❌ Missing required package: {e}")
# #         print("\n📦 Please install required packages:")
# #         print("pip install websockets pywhatkit pyttsx3 SpeechRecognition pyaudio")
# #         exit(1)

# #     # Run the server
# #     asyncio.run(main())








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

    # async def get_openai_response(self, query):
    #     """Get response from OpenRouter."""
    #     logger.info(f"Sending query to OpenRouter: '{query}'")
    #     try:
    #         response = await asyncio.to_thread(
    #             self.openai_client.chat.completions.create,
    #             model="openai/gpt-3.5-turbo",
    #             messages=[
    #                 {"role": "system", "content": "You are Jarvis, a helpful and concise AI assistant."},
    #                 {"role": "user", "content": query}
    #             ],
    #             max_tokens=150,
    #             timeout=20.0, 
    #         )
    #         return response.choices[0].message.content.strip()
        
    #     except OpenAI.APIConnectionError as e:
    #         logger.error(f"OpenRouter Connection Error: {e.__cause__}")
    #         return "I'm having trouble connecting to the AI network. Please check your connection."
    #     except OpenAI.RateLimitError as e:
    #         logger.error(f"OpenRouter Rate Limit Exceeded: {e.status_code} - {e.response}")
    #         return "The AI network is currently busy. Please try again in a moment."
    #     except OpenAI.APIStatusError as e:
    #         logger.error(f"OpenRouter API Status Error: {e.status_code} - {e.response}")
    #         return "The AI network reported an error. Please try again."
    #     except Exception as e:
    #         logger.error(f"An unexpected error occurred with the AI call: {e}")
    #         return "I'm having trouble connecting to my advanced knowledge base right now."
    #     # except Exception as e:
    #     #     logger.error(f"OpenRouter API error: {e}")
    #     #     return "I'm having trouble connecting to my AI brain right now."
    
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

    # async def handle_command(self, command):
    #     """Handle different commands."""
    #     command = command.lower().strip()
        
    #     # Website opening commands
    #     if "open google" in command or "google" in command:
    #         webbrowser.open("https://www.google.com")
    #         return "Opening Google for you."
    #     elif "open youtube" in command or "youtube" in command:
    #         webbrowser.open("https://www.youtube.com")
    #         return "Opening YouTube for you."
    #     elif "open instagram" in command or "instagram" in command:
    #         webbrowser.open("https://www.instagram.com")
    #         return "Opening Instagram for you."
    #     elif "open linkedin" in command or "linkedin" in command:
    #         webbrowser.open("https://www.linkedin.com")
    #         return "Opening LinkedIn for you."
        
    #     # Music commands
    #     elif command.startswith("play "):
    #         song = command.replace("play ", "").strip()
    #         try:
    #             kit.playonyt(song)
    #             return f"Playing {song} on YouTube."
    #         except Exception as e:
    #             logger.error(f"Error playing song: {e}")
    #             search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
    #             webbrowser.open(search_url)
    #             return f"Searching for {song} on YouTube."
        
    #     elif "music" in command:
    #         song_match = None
    #         if "play" in command:
    #             parts = command.split("play")
    #             if len(parts) > 1:
    #                 song_match = parts[1].strip()

    #         if song_match:
    #             try:
    #                 kit.playonyt(song_match)
    #                 return f"Playing {song_match} on YouTube."
    #             except:
    #                 webbrowser.open(f"https://www.youtube.com/results?search_query={song_match.replace(' ', '+')}")
    #                 return f"Searching for {song_match} on YouTube."
    #         else:
    #             webbrowser.open("https://www.youtube.com/results?search_query=music")
    #             return "Opening YouTube music for you."
        
    #     # News command
    #     elif "news" in command:
    #         webbrowser.open("https://news.google.com")
    #         return "Opening Google News for the latest updates."
        
    #     # Time query
    #     elif "time" in command:
    #         current_time = datetime.now().strftime("%I:%M %p")
    #         return f"The current time is {current_time}."
        
    #     # Date query
    #     elif "date" in command or "today" in command:
    #         current_date = datetime.now().strftime("%A, %B %d, %Y")
    #         return f"Today is {current_date}."
        
    #     # Weather query
    #     elif "weather" in command:
    #         webbrowser.open("https://weather.com")
    #         return "I don't have access to real-time weather data, but I've opened Weather.com for you."
        
    #     # Greetings
    #     elif any(word in command for word in ["hello", "hi", "hey", "jarvis"]):
    #         return "Hello! How can I assist you today? I can help you open websites, play music, get news, or answer questions."
        
    #     # Thank you
    #     elif "thank" in command:
    #         return "You're welcome! Is there anything else I can help you with?"
        
    #     # Help command
    #     elif "help" in command:
    #         return "I can help you with: Opening websites (Google, YouTube, Instagram, LinkedIn), Playing music on YouTube, Getting news updates, Telling you the time and date, Managing your chat history, and much more! Try saying 'play some music' or 'open Google'."
        
    #     # AI Fallback for any other query
    #     else:
    #         logger.info(f"No specific rule for '{command}'. Forwarding to AI.")
    #         return await self.get_openai_response(command)
    
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


