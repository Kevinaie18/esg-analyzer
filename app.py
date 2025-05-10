"""
Main Streamlit application for the ESG & Impact Pre-Investment Analyzer.
"""

import os
import yaml
import streamlit as st
from dotenv import load_dotenv
from loguru import logger
import re
import io

from standards.loader import StandardsLoader
from prompts.enhanced_prompts import EnhancedPromptManager
from engine.llm_service import get_llm_manager
from config.risk_classification import (
    RISK_CATEGORIES,
    SECTOR_RISK_MAPPING,
    SUBSECTOR_RISK_MAPPING,
    SECTOR_IFC_STANDARDS,
    IFC_STANDARDS
)
from utils.ehs_processor import EHSProcessor
import json
from formatters.docx_formatter import DocxFormatter
from utils.llm_report_parser import parse_llm_report

# Load environment variables
load_dotenv()

# Load configuration
def load_config():
    try:
        with open("config/config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        st.error("Error loading configuration. Please check the config file.")
        return None

# Initialize components
config = load_config()
if not config:
    st.stop()

# Validate API keys
def validate_api_keys():
    required_keys = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY",
        "DeepSeek": "FIREWORKS_API_KEY"
    }
    
    missing_keys = []
    for provider, key in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"{provider} ({key})")
    
    if missing_keys:
        st.error(f"""
        Missing API keys for: {', '.join(missing_keys)}
        
        Please add them to your .env file:
        ```
        {chr(10).join([f'{key}=your_api_key_here' for key in required_keys.values()])}
        ```
        """)
        return False
    return True

if not validate_api_keys():
    st.stop()

standards_loader = StandardsLoader()
prompt_manager = EnhancedPromptManager(standards_loader)

# Set up Streamlit page
st.set_page_config(
    page_title="ESG & Impact Pre-Investment Analyzer",
    page_icon="🌍",
    layout="wide"
)

st.title("ESG & Impact Pre-Investment Analyzer")
st.markdown("""
## 🎯 Conseils d'utilisation

- **Soyez précis et concis** dans vos réponses au pré-questionnaire.
- **Mettez en avant vos priorités business et ESG** pour un rapport sur-mesure.
- **Choisissez le modèle LLM** selon la profondeur d'analyse souhaitée :

  - **GPT-4 Turbo** : Analyse stratégique, contexte complexe.
  - **GPT-3.5 Turbo** : Synthèse rapide, rapports courts.
  - **Claude 3 Opus/Sonnet/Haiku** : Bon équilibre rapidité/qualité.
  - **DeepSeek** : Réponses factuelles, screening rapide.

---
""")

# LLM provider and model selection OUTSIDE the form for dynamic updates
st.subheader("Analysis Parameters")

if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = "OpenAI"
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = "gpt-4-turbo-preview"
if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 4000
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7

llm_provider = st.selectbox(
    "Select LLM Provider",
    ["OpenAI", "Anthropic", "DeepSeek"],
    index=["OpenAI", "Anthropic", "DeepSeek"].index(st.session_state.llm_provider),
    key="llm_provider_select"
)

# Add temperature and max_tokens controls
col1, col2 = st.columns(2)
with col1:
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Higher values make the output more creative but less focused"
    )
with col2:
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=100,
        max_value=16000,
        value=st.session_state.max_tokens,
        step=100,
        help="Maximum length of the generated response"
    )

st.session_state.temperature = temperature
st.session_state.max_tokens = max_tokens

if llm_provider == "OpenAI":
    model_options = ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"]
    model_key = "openai_model"
elif llm_provider == "Anthropic":
    model_options = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    model_key = "anthropic_model"
else:
    model_options = ["accounts/fireworks/models/deepseek-r1-basic"]
    model_key = "deepseek_model"

llm_model = st.selectbox(
    f"Select {llm_provider} Model",
    model_options,
    index=0,
    key=model_key
)

st.session_state.llm_provider = llm_provider
st.session_state.llm_model = llm_model

with st.form("company_info_form"):
    st.subheader("Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name")
        country = st.text_input("Country of Operation")
        sector = st.selectbox(
            "Sector",
            options=list(SECTOR_RISK_MAPPING.keys()),
            help="Select the main sector of the project"
        )
        # Filter subsectors based on selected sector
        relevant_subsectors = [
            sub for sub in SUBSECTOR_RISK_MAPPING.keys()
            if any(sector.lower() in sub.lower() for sub in [sector])
            or any(sector.lower() in sub.lower() for sub in SUBSECTOR_RISK_MAPPING[sub].get('parent_sectors', []))
        ]
        subsector = st.selectbox(
            "Subsector",
            options=relevant_subsectors,
            help="Select the specific subsector"
        )
    with col2:
        size = st.text_input("Company Size (optional)", placeholder="e.g., Revenue, Number of Employees")
    description = st.text_area(
        "Company Description",
        placeholder="Describe the company's business model, market, customers, and key activities..."
    )
    frameworks = st.multiselect(
        "Select ESG Frameworks",
        ["ifc", "2x", "internal"],
        default=["ifc", "2x"]
    )
    detail_level = st.radio(
        "Analysis Detail Level",
        ["standard", "detailed"],
        horizontal=True
    )
    submitted = st.form_submit_button("Generate Analysis")

if submitted:
    if not company_name or not country or not sector or not description:
        st.error("Please fill in all required fields.")
    elif not frameworks:
        st.error("Please select at least one ESG framework.")
    else:
        try:
            with st.spinner("Generating analysis..."):
                logger.info(f"Starting analysis generation for {company_name}")
                logger.info(f"Using provider: {st.session_state.llm_provider}, model: {st.session_state.llm_model}")
                
                llm_manager = get_llm_manager()
                company_info = {
                    "name": company_name,
                    "country": country,
                    "sector": sector,
                    "subsector": subsector,
                    "description": description,
                    "size": size if size else None
                }
                
                logger.info("Generating analysis prompt...")
                prompt = prompt_manager.generate_analysis_prompt(
                    company_info=company_info,
                    selected_frameworks=frameworks,
                    detail_level=detail_level
                )
                
                logger.info("Sending request to LLM...")
                try:
                    response = llm_manager.generate_response(
                        prompt=prompt,
                        primary_provider=st.session_state.llm_provider.upper(),
                        max_tokens=st.session_state.max_tokens,
                        temperature=st.session_state.temperature
                    )
                    logger.info("Successfully received response from LLM")
                except Exception as llm_error:
                    logger.error(f"LLM request failed: {str(llm_error)}")
                    st.error(f"Error communicating with LLM service: {str(llm_error)}")
                    raise
                
                # Display the analysis results
                st.markdown("## Analysis Results")
                st.markdown(response)

                # DOCX export
                try:
                    parsed = parse_llm_report(response, company_name)
                    docx_formatter = DocxFormatter()
                    docx_formatter.format_analysis(parsed)
                    docx_buffer = io.BytesIO()
                    docx_formatter.document.save(docx_buffer)
                    docx_buffer.seek(0)
                    st.download_button(
                        label="Download Report as Word (.docx)",
                        data=docx_buffer,
                        file_name=f"esg_analysis_{company_name.lower().replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as docx_err:
                    st.warning(f"Could not generate Word report: {docx_err}")

                # Markdown fallback
                st.download_button(
                    label="Download Report as Markdown",
                    data=response,
                    file_name=f"esg_analysis_{company_name.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )
        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            st.error("An error occurred while generating the analysis. Please try again.") 