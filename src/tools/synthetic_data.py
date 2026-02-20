"""
Synthetic Data Factory Tool
Generates high-fidelity executive resumes for testing without incurring API costs
"""
try:
    from crewai_tools import BaseTool
except ImportError:
    # Fallback for older crewai versions
    from crewai.tools import BaseTool

from faker import Faker
import random
import uuid
from typing import List
from flow.state import CandidateProfile, WorkExperience
from pydantic import PrivateAttr


class SyntheticCandidateTool(BaseTool):
    """Generates realistic executive resumes for testing"""
    
    name: str = "Synthetic Candidate Generator"
    description: str = (
        "Generates realistic executive resumes for testing. "
        "Input parameters: role_type (str), requirements (optional str), num_candidates (optional int, default 5). "
        "Output: JSON array of candidate profiles."
    )
    _fake: Faker = PrivateAttr()
    
    def __init__(self):
        super().__init__()
        self._fake = Faker()
        Faker.seed(42)  # For reproducibility
    
    def _run(self, role_type: str, requirements: str = "", num_candidates: int = 10) -> str:
        """
        Generate synthetic candidate profiles
        
        Args:
            role_type: Target role title like CFO or Project Manager
            requirements: Simple text description of requirements
            num_candidates: Number of candidates to generate (default 10)
            
        Returns:
            JSON string of candidate profiles
        """
        print("="*80)
        print("DEBUG: SyntheticCandidateTool._run() CALLED")
        print("="*80)
        print(f"DEBUG: role_type = {role_type}")
        print(f"DEBUG: requirements = {requirements}")
        print(f"DEBUG: num_candidates = {num_candidates}")
        
        profiles = []
        
        # Determine persona distribution: 30% perfect, 40% near-miss, 30% red-flag
        for i in range(num_candidates):
            persona_type = random.choices(
                ["perfect", "near_miss", "red_flag"],
                weights=[30, 40, 30]
            )[0]
            
            profile = self._generate_profile(role_type, requirements, persona_type, i)
            profiles.append(profile)
        
        # Return as JSON-like string (simplified for prototype)
        import json
        result = json.dumps([p.model_dump() for p in profiles], indent=2)
        
        print("="*80)
        print("DEBUG: SyntheticCandidateTool._run() RETURNING")
        print("="*80)
        print(f"DEBUG: Generated {len(profiles)} profiles")
        print(f"DEBUG: Result length: {len(result)} characters")
        print(f"DEBUG: First 300 chars of result:\n{result[:300]}")
        print("="*80)
        
        return result
    
    def _generate_profile(
        self, 
        role_type: str, 
        requirements: str,
        persona_type: str,
        index: int
    ) -> CandidateProfile:
        """Generate a single candidate profile based on persona type"""
        
        fake = self._fake
        
        # Base identity
        full_name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        linkedin_url = f"https://linkedin.com/in/{fake.user_name()}"
        
        # Generate work experience
        experience = []
        flagged_issues = []
        
        if persona_type == "perfect":
            # The "Golden" candidate
            experience = self._generate_golden_experience(role_type, fake)
            summary = self._generate_golden_summary(role_type, fake)
            skills = self._get_role_skills(role_type, "perfect")
            
        elif persona_type == "near_miss":
            # The "Job Hopper" or skill mismatch
            experience = self._generate_job_hopper_experience(role_type, fake)
            summary = self._generate_near_miss_summary(role_type, fake)
            skills = self._get_role_skills(role_type, "near_miss")
            flagged_issues.append("Multiple short tenures")
            
        else:  # red_flag
            # The "Fraud Risk" candidate
            experience = self._generate_red_flag_experience(role_type, fake)
            summary = self._generate_red_flag_summary(role_type, fake)
            skills = self._get_role_skills(role_type, "red_flag")
            flagged_issues.append("Timeline inconsistencies")
            flagged_issues.append("Compliance concerns")
        
        # Generate education
        education = [
            f"MBA from {fake.company()} University",
            f"BS in Business Administration from {fake.city()} State"
        ]
        
        # Build resume text
        resume_text = self._build_resume_text(
            full_name, email, phone, summary, experience, skills, education
        )
        
        return CandidateProfile(
            id=str(uuid.uuid4()),
            full_name=full_name,
            linkedin_url=linkedin_url,
            email=email,
            phone=phone,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            flagged_issues=flagged_issues if flagged_issues else None,
            resume_text=resume_text
        )
    
    def _generate_golden_experience(self, role_type: str, fake: Faker) -> List[WorkExperience]:
        """Generate perfect candidate experience"""
        experiences = []
        
        if "CFO" in role_type:
            # Perfect CFO: Big 4 background, ASC 606 experience, IPO readiness
            experiences.append(WorkExperience(
                title="Interim CFO",
                company=fake.company(),
                start_date="2022-01-01",
                end_date="Present",
                description=f"Led finance transformation for $50M+ ARR SaaS company. Implemented ASC 606 revenue recognition automation using Maxio.",
                key_achievements=[
                    "Implemented ASC 606 compliance across all revenue streams",
                    "Led IPO readiness preparation",
                    "Reduced monthly close time from 15 to 5 days",
                    "Managed Big 4 audit relationships"
                ]
            ))
            experiences.append(WorkExperience(
                title="VP Finance",
                company=fake.company(),
                start_date="2018-06-01",
                end_date="2021-12-31",
                description="Built finance function from ground up for Series B SaaS startup.",
                key_achievements=[
                    "Established GAAP-compliant financial reporting",
                    "Implemented Zuora billing system",
                    "Achieved 95% NRR"
                ]
            ))
            experiences.append(WorkExperience(
                title="Senior Manager",
                company="Big 4 Accounting Firm",
                start_date="2013-01-01",
                end_date="2018-05-31",
                description="Audited SaaS and technology companies.",
                key_achievements=[
                    "Led ASC 606 implementation projects",
                    "Managed audit teams of 5-10 professionals"
                ]
            ))
        
        elif "Healthcare" in role_type or "Ops" in role_type:
            # Perfect Healthcare Ops: EMR experience, throughput optimization, regulatory
            experiences.append(WorkExperience(
                title="Interim Clinical Operations Lead",
                company=fake.company() + " Hospital",
                start_date="2021-03-01",
                end_date="Present",
                description="Led clinical operations transformation for 300-bed hospital.",
                key_achievements=[
                    "Reduced ED wait times by 25%",
                    "Implemented Epic EMR optimization",
                    "Achieved JCAHO survey readiness",
                    "Reduced contract labor costs by 30%"
                ]
            ))
            experiences.append(WorkExperience(
                title="Director of Clinical Operations",
                company=fake.company() + " Health System",
                start_date="2017-01-01",
                end_date="2021-02-28",
                description="Managed clinical throughput and patient flow.",
                key_achievements=[
                    "Reduced LOS by 15%",
                    "Improved CMS star rating from 3 to 4",
                    "Optimized staffing grid"
                ]
            ))
        
        else:  # Project Manager
            # Perfect PM: Methodology, budget control, stakeholder management
            experiences.append(WorkExperience(
                title="Senior Project Manager",
                company=fake.company(),
                start_date="2020-01-01",
                end_date="Present",
                description="Led enterprise digital transformation projects.",
                key_achievements=[
                    "Delivered $5M project on-time and on-budget",
                    "Managed C-level steering committee",
                    "PMP certified, SAFe 5.0 certified",
                    "Reduced project risk by 40%"
                ]
            ))
        
        return experiences
    
    def _generate_job_hopper_experience(self, role_type: str, fake: Faker) -> List[WorkExperience]:
        """Generate job hopper experience (4 roles in 5 years)"""
        experiences = []
        base_year = 2020
        
        for i in range(4):
            start_month = random.randint(1, 6)
            end_month = random.randint(7, 12)
            start_date = f"{base_year + i}-{start_month:02d}-01"
            end_date = f"{base_year + i}-{end_month:02d}-28"
            
            experiences.append(WorkExperience(
                title=f"{role_type} (Contract)",
                company=fake.company(),
                start_date=start_date,
                end_date=end_date,
                description=f"Contract role at {fake.company()}.",
                key_achievements=["Completed assigned projects"]
            ))
        
        return experiences
    
    def _generate_red_flag_experience(self, role_type: str, fake: Faker) -> List[WorkExperience]:
        """Generate experience with red flags (overlapping dates, compliance issues)"""
        experiences = []
        
        if "CFO" in role_type:
            # Red flag CFO: Cash-basis accounting, overlapping employment
            experiences.append(WorkExperience(
                title="CFO",
                company=fake.company(),
                start_date="2020-01-01",
                end_date="2022-06-30",
                description="Managed finance using cash-basis accounting for $10M ARR SaaS company.",
                key_achievements=["Maintained cash flow", "Managed vendor relationships"]
            ))
            experiences.append(WorkExperience(
                title="VP Finance",
                company=fake.company(),
                start_date="2021-12-01",  # Overlapping!
                end_date="2023-12-31",
                description="Finance leadership role.",
                key_achievements=["Led finance team"]
            ))
        else:
            # Generic red flags
            experiences.append(WorkExperience(
                title=role_type,
                company=fake.company(),
                start_date="2020-01-01",
                end_date="2020-06-30",  # Very short tenure
                description="Brief role.",
                key_achievements=[]
            ))
        
        return experiences
    
    def _generate_golden_summary(self, role_type: str, fake: Faker) -> str:
        """Generate perfect candidate summary"""
        if "CFO" in role_type:
            return (
                f"Results-driven Interim CFO with 15+ years of experience in SaaS finance. "
                f"Expert in ASC 606 revenue recognition, IPO readiness, and Big 4 audit management. "
                f"Proven track record of scaling finance functions for high-growth companies."
            )
        elif "Healthcare" in role_type:
            return (
                f"Healthcare operations executive with 12+ years optimizing clinical throughput. "
                f"Expert in Epic/Cerner EMR systems, JCAHO compliance, and value-based care models. "
                f"Track record of reducing LOS and improving CMS ratings."
            )
        else:
            return (
                f"PMP-certified project manager with 10+ years delivering complex enterprise projects. "
                f"Expert in Agile, Waterfall, and SAFe methodologies. "
                f"Consistent track record of on-time, on-budget delivery."
            )
    
    def _generate_near_miss_summary(self, role_type: str, fake: Faker) -> str:
        """Generate near-miss candidate summary"""
        return (
            f"Experienced {role_type} with diverse background across multiple industries. "
            f"Strong track record of delivering results in fast-paced environments."
        )
    
    def _generate_red_flag_summary(self, role_type: str, fake: Faker) -> str:
        """Generate red flag candidate summary"""
        return (
            f"{role_type} with experience in various roles. "
            f"Adaptable professional seeking new opportunities."
        )
    
    def _get_role_skills(self, role_type: str, persona: str) -> List[str]:
        """Get skills based on role and persona"""
        if "CFO" in role_type:
            base_skills = ["Financial Analysis", "GAAP", "Financial Reporting"]
            if persona == "perfect":
                return base_skills + ["ASC 606", "Revenue Recognition", "IPO Readiness", "Maxio", "Zuora", "Big 4 Audit"]
            elif persona == "red_flag":
                return base_skills + ["Cash Basis Accounting", "QuickBooks"]
            else:
                return base_skills + ["Budget Management"]
        
        elif "Healthcare" in role_type:
            base_skills = ["Clinical Operations", "Patient Care"]
            if persona == "perfect":
                return base_skills + ["Epic EMR", "Cerner", "JCAHO", "CMS Compliance", "Throughput Optimization"]
            else:
                return base_skills
        
        else:  # PM
            base_skills = ["Project Management", "Stakeholder Management"]
            if persona == "perfect":
                return base_skills + ["PMP", "SAFe", "Agile", "Budget Control", "Risk Management"]
            else:
                return base_skills
    
    def _build_resume_text(
        self,
        name: str,
        email: str,
        phone: str,
        summary: str,
        experience: List[WorkExperience],
        skills: List[str],
        education: List[str]
    ) -> str:
        """Build full resume text from components"""
        lines = [
            f"CANDIDATE: {name}",
            f"Email: {email}",
            f"Phone: {phone}",
            "",
            "PROFESSIONAL SUMMARY",
            summary,
            "",
            "EXPERIENCE"
        ]
        
        for exp in experience:
            lines.append(f"\n{exp.title} at {exp.company}")
            lines.append(f"{exp.start_date} - {exp.end_date}")
            lines.append(exp.description)
            if exp.key_achievements:
                lines.append("Key Achievements:")
                for achievement in exp.key_achievements:
                    lines.append(f"  • {achievement}")
        
        lines.extend([
            "",
            "SKILLS",
            ", ".join(skills),
            "",
            "EDUCATION"
        ])
        
        for edu in education:
            lines.append(f"  • {edu}")
        
        return "\n".join(lines)
