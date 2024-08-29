import streamlit as st

def load_chain():
    return load_normal_chain()

def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input = ''

def send_input():
    st.session_state.send_input = True
    clear_input_field()

def start():
    st.title('Multimodal Chatbot App')
    chat_container = st.container()

    if 'send_input' not in st.session_state:
        st.session_state.send_input = False
        st.session_state.user_question = ""

    user_input = st.text_input('Type your message: ',  key = 'user_input', on_change=set.send_input)
    send_button = st.button('Send', key = 'send_button')

    if send_button or st.session_state.send_input:
        if st.session_state.user_question != '':
            llm_response = 'This is the response from the LLM model'
            with chat_container:
                st.chat_message('user').write(st.session_state.user_question)
                st.chat_message('ai').write('Here is the answer')

if __name__ == 'main':
    start()