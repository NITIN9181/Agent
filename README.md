# ProNexus Autonomous Executive Search Agent

An AI-powered executive search and vetting system built with CrewAI, designed for high-stakes interim placements including Interim C-Suite Executives, Healthcare Clinical Operations Leaders, and Elite Project Managers.

## Architecture Overview

This system uses a **hybrid CrewAI architecture**:
- **Flows**: Deterministic state management and orchestration
- **Crews**: Autonomous, probabilistic agent collaboration

## Key Features

- **Zero-Cost Prototype**: Uses synthetic data generation instead of expensive APIs
- **Forensic Vetting**: Multi-agent system that acts as a forensic auditor
- **Role-Specific Rubrics**: Specialized vetting logic for CFO, Healthcare Ops, and PM roles
- **Streamlit UI**: Optimized for Google Colab execution with tunneling

## Project Structure

```
pronexus_agent/
├── src/
│   ├── flow/
│   │   ├── search_flow.py      # Main Flow orchestration
│   │   └── state.py             # Pydantic state models
│   ├── crews/
│   │   ├── sourcing_crew.py    # Market Mapper agent
│   │   └── vetting_crew.py     # Forensic Auditor, Domain Evaluator, Matchmaker
│   ├── tools/
│   │   └── synthetic_data.py   # Synthetic candidate generator
│   └── main.py                 # Streamlit entry point
├── .streamlit/
│   └── secrets.toml            # API keys (create this)
└── pyproject.toml              # Dependencies
```

## Installation

### For Google Colab:

```python
!pip install crewai[tools] streamlit pyngrok faker pydantic nest-asyncio openai
!npm install -g localtunnel
```

### For Local Development:

```bash
pip install -r requirements.txt
```

## Configuration

1. Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-openai-key"
```

## Usage

### In Google Colab:

```python
!streamlit run src/main.py &
!npx localtunnel --port 8501
```

### Locally:

```bash
streamlit run src/main.py
```

## Vetting Rubrics

### Interim SaaS CFO
- ASC 606 & Revenue Recognition compliance
- Unit Economics & SaaS Metrics (CAC, LTV, NRR)
- Red flags: Cash-basis accounting, timeline gaps

### Healthcare Clinical Operations Lead
- Throughput & Patient Flow optimization
- Regulatory Stabilization (JCAHO, CMS)
- Workforce Management

### Elite Project Manager
- Methodology & Budget Variance
- Stakeholder Management
- Execution Discipline

## Development Status

This is a functional prototype demonstrating:
- Synthetic data generation
- Multi-agent orchestration
- Domain-specific vetting logic
- State persistence

## Next Steps (Production Roadmap)

- Integration with live APIs (ZoomInfo, LinkedIn Recruiter, Crustdata)
- Parallel vetting execution
- Enhanced reporting with visualizations
- Database persistence

