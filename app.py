import streamlit as st
import openai

# Design

def setup_openai_client(api_key):
    openai.api_key = api_key

def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)
            return transcript['text']
    except Exception as e:  # Use a general exception for debugging purposes
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def fetch_ai_response(input_text):
    try:
        messages = [{"role": "user", "content": input_text}]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        return response.choices[0].message['content']
    except Exception as e:  # Use a general exception for debugging purposes
        st.error(f"Error fetching AI response: {str(e)}")
        return None

def text_to_audio(text, audio_path):
    try:
        response = openai.Audio.create(model="tts-1", voice="nova", input=text)
        with open(audio_path, "wb") as f:
            f.write(response['audio'])
    except Exception as e:  # Use a general exception for debugging purposes
        st.error(f"Error converting text to audio: {str(e)}")

def main():
    st.sidebar.title("API KEY")
    api_key = st.sidebar.text_input("Enter your OpenAI key", type="password")
    st.title("AI Voice Assistant")
    st.write("How can I assist you today?")
    
    if api_key:
        setup_openai_client(api_key)
        
        audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg"])
        
        if audio_file is not None:
            with open("uploaded_audio.mp3", "wb") as f:
                f.write(audio_file.getbuffer())
            
            transcribed_text = transcribe_audio("uploaded_audio.mp3")
            if transcribed_text:
                st.write("Transcribed Text: ", transcribed_text)
                ai_response = fetch_ai_response(transcribed_text)
                if ai_response:
                    response_audio_file = "audio_response.mp3"
                    text_to_audio(ai_response, response_audio_file)
                    st.audio(response_audio_file)
                    st.write("AI Response: ", ai_response)

if __name__ == "__main__":
    main()
