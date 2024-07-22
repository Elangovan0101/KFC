import threading
import pandas as pd
import requests
import streamlit as st
import pyttsx3
import speech_recognition as sr

# Initialize Pyttsx3 for text-to-speech
engine = pyttsx3.init()

# Initialize Speech Recognition
recognizer = sr.Recognizer()

# Gemini API Key
GEMINI_API_KEY = 'AIzaSyAUGR8InzzEjXgc5AyTnR9kLObx3qYRrvs'

def speak_text(text):
    def tts():
        engine.say(text)
        engine.runAndWait()
    
    # Run the TTS in a separate thread
    thread = threading.Thread(target=tts)
    thread.start()

def recognize_speech():
    try:
        if st.sidebar.checkbox("Use Microphone", True, key="microphone_checkbox"):
            with sr.Microphone() as source:
                st.write("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                st.write(f"Recognized text: {text}")
                return text
    except sr.UnknownValueError:
        return "Sorry, I did not understand that."
    except sr.RequestError:
        return "Sorry, the service is down."

def chat_with_gemini(prompt):
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [{'text': prompt}]
                }
            ]
        }
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        response_json = response.json()
        
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Sorry, I'm unable to process your request right now."
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return "Sorry, I'm unable to process your request right now."
    except Exception as e:
        print(f"Error fetching Gemini API response: {e}")
        return "Sorry, I'm unable to process your request right now."

def get_menu():
    try:
        menu_df = pd.read_csv('kfc menu - Sheet1.csv')
        menu = menu_df.to_dict(orient='records')
        return menu
    except Exception as e:
        st.write(f"Error reading menu: {e}")
        return None

def get_item_details(deal_name, menu):
    deal_name = deal_name.lower().strip()
    for item in menu:
        item_deal_name = item['Deal'].lower().strip()
        if item_deal_name == deal_name:
            return item
    return None

# Streamlit app layout
st.title("Voice Assistant Interface")

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #000;
            color: white;
        }
        .button-container {
            text-align: center;
        }
        .round-button {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background-color: #fff;
            color: #000;
            border: none;
            outline: none;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s, box-shadow 0.3s;
        }
        .round-button:hover {
            background-color: #e0e0e0;
            box-shadow: 0px 6px 8px rgba(0, 0, 0, 0.15);
        }
    </style>
</head>
<body>
<div class="button-container">
    <button class="round-button" onclick="startRecognition()">Speak</button>
    <p id="recognized-text">Press the button and speak...</p>
</div>
<script>
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = function(event) {
        const text = event.results[0][0].transcript;
        document.getElementById('recognized-text').textContent = 'You said: ' + text;
        fetch('/process_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            if (data.speech) {
                speakText(data.speech);
            }
        });
    };
    recognition.onerror = function(event) {
        document.getElementById('recognized-text').textContent = 'Error occurred in recognition: ' + event.error;
    };
    function startRecognition() {
        document.getElementById('recognized-text').textContent = 'Listening...';
        recognition.start();
    }
    function speakText(text) {
        const speechSynthesis = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(text);
        speechSynthesis.speak(utterance);
    }
</script>
</body>
</html>
"""

st.components.v1.html(html_content, height=600)

if st.button("Start Voice Assistant"):
    speak_text("Welcome to the drive-in! How can I assist you today?")
    
    order = []
    total_price = 0

    menu = get_menu()
    if not menu:
        speak_text("Sorry, I couldn't retrieve the menu at the moment.")
    else:
        while True:
            user_input = recognize_speech()
            if "thank you" in user_input.lower():
                speak_text("Goodbye! Have a great day!")
                break

            st.write(f"User input: {user_input}")
            
            if "menu" in user_input.lower():
                menu_text = "Here is our menu: " + ", ".join([item['Deal'] for item in menu])
                speak_text(menu_text)

            elif "price of" in user_input.lower():
                deal_name = user_input.split("price of")[-1].strip()
                item_details = get_item_details(deal_name, menu)
                if item_details:
                    price = item_details['Price (in Rs.)']
                    speak_text(f"The price of {deal_name} is Rs. {price}.")
                else:
                    speak_text(f"Sorry, I couldn't find the details for {deal_name}.")

            elif "description of" in user_input.lower():
                deal_name = user_input.split("description of")[-1].strip()
                item_details = get_item_details(deal_name, menu)
                if item_details:
                    description = item_details['Description']
                    speak_text(f"The description of {deal_name} is: {description}.")
                else:
                    speak_text(f"Sorry, I couldn't find the details for {deal_name}.")

            elif "savings of" in user_input.lower():
                deal_name = user_input.split("savings of")[-1].strip()
                item_details = get_item_details(deal_name, menu)
                if item_details:
                    savings = item_details['Savings']
                    speak_text(f"The savings for {deal_name} is {savings}.")
                else:
                    speak_text(f"Sorry, I couldn't find the details for {deal_name}.")

            elif "complete order" in user_input.lower():
                if order:
                    order_summary = ", ".join([item['Deal'] for item in order])
                    speak_text(f"Your order includes: {order_summary}. Your total savings for this order is Rs. {total_price}.")
                else:
                    speak_text("You have not added any items to your order yet.")
                break

            else:
                response = chat_with_gemini(user_input)
                st.write(f"Gemini API response: {response}")
                speak_text(response)
                
                for deal_name in response.split(','):
                    deal_name = deal_name.strip()
                    item_details = get_item_details(deal_name, menu)
                    if item_details:
                        order.append(item_details)
                        savings = item_details.get('Savings', "0")
                        if "Rs." in savings:
                            savings_value = int(''.join(filter(str.isdigit, savings)))
                            total_price += savings_value
