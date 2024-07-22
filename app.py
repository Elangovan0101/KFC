import streamlit as st
import speech_recognition as sr
import openai
import pandas as pd
from streamlit.components.v1 import html

# Initialize the necessary components
openai.api_key = 'YOUR_API_KEY'
recognizer = sr.Recognizer()

def recognize_speech():
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"Recognized text: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Sorry, the service is down."

def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a drive-in assistant. Help customers with their orders."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.write(f"Error fetching GPT-4 Turbo response: {e}")
        return "Sorry, I'm unable to process your request right now."

def get_menu():
    try:
        # Update this path to the actual path of your CSV file
        menu_df = pd.read_csv('path/to/your/menu.csv')
        # Ensure the CSV columns match your code or adjust the column names accordingly
        menu = menu_df.to_dict(orient='records')
        return menu
    except FileNotFoundError:
        st.write("Menu file not found. Please check the file path.")
        return None
    except pd.errors.EmptyDataError:
        st.write("Menu file is empty.")
        return None
    except pd.errors.ParserError:
        st.write("Error parsing the menu file. Please check the file format.")
        return None
    except Exception as e:
        st.write(f"Error reading menu: {e}")
        return None

def get_item_details(deal_name, menu):
    for item in menu:
        if item['Deal'].lower() == deal_name.lower():
            return item
    return None

# Streamlit app layout
st.title("Voice Assistant Interface")

# Display HTML content
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

html(html_content, height=600)

if st.button("Start Voice Assistant"):
    st.write("Welcome to the drive-in! How can I assist you today?")
    
    order = []
    total_price = 0

    menu = get_menu()
    if not menu:
        st.write("Sorry, I couldn't retrieve the menu at the moment.")
    else:
        while True:
            user_input = recognize_speech()
            if "thank you" in user_input.lower():
                st.write("Goodbye! Have a great day!")
                break

            st.write(f"User input: {user_input}")
            
            if "menu" in user_input.lower():
                menu_text = "Here is our menu: " + ", ".join([item['Deal'] for item in menu])
                st.write(menu_text)
                st.markdown(f"<script>speakText('{menu_text}');</script>", unsafe_allow_html=True)

            elif "price of" in user_input.lower():
                deal_name = user_input.split("price of")[-1].strip()
                item_details = get_item_details(deal_name, menu)
                if item_details:
                    price = item_details['Price (in Rs.)']
                    description = item_details['Description']
                    speech = f"The price of {deal_name} is Rs. {price}. Description: {description}"
                    st.write(speech)
                    st.markdown(f"<script>speakText('{speech}');</script>", unsafe_allow_html=True)
                else:
                    st.write(f"Sorry, I couldn't find the details for {deal_name}.")
                    st.markdown("<script>speakText('Sorry, I couldn\'t find the details for that item.');</script>", unsafe_allow_html=True)

            elif "add" in user_input.lower():
                deal_name = user_input.split("add")[-1].strip()
                item_details = get_item_details(deal_name, menu)
                if item_details:
                    order.append(item_details)
                    price = int(item_details['Price (in Rs.)'])
                    total_price += price
                    speech = f"Added {deal_name} to your order. Your current total is Rs. {total_price}."
                    st.write(speech)
                    st.markdown(f"<script>speakText('{speech}');</script>", unsafe_allow_html=True)
                else:
                    st.write(f"Sorry, I couldn't find {deal_name} on the menu.")
                    st.markdown("<script>speakText('Sorry, I couldn\'t find that item on the menu.');</script>", unsafe_allow_html=True)

            elif "total amount" in user_input.lower():
                speech = f"Your current total order amount is Rs. {total_price}."
                st.write(speech)
                st.markdown(f"<script>speakText('{speech}');</script>", unsafe_allow_html=True)

            else:
                response = chat_with_gpt(user_input)
                st.write(f"GPT-4 Turbo response: {response}")
                st.markdown(f"<script>speakText('{response}');</script>", unsafe_allow_html=True)
