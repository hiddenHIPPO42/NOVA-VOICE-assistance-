import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import random
import requests
import json
import re
from datetime import timedelta
from openai import OpenAI

# =========================
# API KEYS & INITIAL SETUP
# =========================

# pyttsx3 TTS
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170)

# OpenAI API
OPENAI_API_KEY = "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"
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    openai_client = None

# =========================
# CORE FUNCTIONS
# =========================

def speak(audio):
    """Speak text using pyttsx3."""
    engine.say(audio)
    engine.runAndWait()

def get_openai_response(query):
    """Get tactical AI response from OpenAI API."""
    if not openai_client:
        return "OpenAI client not initialized."
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Nova, a tactical AI assistant inspired by Iron Man's sidekick, delivering precise, strategic, and witty responses."},
                {"role": "user", "content": query}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def wishMe():
    """Tactical greetings."""
    hour = int(datetime.datetime.now().hour)
    tactical_greetings = {
        (0, 12): [
            "Dawn briefing: Nova online, ready for action, Commander!",
            "Morning ops initiated. What's the mission today, sir?",
            "Systems locked and loaded. Awaiting your orders!"
        ],
        (12, 18): [
            "Midday status: Nova at full capacity, ready to execute, sir!",
            "Afternoon recon complete. What's the next objective, Commander?",
            "Strategic systems primed. Your orders, please!"
        ],
        (18, 24): [
            "Night watch active: Nova reporting for duty, sir!",
            "Evening ops engaged. Ready for your commands, Commander!",
            "Tactical systems online. What's the plan?"
        ]
    }
    for time_range, greetings in tactical_greetings.items():
        if time_range[0] <= hour < time_range[1]:
            speak(random.choice(greetings))
            break
    speak("I am Nova, your tactical AI assistant, powered by OpenAI. Systems ready—how can I assist you today?")

def takeCommand():
    """Listen and recognize voice commands."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            speak("No input detected. Standing by for your orders.")
            return "None"

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Unable to process transmission. Please repeat, Commander.")
        return "None"
    except sr.RequestError as e:
        speak("Comms error with speech service.")
        return "None"

def sendEmail(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('youremail@gmail.com', 'your-password')
        server.sendmail('youremail@gmail.com', to, content)
        server.close()
        speak("Communication dispatched successfully!")
    except Exception as e:
        print(e)
        speak("Unable to send communication.")

def get_weather(city):
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(base_url)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            speak(f"Sitrep for {city}: {weather}, temperature {temp} degrees Celsius.")
        else:
            speak("Unable to retrieve weather data.")
    except Exception as e:
        print(e)
        speak("Error in weather recon.")

def get_news():
    api_key = "YOUR_NEWSAPI_KEY"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        articles = response.json()["articles"][:3]
        speak("Delivering priority news brief:")
        for i, article in enumerate(articles, 1):
            speak(f"Headline {i}: {article['title']}")
    except Exception as e:
        print(e)
        speak("Unable to retrieve news brief.")

def set_reminder(task, minutes):
    speak(f"Locking in reminder for {task} in {minutes} minutes.")
    # Actual timer function can be added here.

def open_application(app_name):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe"
    }
    if app_name in apps:
        os.startfile(apps[app_name])
        speak(f"Deploying {app_name} now.")
    else:
        speak(f"No protocol found for {app_name}.")

def process_query(query):
    if 'wikipedia' in query:
        speak('Initiating Wikipedia recon...')
        query = query.replace("wikipedia", "").strip()
        try:
            results = wikipedia.summary(query, sentences=2)
            speak("Intel from Wikipedia:")
            print(results)
            speak(results)
        except wikipedia.exceptions.DisambiguationError:
            speak("Multiple targets detected.")
        except wikipedia.exceptions.PageError:
            speak("No data found.")

    elif 'open youtube' in query:
        webbrowser.open("https://www.youtube.com")
        speak("Deploying YouTube interface.")

    elif 'open google' in query:
        webbrowser.open("https://www.google.com")
        speak("Launching Google systems.")

    elif 'open stackoverflow' in query:
        webbrowser.open("https://stackoverflow.com")
        speak("Accessing StackOverflow network.")

    elif 'play music' in query:
        music_dir = 'D:\\Non Critical\\songs\\Favorite Songs2'
        if os.path.exists(music_dir):
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, random.choice(songs)))
                speak("Initiating audio playback.")
            else:
                speak("No audio files detected.")
        else:
            speak("Music directory not found.")

    elif 'what is the time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"Current time: {strTime} hours.")

    elif 'email to' in query:
        try:
            recipient = re.search(r'email to (\w+)', query).group(1)
            speak("What's the message content, Commander?")
            content = takeCommand()
            sendEmail(f"{recipient}@gmail.com", content)
        except Exception as e:
            print(e)
            speak("Unable to process communication.")

    elif 'weather in' in query:
        city = query.replace("weather in", "").strip()
        get_weather(city)

    elif 'tell me news' in query:
        get_news()

    elif 'set reminder' in query:
        match = re.search(r'reminder for (.*?)(?: in (\d+) minutes)?', query)
        if match:
            task_name = match.group(1)
            minutes = match.group(2) if match.group(2) else "10"
            set_reminder(task_name, minutes)

    elif 'open' in query:
        app = query.replace("open", "").strip()
        open_application(app)

    elif 'who are you' in query:
        speak("I am Nova, tactical AI assistant, inspired by JARVIS.")

    elif 'shutdown' in query or 'exit' in query:
        speak("Powering down, Commander!")
        return False

    else:
        openai_response = get_openai_response(query)
        if openai_response:
            speak(openai_response)
            print(f"Nova: {openai_response}")
        else:
            speak("Unable to process request.")

    return True

# =========================
# MAIN PROGRAM
# =========================

if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand()
        if query != "None":
            if not process_query(query):
                break