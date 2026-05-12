import streamlit as st
import requests
import pandas as pd

# Page Config
st.set_page_config(page_title="Sentio Vault | Financial HCI Agent", page_icon="🛡️", layout="wide")

# --- Styling ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .reportview-container .main .block-container{ padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Configuration ---
st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=80)
st.sidebar.title("Sentio Vault Settings")

user_id = st.sidebar.text_input("👤 User ID", value="user_101")
category = st.sidebar.selectbox("📂 Category", [
    "Groceries", "Entertainment", "Utilities", "Investments", "Dining Out", "Healthcare"
])

st.sidebar.divider()
st.sidebar.info("This agent uses a Reflective Graph Architecture with AWS Bedrock & Weaviate.")

# --- Main Interface ---
st.title("🛡️ Sentio Vault")
st.subheader("Agentic Financial Intelligence with HCI Insights")

query = st.text_input("💬 Ask your financial agent a question:", placeholder="e.g., How is my spending affecting my cognitive load?")

if st.button("Analyze Transactions"):
    if not query:
        st.warning("Please enter a query first.")
    else:
        with st.spinner("🧠 Sentio is retrieving data and reflecting on the analysis..."):
            try:
                # Pointing to your FastAPI backend (main.py)
                payload = {
                    "query": query,
                    "user_id": user_id,
                    "category": category
                }
                
                response = requests.post("http://localhost:8000/ask", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Analysis Complete")
                    
                    # Layout for Results
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### 📋 Agent Analysis")
                        st.write(data["analysis"])
                    
                    with col2:
                        st.markdown("### 🛠️ Metadata")
                        st.json({
                            "User": user_id,
                            "Filtered Category": category,
                            "Cached": data["is_cached"]
                        })
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"Could not connect to the Sentio API. Is main.py running? \n\n {e}")

# --- Footer ---
st.divider()
st.caption("Sentio Vault 2026 | Built with LangGraph, Weaviate, and Amazon Bedrock.")