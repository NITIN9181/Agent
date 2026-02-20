"""
Pydantic State Models for ProNexus Flow
Defines the structured state that flows through the agent system
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class WorkExperience(BaseModel):
    """Represents a single work experience entry"""
    title: str = Field(description="Job title held")
    company: str = Field(description="Name of the employer")
    start_date: str = Field(description="ISO 8601 start date")
    end_date: str = Field(description="ISO 8601 end date or 'Present'")
    description: str = Field(description="Role summary")
    key_achievements: List[str] = Field(default_factory=list, description="Bulleted list of accomplishments")


class CandidateProfile(BaseModel):
    """Complete candidate profile structure"""
    id: str = Field(description="Unique UUID for the candidate")
    full_name: str
    linkedin_url: str = Field(default="", description="Mock LinkedIn URL")
    email: str = Field(default="")
    phone: str = Field(default="")
    summary: str = Field(description="Professional summary/bio")
    skills: List[str] = Field(default_factory=list, description="List of hard and soft skills")
    experience: List[WorkExperience] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    flagged_issues: Optional[List[str]] = Field(default=None, description="Hidden flags for testing vetting logic")
    resume_text: str = Field(default="", description="Full resume text")


class Candidate(BaseModel):
    """Candidate with attached vetting scores"""
    id: str
    name: str
    resume_text: str
    role: str
    
    # Vetting Scores
    auditor_score: Optional[int] = 0
    auditor_notes: Optional[str] = ""
    domain_score: Optional[int] = 0
    domain_notes: Optional[str] = ""
    matchmaker_score: Optional[int] = 0
    matchmaker_notes: Optional[str] = ""
    
    final_fit: Optional[str] = "Pending"
    red_flags: List[str] = Field(default_factory=list)
    
    # Profile data
    profile: Optional[CandidateProfile] = None


class SearchFlowState(BaseModel):
    """Main state object for the executive search flow"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the flow state")
    job_id: str = Field(default="", description="Unique identifier for the search mandate")
    job_description: str = Field(default="", description="Raw text of the job description")
    query: str = Field(default="", description="Search query")
    
    client_requirements: Dict[str, str] = Field(
        default_factory=dict,
        description="Structured requirements extracted from JD. Example: {'revenue': '$50M+', 'industry': 'SaaS', 'location': 'Remote'}"
    )
    
    candidate_pool: List[Candidate] = Field(
        default_factory=list,
        description="List of sourced candidates"
    )
    
    vetted_candidates: List[Candidate] = Field(
        default_factory=list,
        description="Candidates with attached vetting scores"
    )
    
    final_report: str = Field(
        default="",
        description="Markdown formatted final dossier"
    )
    
    status: str = Field(default="IDLE", description="Current flow status")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
