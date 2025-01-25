import simpleaudio as sa
from google.cloud import texttospeech
import itertools
from google import genai
from google.genai import types
import vertexai
import streamlit as st, os
from audio_recorder_streamlit import audio_recorder
from google.cloud import speech


def page_setup():
    st.header("Use a voice bot to interact with your PDF file!", anchor=False, divider="blue")

    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.sidebar.markdown("Streaming Version")


def get_choice():
    choice = st.sidebar.radio("Choose:", ["Text 2 Audio",
                                          "Audio 2 Audio",
                                          ],)
    st.sidebar.divider()
    return choice


def run_streaming_tts(textsample):
    client2 = texttospeech.TextToSpeechClient()

    streaming_config = texttospeech.StreamingSynthesizeConfig(voice=texttospeech.VoiceSelectionParams(name="en-US-Journey-D", language_code="en-US"))

    config_request = texttospeech.StreamingSynthesizeRequest(streaming_config=streaming_config)

    def request_generator(textsample):
        yield texttospeech.StreamingSynthesizeRequest(input=texttospeech.StreamingSynthesisInput(text=textsample))
        

    streaming_responses = client2.streaming_synthesize(itertools.chain([config_request], request_generator(textsample)))
    for response in streaming_responses:
        fs = 24000
        play_obj = sa.play_buffer(response.audio_content, 1, 2, fs)
        play_obj.wait_done()


def main():
    
    choice = get_choice()
    
    uploaded_files = st.file_uploader("Choose your pdf file",  accept_multiple_files=False)
    if uploaded_files:
        file_name=uploaded_files.name
        file_upload = client.files.upload(path=file_name)

        if choice == 'Text 2 Audio':
            prompt = st.chat_input("What is your question?")
            if prompt:
                
                with st.chat_message("user"):
                    st.write(prompt)
            
                with st.chat_message("model", avatar="🧞‍♀️",):
                   for chunk in client.models.generate_content_stream(
                       model=MODEL_ID,
                       config=types.GenerateContentConfig(
                       system_instruction="You are a helpful assistant. Your answers need to be brief and concise.",
                       temperature=1.0,
                       top_p=0.95,
                       top_k=20,
                       max_output_tokens=100,
                       ),
                       contents=[
                           types.Content(
                               role="user",
                               parts=[
                                   types.Part.from_uri(
                                       file_uri=file_upload.uri,
                                       mime_type=file_upload.mime_type),
                                   ]),
                           prompt,]
                   ):
                       run_streaming_tts(chunk.text)

    
        elif choice == 'Audio 2 Audio':
            audio_bytes = audio_recorder(recording_color="#6aa36f", neutral_color="#e82c58")
            if audio_bytes:
                
                audio = speech.RecognitionAudio(content=audio_bytes)
    
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    #sample_rate_hertz=44100,
                    language_code="en-US",
                    model="default",
                    audio_channel_count=2,
                    enable_word_confidence=True,
                    enable_word_time_offsets=True,
                )
    
                operation = client3.long_running_recognize(config=config, audio=audio)
    
                conversion = operation.result(timeout=90)
                
                for result in conversion.results:
                  pass
                  
                prompt = (result.alternatives[0].transcript)
                
                for chunk in client.models.generate_content_stream(
                    model=MODEL_ID,
                    config=types.GenerateContentConfig(
                    system_instruction="You are a helpful assistant. Your answers need to be brief and concise.",
                    temperature=1.0,
                    top_p=0.95,
                    top_k=20,
                    max_output_tokens=100,
                    ),
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_uri(
                                    file_uri=file_upload.uri,
                                    mime_type=file_upload.mime_type),
                                ]),
                        prompt,]
                ):
                    
                    run_streaming_tts(chunk.text)
                    
 

if __name__ == "__main__":
    page_setup()
    projectid = os.environ.get('GOOG_PROJECT')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY_NEW')
    client = genai.Client(api_key=GOOGLE_API_KEY)
    MODEL_ID = "gemini-2.0-flash-exp"
    vertexai.init(project=projectid, location="us-central1")
    main()
