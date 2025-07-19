import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipediaapi
import os
import subprocess
import requests
import time
import threading
import cv2

engine = pyttsx3.init()
wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='MyBot/1.0 (saisanga@gmail.com)',
    language='en'
)

# Speak function
def speak(text):
    print("Bot:", text)
    engine.say(text)
    engine.runAndWait()

# Greet based on time
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("Say Shiva followed by your command. How can I help you?")

# Listen to voice command
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        command = r.recognize_google(audio, language='en-in')
        print(f"You said: {command}")
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I didn't catch that. Please repeat.")
        return "none"
    return command.lower()

# Wikipedia summary
def fetch_wikipedia(query):
    page = wiki_wiki.page(query)
    if page.exists() and page.summary:
        speak(page.summary[:400])
    else:
        speak("Sorry, I couldn't find that on Wikipedia.")

# Weather feature
def get_weather(city):
    api_key = "ef55cfc9da5b603183c0da80501f6e40"  # Replace with your OpenWeatherMap API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(base_url)
        data = response.json()
        if data["cod"] != "404":
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The weather in {city} is {desc} with a temperature of {temp} degrees Celsius.")
        else:
            speak("City not found.")
    except Exception as e:
        print(f"Error: {e}")
        speak("Unable to retrieve weather data right now.")

# Reminder feature
def set_reminder(message, delay_sec):
    def reminder():
        time.sleep(delay_sec)
        speak(f"Reminder: {message}")
    threading.Thread(target=reminder).start()

# OpenCV feature: face detection
def detect_face():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    speak("Face detection started. Press Q to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.imshow('Face Detection - Press Q to exit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    speak("Face detection ended.")

# Execute commands
def executeCommand(command):
    if 'open google' in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google")
    elif 'open youtube' in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")
    elif 'wikipedia' in command:
        topic = command.replace("wikipedia", "").strip()
        if topic:
            fetch_wikipedia(topic)
        else:
            speak("Please tell me what you want to search on Wikipedia.")
    elif 'time' in command:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")
    elif 'shutdown' in command:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 1")
    elif 'restart' in command:
        speak("Restarting the system.")
        os.system("shutdown /r /t 1")
    elif 'lock' in command:
        speak("Locking the system.")
        subprocess.call('rundll32.exe user32.dll,LockWorkStation')
    elif 'weather in' in command:
        city = command.replace('weather in', '').strip()
        get_weather(city)
    elif 'set reminder' in command:
        speak("What should I remind you about?")
        reminder_text = takeCommand()
        if reminder_text == "none":
            return
        speak("In how many seconds should I remind you?")
        delay = takeCommand()
        if delay.isdigit():
            set_reminder(reminder_text, int(delay))
            speak(f"Reminder set for {delay} seconds.")
        else:
            speak("Sorry, I couldn't understand the time delay.")
    elif 'detect face' in command or 'open camera' in command:
        detect_face()
    elif 'exit' in command or 'quit' in command:
        speak("Goodbye!")
        exit()
    else:
        speak("I didn't understand that command.")

# Main
if __name__ == "__main__":
    wishMe()
    try:
        while True:
            query = takeCommand()
            if query == "none":
                continue
            if 'shiva' in query:
                query = query.replace("shiva", "").strip()
                executeCommand(query)
            else:
                speak("Please start your command with 'Shiva'")
    except KeyboardInterrupt:
        speak("Exiting. Have a nice day!")
