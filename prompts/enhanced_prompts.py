"""
Enhanced prompts for ESG & Impact analysis report generation.
This module contains the master prompt template and section-specific sub-prompts
for generating structured ESG & Impact pre-investment analysis reports.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

# Icons and visual elements
ICONS = {
    "high_risk": "🔴",
    "medium_risk": "🟠",
    "low_risk": "🟡",
    "minimal_risk": "🟢",
    "sdg": "🌍",
    "impact": "💫",
    "stakeholder": "👥",
    "check": "✅",
    "warning": "⚠️",
    "info": "ℹ️",
}

# Color codes for risk levels
RISK_COLORS = {
    "Cat A": "red",
    "Cat B+": "orange",
    "Cat B-": "yellow",
    "Cat C": "green",
}

# Master prompt template
MASTER_PROMPT_TEMPLATE = """
You are an expert ESG & Impact analyst for an African impact investment fund (IPAE3).
Your task is to generate a structured ESG & Impact pre-investment analysis report.

# REQUIRED OUTPUT FORMAT
Your report must strictly follow this structure:

# ACTIONABLE INSIGHTS REPORT

## 1. SUMMARY DASHBOARD
- Create a concise, visual summary dashboard that displays at a glance:
 * E&S Risk Classification (with color-coding: Red for Cat A, Orange for Cat B+, Yellow for Cat B-, Green for Cat C)
 * External DD Required (Yes/No)
 * Top 3 Applicable IFC Standards (numbered list)
 * Primary Sector-Specific Risks (bullet points)
 * IPAE3 Impact Alignment Score (visual gauge or percentage)
 * Key SDG Contributions (using SDG icons)
 * 2X Challenge Eligibility (Yes/Partial/No)
 * Top 3 Due Diligence Priorities (numbered list)
- This dashboard must be highly visual, compact (maximum half-page), and instantly informative
- Use tables, icons, and color-coding for maximum clarity

## 2. E&S CLASSIFICATION
- Based on the sector and subsector, provide the associated risk level (Cat A, Cat B+, Cat B-, Cat C)
- Determine if there is a need to perform external due diligence
- If Category A, clearly flag that IPAE3 cannot invest in this project

## 3. E&S IFC ANALYSIS
### 3.A APPLICABLE STANDARDS
- List the relevant IFC Performance Standards for this company
- For each standard:
 * Explain why it applies to this company
 * Highlight key risks and opportunities associated
 * Suggest implementation priorities

### 3.B SECTORIAL RECOMMENDATIONS
- Provide sector-specific EHS recommendations from IFC guidelines
- Include best practices for:
 * Environmental management
 * Health and safety
 * Social impact
- Prioritize recommendations based on risk level and feasibility

### 3.C OTHER SECTOR-SPECIFIC STANDARDS & RISKS
- Identify important industry-specific standards, guidelines, or corrective measures (e.g., SASB, GRI, ISO, local codes)
- List the top 3 sector-specific ESG risks and the standards that address them
- For each, explain the connection to the company's business model

## 4. STAKEHOLDER ENGAGEMENT ANALYSIS
- Map key stakeholders and their influence:
 * Internal: Management, Employees, Board
 * External: Customers, Suppliers, Community, Regulators
- For each stakeholder group:
 * Current engagement level (High/Medium/Low)
 * Key concerns and expectations
 * Potential risks and opportunities
- Initial engagement recommendations:
 * Priority stakeholders for immediate engagement
 * Key topics to address
 * Suggested engagement methods
 * Timeline for engagement
 * Success metrics

## 5. IMPACT ANALYSIS

### 5.A IPAE3 IMPACT FRAMEWORK ALIGNMENT
- Assess the company's alignment with the following impact pillars:
 * Local entrepreneurship
 * Decent jobs & job creation
 * Gender lens & empowerment
 * Climate action & resilience
- For each pillar, provide a clear assessment (aligned/partially aligned/not aligned) and justification

### 5.B SDG ALIGNMENT
- Identify specific UN Sustainable Development Goals (SDGs) the company contributes to
- For each SDG, explain HOW the company contributes (reference business activities, products, or services)
- Use SDG icons or numbers for clarity

### 5.C 2X CHALLENGE CRITERIA (if applicable)
- Score the company against the 2X Challenge criteria (0-2 scale: 0=not met, 1=partially met, 2=fully met)
- For each criterion, provide a brief justification

## 6. DUE DILIGENCE ACTION CHECKLIST
- List the top 5-10 specific due diligence questions or actions for the investment team
- Make each item actionable and reference the relevant standard or risk

# ANALYSIS APPROACH

For the Summary Dashboard:
- Make it extremely concise and scannable in under 10 seconds
- Use tables, icons, and visual indicators
- Present only the most critical information
- Be concrete and specific in your assessments

For E&S Classification:
- Base classification on IFC EHS Guidelines for the specific sector
- Consider both direct and indirect impacts
- Factor in country-specific risk factors
- Document the rationale for the classification

For IFC Analysis:
- Focus on standards that are most relevant to the company's operations
- Prioritize standards based on potential impact severity
- Consider both current and future operations
- Reference specific IFC guidelines and requirements

For Stakeholder Analysis:
- Identify all relevant stakeholder groups
- Assess current engagement levels
- Consider cultural and local context
- Prioritize based on influence and impact

For Impact Analysis:
- Use concrete metrics where possible
- Consider both direct and indirect impacts
- Assess alignment with IPAE3's impact goals
- Document evidence for each assessment

# COMPANY INFORMATION
Company Name: {company_name}
Sector: {sector}
Subsector: {subsector}
Country: {country}
Company Description: {company_description}

# REFERENCE FRAMEWORKS
- IFC Performance Standards
- IFC EHS Guidelines
- UN Sustainable Development Goals
- 2X Challenge Criteria
- IPAE3 Impact Framework
"""

# Section-specific sub-prompts
SUMMARY_DASHBOARD_PROMPT = """
Generate a concise, visual summary dashboard for {company_name} that includes:
1. E&S Risk Classification with color coding
2. External DD requirement status
3. Top 3 applicable IFC Standards
4. Primary sector-specific risks
5. IPAE3 Impact Alignment Score
6. Key SDG Contributions
7. 2X Challenge Eligibility
8. Top 3 Due Diligence Priorities

Use tables, icons, and color-coding for maximum clarity.
Keep the dashboard to a maximum of half a page.
"""

ES_CLASSIFICATION_PROMPT = """
Based on the following information, determine the E&S Classification for {company_name}:
- Sector: {sector}
- Subsector: {subsector}
- Country: {country}
- Operations: {operations}

Provide:
1. Risk Classification (Cat A/B+/B-/C)
2. External DD requirement
3. Justification for the classification
4. Key risk factors considered
"""

IFC_ANALYSIS_PROMPT = """
Analyze the applicability of IFC Performance Standards for {company_name}:
1. List relevant standards
2. For each standard:
   - Explain applicability
   - Identify key risks
   - Suggest implementation priorities
3. Provide sector-specific EHS recommendations
4. Identify other relevant standards and guidelines

Reference: IFC EHS Guidelines for {sector}
"""

STAKEHOLDER_ANALYSIS_PROMPT = """
Map and analyze stakeholders for {company_name}:
1. Internal stakeholders:
   - Management
   - Employees
   - Board
2. External stakeholders:
   - Customers
   - Suppliers
   - Community
   - Regulators

For each group:
- Current engagement level
- Key concerns
- Potential risks/opportunities
- Recommended engagement approach
"""

IMPACT_ANALYSIS_PROMPT = """
Assess {company_name}'s impact alignment:
1. IPAE3 Impact Framework:
   - Local entrepreneurship
   - Decent jobs & job creation
   - Gender lens & empowerment
   - Climate action & resilience

2. SDG Alignment:
   - Identify relevant SDGs
   - Explain contribution mechanisms
   - Provide evidence

3. 2X Challenge Criteria:
   - Score each criterion (0-2)
   - Justify scores
   - Identify gaps
"""

DD_CHECKLIST_PROMPT = """
Generate a due diligence action checklist for {company_name}:
1. List 5-10 specific actions/questions
2. Reference relevant standards/risks
3. Prioritize based on:
   - Risk level
   - Impact severity
   - Implementation feasibility
4. Include timeline recommendations
"""

@dataclass
class PromptContext:
    """Context data for prompt generation."""
    company_name: str
    sector: str
    subsector: str
    country: str
    company_description: str
    operations: Optional[str] = None
    additional_context: Optional[Dict] = None

def generate_master_prompt(context: PromptContext) -> str:
    """Generate the master prompt with the provided context."""
    return MASTER_PROMPT_TEMPLATE.format(
        company_name=context.company_name,
        sector=context.sector,
        subsector=context.subsector,
        country=context.country,
        company_description=context.company_description
    )

def generate_section_prompt(section: str, context: PromptContext) -> str:
    """Generate a section-specific prompt."""
    prompts = {
        "summary": SUMMARY_DASHBOARD_PROMPT,
        "es_classification": ES_CLASSIFICATION_PROMPT,
        "ifc_analysis": IFC_ANALYSIS_PROMPT,
        "stakeholder": STAKEHOLDER_ANALYSIS_PROMPT,
        "impact": IMPACT_ANALYSIS_PROMPT,
        "dd_checklist": DD_CHECKLIST_PROMPT
    }
    
    if section not in prompts:
        raise ValueError(f"Unknown section: {section}")
        
    return prompts[section].format(
        company_name=context.company_name,
        sector=context.sector,
        subsector=context.subsector,
        country=context.country,
        operations=context.operations or "Not specified"
    )

class EnhancedPromptManager:
    """Manager class for handling enhanced prompts and their generation."""
    
    def __init__(self, standards_loader):
        """Initialize the prompt manager with a standards loader."""
        self.standards_loader = standards_loader

    def generate_analysis_prompt(self, company_info: Dict, selected_frameworks: List[str], detail_level: str = "standard") -> str:
        """
        Generate the main analysis prompt based on company information and selected frameworks.
        
        Args:
            company_info: Dictionary containing company details
            selected_frameworks: List of selected ESG frameworks
            detail_level: Level of detail for the analysis ("standard" or "detailed")
            
        Returns:
            str: Formatted prompt for the LLM
        """
        context = PromptContext(
            company_name=company_info["name"],
            sector=company_info["sector"],
            subsector=company_info.get("subsector", ""),
            country=company_info["country"],
            company_description=company_info["description"],
            operations=company_info.get("size", ""),
            additional_context={
                "frameworks": selected_frameworks,
                "detail_level": detail_level
            }
        )
        
        # Generate the master prompt
        prompt = generate_master_prompt(context)
        
        # Add framework-specific context if needed
        if "ifc" in selected_frameworks:
            prompt += "\n\nIFC Standards Context:\n" + self.standards_loader.get_ifc_standards()
        
        return prompt 