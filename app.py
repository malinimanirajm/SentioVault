import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="Sentio Vault", page_icon="💰", layout="wide")

st.title("💰 Sentio Vault: AI Financial Assistant")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", value="http://localhost:8000/ask")
    user_id = st.text_input("User ID", value="malini_01")
    st.info("Ensure your FastAPI server is running on port 8000!")

# Main chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about your spending (e.g., 'Summarize my grocery costs')"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Sentio is analyzing your vault..."):
            try:
                response = requests.post(
                    api_url,
                    json={"query": prompt, "user_id": user_id}
                )
                if response.status_code == 200:
                    analysis = response.json().get("analysis")
                    st.markdown(analysis)
                    st.session_state.messages.append({"role": "assistant", "content": analysis})
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Could not connect to backend: {e}")