"""
Vetting Crew - Multi-Agent Tribunal
Forensic Auditor, Domain Evaluator, and Matchmaker agents collaborate to vet candidates
"""
from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from typing import List, Optional
import json


class VettingScore(BaseModel):
    """Structured vetting score output"""
    auditor_score: int = Field(description="Score from 0-100 for risk assessment")
    auditor_notes: str = Field(description="Detailed notes on red flags and concerns")
    domain_score: int = Field(description="Score from 0-100 for domain expertise")
    domain_notes: str = Field(description="Detailed notes on technical competencies")
    matchmaker_score: int = Field(description="Final fit score from 0-100")
    matchmaker_notes: str = Field(description="Overall assessment and recommendation")
    red_flags: List[str] = Field(default_factory=list, description="List of identified red flags")
    final_recommendation: str = Field(description="Strong Hire / Hire / Risk Flag / Do Not Hire")


class VettingCrew:
    """Crew responsible for vetting candidates"""
    
    def __init__(self, role_type: str = "Interim CFO"):
        self.role_type = role_type
        self.vetting_rubric = self._get_rubric_for_role(role_type)
    
    def crew(self) -> Crew:
        """Create and return the vetting crew"""
        
        # Agent 2: The Forensic Auditor (The "Bad Cop")
        forensic_auditor = Agent(
            role="Executive Background Investigator",
            goal="Identify risks, inconsistencies, and red flags in the candidate's history, but maintain a fair perspective",
            backstory=(
                "You are a rigorous but fair auditor with a background in forensic accounting and HR compliance. "
                "You look for job hopping, unexplained gaps, timeline inconsistencies, and resume inflation. "
                "You are objective and do not assume malice without evidence. "
                "You are trained to spot SaaS financial irregularities and operational failures. "
                "You note vague action verbs like 'participated in' or 'helped with' as potential weaknesses but consider the overall context/seniority. "
                "You reward ownership verbs like 'Led,' 'Built,' 'Architected,' 'Restructured.'"
            ),
            llm="gpt-4o-mini",
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 3: The Domain Evaluator (The "Good Cop")
        domain_evaluator = Agent(
            role=f"{self.role_type} Subject Matter Expert",
            goal=f"Score the candidate's achievements against specific technical competencies for {self.role_type}",
            backstory=(
                f"You are a former {self.role_type} turned executive recruiter. "
                "You understand the nuance of the job because you have done it. "
                "You value specific, quantified achievements, but also recognize potential and relevant experience even if not perfectly quantified. "
                "You look for evidence of strategic impact and operational excellence."
            ),
            llm="gpt-4o-mini",
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 4: The Matchmaker (The "Closer")
        matchmaker = Agent(
            role="Senior Partner & Account Manager",
            goal="Synthesize the findings of the Auditor and Evaluator into a final 'Fit Score' and write the client presentation",
            backstory=(
                "You represent ProNexus to the client. Your reports are concise, executive-level, and brutally honest. "
                "You never recommend a candidate you wouldn't hire yourself. "
                "You focus on cultural fit and the 'story' behind the candidate."
            ),
            llm="gpt-4o-mini",
            verbose=True,
            allow_delegation=True
        )
        
        # Task 1: Forensic Audit
        audit_task = Task(
            description=(
                f"Analyze the candidate's resume for red flags. "
                f"Step 1: Extract all dates of employment. "
                f"Step 2: Calculate the duration of each role. "
                f"Step 3: Identify any gaps larger than 3 months. "
                f"Step 4: If a C-suite role lasted less than 18 months, classify it as 'Short Tenure' unless 'Interim' is explicitly stated. "
                f"Step 5: Check for overlapping employment dates. "
                f"Step 6: Look for compliance issues (e.g., cash-basis accounting for SaaS companies). "
                f"Based on these steps, provide a Stability Score (0-100) and detailed notes.\n"
                f"IMPORTANT: Calibrate scoring such that typical professional candidates fall in the 75-95 range. "
                f"Reserve scores below 70 for major red flags only (e.g. clearly fraudulent dates, gaps > 1 year without explanation)."
            ),
            agent=forensic_auditor,
            expected_output=(
                "JSON with: auditor_score (0-100), auditor_notes (detailed text), "
                "red_flags (list of specific issues found)"
            )
        )
        
        # Task 2: Domain Evaluation
        domain_task = Task(
            description=(
                f"Evaluate the candidate against {self.role_type} specific competencies:\n"
                f"{self.vetting_rubric}\n\n"
                f"Look for specific, quantified achievements. "
                f"Note vague descriptions but do not overly penalize if the role context implies competence. "
                f"Provide a Domain Expertise Score (0-100) and detailed notes.\n"
                f"IMPORTANT: Calibrate scoring such that typical professional candidates fall in the 75-95 range. "
                f"A candidate with relevant experience but lacking some specific quantifiers should still score in the 70s or 80s."
            ),
            agent=domain_evaluator,
            expected_output=(
                "JSON with: domain_score (0-100), domain_notes (detailed text about competencies)"
            )
        )
        
        # Task 3: Final Matchmaking
        matchmaker_task = Task(
            description=(
                "Synthesize the auditor and domain evaluator findings. "
                "You MUST retrieve and include the specific scores and notes from the previous tasks. "
                "Do NOT generate new generic notes; use the actual findings from the Auditor and Domain Evaluator. "
                "Construct a final JSON object that includes: "
                "1. auditor_score (from Auditor task) "
                "2. auditor_notes (summary of Auditor's findings) "
                "3. domain_score (from Domain Evaluator task) "
                "4. domain_notes (summary of Domain Evaluator's findings) "
                "5. matchmaker_score (your calculated fit score) "
                "6. matchmaker_notes (your executive summary) "
                "7. red_flags (consolidated list from all agents) "
                "8. final_recommendation (Strong Hire/Hire/Risk Flag/Do Not Hire)\n\n"
                "EXAMPLE OUTPUT FORMAT:\n"
                "```json\n"
                "{\n"
                '    "auditor_score": 85,\n'
                '    "auditor_notes": "No major gaps, but frequent job changes in early career.",\n'
                '    "domain_score": 92,\n'
                '    "domain_notes": "Strong ASC 606 experience. Proven track record in SaaS.",\n'
                '    "matchmaker_score": 88,\n'
                '    "matchmaker_notes": "Excellent candidate with strong technical skills and decent stability.",\n'
                '    "red_flags": ["Job hopping in 2015"],\n'
                '    "final_recommendation": "Hire"\n'
                "}\n"
                "```"
            ),
            agent=matchmaker,
            expected_output=(
                "JSON with keys: auditor_score, auditor_notes, domain_score, domain_notes, "
                "matchmaker_score, matchmaker_notes, red_flags, final_recommendation"
            ),
            context=[audit_task, domain_task]
        )
        
        return Crew(
            agents=[forensic_auditor, domain_evaluator, matchmaker],
            tasks=[audit_task, domain_task, matchmaker_task],
            verbose=True,
            process="sequential"
        )
    
    def _get_rubric_for_role(self, role_type: str) -> str:
        """Get role-specific vetting rubric"""
        
        if "CFO" in role_type:
            return """
            Critical Competency: ASC 606 & Revenue Recognition
            - Analyze the 'Experience' section for evidence of 'Revenue Recognition', 'ASC 606', 'Deferred Revenue', or 'RPO'
            - If the candidate lists 'Cash Basis' accounting for a SaaS company >$5M ARR, mark as a concern (not necessarily a critical failure if role was early stage)
            - Look for experience in 'automating revenue recognition' or 'implementing billing systems' like Zuora or Maxio
            
            Critical Competency: Unit Economics & SaaS Metrics
            - Search for quantified metrics: CAC (Customer Acquisition Cost), LTV (Lifetime Value), NRR (Net Revenue Retention), Magic Number
            - A candidate listing only 'revenue growth' without efficiency metrics is a red flag for a modern SaaS CFO role
            
            Red Flag Logic:
            - Mixed cash/accrual accounting mentions
            - Lack of bank reconciliation oversight in previous roles
            - Inability to generate connected financial statements
            """
        
        elif "Healthcare" in role_type or "Ops" in role_type:
            return """
            Critical Competency: Throughput & Patient Flow
            - Evaluate experience in 'Length of Stay (LOS)' reduction, 'ED Boarding' times, and 'Discharge Planning'
            - Look for specific percentage improvements (e.g., 'Reduced ED wait times by 20%')
            
            Critical Competency: Regulatory Stabilization
            - Check for experience with 'Joint Commission' (TJC) surveys, 'CMS' audits, or 'star rating' improvements
            - Look for terms like 'Corrective Action Plan' or 'Survey Readiness'
            
            Critical Competency: Workforce Management
            - Assess experience in reducing 'contract labor' usage or 'overtime' costs
            - Look for 'Staffing Grid' optimization
            """
        
        else:  # Project Manager
            return """
            Critical Competency: Methodology & Budget
            - Identify the specific methodology used (Agile, Waterfall, SAFe)
            - Crucially, identify 'Budget Variance' management. Did they deliver on budget?
            - Look for 'Scope Creep' management examples and 'Change Order' processes
            
            Critical Competency: Stakeholder Management
            - Analyze how they manage C-level stakeholders
            - Look for terms like 'Steering Committee', 'Change Management', 'Communication Plan', 'Risk Register'
            
            Red Flag Logic:
            - Vague descriptions of projects without timelines or budgets
            - Lack of certification (PMP, CSM) for senior roles (though experience can override this)
            """
        
        return "Evaluate candidate against general executive competencies."
