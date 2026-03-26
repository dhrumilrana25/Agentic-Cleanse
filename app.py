import streamlit as st
import os
import pandas as pd
from graph import app

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Agentic-Cleanse SaaS", page_icon="🏭", layout="wide")
st.title("🏭 Agentic Data Cleanse Factory")
st.markdown("### *Autonomous AI Data Engineering for Dhrumil*")

if not os.path.exists("data"):
    os.makedirs("data")

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Factory Controls")
    if st.button("🗑️ Reset & New Upload", use_container_width=True):
        st.session_state.thread_id = os.urandom(4).hex()
        if os.path.exists("final_cleaned_data.csv"):
            os.remove("final_cleaned_data.csv")
        st.rerun()
    
    st.divider()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = os.urandom(4).hex()
    st.info(f"**Session ID:** {st.session_state.thread_id}")

config = {"configurable": {"thread_id": st.session_state.thread_id}}

# --- 3. UI LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload & Instruct")
    uploaded_file = st.file_uploader("Upload messy CSV", type=["csv"])
    user_instructions = st.text_area("What should the AI do?", placeholder="e.g. Add a column 'Cleaned_By' for Dhrumil")
    
    if uploaded_file:
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("🚀 Start AI Workers", type="primary"):
            # We use st.status to make the "Agentic" process visible and cool
            with st.status("🏭 Assembly Line Starting...", expanded=True) as status:
                st.write("🤖 Agent 1: Profiling data structure...")
                initial_state = {
                    "dataset_path": file_path, "user_instructions": user_instructions,
                    "errors": [], "is_cleaned": False, "retry_count": 0
                }
                for event in app.stream(initial_state, config=config):
                    if "engineer" in event:
                        st.write("🤖 Agent 2: Engineering Python logic...")
                    if "security" in event:
                        st.write("🛡️ Agent 4: Scanning code for security risks...")
                
                status.update(label="✅ Ready for Human Review!", state="complete", expanded=False)
            st.rerun()

with col2:
    st.subheader("2. Review & Download")
    
    try:
        current_state = app.get_state(config)
        state_values = current_state.values if current_state else {}
    except:
        state_values = {}

    if state_values:
        # Show Strategy
        with st.expander("📝 View AI Cleaning Strategy"):
            st.info(state_values.get("cleaning_plan", "Planning..."))

        # REVIEW MODE
        if not state_values.get("is_cleaned"):
            # Check for Security Vetoes
            if state_values.get("errors") and "SECURITY VETO" in state_values["errors"][-1]:
                st.error(state_values["errors"][-1])
                st.info("The Security Agent blocked this code. Click Reset to try again.")
            else:
                st.warning("🛑 AI paused. Review code below:")
                st.code(state_values.get("python_code", ""), language="python")
                
                if st.button("✅ Approve & Execute Code", type="primary"):
                    with st.spinner("Agent 3 is executing..."):
                        for event in app.stream(None, config=config):
                            pass
                        st.rerun()
        
        # SUCCESS MODE
        else:
            st.success("🎉 Data Cleaned Successfully!")
            cleaned_file = "final_cleaned_data.csv"
            
            if os.path.exists(cleaned_file):
                # DATA COMPARISON (THE DS FLEX)
                df_old = pd.read_csv(state_values["dataset_path"])
                df_new = pd.read_csv(cleaned_file)
                
                c1, c2 = st.columns(2)
                c1.metric("Original Nulls", df_old.isnull().sum().sum())
                c2.metric("Cleaned Nulls", df_new.isnull().sum().sum(), delta=int(df_new.isnull().sum().sum() - df_old.isnull().sum().sum()), delta_color="inverse")
                
                st.write("#### Result Preview:")
                st.dataframe(df_new.head(5))
                
                with open(cleaned_file, "rb") as f:
                    st.download_button("📥 Download Result", f, "cleaned_data.csv", "text/csv", type="primary")
    else:
        st.info("The factory is waiting for a file.")