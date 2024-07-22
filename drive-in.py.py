import pyttsx3
import speech_recognition as sr
import requests
  
import openai

openai.api_key = 'YOUR API KEY'  
engine = pyttsx3.init()

recognizer = sr.Recognizer()

API_URL = "https://api.sheety.co/52fe1c86580a796963266ef1048a4dce/kfcMenu/sheet1"

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
        print(f"Error fetching GPT-4 Turbo response: {e}")
        return "Sorry, I'm unable to process your request right now."

def get_menu():
    response = requests.get("https://api.sheety.co/52fe1c86580a796963266ef1048a4dce/kfcMenu/sheet1")
    print(f"GET /sheet1 status code: {response.status_code}")
    print(f"Response content: {response.content}")
    if response.status_code == 200:
        return response.json().get('sheet1', [])
    return None

def get_item_details(deal_name, menu):
    for item in menu:
        if item['deal'].lower() == deal_name.lower():
            return item
    return None

def main():
    speak_text("Welcome to the drive-in! How can I assist you today?")
    
    order = []
    total_price = 0

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
            menu_text = "Here is our menu: " + ", ".join([item['deal'] for item in menu])
            speak_text(menu_text)

        elif "price of" in user_input.lower():
            deal_name = user_input.split("price of")[-1].strip()
            item_details = get_item_details(deal_name, menu)
            if item_details:
                price = item_details['price (inRs.)']
                description = item_details['description']
                speak_text(f"The price of {deal_name} is Rs. {price}. Description: {description}")
            else:
                speak_text(f"Sorry, I couldn't find the details for {deal_name}.")

        elif "add" in user_input.lower():
            deal_name = user_input.split("add")[-1].strip()
            item_details = get_item_details(deal_name, menu)
            if item_details:
                order.append(item_details)
                price = int(item_details['price (inRs.)'])
                total_price += price
                speak_text(f"Added {deal_name} to your order. Your current total is Rs. {total_price}.")
            else:
                speak_text(f"Sorry, I couldn't find {deal_name} on the menu.")

        elif "total amount" in user_input.lower():
            speak_text(f"Your current total order amount is Rs. {total_price}.")

        else:
            response = chat_with_gpt(user_input)
            print(f"GPT-4 Turbo response: {response}")
            speak_text(response)

if __name__ == "__main__":
    main()
