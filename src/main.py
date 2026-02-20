"""
ProNexus Autonomous Executive Search Agent
Streamlit Frontend for Google Colab Execution
"""
import streamlit as st
import sys
import os
import nest_asyncio

# Enable nest_asyncio for Colab compatibility
nest_asyncio.apply()

# Disable CrewAI Telemetry to avoid threading errors in Streamlit
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

# Disable LiteLLM logging to prevent threading issues and import errors
os.environ["LITELLM_LOG"] = "ERROR"
os.environ["LITELLM_SUPPRESS_DEBUG_INFO"] = "true"
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "False"

# Disable standard logging payload creation to avoid fastapi import error
import litellm
litellm.suppress_debug_info = True
litellm.drop_params = True
litellm.turn_off_message_logging = True

# Monkey-patch to prevent cold storage handler import error
try:
    from litellm.proxy.spend_tracking import cold_storage_handler
    # Replace the problematic method with a no-op
    cold_storage_handler.ColdStorageHandler._get_configured_cold_storage_custom_logger = lambda: None
except Exception:
    pass  # If import fails, that's fine - we're trying to avoid it anyway


# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load Gemini API key from Streamlit secrets or environment (kept for reference)
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Load OpenRouter API key from Streamlit secrets or environment
try:
    if "OPENROUTER_API_KEY" in st.secrets:
        os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
    if "OPENAI_API_BASE" in st.secrets:
        os.environ["OPENAI_API_BASE"] = st.secrets["OPENAI_API_BASE"]
except Exception as e:
    st.error(f"Error loading secrets: {e}")

# Explicitly load OpenAI Config for Proxy
try:
    if "OPENAI_API_BASE" in st.secrets:
        os.environ["OPENAI_API_BASE"] = st.secrets["OPENAI_API_BASE"]
        os.environ["OPENAI_BASE_URL"] = st.secrets["OPENAI_API_BASE"] # For new OpenAI SDK
        print(f"DEBUG: OPENAI_API_BASE set to: {os.environ['OPENAI_API_BASE']}")
    
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
        print(f"DEBUG: OPENAI_API_KEY set to: {os.environ['OPENAI_API_KEY']}")
except Exception as e:
    st.error(f"Error setting OpenAI env vars: {e}")

# Load SambaNova API key from Streamlit secrets or environment
try:
    if "SAMBANOVA_API_KEY" in st.secrets:
        os.environ["SAMBANOVA_API_KEY"] = st.secrets["SAMBANOVA_API_KEY"]
except Exception:
    # Fallback: check if already in environment
    if not os.getenv("SAMBANOVA_API_KEY"):
        st.warning("SAMBANOVA_API_KEY not found in secrets or environment. Please add it to `.streamlit/secrets.toml` in the project root.")


from flow.search_flow import ProNexusFlow

# Page configuration
st.set_page_config(
    page_title="ProNexus AI Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">ProNexus Autonomous Executive Search</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Sourcing & Vetting Prototype</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Search Configuration")
    
    role = st.selectbox(
        "Target Role",
        [
            "Interim CFO",
            "Healthcare Clinical Operations Lead",
            "Elite Project Manager"
        ]
    )
    
    requirements = st.text_area(
        "Specific Requirements",
        height=150,
        value="Must have ASC 606 experience. Must have managed >$50M revenue."
    )
    
    st.info(" **Prototype Mode:** Using Synthetic Data")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This prototype demonstrates:
    - Multi-agent orchestration
    - Forensic vetting logic
    - Role-specific rubrics
    - Zero-cost data generation
    """)

# Main content area
if st.button("Start Autonomous Search", type="primary", use_container_width=True):
    
    # Initialize flow
    flow = ProNexusFlow()
    flow.state.query = f"{role} - {requirements}"
    
    # Create status container
    with st.status("Orchestrating Agents...", expanded=True) as status:
        
        st.write("**Sourcing Crew:** Initializing Synthetic Data Factory...")
        
        # Step 1: Analyze requirements
        flow.analyze_requirements()
        st.write(f"Requirements analyzed: {len(flow.state.client_requirements)} criteria extracted")
        
        # Step 2: Source candidates
        flow.sourcing_step()
        st.write(f"**Sourcing Complete.** {len(flow.state.candidate_pool)} candidates identified.")
        
        # Step 3: Vet candidates
        st.write(" **Vetting Crew:** Auditing resumes for Red Flags...")
        flow.vetting_step()
        st.write(f"**Vetting Complete.** {len(flow.state.vetted_candidates)} candidates evaluated.")
        
        # Step 4: Generate report
        st.write("**Reporting Crew:** Compiling final dossier...")
        flow.generate_report()
        
        status.update(
            label="Search Complete",
            state="complete",
            expanded=False
        )
    
    # Display results
    st.divider()
    st.markdown("## Executive Summary")
    
    if flow.state.final_report:
        st.markdown(flow.state.final_report)
    else:
        st.warning("No report generated. Check the flow execution.")
    
    # Candidate details
    st.divider()
    st.markdown("## Candidate Details")
    
    if flow.state.vetted_candidates:
        for candidate in flow.state.vetted_candidates:
            with st.expander(f"{candidate.name} - Score: {candidate.matchmaker_score}/100"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Risk Score", f"{candidate.auditor_score}/100")
                    if candidate.auditor_notes:
                        st.text_area("Risk Notes", candidate.auditor_notes, height=200, key=f"auditor_{candidate.id}")
                
                with col2:
                    st.metric("Domain Score", f"{candidate.domain_score}/100")
                    if candidate.domain_notes:
                        st.text_area("Domain Notes", candidate.domain_notes, height=200, key=f"domain_{candidate.id}")
                
                with col3:
                    st.metric("Final Fit", candidate.final_fit)
                    if candidate.red_flags:
                        st.warning("Red Flags:")
                        for flag in candidate.red_flags:
                            st.write(f"- {flag}")
                
                if candidate.resume_text:
                    with st.expander("View Resume"):
                        st.text(candidate.resume_text)
    else:
        st.info("No candidates found. Try adjusting your search criteria.")
    


# Instructions
st.sidebar.markdown("---")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("""
1. Select target role
2. Enter specific requirements
3. Click "Start Autonomous Search"
4. Review results and scores
""")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>ProNexus LLC - AI Executive Search Prototype</div>",
    unsafe_allow_html=True
)
