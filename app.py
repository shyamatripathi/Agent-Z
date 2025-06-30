import streamlit as st
import requests

st.set_page_config(page_title="AGENT-Z", page_icon=":)")
st.title("AGENT-Z — Your Assistant")

# to maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#to display messages
for msg in st.session_state.messages:
    role, content = msg
    with st.chat_message(role):
        st.markdown(content)

#Chat input
user_input = st.chat_input("Ask me to book or check a slot...")

if user_input:
    # to display user message
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # to send message to FastAPI backend
    try:
        res = requests.post(
            "http://127.0.0.1:8000/chat", 
            json={"message": user_input}
        )
        bot_reply = res.json().get("response", " Something went wrong.")
    except Exception as e:
        bot_reply = f" API error: {e}"

    # to display bot reply
    st.session_state.messages.append(("assistant", bot_reply))
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
