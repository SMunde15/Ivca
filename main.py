

from flask import Flask, request, jsonify
import pyttsx3
import speech_recognition as sr
import webbrowser
import tempfile
import requests
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import HarmCategory, HarmBlockThreshold
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Vertex AI
vertexai.init(project="jarvis-ai-420609", location="us-central1")

@app.route('/process_command', methods=['POST'])
def process_command():
    data = request.json.get('data', '')
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    response_text = handle_command(data.lower())
    return jsonify({'response': response_text})


def handle_command(text):
    if "google" in text:
        return process_search_command(text, "google")
    elif "youtube" in text:
        return process_search_command(text, "youtube")
    elif "wikipedia" in text:
        return process_search_command(text, "wikipedia")
    elif "spotify" in text:
        return process_search_command(text, "spotify")
    elif "code" in text or "program" in text or "ivca" in text:
        return process_code_generation(text)
    return "No valid command was found in the text."

def process_search_command(text, service):
    try:
        service_index = text.index(service) + len(service)
        search_query = text[service_index:].strip()
        if search_query:
            if service == "google":
                url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            elif service == "youtube":
                url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}&autoplay=1"
            elif service == "wikipedia":
                url = f"https://en.wikipedia.org/wiki/{search_query.replace(' ', '_')}"
            elif service == "spotify":
                url = f"https://open.spotify.com/search/{search_query.replace(' ', '%20')}"
            return f"I have generated a URL for {service.capitalize()} search: {url}"
        else:
            return f"You mentioned {service.capitalize()}, but no search query was provided."
    except ValueError:
        return f"The command to search on {service.capitalize()} was not clear."



def process_code_generation(text):
    command_start = max(text.find("code"), text.find("program"), text.find("ivca"))
    query = text[command_start:].split(maxsplit=1)[1] if len(text[command_start:].split()) > 1 else ""
    response = generate_response(query)
    if response:
        return "Here is what I generated: " + response
    else:
        return "I was unable to generate any code."

def generate_response(user_input):
    model = GenerativeModel("gemini-1.5-pro-preview-0409")
    generation_config = {
        "max_output_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.95
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
    try:
        response = model.generate_content(
            user_input,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False
        )
        return response.text
    except Exception as e:
        return f"Error during response generation: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)





# import os
# import datetime
# import webbrowser
# import pyttsx3
# import speech_recognition as sr
# import vertexai
# import requests
# import tempfile
# from vertexai.generative_models import GenerativeModel
# from vertexai.generative_models import HarmCategory, HarmBlockThreshold
#
#
# vertexai.init(project="jarvis-ai-420609", location="us-central1")
#
#
# def process_audio_from_url(audio_url):
#     try:
#         response = requests.get(audio_url)
#         response.raise_for_status()  # Check that the request was successful
#         with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
#             tmp_file.write(response.content)
#             tmp_file_path = tmp_file.name
#         # Process the downloaded audio file
#         text = recognize_speech_from_file(tmp_file_path)
#         if text:
#             handle_command(text)
#         else:
#             say("I couldn't understand the command from the audio file.")
#         # Remove the temporary file after processing
#         os.remove(tmp_file_path)
#     except requests.RequestException as e:
#         print(f"Failed to download audio file: {e}")
#         say("Failed to download audio from the provided URL.")
#     except OSError as e:
#         print(f"Error deleting temporary file: {e}")
#
# def recognize_speech_from_file(audio_file_path):
#     r = sr.Recognizer()
#     try:
#         with sr.AudioFile(audio_file_path) as source:
#             audio = r.record(source)  # read the entire audio file
#         text = r.recognize_google(audio)
#         print(f"Recognized Text: {text}")
#         return text.lower()
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand the audio")
#         return None
#     except sr.RequestError as e:
#         print(f"Could not request results from Google Speech Recognition service; {e}")
#         return None
#
# def handle_command(text):
#     if "google" in text:
#         process_search_command(text, "google")
#     elif "youtube" in text:
#         process_search_command(text, "youtube")
#     elif "wikipedia" in text:
#         process_search_command(text, "wikipedia")
#     elif "spotify" in text:
#         process_search_command(text, "spotify")
#     elif "code" in text or "program" in text or "ivca" in text:
#         process_code_generation(text)
#     else:
#         say("No valid command was found in the audio.")
#
#
# def process_search_command(text, service):
#     try:
#         service_index = text.index(service) + len(service)
#         search_query = text[service_index:].strip()
#         if search_query:
#             if service == "google":
#                 url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
#             elif service == "youtube":
#                 url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
#             elif service == "wikipedia":
#                 url = f"https://en.wikipedia.org/wiki/{search_query.replace(' ', '_')}"
#             elif service == "spotify":
#                 url = f"https://open.spotify.com/search/{search_query.replace(' ', '%20')}"
#
#             webbrowser.open(url)
#             say(f"I have opened {service.capitalize()} for your search: {search_query}")
#         else:
#             say(f"You mentioned {service.capitalize()}, but I did not catch what to search for.")
#     except ValueError:
#         say(f"The command to search on {service.capitalize()} was not clear.")
#
#
# def process_code_generation(text):
#     command_start = text.find("code") if "code" in text else text.find("program") if "program" in text else text.find(
#         "ivca")
#     query = text[command_start:].split(maxsplit=1)[1] if len(text[command_start:].split()) > 1 else ""
#     response = generate_response(query)
#     if response:
#         say("Here is the what I generated:")
#         print("Generated Code:", response)
#     else:
#         say("I was unable to generate any code.")

#
# def generate_response(user_input):
#     model = GenerativeModel("gemini-1.5-pro-preview-0409")  # example model, adjust as necessary
#     generation_config = {
#         "max_output_tokens": 500,
#         "temperature": 0.7,
#         "top_p": 0.95
#     }
#     safety_settings = {
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#         HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#     }
#     try:
#         response = model.generate_content(
#             user_input,
#             generation_config=generation_config,
#             safety_settings=safety_settings,
#             stream=False
#         )
#         return response.text  # Assuming generate_content returns a GenerationResponse object directly
#     except Exception as e:
#         print(f"Error during response generation: {e}")
#         return None
#
#
# def say(text):
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()
#
#
# if __name__ == '__main__':
#     audio_url = input("Please provide the URL to the audio file: ")
#     process_audio_from_url(audio_url)
