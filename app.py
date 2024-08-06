import streamlit as st
from openai import OpenAI
import pyaudio
import wave
import io
from pydub import AudioSegment
def setup_openai_client(api_key):
    return OpenAI(api_key=api_key)

def convert_wav_to_flac(audio_path):
    try:
        audio = AudioSegment.from_wav(audio_path)
        flac_path = audio_path.replace(".wav", ".flac")
        audio.export(flac_path, format="flac")
        return flac_path
    except Exception as e:
        st.error(f"Error converting audio: {str(e)}")
        return None

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

def fetch_ai_response(client,input_text):
    messages=[{"role":"user","content":input_text}]
    response=client.chat.completions.create(model="gpt-3.5-turbo-1106",messages=messages)
    return response.choices[0].message.content

def text_to_audio(client,text,audio_path):
    response=client.audio.speech.create(model="tts-1",voice="nova",input=text)
    response.stream_to_file(audio_path)



def main():
    st.sidebar.title("API KEY")
    api_key = st.sidebar.text_input("Enter your OpenAI key", type="password")
    st.title("AI Voice Assistant")
    st.write("How can I assist you today?")
    
    if api_key:
        client = setup_openai_client(api_key)
        
        if st.button("Start Recording"):
            # Real-time audio capture using pyaudio
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            RECORD_SECONDS = 5
            WAVE_OUTPUT_FILENAME = "output.wav"

            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            frames = []

            st.write("Recording...")
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            st.write("Finished recording.")

            stream.stop_stream()
            stream.close()
            audio.terminate()

            with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            # Convert WAV to FLAC
            flac_file = convert_wav_to_flac(WAVE_OUTPUT_FILENAME)
            if flac_file:
                transcribed_text = transcribe_audio(client, flac_file)
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
