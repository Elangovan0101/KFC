import pyttsx3
import speech_recognition as sr
import mysql.connector
import requests

GEMINI_API_KEY = 'AIzaSyAUGR8InzzEjXgc5AyTnR9kLObx3qYRrvs'

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")
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
        
        # Extract content from the response
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
    db_connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="123456",
        database="kfc_menu_db"
    )
    
    cursor = db_connection.cursor(dictionary=True)
    
    query = 'SELECT * FROM `kfc menu - sheet1`;' 
    cursor.execute(query)
    
    menu_data = cursor.fetchall()
    
    cursor.close()
    db_connection.close()
    
    return menu_data

def get_item_details(deal_name, menu):
    deal_name = deal_name.lower().strip()
    for item in menu:
        item_deal_name = item['Deal'].lower().strip()
        if item_deal_name == deal_name:
            return item
    return None

def main():
    speak_text("Welcome to the KFC drive-in! How can I assist you today?")
    
    order = []
    total_savings = 0

    menu = get_menu()
    if not menu:
        speak_text("Sorry, I couldn't retrieve the menu at the moment.")
        return
    
    while True:
        user_input = recognize_speech()
        if "thank you" in user_input.lower():
            speak_text("Goodbye! Have a great day!")
            break

        print(f"User input: {user_input}")
        
        if "menu" in user_input.lower():
            menu_text = "Here is our menu: " + ", ".join([item['Deal'] for item in menu])
            speak_text(menu_text)

        elif "price" in user_input.lower():
            deal_name = user_input.split("price of")[-1].strip()
            item_details = get_item_details(deal_name, menu)
            if item_details:
                price = item_details['Price (in Rs.)']
                speak_text(f"The price of {deal_name} is Rs. {price}.")
            else:
                speak_text(f"Sorry, I couldn't find the details for {deal_name}.")

        elif "description" in user_input.lower():
            deal_name = user_input.split("description of")[-1].strip()
            item_details = get_item_details(deal_name, menu)
            if item_details:
                description = item_details['Description']
                speak_text(f"The description of {deal_name} is: {description}.")
            else:
                speak_text(f"Sorry, I couldn't find the details for {deal_name}.")

        elif "savings" in user_input.lower():
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
                speak_text(f"Your order includes: {order_summary}. Your total savings for this order is Rs. {total_savings}.")
            else:
                speak_text("You have not added any items to your order yet.")
            break

        else:
            response = chat_with_gemini(user_input)
            print(f"Gemini API response: {response}")
            speak_text(response)
            
            for deal_name in response.split(','):
                deal_name = deal_name.strip()
                item_details = get_item_details(deal_name, menu)
                if item_details:
                    order.append(item_details)
                    savings = item_details.get('Savings', "0")
                    if "Rs." in savings:
                        savings_value = int(''.join(filter(str.isdigit, savings)))
                        total_savings += savings_value
            
if __name__ == "__main__":
    main()
