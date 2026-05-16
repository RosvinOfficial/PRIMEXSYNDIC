import speech_recognition as sr
import asyncio
import edge_tts
from playsound import playsound

VOICE = "en-US-GuyNeural"

recognizer = sr.Recognizer()

async def speak(text):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE
    )

    await communicate.save("voice.mp3")

    playsound("voice.mp3")

while True:

    try:

        with sr.Microphone() as source:

            print("Listening...")

            recognizer.adjust_for_ambient_noise(source)

            audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio)

            print("You said:", text)

            if "hello" in text.lower():

                asyncio.run(
                    speak("Hello sir, how can I help you?")
                )

            elif "time" in text.lower():

                asyncio.run(
                    speak("I cannot access real time yet.")
                )

            elif "stop" in text.lower():

                asyncio.run(
                    speak("Goodbye sir.")
                )

                break

            else:

                asyncio.run(
                    speak(
                        "I heard you say " + text
                    )
                )

    except Exception as e:

        print(e)