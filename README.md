# ESG & Impact Pre-Investment Analyzer

## Description
Pre-investment ESG and impact analysis application based on IFC and 2X standards.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Kevinaie18/esg-analyzer.git
cd esg-analyzer
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Get IFC EHS Guidelines:
   - Create an `ifc-ehs` directory in the project root
   - Download the EHS Guidelines PDF files from https://www.ifc.org/en/ehs-guidelines
   - Place the files in the `ifc-ehs` directory

## Usage

Launch the application:
```bash
streamlit run app.py
```

## Features

- Automatic E&S risk classification according to IFC standards
- Sector-specific recommendations based on IFC EHS Guidelines
- Detailed ESG analysis with IFC and 2X standards
- Custom report generation

## Project Structure

```
esg-analyzer/
├── app.py                 # Main Streamlit application
├── config/               # Configuration and mappings
├── engine/              # Analysis engine and LLM services
├── prompts/             # Prompt templates
├── standards/           # ESG standards (IFC, 2X)
├── utils/               # Utilities
├── ifc-ehs/            # IFC EHS Guidelines (to be added manually)
└── requirements.txt     # Python dependencies
```

## Contributing

Contributions are welcome! Feel free to open an issue or a pull request.

## License

MIT 