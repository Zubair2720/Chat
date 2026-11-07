
import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

# Load API Key
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Page Configuration
st.set_page_config(
    page_title="Gemini AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize Gemini
@st.cache_resource
def get_client():
    return genai.Client(api_key=API_KEY)

client = get_client()

# Model
MODEL = "gemini-3.5-flash-lite"

# App Heading
st.title("🤖 Gemini AI Assistant")
st.caption("Powered by Google Gemini | Text + Image Understanding")

st.divider()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Gemini chat
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL
    )

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.write("Model:", MODEL)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat = client.chats.create(
            model=MODEL
        )
        st.rerun()

    st.divider()

    st.subheader("🖼️ Upload Image")

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(
            image,
            caption="Uploaded Image",
            use_container_width=True
        )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Ask Gemini anything...")

if prompt:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Gemini response
    with st.chat_message("assistant"):

        with st.spinner("Gemini is thinking..."):

            try:
                if uploaded_file:
                    image = Image.open(uploaded_file)

                    response = client.models.generate_content(
                        model=MODEL,
                        contents=[prompt, image]
                    )

                else:
                    response = st.session_state.chat.send_message(
                        prompt
                    )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")
