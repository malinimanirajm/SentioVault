import streamlit as st
import requests

st.set_page_config(
    page_title="Sentio Vault | Financial HCI Agent", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    div.stTextInput>div>div>input {
        background-color: #161b22 !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 6px; 
        height: 3.2em; 
        background: linear-gradient(135deg, #007bff 0%, #00d2ff 100%); 
        color: white; 
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 210, 255, 0.4);
        color: white !important;
    }
    .metric-card {
        background: rgba(22, 27, 34, 0.8);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    .metric-title { color: #8b949e; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; }
    .metric-value { color: #58a6ff; font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
    .sidebar-footer {
        font-size: 0.85rem;
        color: #8b949e;
        background-color: #161b22;
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #58a6ff;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=70)
    st.markdown("<h2 style='color: #f0f6fc; margin-top: 0;'>Sentio Control Vault</h2>", unsafe_allow_html=True)
    st.markdown("Configure context parameters for the multi-tenant agent graph loop below.")
    st.divider()
    
    user_id = st.text_input("👤 Target User ID", value="T0015")
    
    # FIX: Categories match singular vs plural conventions inside backend datasets
    category = st.selectbox("📂 Operating Category Room", [
        "Groceries", "Entertainment", "Utilities", "Investment", "Dining Out", "Healthcare"
    ])
    
    st.divider()
    st.markdown("""
        <div class="sidebar-footer">
            <strong>Architecture Engine:</strong><br>
            • LangGraph Reflective Loop<br>
            • AWS Bedrock (Nova Micro)<br>
            • Vector Layer: Weaviate DB
        </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='color: #f0f6fc;'>🛡️ Sentio Vault</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.2rem; color: #8b949e; margin-top:-15px;'>Agentic Financial Intelligence & HCI Behavioral Diagnostics</p>", unsafe_allow_html=True)
st.markdown("---")

query = st.text_input("💬 Challenge the financial intelligence core:", placeholder="e.g., Get my transaction trends and evaluate my stress load profile.")

if st.button("Analyze & Audit Transactions"):
    if not query:
        st.warning("⚠️ Input prompt sequence empty. Please enter a valid query string.")
    else:
        with st.spinner("🧠 Initializing Secure Vault Pipeline..."):
            try:
                payload = {
                    "query": query,
                    "user_id": user_id,
                    "category": category
                }
                
                response = requests.post("http://localhost:8000/ask", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.toast("Pipeline Finished Cleanly!", icon="✅")
                    
                    col1, col2 = st.columns([5, 2], gap="large")
                    
                    with col1:
                        st.markdown("<h3 style='color: #f0f6fc;'>📋 Core Diagnostics Report</h3>", unsafe_allow_html=True)
                        output_text = data.get("analysis") or data.get("final_output") or "No analysis returned."
                        
                        st.markdown(f"""
                        <div style='background-color: #161b22; padding: 25px; border-radius: 8px; border: 1px solid #30363d; line-height: 1.6; white-space: pre-wrap;'>
                            {output_text}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<h3 style='color: #f0f6fc;'>🛠️ Telemetry Data</h3>", unsafe_allow_html=True)
                        
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Active Tenant Context</div>
                                <div class="metric-value" style="color: #ffc107;">{user_id}</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-title">Isolated Scope Filter</div>
                                <div class="metric-value" style="color: #28a745;">{category}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        cache_color = "#17a2b8" if data.get("is_cached") else "#dc3545"
                        cache_text = "HIT (Saved Tokens)" if data.get("is_cached") else "MISS (Full Compute)"
                        
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Semantic Cache Layer</div>
                                <div class="metric-value" style="color: {cache_color}; font-size: 1.4rem;">{cache_text}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Core Gateway Failure: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"🔌 Connection Timeout: Interface could not establish a pipeline link to main.py at port 8000.\n\nError Context: {e}")

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 0.85rem;'>Sentio Vault Engine v2.0.0 • Production Level Cryptographic Sandbox • 2026</p>", unsafe_allow_html=True)