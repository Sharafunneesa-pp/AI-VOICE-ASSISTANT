import streamlit as st
from openai import OpenAI
# import pyaudio
# from dotenv import load_dotenv
from openai import OpenAI
import os
from audio_recorder_streamlit import audio_recorder
# load_dotenv()
from audio_recorder_streamlit import audio_recorder

# OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
# openai_client = OpenAI(api_key=OPENAI_API_KEY)

def setup_openai_client(api_key):
    return OpenAI(api_key=api_key)

def transcribe_audio(client, audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            # Inspect the response structure
            if 'text' in response:
                return response['text']
            elif hasattr(response, 'text'):
                return response.text
            else:
                return 'Transcription text not found'
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None





def setup_openai_client(api_key):
    return OpenAI(api_key=api_key)

sys_msg = ( 'you are a multimodal AI voice assistant. Your user may request assistance for cooking '
    ' Generate the most useful and stop after first instruction and say once you completed this let me know and continue after user response '
    'factual response possible, carefully considering all previous generated text in your response before '
    'adding new tokens to the response.  just use the context if added. '
    'Use all of the context of this conversation so your response is relevant to the conversation. Make '
    'your responses clear and concise, avoiding any verbosity.')

messages = [{'role': 'system', 'content': sys_msg}]


def fetch_ai_response(client,input_text):
    messages.append({"role":"user","content":input_text})
    chat_completion=client.chat.completions.create(model="gpt-3.5-turbo-1106",messages=messages)
    response = chat_completion.choices[0].message
    messages.append(response)
    return response.content



def speak(text,client):
    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
    stream_start = False

    with client.audio.speech.with_streaming_response.create(
            model='tts-1',
            voice='onyx',
            response_format='pcm',
            input=text,
    ) as response:
        silence_threshold = 0.01
        for chunk in response.iter_bytes(chunk_size=1024):
            if stream_start:
                player_stream.write(chunk)
            else:
                if max(chunk) > silence_threshold:
                    player_stream.write(chunk)
                    stream_start = True


def main():
    st.sidebar.title("API KEY")
    api_key = st.sidebar.text_input("Enter your OpenAI key", type="password")
    st.title("AI Voice Assistant")
    st.write("How can I assist you today?")
    
    if api_key:
        client = setup_openai_client(api_key)
        recorded_audio=audio_recorder()
        if recorded_audio:
                audio_file="audio.mp3"
                with open(audio_file,"wb") as f:
                    f.write(recorded_audio)
        
                transcribed_text = transcribe_audio(client, audio_file)
                st.write("Transcribed Text: ", transcribed_text)
                ai_response = fetch_ai_response(client, transcribed_text)
                st.write("AI Response: ", ai_response)
                speak(ai_response,client)

if __name__ == "__main__":
    main()

