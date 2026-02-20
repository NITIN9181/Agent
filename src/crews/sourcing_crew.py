"""
Sourcing Crew - Market Mapper Agent
Responsible for finding candidates who match hard requirements
"""
from crewai import Agent, Task, Crew
try:
    from crewai_tools import SerperDevTool
except ImportError:
    SerperDevTool = None

from tools.synthetic_data import SyntheticCandidateTool
import json
import os


class SourcingCrew:
    """Crew responsible for sourcing candidates"""
    
    def __init__(self):
        self.synthetic_tool = SyntheticCandidateTool()
        # Optional: Add SerperDevTool for live search (requires API key)
        # self.search_tool = SerperDevTool() if os.getenv("SERPER_API_KEY") else None
    
    def crew(self) -> Crew:
        """Create and return the sourcing crew"""
        
        # Agent 1: The Market Mapper (Sourcer)
        market_mapper = Agent(
            role="Senior Executive Researcher",
            goal="Generate a pool of 10-20 candidates who fundamentally match the hard requirements (Title, Location, Industry)",
            backstory=(
                "You are an expert researcher at ProNexus. Your ONLY task is to identify candidates. "
                "You MUST use the 'Synthetic Candidate Generator' tool immediately with the provided query and requirements. "
                "Do NOT ask for more information. Do NOT have a conversation. Just use the tool and return the result."
            ),
            tools=[self.synthetic_tool],
            llm="gpt-4o-mini",
            verbose=True,
            allow_delegation=False
        )
        
        # Task: Source candidates
        sourcing_task = Task(
            description=(
                "1. Take the search query: {query} and requirements: {requirements}.\n"
                "2. IMMEDIATELY call the 'Synthetic Candidate Generator' tool to generate profiles.\n"
                "3. Ensure the tool is called with role_type focusing on the core title (e.g., 'CFO', 'PM').\n"
                "4. Return ONLY the JSON output provided by the tool. NO preamble, NO explanations."
            ),
            agent=market_mapper,
            expected_output=(
                "A JSON array of candidate profiles. DO NOT include any text outside the JSON block."
            )
        )
        
        return Crew(
            agents=[market_mapper],
            tasks=[sourcing_task],
            verbose=True,
            process="sequential"
        )
