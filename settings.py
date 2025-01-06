RELEVANT_KEYWORDS = [
    "climate change", "global warming", "carbon emission", "greenhouse gas",
    "carbon footprint", "Paris Agreement", "climate action", "renewable energy",
    "carbon neutrality", "sustainability", "climate crisis", "greenhouse effect",
    "climate policy", "clean energy", "environmental impact", "extreme weather",
    "carbon taxes", "climate adaptation", "climate mitigation", "fossil fuel",
    "clean technology", "green tech", "electric vehicle", "solar power", "wind power",
    "energy transition", "carbon pricing", "climate finance",
    "carbon credit", "carbon trading", "sustainable development", "climate justice",
    "climate activism", "climate legislation", "climate model",
    "climate science" "oceans and climate change",
    "melting ice", "sea level rise", "biodiversity loss",
    "geoengineering", "natural disasters", "heatwave", "wildfire", "drought", "flooding",
    "hurricane", "sustainable agriculture", "water scarcity",
    "deforestation", "forest conservation",
    "un climate summit", "cop27", "climate pact", "net zero", "friday for future",
    "warming climate", "global temperature", "changing temperature", "warmer temperature",
    "climate denial"
]

label_keywords = {
    "causes": {
        "Energy and Industry": [
            "Fossil Fuel", "Transportation", "Fossil Fuel Emission", "Oil", "Gas", "Coal", "Electricity", 
            "Power Plant", "Carbon Emission", "Natural Gas", "Hydraulic Fracturing", "Greenhouse Gas",
            "Carbon Intensity", "Nuclear Power", "Fossil Fuel Subsidie", "Oil Sand", "Carbon Capture", "Oil Refining", 
            "Gasoline", "Methane Emission", "Coal Mining", "Diesel", "Energy infrastructure", "Energy consumption",
            "Industry", "Shipping", "supply chain", "greenhouse effect"
        ],
        "Land Use and Agriculture": [
            "Deforestation", "Agriculture", "Farming", "Farm", "Soil Degradation", "Land degradation", "Crop", "Land Clearing", "Monoculture", 
            "Pesticide", "Livestock", "Agroforestry", "Irrigation", "Desertification", "Overgrazing", "Crop Monoculture", 
            "Soil Erosion", "Wetland", "Greenhouse Gas Emission", "Water Usage", "Fertilizer", "environmental degradation", 
            "Biodiversity loss", "Land conversion", "Real estate development", "Intensive Farming"
        ],
        "Governance and Policy (Causes)": [
            "Policy", "Government", "Governance", "Inaction", "Policy Gap", "Legislation", "Subsidy", "Lobbying", "Bureaucracy", 
            "Fossil Fuel Subsidy", "Carbon Pricing", "Environmental Regulation", "Political Will", "Policy Maker", 
            "Government Inaction", "Lobbying Influence", "Energy Policy", "Climate Denial", "Corporate Interest", 
            "Regulation", "Policy Failure", "Skepticism", "Greenwashing", "Politic"
        ],
        "Personal Consumption": [
            "Consumption", "Waste", "Footprint", "Lifestyle", "Carbon Footprint", "Materialism", "Affluence", "Diet", 
            "Overconsumption", "Greenwashing", "Packaging", "car emission", "Flying", "Plane", "Air traffic", "Air travel",
            "Gasoline", "Meat consumption", "Beef", "Processed food", "Food waste", "Plastic", "Package", "Fast fashion", "Disposable",
            "Shipping", "E-waste", "Tourism", "Cruise", "Water consumption", "consuming"
        ]
    },
    "consequences": {
        "Ecosystem Disruption": [
            "Biodiversity", "Ecosystem", "Habitat Loss", "Habitat", "Coral", "Specie", "Extinction", "Marine Life", "Forest",
            "Forest Loss", "Erosion", "Invasive Specie", "Ocean Acidification", "Specie Decline", "Coastal Erosion", 
            "Marine Ecosystem", "Biodiversity", "Ecological Imbalance", "disruption", "Pollution", "water pollution", "ocean",
            "Crisis"
        ],
        "Extreme Weather Events": [
            "Heatwave", "Flooding", "Drought", "Wildfire", "Hurricane", "Storm", "Cyclone", "Typhoon", "Flood", 
            "Weather Event", "Severe Weather", "Tornadoes", "Intense Storm", "Extreme Temperature", "Rain",
            "Tidal Wave", "Blizzard", "Ice Storm", "Weather Disaster", "ocean circulation", "melting", "melt", "global heating", 
            "climate change", "ocean rise", "ocean", "warmer", "warming"
        ],
        "Health Risks": [
            "Health", "Disease", "Air Pollution", "Heat Stroke", "Malnutrition", "Vector-Borne Disease", "Respiratory Illness", 
            "Cancer", "Water Scarcity", "Scarcity", "Mental Health", "Infectious", "Nutrition", "Nutriance" "Illness", "Pollution", 
            "Food Insecurity", "Waterborne Disease", "Cholera", "Diarrhea", "Diarrheal", "Vector-Borne Infection", "Infection"
            "Temperature-related Illness", "virus", "water pollution", "Health"
        ],
        "Economic Impact": [
            "Economic Loss", "Cost", "Food Security", "Job Loss", "Poverty", "Infrastructure Damage", "Infrastructure", "Insurance", "GDP", 
            "Investment", "Market Disruption", "Economic Loss", "Economic downturn", "Crisis", "Agricultural Loss", "Supply Chain Disruption", "Financial loss"
            "Energy Cost", "Insurance Claim", "Property Damage", "Economic Strain", "Business Loss", "Trade Impact", "Export decline", "Inflation"
        ],
        "Displacement and Migration": [
            "Migration", "Displacement", "Refugee", "Sea Level", "Climate Refugee", "Natural Disaster", "Conflict", 
            "Relocation", "Livelihood Loss", "Environmental Migration", "Climate Migration", "Forced Migration", "Land Loss", 
            "Desertification", "Coastal Flooding", "Displaced Community", "Temporary Shelter", "Climate-induced Displacement", 
            "Depopulation"
        ]
    },
    "solutions": {
        "Technological Solutions": [
            "Solar", "Wind", "Electric Vehicle", "Electric", "Electrical", "Energy Efficiency", "Storage", "Hydrogen", "Green Tech", "Carbon Capture", 
            "Energy Storage", "Smart Grid", "Battery Technology", "Electric Mobility", "Geothermal", "Nuclear", "Innovation", 
            "Clean Tech", "clean technology", "Carbon Neutral", "Sustainability", "Sustainable", "clean energy",
            "Energy Efficiency", "Circular Economy", "Green Technology", "Green Energy", "Green Job", "Eco-friendly", "Eco", "Efficiency", "Smart Home"
        ],
        "Governance and Policy (Solutions)": [
            "Climate Action", "Net Zero", "Carbon Pricing", "Regulation", "International Agreement", "Carbon Tax", 
            "Climate Legislation", "Paris Agreement", "Sustainable Development Goal", "Carbon Neutrality", "Environmental Standard", 
            "Climate Policy", "Emissions Trading", "Policy Reform", "Green New Deal", "Green Taxation", "Climate March", "Climate Strike",
            "cop27", "Carbon Offset", "Policy", "Government", "Governance"
        ],
        "Adaptation and Resilience": [
            "Adaptation", "Resilience", "Infrastructure", "Urban Planning", "Water Management", "Disaster Management", 
            "Early Warning", "Flood Protection", "Climate Resilience", "Drought Management", "Coastal Defense", 
            "Risk Management", "Building Resilience", "Resilient Infrastructure", "Climate Proofing", "Heat-resistant infrastructure"
        ],
        "Lifestyle Solutions": [
            "vegan", "vegetarian", "Vega", "Plant-based", "Veganism", "Eco-conscious", "Plant-based diet", "Recycle", "Recycling", "Recycled", 
            "Energy Star Product", "Sustainable Living", "Eco-friendly", "Eco", "Upcycling", "Minimalism", "Ethical Consumption", "flexitarian", 
            "Local food", "Organic food", "Zero waste", "Zero food waste", "Bike sharing", "Public transport", "Electric Vehicles", "Energy Effiency",
            "Solar panel", "Green energy", "Plastic free", "Plastic-free", "Reusable", "Circular", "Second-hand", "Reuse", "Reusing", "Tiny home", 
            "Tiny house", "Off-grid", "Smart Home"
        ],
        "Nature-Based Solutions": [
            "Reforestation", "Conservation", "Wetland", "Forest", "Coastal Protection", "Sustainability", "Ecosystem", 
            "Agroforestry", "Biodiversity", "Soil Conservation", "Wetland Restoration", "Green Infrastructure",  "Urban Green Space", 
            "Habitat Restoration", "Mangrove", "Nature Conservation", "Crop Diversity", "Organic Farming", "Soil Fertility", "Food Security"
        ]
    }
}

SUBREDDITS = ["climate", "climatechange", "climateskeptics", "climateactionplan", "climateoffensive"]

label_colors = {
    "Energy and Industry": "#1f77b4",  # Blue
    "Land Use and Agriculture": "#ff7f0e",  # Orange
    "Governance and Policy (Causes)": "#2ca02c",  # Green
    "Personal Consumption": "#d62728",  # Red
    "Ecosystem Disruption": "#9467bd",  # Purple
    "Extreme Weather Events": "#8c564b",  # Brown
    "Health Risks": "#e377c2",  # Pink
    "Economic Impact": "#7f7f7f",  # Gray
    "Displacement and Migration": "#bcbd22",  # Lime
    "Technological Solutions": "#17becf",  # Cyan
    "Governance and Policy (Solutions)": "#aec7e8",  # Light Blue
    "Adaptation and Resilience": "#ffbb78",  # Light Orange
    "Lifestyle Solutions": "#98df8a",  # Light Green
    "Nature-Based Solutions": "#ff9896",  # Light Red
}