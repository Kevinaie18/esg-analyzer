"""
Enhanced prompt templates for actionable ESG and Impact analysis with dynamic sector adaptation.
"""

from typing import Dict, List, Optional
from jinja2 import Template
from loguru import logger
from standards.loader import StandardsLoader, StandardCriterion

# Example sector-specific prompt blocks (expand as needed)
SECTOR_PROMPT_BLOCKS = {
    "Agribusiness": """
### SECTOR-SPECIFIC FOCUS: AGRIBUSINESS

INDUSTRY BEST PRACTICES:
- Water Management:
  * Efficient irrigation systems
  * Water recycling programs
  * Rainwater harvesting
  * Water usage monitoring
  * Drought-resistant crops
- Soil Conservation:
  * Crop rotation practices
  * Organic farming methods
  * Regular soil testing
  * Erosion control measures
  * Sustainable land management
- Labor Standards:
  * Fair wages and working conditions
  * Training programs
  * Health and safety protocols
  * Worker housing standards
  * Child labor prevention
- Supply Chain:
  * Traceability systems
  * Smallholder inclusion
  * Fair trade practices
  * Local sourcing
  * Quality control
- Pay special attention to land use, biodiversity, water management, supply chain traceability, and labor rights in rural areas.
- Highlight SDGs 2, 12, 15, and relevant IFC PS6, PS1, and local agricultural standards.
- Identify risks related to deforestation, pesticide use, and smallholder inclusion.
""",
    "Manufacturing": """
### SECTOR-SPECIFIC FOCUS: MANUFACTURING
- Focus on resource efficiency, emissions, waste management, occupational health & safety, and supply chain labor standards.
- Highlight SDGs 9, 12, 13, and relevant IFC PS2, PS3, PS6, and ISO standards.
- Identify risks related to hazardous materials, energy use, and labor conditions.
""",
    "Services": """
### SECTOR-SPECIFIC FOCUS: SERVICES
- Emphasize data privacy, customer well-being, gender equality, and indirect environmental impacts (e.g., energy use in IT).
- Highlight SDGs 5, 8, 9, and relevant IFC PS2, PS4, and digital sector codes.
- Identify risks related to gender disparity, digital inclusion, and E&S management systems.
""",
    "Healthcare": """
### SECTOR-SPECIFIC FOCUS: HEALTHCARE
- Focus on patient safety, access to healthcare, supply chain ethics, and waste management (medical waste).
- Highlight SDGs 3, 5, 10, and relevant IFC PS2, PS4, and healthcare regulations.
- Identify risks related to access, affordability, and regulatory compliance.
"""
}

class EnhancedPromptManager:
    """Manages the generation and assembly of enhanced prompts for ESG analysis, with dynamic sector adaptation."""
    
    def __init__(self, standards_loader: StandardsLoader):
        self.standards_loader = standards_loader
        
    def _get_criteria_text(self, criteria: List[StandardCriterion]) -> str:
        """Convert criteria to formatted text with priority indicators."""
        return "\n".join([
            f"- {c.id}: {c.title} ({c.priority.upper()} priority)\n  {c.description}"
            for c in criteria
        ])

    def _get_sector_prompt_block(self, sector: str) -> str:
        """Return sector-specific prompt block if available."""
        return SECTOR_PROMPT_BLOCKS.get(sector, "")

    def generate_analysis_prompt(
        self,
        company_info: Dict,
        selected_frameworks: List[str],
        detail_level: str = "standard"
    ) -> str:
        """Generate the actionable main analysis prompt, dynamically adapted to sector, size, and geography."""
        
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
        
        # Get sector-specific block
        sector_block = self._get_sector_prompt_block(company_info.get("sector", ""))
        
        # Generate the actionable prompt template
        template = Template("""
You are an expert ESG and Impact analyst. Your task is to extract actionable, investment-relevant insights for the following company. Focus on identifying the most critical ESG and impact issues, referencing specific standards and frameworks.

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

{{ sector_block }}

---

# ACTIONABLE INSIGHTS REPORT

## 1. SDG ALIGNMENT
- Which specific UN Sustainable Development Goals (SDGs) does the company contribute to?
- For each SDG, explain HOW the company contributes (reference business activities, products, or services).
- Use SDG icons or numbers for clarity.

## 2. IFC PERFORMANCE STANDARDS
- Which IFC Performance Standards are most relevant to this company's operations? List the top 3-5.
- For each, explain WHY it applies (reference company activities, sector, geography, or risks).
- If any standards are not relevant, briefly state why.

## 3. SECTOR-SPECIFIC STANDARDS & RISKS
- Identify the most important industry-specific standards, guidelines, or corrective measures for this company (e.g., SASB, GRI, ISO, local codes).
- List the top 3 sector-specific ESG risks and the standards that address them.
- For each, explain the connection to the company's business model.

## 4. IPAE3 IMPACT FRAMEWORK ALIGNMENT
- Assess the company's alignment with the following impact pillars:
  - Local entrepreneurship
  - Decent jobs & job creation
  - Gender lens & empowerment
  - Climate action & resilience
- For each pillar, provide a clear assessment (aligned/partially aligned/not aligned) and justification.

## 5. 2X CHALLENGE CRITERIA (if applicable)
- Score the company against the 2X Challenge criteria (0-2 scale: 0=not met, 1=partially met, 2=fully met).
- For each criterion, provide a brief justification.

## 6. STAKEHOLDER ENGAGEMENT ANALYSIS
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

## 7. SUMMARY DASHBOARD
- Create a summary table showing:
  - SDGs addressed (with icons/numbers)
  - Relevant IFC standards
  - Key sector standards
  - IPAE3 pillar alignment (with color-coded status)
  - 2X Challenge scores

## 7. DUE DILIGENCE ACTION CHECKLIST
- List the top 5-10 specific due diligence questions or actions for the investment team, derived from the standards and risks identified above.
- Make each item actionable and reference the relevant standard or risk.

---

**Instructions:**
- Be concise, specific, and actionable.
- Reference standards and frameworks directly (use numbers, icons, or color codes where possible).
- Justify all matches and scores.
- Lead with the summary dashboard and action checklist.
- Avoid generic analysis; focus on what matters most for investment decision-making.
""")
        
        # Render the template
        prompt = template.render(
            company_info=company_info,
            selected_frameworks=selected_frameworks,
            criteria_e=self._get_criteria_text(criteria_by_pillar['E']),
            criteria_s=self._get_criteria_text(criteria_by_pillar['S']),
            criteria_g=self._get_criteria_text(criteria_by_pillar['G']),
            sector_block=sector_block
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