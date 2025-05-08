"""
Enhanced prompt templates for comprehensive ESG and Impact analysis.
"""

from typing import Dict, List, Optional
from jinja2 import Template
from loguru import logger
from standards.loader import StandardsLoader, StandardCriterion

class EnhancedPromptManager:
    """Manages the generation and assembly of enhanced prompts for ESG analysis."""
    
    def __init__(self, standards_loader: StandardsLoader):
        self.standards_loader = standards_loader
        
    def _get_criteria_text(self, criteria: List[StandardCriterion]) -> str:
        """Convert criteria to formatted text with priority indicators."""
        return "\n".join([
            f"- {c.id}: {c.title} ({c.priority.upper()} priority)\n  {c.description}"
            for c in criteria
        ])
        
    def _get_business_activities_template(self) -> str:
        """Template for business activities analysis."""
        return """
BUSINESS ACTIVITIES ANALYSIS:
For each significant business activity identified, please provide:
1. Activity name and description
2. Estimated % of revenue/operations
3. Key ESG risks and opportunities specific to this activity
4. Climate impact and solutions
5. Social impact potential
6. Alignment with IPAE3's impact thesis

Please use this format for each activity:
ACTIVITY: [Name]
REVENUE SHARE: [Percentage]
KEY ESG FACTORS:
- Environmental: [List key factors]
- Social: [List key factors]
- Governance: [List key factors]
CLIMATE IMPACT: [Analysis]
SOCIAL IMPACT: [Analysis]
IPAE3 ALIGNMENT: [Analysis]
"""
        
    def generate_analysis_prompt(
        self,
        company_info: Dict,
        selected_frameworks: List[str],
        detail_level: str = "standard"
    ) -> str:
        """Generate the enhanced main analysis prompt."""
        
        # Load selected standards
        standards = {
            fw: self.standards_loader.load_standard(fw)
            for fw in selected_frameworks
        }
        
        # Extract criteria by pillar
        criteria_by_pillar = {
            pillar: []
            for pillar in ['E', 'S', 'G']
        }
        
        for standard in standards.values():
            if standard:
                for criterion in standard.criteria:
                    criteria_by_pillar[criterion.pillar].append(criterion)
        
        # Generate the enhanced prompt template
        template = Template("""
You are an expert ESG and Impact analyst specializing in pre-investment analysis. Your task is to analyze the following company information and provide a comprehensive ESG and Impact assessment based on the specified frameworks.

COMPANY INFORMATION:
Name: {{ company_info.name }}
Country: {{ company_info.country }}
Sector: {{ company_info.sector }}
Description: {{ company_info.description }}
{% if company_info.size %}
Size: {{ company_info.size }}
{% endif %}

ANALYSIS FRAMEWORKS:
{% for framework in selected_frameworks %}
- {{ framework.upper() }}
{% endfor %}

RELEVANT CRITERIA:

ENVIRONMENTAL (E):
{{ criteria_e }}

SOCIAL (S):
{{ criteria_s }}

GOVERNANCE (G):
{{ criteria_g }}

{{ business_activities_template }}

Please provide a structured analysis following this format:

1. EXECUTIVE SUMMARY (1 page max)
   - Key ESG risks and opportunities
   - Main impact potential
   - Critical areas for due diligence
   - Overall alignment with IPAE3's impact thesis

2. BUSINESS ACTIVITIES BREAKDOWN
   - Detailed analysis of each major business activity
   - Revenue/operations distribution
   - Activity-specific ESG risks and opportunities
   - Cross-activity synergies and conflicts

3. ENVIRONMENTAL ANALYSIS
   - Key environmental risks and opportunities
   - Climate impact assessment:
     * Climate solutions provided by the company
     * Company's vulnerability to climate risks
     * Adaptation strategies and readiness
     * Carbon footprint analysis
     * Potential for decoupling growth from emissions
   - Environmental management practices
   - Scoring against key environmental standards

4. SOCIAL ANALYSIS
   - Key social risks and opportunities
   - Labor and community relations
   - Social impact potential
   - Gender empowerment assessment
   - Decent jobs creation potential
   - Scoring against key social standards

5. GOVERNANCE ANALYSIS
   - Key governance risks and opportunities
   - Corporate structure and controls
   - Compliance and ethics
   - Scoring against key governance standards

6. IMPACT THESIS ALIGNMENT
   - Local entrepreneurship support
   - Decent jobs creation
   - Climate action and resilience
   - Gender empowerment
   - Overall impact potential
   - Alignment with IPAE3's objectives

7. RECOMMENDATIONS
   - Priority actions for due diligence
   - Suggested ESG clauses for shareholder agreement
   - Key performance indicators to track
   - Activity-specific recommendations
   - Cross-activity improvement opportunities

Please ensure your analysis is:
- Evidence-based and focused on the information provided
- Aligned with the specified frameworks
- Actionable and specific to the company's context
- Clear about any assumptions or limitations
- Includes specific references to relevant standards
- Provides clear risk scoring and prioritization
- Addresses both individual activities and their combined impact
""")
        
        # Render the template
        prompt = template.render(
            company_info=company_info,
            selected_frameworks=selected_frameworks,
            criteria_e=self._get_criteria_text(criteria_by_pillar['E']),
            criteria_s=self._get_criteria_text(criteria_by_pillar['S']),
            criteria_g=self._get_criteria_text(criteria_by_pillar['G']),
            business_activities_template=self._get_business_activities_template()
        )
        
        return prompt

    def generate_docx_template(self) -> str:
        """Generate the template for DOCX export formatting."""
        return """
DOCX FORMATTING INSTRUCTIONS:

1. Document Structure
   - Title: Company Name - ESG & Impact Analysis
   - Executive Summary: 1 page
   - Table of Contents
   - Main sections with clear headings
   - Appendices for detailed criteria

2. Formatting Guidelines
   - Headings: Arial, 14pt, Bold
   - Subheadings: Arial, 12pt, Bold
   - Body text: Arial, 11pt
   - Tables: Arial, 10pt
   - Colors: Use IPAE3 brand colors for highlights

3. Tables and Visualizations
   - Business activities breakdown
   - ESG risk matrix
   - Impact alignment scoring
   - Climate vulnerability assessment
   - Cross-activity comparison

4. Appendices
   - Detailed criteria assessment
   - Risk scoring methodology
   - Impact metrics definitions
   - Climate analysis methodology
""" 