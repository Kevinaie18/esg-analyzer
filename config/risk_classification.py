"""
Configuration du système de classification des risques E&S basé sur les directives IFC.
"""

RISK_CATEGORIES = {
    'A': {
        'name': 'High Risk',
        'description': 'Projects with potential significant adverse environmental and/or social risks and/or impacts that are diverse, irreversible or unprecedented.',
        'investment_allowed': False,
        'due_diligence': 'Full external ESG due diligence required'
    },
    'B+': {
        'name': 'Medium-High Risk',
        'description': 'Projects with potential limited adverse environmental and/or social risks and/or impacts that are few in number, generally site-specific, largely reversible and readily addressed through mitigation measures.',
        'investment_allowed': True,
        'due_diligence': 'External ESG due diligence required'
    },
    'B-': {
        'name': 'Medium-Low Risk',
        'description': 'Projects with minimal adverse environmental and/or social risks and/or impacts that are few in number, site-specific, largely reversible and readily addressed through mitigation measures.',
        'investment_allowed': True,
        'due_diligence': 'Internal ESG review required'
    },
    'C': {
        'name': 'Low Risk',
        'description': 'Projects with minimal or no adverse environmental and/or social risks and/or impacts.',
        'investment_allowed': True,
        'due_diligence': 'Basic ESG screening required'
    }
}

# Mapping des secteurs vers les catégories de risque
SECTOR_RISK_MAPPING = {
    'Mining': 'A',
    'Oil & Gas': 'A',
    'Thermal Power': 'A',
    'Nuclear Power': 'A',
    'Large Dams': 'A',
    'Infrastructure': 'B+',
    'Manufacturing': 'B+',
    'Agriculture': 'B+',
    'Forestry': 'B+',
    'Tourism': 'B-',
    'Healthcare': 'B-',
    'Education': 'B-',
    'Technology': 'C',
    'Services': 'C'
}

# Mapping des sous-secteurs vers les catégories de risque
SUBSECTOR_RISK_MAPPING = {
    # Mining
    'Coal Mining': 'A',
    'Metal Mining': 'A',
    'Mineral Mining': 'A',
    
    # Oil & Gas
    'Onshore Oil & Gas': 'A',
    'Offshore Oil & Gas': 'A',
    'LNG': 'A',
    
    # Power
    'Coal Power': 'A',
    'Gas Power': 'B+',
    'Wind Power': 'B-',
    'Solar Power': 'B-',
    'Geothermal': 'B-',
    
    # Manufacturing
    'Steel': 'B+',
    'Cement': 'B+',
    'Chemicals': 'B+',
    'Textiles': 'B+',
    'Food Processing': 'B+',
    
    # Infrastructure
    'Ports': 'B+',
    'Airports': 'B+',
    'Railways': 'B+',
    'Roads': 'B+',
    
    # Agriculture
    'Large Scale Agriculture': 'B+',
    'Livestock': 'B+',
    'Aquaculture': 'B+',
    
    # Services
    'IT Services': 'C',
    'Financial Services': 'C',
    'Healthcare Services': 'B-',
    'Education Services': 'B-'
}

# Mapping des secteurs vers les standards IFC applicables
SECTOR_IFC_STANDARDS = {
    'Mining': [1, 2, 3, 4, 6, 7, 8],
    'Oil & Gas': [1, 2, 3, 4, 6, 7, 8],
    'Thermal Power': [1, 2, 3, 4, 6, 7, 8],
    'Infrastructure': [1, 2, 3, 4, 5, 6, 7, 8],
    'Manufacturing': [1, 2, 3, 4, 6, 7, 8],
    'Agriculture': [1, 2, 3, 4, 5, 6, 7, 8],
    'Forestry': [1, 2, 3, 4, 5, 6, 7, 8],
    'Tourism': [1, 2, 3, 4, 5, 6, 7, 8],
    'Healthcare': [1, 2, 3, 4, 5, 6, 7, 8],
    'Education': [1, 2, 3, 4, 5, 6, 7, 8],
    'Technology': [1, 2, 3, 4, 5, 6, 7, 8],
    'Services': [1, 2, 3, 4, 5, 6, 7, 8]
}

# Description des standards IFC
IFC_STANDARDS = {
    1: 'Assessment and Management of Environmental and Social Risks and Impacts',
    2: 'Labor and Working Conditions',
    3: 'Resource Efficiency and Pollution Prevention',
    4: 'Community Health, Safety and Security',
    5: 'Land Acquisition and Involuntary Resettlement',
    6: 'Biodiversity Conservation and Sustainable Natural Resource Management',
    7: 'Indigenous Peoples',
    8: 'Cultural Heritage'
} 