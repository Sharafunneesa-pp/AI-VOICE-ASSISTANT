import streamlit as st
from openai import OpenAI

def setup_openai_client(api_key):
    return OpenAI(api_key=api_key)

def transcribe_audio(client, audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            # Directly access the text attribute or method
            transcription_text = response['text'] if 'text' in response else 'Transcription text not found'
            return transcription_text
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def fetch_ai_response(client, input_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": input_text}
            ]
        )
        # Extracting the response content
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message['content']
        else:
            return 'No response choices found'
    except Exception as e:
        st.error(f"Error fetching AI response: {str(e)}")
        return None

def text_to_audio(client, text, audio_path):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        with open(audio_path, "wb") as f:
            f.write(response['audio'])
    except Exception as e:
        st.error(f"Error converting text to audio: {str(e)}")

def main():
    st.sidebar.title("API KEY")
    api_key = st.sidebar.text_input("Enter your OpenAI key", type="password")
    st.title("AI Voice Assistant")
    st.write("How can I assist you today?")
    
    if api_key:
        client = setup_openai_client(api_key)
        
        audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg"])
        
        if audio_file is not None:
            with open("uploaded_audio.mp3", "wb") as f:
                f.write(audio_file.getbuffer())
            
            transcribed_text = transcribe_audio(client, "uploaded_audio.mp3")
            if transcribed_text:
                st.write("Transcribed Text: ", transcribed_text)
                ai_response = fetch_ai_response(client, transcribed_text)
                if ai_response:
                    st.write("AI Response: ", ai_response)
                    response_audio_file = "audio_response.mp3"
                    text_to_audio(client, ai_response, response_audio_file)
                    st.audio(response_audio_file)

if __name__ == "__main__":
    main()
