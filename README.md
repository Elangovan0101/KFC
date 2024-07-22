# Drive-in-VoiceAssistant
This is a voice-interactive drive-in assistant application that uses speech recognition, text-to-speech, and the GPT-4 Turbo model to help customers with their orders at a drive-in. The application retrieves the menu from an API and processes voice commands to interact with customers.
## Features
- Speech recognition for understanding customer commands.
- Text-to-speech for interacting with customers.
- Integration with GPT-4 Turbo for handling complex queries.
- Fetches and displays the menu from a specified API.
- Provides item details and handles order placement.
- Calculates and announces the total order amount.
## Requirements

- Python 3.7 or higher
- `pyttsx3` for text-to-speech
- `speech_recognition` for recognizing speech
- `requests` for API calls
- `openai` for interacting with the GPT-4 Turbo model
## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/drive-in-assistant.git
    cd drive-in-assistant
    ```

2. Install the required packages:
    ```bash
    pip install pyttsx3 SpeechRecognition requests openai
    ```

## Configuration

1. Set your OpenAI API key:
    ```python
    openai.api_key = 'your-openai-api-key'
    ```

2. Ensure your API URL for fetching the menu is correct:
    ```python
    API_URL = "https://api.sheety.co/52fe1c86580a796963266ef1048a4dce/kfcMenu/sheet1"
    ```

## Usage

Run the main script to start the drive-in assistant:

```bash
python main.py

## Example Interaction

*Assistant: "Welcome to the drive-in! How can I assist you today?"
*User: "Show me the menu."
*Assistant: "Here is our menu: [List of items]."
*User: "Price of Zinger Burger."
*Assistant: "The price of Zinger Burger is Rs. 250. Description: A delicious chicken burger."
*User: "Add Zinger Burger."
*Assistant: "Added Zinger Burger to your order. Your current total is Rs. 250."
*User: "Total amount."
*Assistant: "Your current total order amount is Rs. 250."
*User: "Thank you."
*Assistant: "Goodbye! Have a great day!"



Make sure to replace the placeholder URL and API key with the actual values you are using. This `README.md` file provides an overview, installation instructions, configuration details, usage guide, and example interactions for your drive-in assistant project.

