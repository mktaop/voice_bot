#pip install google-genai
#pip install google-cloud-speech
import streamlit as st, os, base64, time
from playsound import playsound
from google import genai
from google.genai import types
from google.cloud import texttospeech
from audio_recorder_streamlit import audio_recorder
from google.cloud import speech
import vertexai


def page_setup():
    st.header("Use a voice bot to interact with your PDF file!", anchor=False, divider="blue")

    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.sidebar.markdown("Non-Streaming Version")


def get_choice():
    choice = st.sidebar.radio("Choose:", ["Text 2 Audio",
                                          "Audio 2 Audio",
                                          ],)
    st.sidebar.divider()
    return choice
            


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
                    response = client.models.generate_content(
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
                            prompt,
                        ]
                    )

                input_text = texttospeech.SynthesisInput(text=response.text)
            

                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Studio-O",
                )
            
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    speaking_rate=1
                )
            
                response = client2.synthesize_speech(
                    request={"input": input_text, "voice": voice, "audio_config": audio_config}
                )
            

                with open("/Users/avi_patel/Documents/output.wav", "wb") as out:
                    out.write(response.audio_content)
                    
                file_ = open("/Users/avi_patel/Downloads/spkr.gif", "rb")
                contents = file_.read()
                data_url = base64.b64encode(contents).decode("utf-8")
                file_.close()
                placeholder = st.empty()
                placeholder = st.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
                    unsafe_allow_html=True,
                )
                playsound("/Users/avi_patel/Documents/output.wav")
                placeholder.empty()
    
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
                      #st.write("Transcript: {}".format(result.alternatives[0].transcript))
                      pass
                      
                    prompt = (result.alternatives[0].transcript)

                    response = client.models.generate_content(
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
                            prompt,
                        ]
                    )

                    input_text = texttospeech.SynthesisInput(text=response.text)
                

                    voice = texttospeech.VoiceSelectionParams(
                        language_code="en-US",
                        name="en-US-Studio-M",
                    )
                
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                        speaking_rate=1
                    )
                
                    response = client2.synthesize_speech(
                        request={"input": input_text, "voice": voice, "audio_config": audio_config}
                    )
                
                    with open("/Users/avi_patel/Documents/output.wav", "wb") as out:
                        out.write(response.audio_content)
                        
                    file_ = open("/Users/avi_patel/Downloads/spkr.gif", "rb")
                    contents = file_.read()
                    data_url = base64.b64encode(contents).decode("utf-8")
                    file_.close()
                    placeholder = st.empty()
                    placeholder = st.markdown(
                        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
                        unsafe_allow_html=True,
                    )
                    playsound("/Users/avi_patel/Documents/output.wav")
                    placeholder.empty()

            
if __name__ == '__main__':
    page_setup()
    projectid = os.environ.get('GOOG_PROJECT')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY_NEW')
    client = genai.Client(api_key=GOOGLE_API_KEY)
    MODEL_ID = "gemini-2.0-flash-exp"
    vertexai.init(project=projectid, location="us-central1")
    client2 = texttospeech.TextToSpeechClient()
    client3 = speech.SpeechClient()
    main()
