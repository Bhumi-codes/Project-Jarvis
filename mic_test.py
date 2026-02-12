import speech_recognition as sr

import speech_recognition as sr

mics = sr.Microphone.list_microphone_names()
for i, mic in enumerate(mics):
    print(i, mic)
