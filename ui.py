# ui.py
# import io
# import time
# import uuid
# from typing import Optional, Tuple, List

# import streamlit as st
# import requests
# import speech_recognition as sr
# from gtts import gTTS

# import main as backend  # reuses aiProcess and newsapi, without changing backend
# import musicLibrary     # reuses your music mapping

# # -----------------------------
# # Minimal, modern, futuristic theme via CSS
# # -----------------------------
# FUTURE_CSS = """
# <style>
# /* Page background and typography */
# .stApp {
#   background: radial-gradient(1200px 600px at 10% 10%, #0d1b2a 0%, #000510 60%) fixed;
#   color: #e0e6ed;
#   font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif;
# }

# /* Chat bubbles */
# [data-testid="stChatMessage"] {
#   border-radius: 16px;
#   border: 1px solid rgba(255,255,255,0.06);
#   background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
#   box-shadow: 0 10px 30px rgba(0, 255, 255, 0.05);
# }

# /* Inputs and buttons */
# .stTextInput > div > div > input,
# .stChatInput textarea {
#   background: rgba(255,255,255,0.06) !important;
#   color: #e0e6ed !important;
#   border: 1px solid rgba(0, 255, 255, 0.18) !important;
#   border-radius: 12px !important;
# }

# .stButton>button, .stLinkButton>button {
#   background: linear-gradient(135deg, #0ea5ea 0%, #0bd1d1 100%) !important;
#   color: #0b1220 !important;
#   border: 0 !important;
#   border-radius: 12px !important;
#   box-shadow: 0 8px 24px rgba(14,165,234,0.35);
# }

# .stButton>button:hover, .stLinkButton>button:hover {
#   filter: brightness(1.05);
#   transform: translateY(-1px);
#   transition: all 150ms ease;
# }

# /* Quick actions layout */
# .quick-actions .stButton {
#   margin-right: 6px;
# }

# .sidebar-profile {
#   text-align: center;
#   padding: 8px 4px;
# }

# .sidebar-profile img {
#   width: 88px;
#   height: 88px;
#   border-radius: 50%;
#   border: 1px solid rgba(0, 255, 255, 0.25);
#   box-shadow: 0 10px 24px rgba(0, 255, 255, 0.12);
#   object-fit: cover;
#   background: rgba(0, 0, 0, 0.2);
# }

# .sidebar-card {
#   border-radius: 14px;
#   border: 1px solid rgba(255,255,255,0.08);
#   background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
#   padding: 12px;
# }
# </style>
# """

# # -----------------------------
# # Helpers
# # -----------------------------
# def tts_to_bytes(text: str) -> bytes:
#   """Generate MP3 bytes for inline browser playback using gTTS."""
#   tts = gTTS(text=text, lang="en")
#   buf = io.BytesIO()
#   tts.write_to_fp(buf)
#   buf.seek(0)
#   return buf.read()

# def recognize_from_audio_bytes(wav_or_webm_bytes: bytes) -> Optional[str]:
#   """Use SpeechRecognition to transcribe uploaded audio bytes."""
#   r = sr.Recognizer()
#   try:
#     with sr.AudioFile(io.BytesIO(wav_or_webm_bytes)) as source:
#       audio = r.record(source)
#     return r.recognize_google(audio)
#   except Exception:
#     return None

# def news_headlines(api_key: str, q: str = "bitcoin", limit: int = 5) -> List[str]:
#   try:
#     resp = requests.get(
#       "https://newsapi.org/v2/everything",
#       params={"q": q, "apiKey": api_key, "pageSize": max(1, min(limit, 10))},
#       timeout=10
#     )
#     data = resp.json()
#     if data.get("status") == "ok":
#       return [a.get("title", "").strip() for a in data.get("articles", []) if a.get("title")]
#     return []
#   except Exception:
#     return []

# def handle_command(command: str) -> Tuple[str, Optional[bytes]]:
#   """
#   Mirror your backend's routing without altering it:
#   - For web actions, return links instead of launching server-side browsers.
#   - For news, call with the same key.
#   - For general queries, use backend.aiProcess.
#   Returns (assistant_text, optional_audio_bytes).
#   """
#   c = command.strip()
#   cl = c.lower()

#   # Web quick opens → respond with an actionable link instead of server-side open
#   if "open google" in cl:
#     text = "Opening Google."
#     link = "https://google.com"
#     return f"{text}\n\n[Open Google]({link})", tts_to_bytes(text)

#   if "open instagram" in cl:
#     text = "Opening Instagram."
#     link = "https://instagram.com"
#     return f"{text}\n\n[Open Instagram]({link})", tts_to_bytes(text)

#   if "open youtube" in cl:
#     text = "Opening YouTube."
#     link = "https://youtube.com"
#     return f"{text}\n\n[Open YouTube]({link})", tts_to_bytes(text)

#   if "open linkedin" in cl:
#     text = "Opening LinkedIn."
#     link = "https://linkedin.com"
#     return f"{text}\n\n[Open LinkedIn]({link})", tts_to_bytes(text)

#   # Music play → lookup in your musicLibrary and present a link
#   if cl.startswith("play"):
#     song = cl.replace("play", "", 1).strip()
#     if not song:
#       text = "Please specify a song to play."
#       return text, tts_to_bytes(text)
#     url = musicLibrary.music.get(song)
#     if not url:
#       # try a relaxed match
#       url = next((v for k, v in musicLibrary.music.items() if song in k.lower()), None)
#     if url:
#       text = f"Playing {song}."
#       return f"{text}\n\n[Listen on YouTube]({url})", tts_to_bytes(text)
#     text = f"I couldn't find '{song}' in your library."
#     return text, tts_to_bytes(text)

#   # News via same key
#   if "news" in cl:
#     titles = news_headlines(backend.newsapi, q="technology", limit=5)
#     if titles:
#       joined = "\n".join([f"- {t}" for t in titles])
#       text = f"Here are the latest headlines:\n\n{joined}"
#       # Keep audio short to avoid long playback
#       speak_short = "Here are the latest technology headlines."
#       return text, tts_to_bytes(speak_short)
#     text = "I couldn't fetch the news right now."
#     return text, tts_to_bytes(text)

#   # Exit/quit
#   if any(x in cl for x in ["exit", "quit", "goodbye"]):
#     text = "Goodbye! Shutting down."
#     return text, tts_to_bytes(text)

#   # Fallback to your LLM via OpenRouter through backend.aiProcess
#   try:
#     output = backend.aiProcess(c)
#   except Exception as e:
#     output = f"Sorry, I ran into an error processing that: {e}"
#   return output, tts_to_bytes(output)

# # -----------------------------
# # Streamlit App
# # -----------------------------
# st.set_page_config(page_title="Jarvis", page_icon="🤖", layout="wide")
# st.markdown(FUTURE_CSS, unsafe_allow_html=True)

# # Sidebar: Profile
# with st.sidebar:
#   st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
#   st.markdown('<div class="sidebar-profile">', unsafe_allow_html=True)
#   # Placeholder avatar
#   st.image("https://api.dicebear.com/7.x/bottts-neutral/svg?seed=jarvis", caption=None, use_container_width=False)
#   st.markdown("</div>", unsafe_allow_html=True)
#   st.subheader("Jarvis")
#   st.caption("Virtual AI assistant. Fast, helpful, and always learning.")
#   username = st.text_input("Username", value="User", help="Displayed in the chat bubbles.")
#   st.markdown("</div>", unsafe_allow_html=True)

# # Session state for chat memory
# if "messages" not in st.session_state:
#   st.session_state.messages = []  # each item: {"role": "user"/"assistant", "content": str, "audio": Optional[bytes]}

# # Header with quick actions
# left, right = st.columns([0.72, 0.28])
# with left:
#   st.markdown("### Jarvis")
#   st.caption("Minimal. Modern. Futuristic.")

# with right:
#   st.markdown("#### Quick Actions")
#   qa1, qa2, qa3 = st.columns(3)
#   with qa1:
#     if st.button("Google", use_container_width=True):
#       st.session_state.messages.append({"role": "user", "content": "open google", "audio": None})
#       text, audio = handle_command("open google")
#       st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})
#   with qa2:
#     if st.button("YouTube", use_container_width=True):
#       st.session_state.messages.append({"role": "user", "content": "open youtube", "audio": None})
#       text, audio = handle_command("open youtube")
#       st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})
#   with qa3:
#     if st.button("Instagram", use_container_width=True):
#       st.session_state.messages.append({"role": "user", "content": "open instagram", "audio": None})
#       text, audio = handle_command("open instagram")
#       st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})

# qa4, qa5, qa6 = st.columns(3)
# with qa4:
#   if st.button("LinkedIn", use_container_width=True):
#     st.session_state.messages.append({"role": "user", "content": "open linkedin", "audio": None})
#     text, audio = handle_command("open linkedin")
#     st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})
# with qa5:
#   if st.button("News", use_container_width=True):
#     st.session_state.messages.append({"role": "user", "content": "news", "audio": None})
#     text, audio = handle_command("news")
#     st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})
# with qa6:
#   if st.button("Music", use_container_width=True):
#     # Simple example: propose a song key
#     st.session_state.messages.append({"role": "user", "content": "play shape of you", "audio": None})
#     text, audio = handle_command("play shape of you")
#     st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})

# st.divider()

# # Chat history window
# for msg in st.session_state.messages:
#   with st.chat_message("user" if msg["role"] == "user" else "assistant"):
#     st.markdown(msg["content"])
#     if msg["role"] == "assistant" and msg.get("audio"):
#       st.audio(msg["audio"], format="audio/mp3")

# st.divider()

# # Input area: text and mic
# c1, c2 = st.columns([0.7, 0.3])

# # Text chat input
# with c1:
#   user_input = st.chat_input(f"Message Jarvis as {username}...")
#   if user_input:
#     st.session_state.messages.append({"role": "user", "content": user_input, "audio": None})
#     text, audio = handle_command(user_input)
#     st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})
#     st.experimental_rerun()

# # Microphone input (browser-side)
# with c2:
#   st.markdown("##### 🎙️ Microphone")
#   mic = st.audio_input("Speak to Jarvis", help="Record short audio and Jarvis will transcribe it.", key=f"mic-{uuid.uuid4()}")
#   if mic is not None and mic.getvalue():
#     st.info("Processing your audio…")
#     audio_bytes = mic.getvalue()
#     transcript = recognize_from_audio_bytes(audio_bytes)
#     if transcript:
#       st.session_state.messages.append({"role": "user", "content": transcript, "audio": None})
#       text, audio = handle_command(transcript)
#       st.session_state.messages.append({"role": "assistant", "content": text, "audio": audio})
#     else:
#       err = "Sorry, I couldn't understand the audio."
#       st.session_state.messages.append({"role": "assistant", "content": err, "audio": tts_to_bytes(err)})
#     st.experimental_rerun()









import customtkinter as ctk
import speech_recognition as sr
import threading
from main import process_command, listen_for_command, speak

# Set the appearance mode and default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class JarvisUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure the main window
        self.title("Jarvis Voice Assistant")
        self.geometry("450x600")
        self.resizable(False, False)

        # Main frame for the UI
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Heading label
        self.heading_label = ctk.CTkLabel(self.main_frame, text="Jarvis", font=("Arial", 28, "bold"))
        self.heading_label.pack(pady=(10, 20))

        # Textbox for conversation history
        self.chat_history = ctk.CTkTextbox(self.main_frame, width=400, height=400, corner_radius=10, state="disabled")
        self.chat_history.pack(pady=(0, 10), padx=10)

        # Input frame for text entry and voice command button
        self.input_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Text entry field
        self.command_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type your command here...", font=("Arial", 14), width=280)
        self.command_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        # Voice command button
        self.voice_button = ctk.CTkButton(self.input_frame, text="🎤", width=50, command=self.start_voice_command)
        self.voice_button.grid(row=0, column=1, padx=(5, 10), pady=10)
        
        # Send button for text command
        self.send_button = ctk.CTkButton(self.input_frame, text="Send", width=50, command=self.send_text_command)
        self.send_button.grid(row=0, column=2, padx=(5, 10), pady=10)

        # Configure column weights to make entry field expand
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Initial message
        self.update_chat("Jarvis: Hello! I'm ready for your command.", "Jarvis")

    def update_chat(self, message, sender):
        """Updates the chat history with a new message."""
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        self.chat_history.yview_moveto(1.0) # Scroll to the bottom
        self.chat_history.configure(state="disabled")

    def start_voice_command(self):
        """Starts a new thread for the voice command."""
        self.voice_button.configure(state="disabled", text="Listening...")
        self.update_chat("You: Listening for your command...", "You")
        threading.Thread(target=self.voice_command_thread, daemon=True).start()

    def voice_command_thread(self):
        """Handles the voice recognition and command processing in a separate thread."""
        try:
            self.update_chat("You: Waiting for a command...", "You")
            # Listen for "Jarvis" wake word
            with sr.Microphone() as source:
                audio = sr.Recognizer().listen(source, timeout=2, phrase_time_limit=3)
            
            word = sr.Recognizer().recognize_google(audio)

            if "jarvis" in word.lower():
                self.update_chat("Jarvis: Yeah.", "Jarvis")
                speak("Yeah")
                command = listen_for_command()
                if command:
                    self.update_chat(command, "You")
                    response = process_command(command)
                    self.update_chat(response, "Jarvis")
                else:
                    self.update_chat("Sorry, I didn't catch that.", "Jarvis")
                    speak("Sorry, I didn't catch that.")
        except Exception as e:
            self.update_chat(f"Error: {e}", "System")
        finally:
            self.voice_button.configure(state="normal", text="🎤")
            
    def send_text_command(self):
        """Processes the command from the text entry field."""
        command = self.command_entry.get()
        if command:
            self.update_chat(command, "You")
            self.command_entry.delete(0, "end")
            response = process_command(command)
            self.update_chat(response, "Jarvis")

# Create and run the UI
if __name__ == "__main__":
    app = JarvisUI()
    app.mainloop()



# import customtkinter as ctk
# import threading
# from main import process_command, listen_for_command, speak
# import speech_recognition as sr # Import sr for the Recognizer
# from PIL import Image # Required for CTkImage

# # Set the appearance mode and default color theme
# ctk.set_appearance_mode("Dark") # Options: "Dark", "Light", "System"
# ctk.set_default_color_theme("blue") # Options: "blue", "green", "dark-blue"

# class JarvisUI(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         # --- Window Configuration ---
#         self.title("Jarvis Voice Assistant")
#         self.geometry("500x700") # Slightly larger window
#         self.resizable(False, False)

#         # --- Fonts ---
#         self.font_heading = ctk.CTkFont(family="Segoe UI", size=32, weight="bold")
#         self.font_chat = ctk.CTkFont(family="Segoe UI", size=15)
#         self.font_button = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
#         self.font_entry = ctk.CTkFont(family="Segoe UI", size=14)
#         self.font_status = ctk.CTkFont(family="Segoe UI", size=13, slant="italic")

#         # --- Main Frame ---
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(0, weight=1)

#         self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent") # Transparent for background
#         self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
#         self.main_frame.grid_rowconfigure(1, weight=1) # Chat history should expand
#         self.main_frame.grid_columnconfigure(0, weight=1)

#         # --- Heading ---
#         self.heading_label = ctk.CTkLabel(self.main_frame, text="Jarvis AI", font=self.font_heading, text_color="#2196F3") # Accent color
#         self.heading_label.grid(row=0, column=0, pady=(0, 20))

#         # --- Chat History Display ---
#         self.chat_frame = ctk.CTkScrollableFrame(self.main_frame, corner_radius=10, fg_color="#2b2b2b") # Slightly lighter than window for contrast
#         self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
#         self.chat_frame.grid_columnconfigure(0, weight=1)

#         # To store chat bubbles
#         self.chat_messages = [] 
#         self.chat_row_counter = 0

#         # --- Input Section ---
#         self.input_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="transparent")
#         self.input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 0))
#         self.input_frame.grid_columnconfigure(0, weight=1) # Entry field expands

#         self.command_entry = ctk.CTkEntry(
#             self.input_frame, 
#             placeholder_text="Type your command or click mic...", 
#             font=self.font_entry, 
#             height=40, 
#             corner_radius=10
#         )
#         self.command_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
#         self.command_entry.bind("<Return>", self.send_text_command) # Bind Enter key

#         # --- Microphone Icon (try loading, fallback to text) ---
#         try:
#             mic_image = ctk.CTkImage(Image.open("mic_icon.png"), size=(24, 24))
#             self.voice_button = ctk.CTkButton(
#                 self.input_frame, 
#                 text="", 
#                 image=mic_image, 
#                 width=50, 
#                 height=40, 
#                 corner_radius=10, 
#                 command=self.start_voice_command,
#                 fg_color="#4CAF50", # Green for active mic
#                 hover_color="#66BB6A"
#             )
#         except FileNotFoundError:
#             self.voice_button = ctk.CTkButton(
#                 self.input_frame, 
#                 text="🎙️", # Fallback to emoji
#                 font=self.font_button,
#                 width=50, 
#                 height=40, 
#                 corner_radius=10, 
#                 command=self.start_voice_command,
#                 fg_color="#4CAF50",
#                 hover_color="#66BB6A"
#             )
#         self.voice_button.grid(row=0, column=1, padx=(0, 5), pady=10)
        
#         # --- Send Button ---
#         self.send_button = ctk.CTkButton(
#             self.input_frame, 
#             text="Send", 
#             font=self.font_button,
#             width=50, 
#             height=40, 
#             corner_radius=10, 
#             command=self.send_text_command,
#             fg_color="#2196F3", # Blue accent
#             hover_color="#42A5F5"
#         )
#         self.send_button.grid(row=0, column=2, padx=(0, 0), pady=10)

#         # --- Status Label ---
#         self.status_label = ctk.CTkLabel(self.main_frame, text="Jarvis: Ready.", font=self.font_status, text_color="#A9A9A9")
#         self.status_label.grid(row=3, column=0, pady=(5, 0))

#         # Initial message
#         self.add_chat_bubble("Hello! I'm Jarvis, your personal AI assistant. How can I help you today?", "Jarvis")

#     def add_chat_bubble(self, message, sender):
#         """Adds a chat bubble to the scrollable frame."""
#         bubble_color = "#3a3a3a" if sender == "You" else "#2196F3" # Darker grey for user, blue for Jarvis
#         text_color = "white"
        
#         # Create a frame for the bubble to allow padding and background color
#         bubble_frame = ctk.CTkFrame(self.chat_frame, fg_color=bubble_color, corner_radius=10)
        
#         # Determine alignment based on sender
#         if sender == "You":
#             # User messages aligned right
#             bubble_frame.grid(row=self.chat_row_counter, column=0, sticky="e", pady=5, padx=(100, 10))
#         else:
#             # Jarvis messages aligned left
#             bubble_frame.grid(row=self.chat_row_counter, column=0, sticky="w", pady=5, padx=(10, 100))
        
#         # Add the label inside the bubble frame
#         msg_label = ctk.CTkLabel(bubble_frame, text=message, font=self.font_chat, wraplength=350, justify="left", text_color=text_color)
#         msg_label.pack(padx=12, pady=8, anchor="w") # Padding inside the bubble

#         self.chat_messages.append((bubble_frame, msg_label))
#         self.chat_row_counter += 1
#         self.chat_frame._parent_canvas.yview_moveto(1.0) # Scroll to bottom

#     def update_status(self, message):
#         """Updates the status label below the input field."""
#         self.status_label.configure(text=message)

#     def start_voice_command(self):
#         """Starts a new thread for the voice command."""
#         self.voice_button.configure(state="disabled", fg_color="#FFC107", hover_color="#FFD54F") # Orange for thinking/listening
#         self.send_button.configure(state="disabled")
#         self.command_entry.configure(state="disabled")
#         self.update_status("Jarvis: Listening for your command...")
#         threading.Thread(target=self.voice_command_thread, daemon=True).start()

#     def voice_command_thread(self):
#         """Handles the voice recognition and command processing in a separate thread."""
#         try:
#             # Try to listen for the wake word "Jarvis" first
#             with sr.Microphone() as source:
#                 self.update_status("You: Say 'Jarvis' to activate...")
#                 audio = sr.Recognizer().listen(source, timeout=3, phrase_time_limit=2)
            
#             wake_word = sr.Recognizer().recognize_google(audio).lower()

#             if "jarvis" in wake_word:
#                 self.add_chat_bubble("Jarvis: Yeah?", "Jarvis")
#                 speak("Yeah")
#                 self.update_status("Jarvis: Active. Please speak your command.")

#                 # Now listen for the actual command
#                 command = listen_for_command()
#                 if command:
#                     self.add_chat_bubble(command.capitalize(), "You")
#                     self.update_status("Jarvis: Processing command...")
#                     response = process_command(command)
#                     self.add_chat_bubble(response, "Jarvis")
#                     self.update_status("Jarvis: Command processed.")
#                 else:
#                     self.add_chat_bubble("Sorry, I didn't catch that.", "Jarvis")
#                     speak("Sorry, I didn't catch that.")
#                     self.update_status("Jarvis: Waiting for command...")
#             else:
#                 self.update_status("Jarvis: Didn't hear 'Jarvis'. Retrying...")
#         except sr.WaitTimeoutError:
#             self.update_status("Jarvis: Listening timed out. Please try again.")
#         except sr.UnknownValueError:
#             self.update_status("Jarvis: Could not understand audio.")
#         except sr.RequestError as e:
#             self.update_status(f"Jarvis: Speech service error: {e}")
#         except Exception as e:
#             self.update_status(f"Jarvis: Unexpected error: {e}")
#         finally:
#             self.voice_button.configure(state="normal", fg_color="#4CAF50", hover_color="#66BB6A")
#             self.send_button.configure(state="normal")
#             self.command_entry.configure(state="normal")
#             self.update_status("Jarvis: Ready.")
            
#     def send_text_command(self, event=None): # event=None for binding with <Return>
#         """Processes the command from the text entry field."""
#         command = self.command_entry.get().strip()
#         if command:
#             self.add_chat_bubble(command.capitalize(), "You")
#             self.command_entry.delete(0, "end")
#             self.update_status("Jarvis: Processing text command...")
            
#             # Run text command processing in a thread to keep UI responsive
#             threading.Thread(target=self._process_text_command_threaded, args=(command,), daemon=True).start()
#         else:
#             self.update_status("Jarvis: Please enter a command.")

#     def _process_text_command_threaded(self, command):
#         """Helper to run process_command in a thread for text input."""
#         try:
#             response = process_command(command)
#             self.add_chat_bubble(response, "Jarvis")
#             self.update_status("Jarvis: Command processed.")
#         except Exception as e:
#             self.add_chat_bubble(f"Error processing text command: {e}", "Jarvis")
#             self.update_status(f"Jarvis: Error - {e}")

# # Create and run the UI
# if __name__ == "__main__":
#     app = JarvisUI()
#     app.mainloop()