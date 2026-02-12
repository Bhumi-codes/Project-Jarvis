# import speech_recognition as sr
# from gtts import gTTS
# import pygame
# import webbrowser
# import time
# import os
# import uuid
# import musicLibrary
# import requests
# from openai import OpenAI

# # Initialize pygame mixer
# recognizer = sr.Recognizer()
# pygame.mixer.init()
# newsapi = "c1845519161e4f7dac0da8ec4f55dce5"

# def speak(text):
#     print(f"Jarvis should say: {text}")
#     try:
#         tts = gTTS(text=text, lang='en')
#         filename = f"voice_{uuid.uuid4()}.mp3"
#         tts.save(filename)
#         pygame.mixer.music.load(filename)
#         pygame.mixer.music.play()

#         # Wait until speech is finished
#         while pygame.mixer.music.get_busy():
#             pygame.time.Clock().tick(10)
        
#         pygame.mixer.music.stop()
#         pygame.mixer.music.unload()

#         if os.path.exists(filename):
#             os.remove(filename) 
            
#     except Exception as e:
#         print(f"[TTS ERROR]: {e}")

# def aiProcess(command):
#     client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="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",
#     )

#     response = client.chat.completions.create(
#         model="openai/gpt-4o-mini",  # OpenRouter routes this to GPT-4o-mini
#         messages=[
#             {"role": "system", "content": "You are a virtual assistant named jarvis, skilled in general tasks like Alexa and Google"},
#             {"role": "user", "content": command},
#         ],
#     )

#     return response.choices[0].message.content



# def process_command(command):
#     if "open google" in command.lower():
#         webbrowser.open("https://google.com")
#     elif "open instagram" in command.lower():
#         webbrowser.open("https://instagram.com")
#     elif "open youtube" in command.lower():
#         webbrowser.open("https://youtube.com")
#     elif "open linkedin" in command.lower():
#         webbrowser.open("https://linkedin.com")
#     elif command.lower().startswith("play"):
#         song = command.lower().replace("play", "").strip()
#         link = musicLibrary.music[song]
#         webbrowser.open(link)
    
#     elif "news" in command.lower():
#         r= requests.get(f"https://newsapi.org/v2/everything?q=bitcoin&apiKey={newsapi}")
#         data = r.json()
#         print(data)
        

#         # Check if the request was successful
#         if data["status"] == "ok":
            
#             for article in data["articles"]:
#                 speak(article["title"])
#         else:
#             print("Error:", data)
#     elif "exit" in command.lower() or "quit" in command.lower() or "goodbye" in command.lower():
#         speak("Goodbye! Shutting down.")
#         exit()
    
#     elif command.strip() == "" or len(command.split()) < 2:
#         speak("Sorry, I didn’t catch a valid command.")
#     else:
#         output = aiProcess(command)
#         speak(output)




# if __name__ == "__main__":
#     recognizer = sr.Recognizer()

#     while True:
#         try:
#             with sr.Microphone() as source:
#                 print("Initialising Jarvis...")
#                 audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)

#             word = recognizer.recognize_google(audio)

#             if "jarvis" in word.lower():
#                 speak("Yeah")
#                 with sr.Microphone() as source:
#                     print("Jarvis Active...")
#                     audio = recognizer.listen(source,timeout=10, phrase_time_limit=8)
#                     command = recognizer.recognize_google(audio)
#                     process_command(command)

#         except sr.WaitTimeoutError:
#             print("Listening timed out.")
#             speak("I didn't hear anything.")
#         except sr.UnknownValueError:
#             print("Could not understand audio.")
#             speak("Sorry, I didn't catch that.")
#         except sr.RequestError as e:
#             print(f"Could not request results; {e}")
#             speak("There was a problem with the speech recognition service.")
#         except Exception as e:
#             print(f"Unexpected error: {e}")
#             speak("Something went wrong.")

import os
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import pygame
import webbrowser
import time
import uuid
import musicLibrary
import requests
from openai import OpenAI
load_dotenv()

# Initialize pygame mixer
recognizer = sr.Recognizer()
pygame.mixer.init()
newsapi = os.getenv("NEWS_API_KEY")

def speak(text):
    print(f"Jarvis should say: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        filename = f"voice_{uuid.uuid4()}.mp3"
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait until speech is finished
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        if os.path.exists(filename):
            os.remove(filename)  
            
    except Exception as e:
        print(f"[TTS ERROR]: {e}")
        return f"[TTS ERROR]: {e}"
    return text

def aiProcess(command):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",  # OpenRouter routes this to GPT-4o-mini
        messages=[
            {"role": "system", "content": "You are a virtual assistant named jarvis, skilled in general tasks like Alexa and Google"},
            {"role": "user", "content": command},
        ],
    )

    return response.choices[0].message.content


def process_command(command):
    if "open google" in command.lower():
        webbrowser.open("https://google.com")
        return "Opening Google."
    elif "open instagram" in command.lower():
        webbrowser.open("https://instagram.com")
        return "Opening Instagram."
    elif "open youtube" in command.lower():
        webbrowser.open("https://youtube.com")
        return "Opening YouTube."
    elif "open linkedin" in command.lower():
        webbrowser.open("https://linkedin.com")
        return "Opening LinkedIn."
    elif command.lower().startswith("play"):
        song = command.lower().replace("play", "").strip()
        if song in musicLibrary.music:
            link = musicLibrary.music[song]
            webbrowser.open(link)
            return f"Playing {song} on YouTube."
        else:
            return f"Sorry, I couldn't find the song '{song}'."
    elif "news" in command.lower():
        r = requests.get(f"https://newsapi.org/v2/everything?q=bitcoin&apiKey={newsapi}")
        data = r.json()
        print(data)
        if data["status"] == "ok":
            news_titles = [article["title"] for article in data["articles"][:3]]
            speak_text = "Here are the top headlines: " + ". ".join(news_titles)
            speak(speak_text)
            return speak_text
        else:
            print("Error:", data)
            return "Sorry, I couldn't fetch the news at the moment."
    elif "exit" in command.lower() or "quit" in command.lower() or "goodbye" in command.lower():
        speak("Goodbye! Shutting down.")
        exit()
    elif command.strip() == "" or len(command.split()) < 2:
        return "Sorry, I didn’t catch a valid command."
    else:
        output = aiProcess(command)
        speak(output)
        return output

def listen_for_command():
    with sr.Microphone() as source:
        print("Jarvis Active...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
        command = recognizer.recognize_google(audio)
        return command

def initialize_jarvis():
    while True:
        try:
            with sr.Microphone() as source:
                print("Initialising Jarvis...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
            
            word = recognizer.recognize_google(audio)
            
            if "jarvis" in word.lower():
                speak("Yeah")
                command = listen_for_command()
                return command
        
        except sr.WaitTimeoutError:
            print("Listening timed out. Initializing again...")
        except sr.UnknownValueError:
            print("Could not understand audio. Initializing again...")
        except sr.RequestError as e:
            print(f"Could not request results; {e}. Initializing again...")
        except Exception as e:
            print(f"Unexpected error: {e}. Initializing again...")

if __name__ == "__main__":
    while True:
        try:
            command = initialize_jarvis()
            if command:
                process_command(command)
        except Exception as e:
            print(f"Error in main loop: {e}")