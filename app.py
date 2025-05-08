"""
Main Streamlit application for the ESG & Impact Pre-Investment Analyzer.
"""

import os
import yaml
import streamlit as st
from dotenv import load_dotenv
from loguru import logger
import re

from standards.loader import StandardsLoader
from prompts.enhanced_prompts import EnhancedPromptManager
from engine.llm_service import get_llm_service

# Load environment variables
load_dotenv()

# Load configuration
def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

# Initialize components
config = load_config()
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
- **Choisissez le modèle LLM** selon la profondeur d'analyse souhaitée:

---
""")

# LLM provider and model selection OUTSIDE the form for dynamic updates
st.subheader("Analysis Parameters")

if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = "OpenAI"
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = "gpt-4-turbo-preview"

llm_provider = st.selectbox(
    "Select LLM Provider",
    ["OpenAI", "Anthropic", "DeepSeek"],
    index=["OpenAI", "Anthropic", "DeepSeek"].index(st.session_state.llm_provider),
    key="llm_provider_select"
)

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
            ["Agribusiness", "Manufacturing", "Services", "Healthcare", "Other"]
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
                llm_service = get_llm_service(
                    provider=st.session_state.llm_provider.lower(),
                    model=st.session_state.llm_model,
                    temperature=config["llm"]["temperature"]
                )
                company_info = {
                    "name": company_name,
                    "country": country,
                    "sector": sector,
                    "description": description,
                    "size": size if size else None
                }
                prompt = prompt_manager.generate_analysis_prompt(
                    company_info=company_info,
                    selected_frameworks=frameworks,
                    detail_level=detail_level
                )
                response = llm_service.generate_response(
                    prompt,
                    max_tokens=config["llm"]["max_tokens"]
                )
                st.markdown("## Analysis Results")
                st.markdown(response)
                st.download_button(
                    label="Download Report",
                    data=response,
                    file_name=f"esg_analysis_{company_name.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )
        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            st.error("An error occurred while generating the analysis. Please try again.") 