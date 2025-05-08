# ESG & Impact Pre-Investment Analyzer

An AI-powered tool for generating comprehensive ESG and Impact reports during the pre-investment phase.

## Features

- Automated ESG and Impact analysis based on multiple frameworks
- Support for IFC, 2X Challenge, and internal standards
- Detailed analysis of Environmental, Social, and Governance aspects
- Impact assessment and recommendations
- Exportable reports in Markdown format

## Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd esg-analyzer
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

4. Run the application:
```bash
streamlit run app.py
```

## Deployment to Streamlit Cloud

1. Push your code to a GitHub repository

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Sign in with your GitHub account

4. Click "New app"

5. Select your repository, branch, and main file (app.py)

6. Add your secrets in the "Secrets" section:
```toml
OPENAI_API_KEY = "your_openai_api_key"
ANTHROPIC_API_KEY = "your_anthropic_api_key"
```

7. Click "Deploy"

## Project Structure

```
esg-analyzer/
├── app.py                 # Main Streamlit application
├── config/
│   └── config.yaml       # Application configuration
├── standards/            # ESG frameworks
│   ├── 2x/
│   ├── ifc/
│   └── internal/
├── engine/
│   └── llm_service.py    # LLM service interface
├── prompts/
│   └── master_prompt.py  # Prompt management
└── requirements.txt      # Python dependencies
```

## Configuration

The application can be configured through `config/config.yaml`:

- LLM provider selection (OpenAI/Anthropic)
- Model parameters
- Application settings
- Standards configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 