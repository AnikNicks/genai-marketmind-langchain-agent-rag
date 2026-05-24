"""
Streamlit Interface Dashboard for MarketMind
"""
import os
import streamlit as st
from src.config import DATA_DIR
from src.tools.rag_tool import initialize_vector_db, query_internal_financials
from src.agent import initialize_agent_executor

# 1. Page Setup
st.set_page_config(page_title="MarketMind", page_icon="📈", layout="wide")

# 2. IMMEDIATELY SECOND: Absolute State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hello. I am **MarketMind**. Ready to synthesize internal documentation records against live 2026 web events."
        }
    ]

if "agent" not in st.session_state:
    st.session_state.agent = initialize_agent_executor()


# 3. UI Presentation Layout
st.title("📈 MarketMind // Autonomous Financial Analyst")
st.markdown("---")

# 4. Sidebar Configuration
st.sidebar.header("📁 Document Ingestion System")
uploaded_files = st.sidebar.file_uploader(
    "Upload financial PDFs into vector storage", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    new_files = False
    for f in uploaded_files:
        path = os.path.join(DATA_DIR, f.name)
        if not os.path.exists(path):
            with open(path, "wb") as buffer:
                buffer.write(f.getbuffer())
            st.sidebar.success(f"Ingested: {f.name}")
            new_files = True
            
    if new_files:
        with st.sidebar.spinner("Re-indexing vector embedding collections..."):
            initialize_vector_db()
        st.sidebar.info("Database updated!")

# 5. Render Historical Chat Interface (Safely initialized now!)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Process Real-Time User Input
if user_input := st.chat_input("Ex: Compare our Q3 performance results with top market trends in 2026"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("Processing ReAct routing execution vectors..."):
            try:
                res = st.session_state.agent.invoke({"input": user_input})
                output = res.get("output", "Execution lifecycle failed to generate output payload.")
            except Exception as e:
                output = f"Runtime agent boundary execution fault: {str(e)}"
        
        st.markdown(output)
        st.session_state.messages.append({"role": "assistant", "content": output})