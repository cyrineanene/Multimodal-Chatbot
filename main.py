import streamlit as st
from llm_chains import load_normal_chain
from utils import save_chat_history_json, load_chat_history_json, get_timestamp
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from streamlit_mic_recorder import mic_recorder
from types_handlers.audio_handler import transcribe_audio
from types_handlers.image_handler import handle_image
from types_handlers.pdf_handler import add_documents_to_db
import yaml
import os

#Loading the config file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def load_chain(chat_history):
    return load_normal_chain(chat_history)

def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input = ""

def send_input():
    st.session_state.send_input = True
    clear_input_field()

def track_index():
    st.session_state.session_index_tracker = st.session_state.session_key

def save_chat_history():
    if st.session_state.history != []:
        if st.session_state.session_key == "new_session":
            st.session_state.new_session_key = get_timestamp() + '.json'
            save_chat_history_json(st.session_state.history, config["chat_history_path"] + st.session_state.new_session_key)
        else:
            save_chat_history_json(st.session_state.history, config["chat_history_path"] + st.session_state.session_key)

def start():
    st.title("Multimodal Chatbot App")
    chat_container = st.container()
    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])

    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
    
    if st.session_state.session_key == "new_session" and st.session_state.new_session_key != None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    index = chat_sessions.index(st.session_state.session_index_tracker)    
    st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index = index, on_change=track_index)

    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(config['chat_history_path'] + st.session_state.session_key)
    else:
        st.session_state.history = []
    
    chat_history = StreamlitChatMessageHistory(key="history")
    llm_chain = load_chain(chat_history)

    user_input = st.text_input("Type your message: ",  key = "user_input", on_change=send_input)
    
    voice_recording_column, send_button_column = st.columns(2)
    with voice_recording_column:
        voice_recording = mic_recorder(start_prompt="Start recording", stop_prompt="Stop recording")
    with send_button_column:
        send_button = st.button("Send", key = "send_button", on_click = clear_input_field)

    uploaded_audio = st.sidebar.file_uploader("Upload an audio file", type=['wav', 'mp3', 'ogg'])
    uploaded_image = st.sidebar.file_uploader("Upload an image file", type=['jpg', 'jpeg', 'png'])
    uploaded_pdf = st.sidebar.file_uploader("Upload an pdf file", accept_multiple_files=True, key="pdf_upload", type=['pdf'])

    if uploaded_pdf:
        with st.spinner('Processing pdf...'):
            add_documents_to_db(uploaded_pdf)

    if uploaded_audio:
        transcribed_audio = transcribe_audio(uploaded_audio.getvalue())
        #Summaring the audio text for easier use
        llm_chain.run("Summarize this text: "+ transcribed_audio)

    if voice_recording:
        transcribed_audio = transcribe_audio(voice_recording["bytes"])
        llm_response = llm_chain.run(transcribed_audio)

    if send_button or st.session_state.send_input:
        if uploaded_image:
            with st.spinner('Processing image...'):
                user_message = 'Describe this image in detail.' #if we only enter the image and click on the button then this will be the given prompt
            if st.session_state.user_question != "":
                user_message = st.session_state.user_question
                st.session_state.user_question = ""
            llm_answer = handle_image(uploaded_image.getvalue(), st.session_state.user_question)

            #Writing the messages in the memory because Llava model doesn't automatically do that
            chat_history.add_user_message(user_message)
            chat_history.add_ai_message(llm_answer)

        if st.session_state.user_question != "":
            llm_response = llm_chain.run(st.session_state.user_question)
            st.session_state.user_question = ""

    if chat_history.messages != []:
        with chat_container:
            st.write("Chat History:")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)
    
    save_chat_history()

if __name__ == "__main__":
    start()