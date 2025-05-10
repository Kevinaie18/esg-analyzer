import re
from typing import List, Dict

def parse_section(text: str, section_title: str) -> str:
    """Extract a section by its title (case-insensitive, flexible heading)."""
    pattern = rf"^#+\s*{re.escape(section_title)}.*$"
    matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
    if not matches:
        return ""
    start = matches[0].end()
    next_match = next((m for m in re.finditer(r"^#+\s*", text[start:], re.MULTILINE)), None)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()

def parse_list_section(section: str) -> List[str]:
    """Parse a bullet or numbered list section into a list of strings."""
    lines = section.splitlines()
    items = []
    for line in lines:
        line = line.strip()
        if re.match(r"^[-*\d+.]", line):
            items.append(re.sub(r"^[-*\d+.]+\s*", "", line))
    return items

def parse_table_section(section: str, header_fields: List[str]) -> List[Dict]:
    """Parse a Markdown table into a list of dicts with given header fields."""
    lines = [l for l in section.splitlines() if l.strip()]
    table = []
    header_idx = None
    for i, line in enumerate(lines):
        if all(h.lower() in line.lower() for h in header_fields):
            header_idx = i
            break
    if header_idx is None or header_idx + 2 >= len(lines):
        return table
    for row in lines[header_idx + 2:]:
        cells = [c.strip() for c in row.split('|') if c.strip()]
        if len(cells) == len(header_fields):
            table.append(dict(zip(header_fields, cells)))
    return table

def parse_climate_impact(section: str) -> Dict:
    """Parse the climate impact assessment section into a dict."""
    keys = [
        ("climate_solutions", "Climate Solutions"),
        ("vulnerability", "Vulnerability"),
        ("adaptation", "Adaptation"),
        ("carbon_footprint", "Carbon Footprint"),
        ("decoupling", "Decoupling Potential")
    ]
    result = {}
    for key, label in keys:
        m = re.search(rf"{label}[:\-\s]+(.+)", section, re.IGNORECASE)
        result[key] = m.group(1).strip() if m else ""
    return result

def parse_impact_alignment(section: str) -> Dict:
    keys = [
        ("local_entrepreneurship", "Local Entrepreneurship"),
        ("decent_jobs", "Decent Jobs"),
        ("climate_action", "Climate Action"),
        ("gender_empowerment", "Gender Empowerment"),
        ("resilience", "Resilience"),
        ("overall_impact", "Overall Impact")
    ]
    result = {}
    for key, label in keys:
        m = re.search(rf"{label}[:\-\s]+(.+)", section, re.IGNORECASE)
        result[key] = m.group(1).strip() if m else ""
    return result

def parse_kpis(section: str) -> List[Dict]:
    """Parse KPIs from a Markdown table or list."""
    # Try table first
    table = parse_table_section(section, ["KPI", "Target", "Frequency"])
    if table:
        return table
    # Fallback: parse as list
    items = parse_list_section(section)
    return [dict(name=item, target="", frequency="") for item in items]

def parse_llm_report(text: str, company_name: str) -> dict:
    """Parse the LLM output into the structure expected by DocxFormatter."""
    # Initialize with default values
    analysis = {
        "company_name": company_name,
        "executive_summary": "",
        "business_activities": [],
        "environmental_analysis": "",
        "climate_impact": {
            "climate_solutions": "Not specified",
            "vulnerability": "Not specified",
            "adaptation": "Not specified",
            "carbon_footprint": "Not specified",
            "decoupling": "Not specified"
        },
        "social_analysis": "",
        "governance_analysis": "",
        "impact_alignment": {
            "local_entrepreneurship": "Not specified",
            "decent_jobs": "Not specified",
            "climate_action": "Not specified",
            "gender_empowerment": "Not specified",
            "resilience": "Not specified",
            "overall_impact": "Not specified"
        },
        "recommendations": {
            "due_diligence": [],
            "esg_clauses": [],
            "kpis": []
        }
    }

    try:
        # Executive Summary
        summary = parse_section(text, "Executive Summary")
        if summary:
            analysis["executive_summary"] = summary

        # Business Activities
        ba_section = parse_section(text, "Business Activities Breakdown")
        if ba_section:
            activities = parse_table_section(
                ba_section, ["Activity", "Revenue Share", "Key ESG Factors", "Impact Alignment"]
            )
            if activities:
                analysis["business_activities"] = activities

        # Environmental Analysis
        env_analysis = parse_section(text, "Environmental Analysis")
        if env_analysis:
            analysis["environmental_analysis"] = env_analysis

        # Climate Impact
        climate_section = parse_section(text, "Climate Impact Assessment")
        if climate_section:
            climate_impact = parse_climate_impact(climate_section)
            if climate_impact:
                analysis["climate_impact"].update(climate_impact)

        # Social Analysis
        social_analysis = parse_section(text, "Social Analysis")
        if social_analysis:
            analysis["social_analysis"] = social_analysis

        # Governance Analysis
        gov_analysis = parse_section(text, "Governance Analysis")
        if gov_analysis:
            analysis["governance_analysis"] = gov_analysis

        # Impact Thesis Alignment
        impact_section = parse_section(text, "Impact Thesis Alignment")
        if impact_section:
            impact_alignment = parse_impact_alignment(impact_section)
            if impact_alignment:
                analysis["impact_alignment"].update(impact_alignment)

        # Recommendations
        rec_section = parse_section(text, "Recommendations")
        if rec_section:
            # Due Diligence Actions
            dd_section = parse_section(rec_section, "Priority Due Diligence Actions")
            if dd_section:
                dd_actions = parse_list_section(dd_section)
                if dd_actions:
                    analysis["recommendations"]["due_diligence"] = dd_actions

            # ESG Clauses
            esg_section = parse_section(rec_section, "Suggested ESG Clauses")
            if esg_section:
                esg_clauses = parse_list_section(esg_section)
                if esg_clauses:
                    analysis["recommendations"]["esg_clauses"] = esg_clauses

            # KPIs
            kpi_section = parse_section(rec_section, "Key Performance Indicators")
            if kpi_section:
                kpis = parse_kpis(kpi_section)
                if kpis:
                    analysis["recommendations"]["kpis"] = kpis

    except Exception as e:
        print(f"Warning: Error parsing LLM response: {str(e)}")
        # Return the analysis with default values if parsing fails

    return analysis 