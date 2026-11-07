
import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

# --------------------------------
# 1. Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Gemini AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------
# 2. Load API Key
# --------------------------------

load_dotenv()

try:
    API_KEY = st.secrets.get("Gemini_API_Key", "") or os.getenv("Gemini_API_Key", "") or os.getenv("GEMINI_API_KEY", "")
except Exception:
    API_KEY = os.getenv("Gemini_API_Key", "") or os.getenv("GEMINI_API_KEY", "")

if not API_KEY or not API_KEY.strip():
    st.error("Gemini API Key missing! Please add it in Streamlit Secrets.")
    st.stop()

# --------------------------------
# 3. Initialize Gemini Client
# --------------------------------

@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)

try:
    client = get_client(API_KEY.strip())
except Exception as e:
    st.error(f"Gemini connection error: {e}")
    st.stop()

# Model
MODEL = "gemini-3.5-flash-lite"

# --------------------------------
# 4. App Heading
# --------------------------------

st.title("🤖 Gemini AI Assistant")

st.caption(
    "Powered by Google Gemini | Text Generation | Image Understanding"
)

st.divider()

# --------------------------------
# 5. Initialize Session State
# --------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model=MODEL
    )

# --------------------------------
# 6. Sidebar
# --------------------------------

with st.sidebar:

    st.title("⚙️ Settings")

    st.write("Model:", MODEL)

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

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []

        st.session_state.chat = client.chats.create(
            model=MODEL
        )

        st.rerun()

    st.divider()

    st.caption("Gemini AI Chatbot")

# --------------------------------
# 7. Display Chat History
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# --------------------------------
# 8. User Input
# --------------------------------

prompt = st.chat_input(
    "Ask Gemini anything..."
)

# --------------------------------
# 9. Generate Response
# --------------------------------

if prompt:

    # Display user message

    with st.chat_message("user"):

        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Gemini Response

    with st.chat_message("assistant"):

        with st.spinner("Gemini is thinking..."):

            try:

                # If image uploaded
                if uploaded_file is not None:

                    image = Image.open(uploaded_file)

                    response = client.models.generate_content(
                        model=MODEL,
                        contents=[prompt, image]
                    )

                # Normal text chat
                else:

                    response = st.session_state.chat.send_message(
                        prompt
                    )

                answer = response.text or "Gemini did not return any text."

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(f"Something went wrong: {e}")
