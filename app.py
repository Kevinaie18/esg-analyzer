"""
Main Streamlit application for the ESG & Impact Pre-Investment Analyzer.
"""

import os
import yaml
import streamlit as st
from dotenv import load_dotenv
from loguru import logger

from standards.loader import StandardsLoader
from prompts.master_prompt import PromptManager
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
prompt_manager = PromptManager(standards_loader)
llm_service = get_llm_service(
    provider=config["llm"]["provider"],
    model=config["llm"]["model"],
    temperature=config["llm"]["temperature"]
)

# Set up Streamlit page
st.set_page_config(
    page_title="ESG & Impact Pre-Investment Analyzer",
    page_icon="🌍",
    layout="wide"
)

st.title("ESG & Impact Pre-Investment Analyzer")
st.markdown("""
This tool helps investment teams generate comprehensive ESG and Impact reports during the pre-investment phase.
Enter the company information below to generate an analysis based on selected frameworks.
""")

# Input form
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
    
    st.subheader("Analysis Parameters")
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

# Process form submission
if submitted:
    if not company_name or not country or not sector or not description:
        st.error("Please fill in all required fields.")
    elif not frameworks:
        st.error("Please select at least one ESG framework.")
    else:
        try:
            with st.spinner("Generating analysis..."):
                # Prepare company info
                company_info = {
                    "name": company_name,
                    "country": country,
                    "sector": sector,
                    "description": description,
                    "size": size if size else None
                }
                
                # Generate prompt
                prompt = prompt_manager.generate_analysis_prompt(
                    company_info=company_info,
                    selected_frameworks=frameworks,
                    detail_level=detail_level
                )
                
                # Get LLM response
                response = llm_service.generate_response(
                    prompt,
                    max_tokens=config["llm"]["max_tokens"]
                )
                
                # Display results
                st.markdown("## Analysis Results")
                st.markdown(response)
                
                # Add download button for the report
                st.download_button(
                    label="Download Report",
                    data=response,
                    file_name=f"esg_analysis_{company_name.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )
                
        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            st.error("An error occurred while generating the analysis. Please try again.") 