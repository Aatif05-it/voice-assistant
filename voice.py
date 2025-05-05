import os
import webbrowser
import datetime
import urllib.parse
import requests
import random
import threading
import tkinter as tk
from firebase_setup import login_user
from tkinter import Label, Button, StringVar, OptionMenu, Entry, Toplevel, messagebox
from PIL import Image, ImageTk, ImageSequence
import pyttsx3
import queue
import speech_recognition as sr
import time
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_setup import register_user
from firebase_firestore import add_user, get_user
import auth_system  # To use the login and register functions from auth_system.py

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("C:\\Users\\KHAN\\Desktop\\python_Ass\\firebase_config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize text-to-speech engine
engine = pyttsx3.init()
# Create a Queue to hold speech requests
speech_queue = queue.Queue()
voices = engine.getProperty('voices')
language = "en"  # Default language

# Function to set language and voice
def set_language(lang):
    global language
    language = lang
    if lang == "hi":
        engine.setProperty('voice', voices[0].id)
        speak("भाषा हिंदी में बदल दी गई है")  # Confirm in Hindi
    else:
        engine.setProperty('voice', voices[1].id)
        speak("Language changed to English")  # Confirm in English

# Function to speak the given audio
def speak(audio):
    def run():
        engine.say(audio)
        engine.runAndWait()

    # Create and start a new thread to speak the audio without blocking the main thread
    t = threading.Thread(target=run)
    t.start()
# Function to take a voice command
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        animate_mic(True)  # Start glowing effect
        speak("Listening..." if language == "en" else "सुन रहा हूँ...")  # Announcement in chosen language
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        try:
            audio = r.listen(source, timeout=5)
            query = r.recognize_google(audio, language="hi-IN" if language == "hi" else "en-IN").lower()
            animate_mic(False)  # Stop glowing effect
            return query
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that." if language == "en" else "मुझे समझ नहीं आया")  # Error message in chosen language
            animate_mic(False)
        except sr.RequestError:
            speak("There was an error with the service." if language == "en" else "सर्विस में कोई समस्या है")  # Error message in chosen language
            animate_mic(False)
    return ""

# Function to respond based on voice commands
def assistant_response():
    query = take_command()
    if not query:
        return None  # If no query is recognized

    query = query.lower()

    # ✅ Time and Date Queries
    if "time" in query or "समय" in query:
        return time.strftime("%I:%M %p")

    elif "date" in query or "तारीख" in query:
        return time.strftime("%d %B %Y")

    # ✅ Greetings
    elif any(word in query for word in ["hello", "hi", "hey", "नमस्ते", "हाय"]):
        return "Hello! How can I assist you?" if language == "en" else "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?"

    elif any(word in query for word in ["how are you", "आप कैसे हैं"]):
        return "I'm just a virtual assistant, but I'm great! How about you?" if language == "en" else "मैं एक आभासी सहायक हूँ, लेकिन मैं बहुत अच्छा हूँ! आप कैसे हैं?"

    # ✅ Open Applications (Offline Feature)
    elif "open notepad" in query or "नोटपैड खोलें" in query:
        os.system("notepad")
        return "Opening Notepad." if language == "en" else "नोटपैड खोल रहा हूँ।"

    elif "open calculator" in query or "कैलकुलेटर खोलें" in query:
        os.system("calc")
        return "Opening Calculator." if language == "en" else "कैलकुलेटर खोल रहा हूँ।"

    elif "open command prompt" in query or "कमांड प्रॉम्प्ट खोलें" in query:
        os.system("cmd")
        return "Opening Command Prompt." if language == "en" else "कमांड प्रॉम्प्ट खोल रहा हूँ।"

    # ✅ Web Search
    elif "search for" in query or "खोजें" in query:
        search_query = query.replace("search for", "").replace("खोजें", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        return f"Searching for {search_query} on Google." if language == "en" else f"गूगल पर {search_query} खोज रहा हूँ।"

    elif "open youtube" in query or "यूट्यूब खोलें" in query:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube." if language == "en" else "यूट्यूब खोल रहा हूँ।"

    elif "open google" in query or "गूगल खोलें" in query:
        webbrowser.open("https://www.google.com")
        return "Opening Google." if language == "en" else "गूगल खोल रहा हूँ।"
    
    elif "open whatsapp" in query or "whatsapp खोलें" in query:
        
        # Check if user wants to send a message
        if "send message to" in query and "saying" in query:
            try:
                number = query.split("send message to")[1].split("saying")[0].strip()
                message = query.split("saying")[1].strip()
                encoded_message = urllib.parse.quote(message)
                url = f"https://wa.me/{number}?text={encoded_message}"
                webbrowser.open(url)
                return (
                    f"Sending message to {number}." 
                    if language == "en" else f"{number} को संदेश भेज रहा हूँ।"
                )
            except Exception:
                return (
                    "I couldn't understand the number or message." 
                    if language == "en" else "मैं नंबर या संदेश नहीं समझ सका।"
                )
        else:
            # Default behavior: just open WhatsApp Web
            webbrowser.open("https://web.whatsapp.com")
            return (
                "Opening WhatsApp Web." 
                if language == "en" else "व्हाट्सएप वेब खोल रहा हूँ।"
            )


    # ✅ Weather Query
    elif "weather" in query or "मौसम" in query:
        city = "Delhi"  # Default city (Can be modified to detect user's location)
        api_key = "YOUR_OPENWEATHER_API_KEY"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        try:
            response = requests.get(url)
            data = response.json()
            if data["cod"] == 200:
                temp = data["main"]["temp"]
                weather_desc = data["weather"][0]["description"]
                return f"The weather in {city} is {temp}°C with {weather_desc}." if language == "en" else f"{city} का मौसम {temp}°C है और {weather_desc} है।"
            else:
                return "Sorry, I couldn't fetch the weather data." if language == "en" else "माफ़ कीजिए, मैं मौसम डेटा प्राप्त नहीं कर सका।"
        except:
            return "Unable to connect to the weather service." if language == "en" else "मौसम सेवा से कनेक्ट नहीं हो पा रहा है।"

    # ✅ Set and Show Reminders
    elif "set reminder" in query or "मुझे याद दिलाएं" in query:
        reminder = query.replace("set reminder", "").replace("मुझे याद दिलाएं", "").strip()
        if reminder:
            with open("reminders.txt", "a") as file:
                file.write(reminder + "\n")
            return f"Reminder set: {reminder}" if language == "en" else f"याद दिलाने वाला सेट किया गया: {reminder}"
        else:
            return "Please specify what you want to be reminded about." if language == "en" else "कृपया बताएं कि आपको किस बारे में याद दिलाना है।"

    elif "show reminders" in query or "मेरी यादें दिखाओ" in query:
        try:
            with open("reminders.txt", "r") as file:
                reminders = file.readlines()
            if reminders:
                return "Your reminders: " + ", ".join(reminders).strip() if language == "en" else "आपकी यादें: " + ", ".join(reminders).strip()
            else:
                return "You have no reminders set." if language == "en" else "आपके पास कोई यादें नहीं हैं।"
        except FileNotFoundError:
            return "You have no reminders set." if language == "en" else "आपके पास कोई यादें नहीं हैं।"

    # ✅ Jokes
    elif "tell me a joke" in query or "कोई चुटकुला सुनाओ" in query:
        jokes_en = [
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why don’t scientists trust atoms? Because they make up everything!"
        ]
        jokes_hi = [
            "टीचर: सबसे ज्यादा सफाई कौन करता है? बच्चा: धोबी!",
            "पत्नी: तुम हमेशा देर से क्यों आते हो? पति: क्योंकि वक्त किसी के लिए नहीं रुकता!"
        ]
        return random.choice(jokes_en) if language == "en" else random.choice(jokes_hi)
    
    # ✅ News
    elif "news" in query or "समाचार" in query:
        return "Fetching the latest news..." if language == "en" else "ताज़ा खबरें ला रहा हूँ..."

    # ✅ System Commands
    elif "shutdown" in query or "शटडाउन" in query:
        os.system("shutdown /s /t 1")
        return "Shutting down the system." if language == "en" else "सिस्टम बंद कर रहा हूँ।"

    elif "restart" in query or "रीस्टार्ट" in query:
        os.system("shutdown /r /t 1")
        return "Restarting the system." if language == "en" else "सिस्टम पुनः आरंभ कर रहा हूँ।"

    # ✅ Exit Command
    elif "exit" in query or "बंद करें" in query:
        speak("Goodbye!" if language == "en" else "अलविदा")
        root.destroy()

    # ✅ Default Response
    else:
        return "Command not recognized." if language == "en" else "आदेश पहचाना नहीं गया।"

# Function for microphone button action
def on_listen():
    response = assistant_response()
    if response:
        result_label.config(text=response)

# Function for the login window
def login():
    def authenticate():
        email = username_entry.get()
        password = password_entry.get()
        user_id = login_user(email)
        if user_id:
            messagebox.showinfo("Login Successful", "Welcome back!")
            login_window.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid email or not registered!")
    
    login_window = Toplevel(root)
    login_window.title("Login")
    login_window.geometry("300x200")
    
    Label(login_window, text="Email:").pack()
    username_entry = Entry(login_window)
    username_entry.pack()
    
    Label(login_window, text="Password:").pack()
    password_entry = Entry(login_window, show="*")
    password_entry.pack()
    
    Button(login_window, text="Login", command=authenticate).pack()

# GUI Setup
root = tk.Tk()
root.title("Your Personal Assistant")
root.geometry("400x500")
root.configure(bg="#1e1e2e")  # Dark futuristic theme

# Load Animated Background
bg_image = Image.open("C:\\Users\\KHAN\\Desktop\\python_Ass\\realistic_animated_with_voice_logo.gif")
frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(bg_image)]

canvas = tk.Canvas(root, width=400, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)

bg_label = Label(root)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def animate_background(frame=0):
    bg_label.config(image=frames[frame])
    root.after(100, animate_background, (frame + 1) % len(frames))

animate_background()

# Result Label
result_label = Label(root, text="Welcome!", font=("Arial", 14, "bold"), fg="white", bg="#1e1e2e")
result_label.place(relx=0.5, rely=0.6, anchor="center")

# Language Selection Dropdown
selected_language = StringVar(root)
selected_language.set("English")  # Default selection

def on_language_change(*args):
    set_language("hi" if selected_language.get() == "हिंदी" else "en")

selected_language.trace("w", on_language_change)
language_menu = OptionMenu(root, selected_language, "English", "हिंदी")
language_menu.config(font=("Arial", 12), bg="#444", fg="white", relief="flat")
language_menu.place(relx=0.5, rely=0.9, anchor="center")

# Hindi Button
def change_to_hindi():
    set_language("hi")
    selected_language.set("हिंदी")  # Set dropdown to Hindi
    result_label.config(text="आपका स्वागत है!")  # Display message in Hindi

# Hindi Button
hindi_button = Button(root, text="हिंदी", command=change_to_hindi, font=("Arial", 12), bg="#444", fg="white", relief="flat", padx=10, pady=5)
hindi_button.place(relx=0.3, rely=0.9, anchor="center")

# Animated Microphone Button
def animate_mic(glow):
    if glow:
        mic_button.config(bg="#ff4d4d")  # Glowing red effect
        mic_button.after(500, lambda: mic_button.config(bg="#ff9999"))  # Light glow
    else:
        mic_button.config(bg="#333")

mic_button = Button(root, text="🎤", command=on_listen, font=("Arial", 18), bg="#333", fg="white", relief="flat", padx=10, pady=5)
mic_button.place(relx=0.5, rely=0.75, anchor="center")

# Login Button
login_button = Button(root, text="Login", command=login, font=("Arial", 12), bg="#444", fg="white", relief="flat", padx=10, pady=5)
login_button.place(relx=0.5, rely=0.1, anchor="center")

root.mainloop()
