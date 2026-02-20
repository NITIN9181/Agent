# Quick Start Guide

## Local Development

### 1. Install Dependencies

```bash
cd pronexus_agent
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create `.streamlit/secrets.toml`:

```toml
# SambaNova API Key (Primary - get yours at: https://cloud.sambanova.ai/apis)
SAMBANOVA_API_KEY = "your-sambanova-api-key"

# Optional: Gemini API Key (for reference)
GEMINI_API_KEY = "your-gemini-api-key"

# Optional: OpenRouter API Key
OPENROUTER_API_KEY = "your-openrouter-api-key"
OPENAI_API_BASE = "https://openrouter.ai/api/v1"
```

Or set environment variable:

```bash
export SAMBANOVA_API_KEY="your-sambanova-api-key"
```

### 3. Run the Application

```bash
streamlit run src/main.py
```

The app will open at `http://localhost:8501`

## Google Colab

See `COLAB_SETUP.md` for detailed Colab instructions.

Quick version:

```python
# Install dependencies
!pip install crewai[tools] streamlit faker pydantic nest-asyncio openai

# Set API key
import os
os.environ["SAMBANOVA_API_KEY"] = "your-sambanova-api-key"

# Upload files or clone repo
# Then run:
!streamlit run src/main.py --server.port 8501 &
!npx localtunnel --port 8501
```

## Project Structure

```
pronexus_agent/
├── src/
│   ├── flow/
│   │   ├── search_flow.py    # Main orchestration
│   │   └── state.py          # State models
│   ├── crews/
│   │   ├── sourcing_crew.py  # Market Mapper
│   │   └── vetting_crew.py   # Forensic Auditor, Domain Evaluator, Matchmaker
│   ├── tools/
│   │   └── synthetic_data.py # Data generator
│   └── main.py               # Streamlit UI
├── .streamlit/
│   └── secrets.toml          # API keys
└── requirements.txt
```

## Usage

1. **Select Role**: Choose from Interim CFO, Healthcare Ops Lead, or Project Manager
2. **Enter Requirements**: Specify key requirements (e.g., "Must have ASC 606 experience")
3. **Start Search**: Click "Start Autonomous Search"
4. **Review Results**: View vetting scores, red flags, and recommendations

## Features

- ✅ Zero-cost synthetic data generation
- ✅ Multi-agent vetting system
- ✅ Role-specific rubrics (CFO, Healthcare, PM)
- ✅ Forensic audit capabilities
- ✅ Red flag detection
- ✅ Executive-level reporting

## Troubleshooting

### Import Errors
- Make sure you're in the `pronexus_agent` directory
- Check that all dependencies are installed: `pip install -r requirements.txt`

### API Key Issues
- Verify SAMBANOVA_API_KEY is set correctly
- Check `.streamlit/secrets.toml` or environment variables
- Get your API key from https://cloud.sambanova.ai/apis

### CrewAI Errors
- Ensure you have the latest version: `pip install --upgrade crewai[tools]`
- Check CrewAI documentation for any breaking changes

## Next Steps

- Review the architecture in `README.md`
- Customize vetting rubrics in `src/crews/vetting_crew.py`
- Add live API integrations (see architecture PDF)
- Enhance synthetic data generation in `src/tools/synthetic_data.py`
