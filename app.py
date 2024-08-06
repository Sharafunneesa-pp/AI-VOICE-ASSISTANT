import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64


# Design

def setup_openai_client(api_key):
    return openai.OpenAI(api_key=api_key)

def transcribe_audio(client, audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
    except openai.error.OpenAIError as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def fetch_ai_response(client, input_text):
    try:
        messages = [{"role": "user", "content": input_text}]
        response = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=messages)
        return response.choices[0].message.content
    except openai.error.OpenAIError as e:
        st.error(f"Error fetching AI response: {str(e)}")
        return None

def text_to_audio(client, text, audio_path):
    try:
        response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
        response.stream_to_file(audio_path)
    except openai.error.OpenAIError as e:
        st.error(f"Error converting text to audio: {str(e)}")

def main():
    st.sidebar.title("API KEY")
    api_key = st.sidebar.text_input("Enter your OpenAI key", type="password")
    st.title("Start Speaking")
    st.write("How can I assist you today?")
    if api_key:
        client = setup_openai_client(api_key)
        recorded_audio = audio_recorder()
        if recorded_audio:
            audio_file = "audio.mp3"
            with open(audio_file, "wb") as f:
                f.write(recorded_audio)
            transcribed_text = transcribe_audio(client, audio_file)
            if transcribed_text:
                st.write("Transcribed Text: ", transcribed_text)
                ai_response = fetch_ai_response(client, transcribed_text)
                if ai_response:
                    response_audio_file = "audio_response.mp3"
                    text_to_audio(client, ai_response, response_audio_file)
                    st.audio(response_audio_file)
                    st.write("AI Response: ", ai_response)

if __name__ == "__main__":
    main()
