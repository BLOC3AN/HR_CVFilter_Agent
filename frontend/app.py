"""
Frontend UI Service for HR CV Filter Agent
Streamlit application that communicates with Backend API
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.api_client import APIClient
from src.utils.cv_extractor import CVExtractor
from src.utils.logger import Logger

logger = Logger(__name__)

# Initialize API client
api_client = APIClient()

# Page config
st.set_page_config(
    page_title="HR CV Filter Agent",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'cv_evaluations' not in st.session_state:
    st.session_state.cv_evaluations = []
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'custom_rules' not in st.session_state:
    st.session_state.custom_rules = ""
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = "gemini-2.0-flash"
if 'selected_rule_name' not in st.session_state:
    st.session_state.selected_rule_name = None
if 'rule_content' not in st.session_state:
    st.session_state.rule_content = ""
if 'rule_description' not in st.session_state:
    st.session_state.rule_description = ""

# Title
st.title("📄 HR CV Filter Agent")
st.markdown("---")

# Check backend health
health = api_client.health_check()
if health.get("status") != "healthy":
    st.error(f"⚠️ Backend API is not available: {health.get('error', 'Unknown error')}")
    st.info("Please make sure the backend service is running at: " + api_client.base_url)
    st.stop()

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # LLM Model selection
    llm_model = st.selectbox(
        "Select LLM Model",
        options=["gemini-2.0-flash", "gemini-1.5-pro", "gemini-2.5-flash"],
        index=0
    )
    st.session_state.llm_model = llm_model
    
    st.markdown("---")
    
    # Job Description
    st.header("💼 Job Description")
    job_description = st.text_area(
        "Enter the job description",
        value=st.session_state.job_description,
        height=200,
        placeholder="Paste the job description here..."
    )
    st.session_state.job_description = job_description
    
    st.markdown("---")
    
    # Custom Evaluation Rules with MongoDB CRUD
    st.header("📋 Custom Evaluation Rules")
    
    # Get all rule names from backend
    rule_names_response = api_client.get_rule_names()
    if rule_names_response.get("success"):
        rule_names = rule_names_response.get("names", [])
    else:
        st.error("Failed to load rules from backend")
        rule_names = []
    
    # Rule selection
    selected_rule = st.selectbox(
        "Select a rule",
        options=["-- Create New --"] + rule_names,
        index=0 if st.session_state.selected_rule_name is None else 
              (rule_names.index(st.session_state.selected_rule_name) + 1 if st.session_state.selected_rule_name in rule_names else 0)
    )
    
    # Load selected rule
    if selected_rule != "-- Create New --" and selected_rule != st.session_state.selected_rule_name:
        rule_response = api_client.get_rule(selected_rule)
        if rule_response.get("success"):
            rule = rule_response.get("rule")
            st.session_state.selected_rule_name = selected_rule
            st.session_state.rule_content = rule.get("rules", "")
            st.session_state.rule_description = rule.get("description", "")
            st.session_state.custom_rules = rule.get("rules", "")
    elif selected_rule == "-- Create New --":
        st.session_state.selected_rule_name = None
    
    # Rule name input
    rule_name = st.text_input(
        "Rule Name",
        value=st.session_state.selected_rule_name if st.session_state.selected_rule_name else "",
        placeholder="Enter rule name..."
    )
    
    # Rule description
    rule_description = st.text_input(
        "Description (optional)",
        value=st.session_state.rule_description,
        placeholder="Brief description of this rule..."
    )
    st.session_state.rule_description = rule_description
    
    # Rule content
    rule_content = st.text_area(
        "Rule Content",
        value=st.session_state.rule_content,
        height=150,
        placeholder="Example:\n- Prioritize candidates with 5+ years experience\n- Must have Python skills\n- Prefer candidates with ML background"
    )
    st.session_state.rule_content = rule_content
    st.session_state.custom_rules = rule_content
    
    # Action buttons
    col_create, col_update, col_delete = st.columns(3)
    
    with col_create:
        if st.button("Create Rule", use_container_width=True):
            if not rule_name:
                st.error("Please enter a rule name")
            elif not rule_content:
                st.error("Please enter rule content")
            elif rule_name in rule_names:
                st.error(f"Rule '{rule_name}' already exists")
            else:
                result = api_client.create_rule(rule_name, rule_content, rule_description)
                if result.get("success"):
                    st.success(f"Created rule: {rule_name}")
                    st.session_state.selected_rule_name = rule_name
                    st.rerun()
                else:
                    st.error(f"Failed to create rule: {result.get('error', 'Unknown error')}")
    
    with col_update:
        if st.button("Update Rule", use_container_width=True):
            if not st.session_state.selected_rule_name:
                st.error("Please select a rule to update")
            elif not rule_content:
                st.error("Please enter rule content")
            else:
                result = api_client.update_rule(
                    st.session_state.selected_rule_name,
                    rule_content,
                    rule_description
                )
                if result.get("success"):
                    st.success(f"Updated rule: {st.session_state.selected_rule_name}")
                    st.rerun()
                else:
                    st.error(f"Failed to update rule: {result.get('error', 'Unknown error')}")
    
    with col_delete:
        if st.button("Delete Rule", use_container_width=True):
            if not st.session_state.selected_rule_name:
                st.error("Please select a rule to delete")
            else:
                result = api_client.delete_rule(st.session_state.selected_rule_name)
                if result.get("success"):
                    st.success(f"Deleted rule: {st.session_state.selected_rule_name}")
                    st.session_state.selected_rule_name = None
                    st.session_state.rule_content = ""
                    st.session_state.rule_description = ""
                    st.session_state.custom_rules = ""
                    st.rerun()
                else:
                    st.error(f"Failed to delete rule: {result.get('error', 'Unknown error')}")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload CVs")
    uploaded_files = st.file_uploader(
        "Upload CV files (PDF, DOCX, TXT, MD)",
        type=['pdf', 'docx', 'txt', 'md'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("🔍 Evaluate CVs", type="primary"):
            if not st.session_state.job_description:
                st.warning("⚠️ Please enter a job description first")
            else:
                st.session_state.cv_evaluations = []
                
                for uploaded_file in uploaded_files:
                    with st.spinner(f"Evaluating {uploaded_file.name}..."):
                        try:
                            # Extract CV text
                            cv_content = CVExtractor.extract_text(uploaded_file)
                            
                            # Call backend API to evaluate
                            result = api_client.evaluate_cv(
                                cv_content=cv_content,
                                job_description=st.session_state.job_description,
                                custom_rules=st.session_state.custom_rules,
                                llm_model=st.session_state.llm_model
                            )
                            
                            if result.get("success"):
                                st.session_state.cv_evaluations.append({
                                    'filename': uploaded_file.name,
                                    'evaluation': result.get("evaluation", "")
                                })
                                st.success(f"✅ Evaluated {uploaded_file.name}")
                            else:
                                st.error(f"❌ Failed to evaluate {uploaded_file.name}: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                            logger.error(f"Error processing {uploaded_file.name}: {str(e)}")

with col2:
    st.header("📊 Evaluation Results")
    
    if st.session_state.cv_evaluations:
        for idx, cv_eval in enumerate(st.session_state.cv_evaluations):
            with st.expander(f"📄 {cv_eval['filename']}", expanded=(idx == 0)):
                st.markdown(cv_eval['evaluation'])
    else:
        st.info("No evaluations yet. Upload and evaluate CVs to see results here.")

# Chat section
st.markdown("---")
st.header("💬 Chat with Agent")

# Display chat messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask questions about the evaluated CVs..."):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = api_client.chat(
                message=prompt,
                job_description=st.session_state.job_description,
                custom_rules=st.session_state.custom_rules,
                cv_evaluations=st.session_state.cv_evaluations,
                chat_history=st.session_state.chat_messages[:-1],
                llm_model=st.session_state.llm_model
            )
            
            if result.get("success"):
                response = result.get("response", "")
                st.markdown(response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
            else:
                error_msg = f"Error: {result.get('error', 'Unknown error')}"
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

