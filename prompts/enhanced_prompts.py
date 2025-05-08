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

Please provide a detailed analysis following this format:

1. EXECUTIVE SUMMARY (1 page max)
   - Key ESG risks and opportunities (minimum 3 each)
   - Main impact potential (quantify where possible)
   - Critical areas for due diligence (prioritized list)
   - Overall alignment with IPAE3's impact thesis
   - Key findings and recommendations (top 5)

2. BUSINESS ACTIVITIES BREAKDOWN
   - Detailed analysis of each major business activity:
     * Revenue/operations distribution
     * Activity-specific ESG risks and opportunities
     * Climate impact and solutions
     * Social impact potential
     * Alignment with IPAE3's impact thesis
   - Cross-activity synergies and conflicts
   - Combined impact assessment
   - Activity-specific recommendations

3. ENVIRONMENTAL ANALYSIS
   - Key environmental risks and opportunities:
     * Direct environmental impacts
     * Indirect environmental impacts
     * Supply chain environmental risks
     * Resource efficiency opportunities
   - Climate impact assessment:
     * Climate solutions provided by the company
     * Company's vulnerability to climate risks
     * Adaptation strategies and readiness
     * Carbon footprint analysis
     * Potential for decoupling growth from emissions
   - Environmental management practices:
     * Current systems and policies
     * Compliance with environmental regulations
     * Environmental performance monitoring
     * Environmental training and awareness
   - Scoring against key environmental standards
   - Recommendations for environmental improvement

4. SOCIAL ANALYSIS
   - Key social risks and opportunities:
     * Labor rights and working conditions
     * Health and safety
     * Community relations
     * Human rights considerations
   - Labor and community relations:
     * Employee engagement
     * Community engagement
     * Stakeholder management
     * Grievance mechanisms
   - Social impact potential:
     * Job creation and quality
     * Skills development
     * Community development
     * Social inclusion
   - Gender empowerment assessment:
     * Gender representation
     * Equal opportunities
     * Gender-sensitive policies
     * Leadership development
   - Decent jobs creation potential:
     * Job quality metrics
     * Career development
     * Employee benefits
     * Work-life balance
   - Scoring against key social standards
   - Recommendations for social improvement

5. GOVERNANCE ANALYSIS
   - Key governance risks and opportunities:
     * Board composition and independence
     * Executive compensation
     * Shareholder rights
     * Anti-corruption measures
   - Corporate structure and controls:
     * Organizational structure
     * Internal controls
     * Risk management
     * Compliance systems
   - Compliance and ethics:
     * Code of conduct
     * Anti-corruption policies
     * Whistleblower protection
     * Ethics training
   - ESG integration:
     * ESG governance structure
     * ESG risk management
     * ESG performance monitoring
     * ESG reporting
   - Scoring against key governance standards
   - Recommendations for governance improvement

6. IMPACT THESIS ALIGNMENT
   - Local entrepreneurship support:
     * Local value chain development
     * Local supplier development
     * Local innovation support
     * Local market development
   - Decent jobs creation:
     * Job creation potential
     * Job quality assessment
     * Skills development
     * Career progression
   - Climate action and resilience:
     * Climate solutions
     * Climate risk management
     * Climate adaptation
     * Climate mitigation
   - Gender empowerment:
     * Gender representation
     * Equal opportunities
     * Gender-sensitive policies
     * Leadership development
   - Overall impact potential:
     * Combined impact assessment
     * Impact scalability
     * Impact sustainability
     * Impact measurement
   - Alignment with IPAE3's objectives:
     * Strategic alignment
     * Impact additionality
     * Impact risks
     * Impact opportunities

7. RECOMMENDATIONS
   - Priority actions for due diligence:
     * Critical areas to investigate
     * Key documents to review
     * Key stakeholders to engage
     * Key metrics to verify
   - Suggested ESG clauses for shareholder agreement:
     * Governance requirements
     * Environmental commitments
     * Social commitments
     * Impact commitments
   - Key performance indicators to track:
     * Environmental KPIs
     * Social KPIs
     * Governance KPIs
     * Impact KPIs
   - Activity-specific recommendations:
     * Environmental improvements
     * Social improvements
     * Governance improvements
     * Impact improvements
   - Cross-activity improvement opportunities:
     * Synergies to leverage
     * Conflicts to resolve
     * Combined improvements
     * Integrated solutions

Please ensure your analysis is:
- Evidence-based and focused on the information provided
- Aligned with the specified frameworks
- Actionable and specific to the company's context
- Clear about any assumptions or limitations
- Includes specific references to relevant standards
- Provides clear risk scoring and prioritization
- Addresses both individual activities and their combined impact
- Quantifies impacts and risks where possible
- Provides concrete examples and specific recommendations
- Considers both short-term and long-term implications
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