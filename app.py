import streamlit as st
from src.agent.HR_CVFilter_agent import HRCVFilterAgent
from src.utils.cv_extractor import CVExtractor
from src.utils.logger import Logger

logger = Logger(__name__)

# Page config
st.set_page_config(
    page_title="HR CV Filter Agent",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
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

# Title
st.title("📄 HR CV Filter Agent")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # LLM Model selection
    llm_model = st.selectbox(
        "Select LLM Model",
        ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        index=0
    )
    st.session_state.llm_model = llm_model

    # Auto-initialize agent if not exists
    if st.session_state.agent is None or st.session_state.agent.llm.model_name != llm_model:
        try:
            st.session_state.agent = HRCVFilterAgent(llm_model_name=llm_model)
            logger.info(f"Agent auto-initialized with model: {llm_model}")
        except Exception as e:
            st.error(f"❌ Error initializing agent: {str(e)}")
            logger.error(f"Error initializing agent: {str(e)}")

    # Clear history button
    if st.button("Clear History"):
        if st.session_state.agent:
            st.session_state.agent.clear_history()
        st.session_state.cv_evaluations = []
        st.session_state.chat_messages = []
        st.success("✅ History cleared!")

    st.markdown("---")
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. Enter job description
    2. Set custom rules (optional)
    3. Upload CV files
    4. Review evaluations
    5. Chat with agent

    **Note:** Agent automatically reads all available fields and provides hints if information is missing.
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Job Description")
    job_description = st.text_area(
        "Enter the job description",
        value=st.session_state.job_description,
        height=200,
        placeholder="Paste the job description here..."
    )
    st.session_state.job_description = job_description
    
    st.header("📋 Custom Evaluation Rules")
    custom_rules = st.text_area(
        "Enter custom rules for CV evaluation (optional)",
        value=st.session_state.custom_rules,
        height=150,
        placeholder="Example:\n- Prioritize candidates with 5+ years experience\n- Must have Python skills\n- Prefer candidates with ML background"
    )
    st.session_state.custom_rules = custom_rules

with col2:
    st.header("📤 Upload CV Files")
    uploaded_files = st.file_uploader(
        "Upload CV files (PDF, DOCX, TXT, MD)",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("Evaluate CVs", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")

            # Extract CV content
            file_extension = uploaded_file.name.split('.')[-1].lower()
            cv_content = CVExtractor.extract(uploaded_file, file_extension)

            if cv_content:
                # Evaluate CV with all available context
                evaluation = st.session_state.agent.evaluate_cv(
                    cv_content=cv_content,
                    cv_filename=uploaded_file.name,
                    job_description=st.session_state.job_description,
                    custom_rules=st.session_state.custom_rules
                )

                # Store evaluation
                st.session_state.cv_evaluations.append({
                    "filename": uploaded_file.name,
                    "evaluation": evaluation
                })
            else:
                st.error(f"❌ Failed to extract content from {uploaded_file.name}")

            # Update progress
            progress_bar.progress((idx + 1) / len(uploaded_files))

        status_text.text("✅ All CVs processed!")
        st.success(f"✅ Evaluated {len(uploaded_files)} CV(s)")

# Display evaluations
if st.session_state.cv_evaluations:
    st.markdown("---")
    st.header("📊 CV Evaluations")
    
    for idx, eval_data in enumerate(st.session_state.cv_evaluations, 1):
        with st.expander(f"📄 {eval_data['filename']}", expanded=(idx == len(st.session_state.cv_evaluations))):
            st.markdown(eval_data['evaluation'])

# Chat interface
st.markdown("---")
st.header("💬 Chat with Agent")

# Display chat messages
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask questions about the CV evaluations..."):
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response with all available context
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.chat(
                message=prompt,
                job_description=st.session_state.job_description,
                custom_rules=st.session_state.custom_rules
            )
            st.markdown(response)

    # Add assistant message
    st.session_state.chat_messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>HR CV Filter Agent | Powered by Google Gemini</p>
    </div>
    """,
    unsafe_allow_html=True
)

