import streamlit as st
from openai import OpenAI
import base64
import os
from audio_recorder_streamlit import audio_recorder

def setup_openai_client(api_key):
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Error setting up OpenAI client: {str(e)}")
        return None

def transcribe_audio(client, audio_path):
    try:
        if client is None:
            raise ValueError("OpenAI client is not initialized")
        
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            if 'text' in response:
                return response['text']
            elif hasattr(response, 'text'):
                return response.text
            else:
                return 'Transcription text not found'
    except Exception as e:
        st.error(f" Your audio is too short.")
        return None

sys_msg = (
    'You are a multimodal AI voice assistant. Your user may request assistance for cooking. '
    'Answer for cooking or food related questions only. '
    'Generate the most useful and stop after the first instruction and say once you completed this let me know and continue after user response. '
    'Provide a factual response, carefully considering all previous generated text in your response before '
    'adding new tokens to the response. Just use the context if added. '
    'Use all of the context of this conversation so your response is relevant to the conversation. Make '
    'your responses clear and concise, avoiding any verbosity.'
)

if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'system', 'content': sys_msg}]
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

def fetch_ai_response(client, input_text):
    try:
        st.session_state.messages.append({"role": "user", "content": input_text})
        chat_completion = client.chat.completions.create(model="gpt-3.5-turbo-1106", messages=st.session_state.messages)
        response = chat_completion.choices[0].message
        st.session_state.messages.append(response)
        return response.content
    except Exception as e:
        st.error(f"Error fetching AI response: {str(e)}")
        return "Sorry, I couldn't process your request."

def speak(client, text, audio_path):
    try:
        response = client.audio.speech.create(model="tts-1", voice="onyx", input=text)
        if hasattr(response, 'with_streaming_response'):
            with response.with_streaming_response() as streaming_response:
                with open(audio_path, "wb") as audio_file:
                    for chunk in streaming_response.iter_content(chunk_size=1024):
                        audio_file.write(chunk)
        else:
            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.content)
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")

def auto_play_audio(audio_file):
    try:
        with open(audio_file, "rb") as audio_file:
            audio_bytes = audio_file.read()
        base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error playing audio: {str(e)}")

def create_text_card(text, title="Response"):
    try:
        card_html = f"""
        <style>
        .card {{
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: 0.3s;
            border-radius: 15px;
            padding: 20px;
            background-color: #ffffff;
            margin: 20px 0;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
            border: 1px solid #e0e0e0;
        }}
        .card:hover {{
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
        }}
        .container {{
            padding: 16px;
        }}
        .card-title {{
            background: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
            padding: 15px;
            border-radius: 15px 15px 0 0;
            font-size: 24px;
            text-align: center;
            font-weight: bold;
        }}
        .card-text {{
            font-size: 18px;
            color: #555;
            line-height: 1.8;
            text-align: justify;
        }}
        .card-footer {{
            margin-top: 20px;
            text-align: right;
            font-size: 14px;
            color: #999;
        }}
        </style>
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="container">
                <p class="card-text">{text}</p>
            </div>
            <div class="card-footer">Chef Mate: Ur cooking assistant 👨‍🍳 </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error creating text card: {str(e)}")

def main():
    try:
        st.sidebar.title("API KEY")
        api_key = st.sidebar.text_input("Enter your OpenAI key", type="password")
        st.title("AI Voice Assistant")
        st.write("How can I assist you today?")
        
        if api_key:
            client = setup_openai_client(api_key)
            if client is None:
                return

            recorded_audio = audio_recorder()
            if recorded_audio:
                audio_file = "audio.mp3"
                with open(audio_file, "wb") as f:
                    f.write(recorded_audio)
                
                transcribed_text = transcribe_audio(client, audio_file)
                if transcribed_text:
                    create_text_card(transcribed_text, "USER")
                    st.session_state.current_chat.append({"role": "user", "content": transcribed_text})

                    ai_response = fetch_ai_response(client, transcribed_text)
                    response_audio = "audio_res.mp3"
                    speak(client, ai_response, response_audio)
                    auto_play_audio(response_audio)
                    create_text_card(ai_response, "CHEFMATE")
                    st.session_state.current_chat.append({"role": "assistant", "content": ai_response})

            # Display chat history
            for message in st.session_state.current_chat:
                create_text_card(message["content"], message["role"].upper())
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
