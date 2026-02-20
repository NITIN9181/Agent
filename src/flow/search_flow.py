"""
ProNexus Executive Search Flow
Orchestrates the sourcing, vetting, and reporting process using CrewAI Flows
"""
from crewai.flow.flow import Flow, start, listen
from flow.state import SearchFlowState, Candidate, CandidateProfile
from crews.sourcing_crew import SourcingCrew
from crews.vetting_crew import VettingCrew
import json
import re


class ProNexusFlow(Flow[SearchFlowState]):
    """Main flow for executive search orchestration"""
    initial_state = SearchFlowState
    
    @start()
    def analyze_requirements(self):
        """Parse job description and extract structured requirements"""
        print(f"Analyzing requirements for: {self.state.query}")
        self.state.status = "Analyzing"
        
        # Simple extraction for prototype (in production, use LLM)
        # Extract role type from query
        role_type = "Interim CFO"  # Default
        if "CFO" in self.state.query.upper():
            role_type = "Interim CFO"
        elif "Healthcare" in self.state.query or "Ops" in self.state.query:
            role_type = "Healthcare Clinical Operations Lead"
        elif "Project Manager" in self.state.query or "PM" in self.state.query:
            role_type = "Elite Project Manager"
        
        # Extract key requirements
        requirements = {}
        if "$" in self.state.query:
            # Extract revenue requirement
            revenue_match = re.search(r'\$(\d+M?)', self.state.query)
            if revenue_match:
                requirements["revenue"] = f"${revenue_match.group(1)}"
        
        if "ASC 606" in self.state.query:
            requirements["asc_606"] = "required"
        
        if "Remote" in self.state.query:
            requirements["location"] = "Remote"
        
        self.state.client_requirements = requirements
        self.state.job_description = self.state.query
        self.state.status = "Requirements Analyzed"
        
        return self.state
    
    @listen(analyze_requirements)
    def sourcing_step(self):
        """Generate candidate pool using Sourcing Crew"""
        print("="*80)
        print("DEBUG: Starting Sourcing Crew...")
        print("="*80)
        self.state.status = "Sourcing"
        
        # Initialize Sourcing Crew
        sourcing_crew = SourcingCrew().crew()
        print(f"DEBUG: Sourcing crew initialized with {len(sourcing_crew.agents)} agent(s)")
        print(f"DEBUG: Agent tools: {[tool.name for tool in sourcing_crew.agents[0].tools] if sourcing_crew.agents[0].tools else 'No tools'}")
        
        # Kickoff sourcing
        print(f"DEBUG: Kickoff inputs:")
        print(f"  - query: {self.state.query}")
        print(f"  - requirements: {json.dumps(self.state.client_requirements)}")
        print("DEBUG: Calling crew.kickoff()...")
        
        result = sourcing_crew.kickoff(inputs={
            "query": self.state.query,
            "requirements": json.dumps(self.state.client_requirements)
        })
        
        # Improved parsing logic - handle CrewOutput object
        import sys
        from datetime import datetime
        
        def log_debug(msg):
            """Helper to log to both console and file"""
            print(msg)
            sys.stdout.flush()
            try:
                with open("d:/PRONEXUS/pronexus_agent/sourcing_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now()}: {msg}\n")
            except Exception as e:
                print(f"Logging failed: {e}")
        
        log_debug("="*80)
        log_debug("DEBUG: Sourcing Result Received")
        log_debug("="*80)
        log_debug(f"DEBUG: Result type: {type(result)}")
        log_debug(f"DEBUG: Result class name: {result.__class__.__name__}")
        log_debug(f"DEBUG: Available attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
        
        # Try to get the raw output from CrewOutput object
        result_str = None
        if hasattr(result, 'raw'):
            result_str = str(result.raw)
            log_debug(f"DEBUG: Using result.raw (length: {len(result_str)} chars)")
        elif hasattr(result, 'json_dict'):
            log_debug(f"DEBUG: result.json_dict available: {result.json_dict}")
            if result.json_dict:
                result_str = json.dumps(result.json_dict)
        elif hasattr(result, 'pydantic'):
            log_debug(f"DEBUG: result.pydantic available")
            result_str = str(result.pydantic)
        else:
            result_str = str(result)
            log_debug(f"DEBUG: Using str(result) fallback")
        
        log_debug(f"DEBUG: Result string length: {len(result_str)} characters")
        if len(result_str) > 1000:
             log_debug(f"DEBUG: First 500 chars of result:\n{result_str[:500]}")
             log_debug(f"DEBUG: Last 500 chars of result:\n{result_str[-500:]}")
        else:
             log_debug(f"DEBUG: Full result:\n{result_str}")
        log_debug("="*80)
        
        candidates_data = None
        
       # 1. Try to extract from markdown code blocks if present
        log_debug("DEBUG: Attempting Method 1: Markdown code block extraction")
        # Check for fences
        log_debug(f"DEBUG: result_str contains '```': {result_str.count('```')} times")
        log_debug(f"DEBUG: result_str contains 'json': {result_str.lower().count('json')} times")
        # Updated regex to handle extra spaces: ```json  (with spaces after json)
        json_match = re.search(r'```\s*json\s*(.*?)\s*```', result_str, re.DOTALL | re.IGNORECASE)
        if json_match:
            log_debug(f"DEBUG: Found JSON markdown block")
            log_debug(f"DEBUG: Matched content (first 200 chars): {json_match.group(1)[:200]}")
            try:
                parsed = json.loads(json_match.group(1))
                log_debug(f"DEBUG: Successfully parsed JSON from markdown. Type: {type(parsed)}")
                # Handle if it's wrapped in an object
                if isinstance(parsed, dict):
                    log_debug(f"DEBUG: Parsed as dict. Keys: {list(parsed.keys())}")
                    # Try to find a list value in the dict
                    for key, value in parsed.items():
                        if isinstance(value, list):
                            candidates_data = value
                            log_debug(f"DEBUG: Found list in dict key '{key}' with {len(value)} items")
                            break
                elif isinstance(parsed, list):
                    candidates_data = parsed
                    log_debug(f"DEBUG: Parsed as list with {len(parsed)} items")
                
                if candidates_data:
                    log_debug(f"Successfully parsed JSON from markdown block - {len(candidates_data)} candidates")
            except json.JSONDecodeError as e:
                log_debug(f"Failed to parse JSON from markdown: {e}")
                log_debug(f"DEBUG: Error at position {e.pos}")
        else:
            log_debug("DEBUG: No markdown code block found")
       
        # 2. Try to parse the raw result if it's already JSON
        if not candidates_data:
            log_debug("DEBUG: Attempting Method 2: Raw JSON parsing")
            try:
                parsed = json.loads(result_str)
                log_debug(f"DEBUG: Successfully parsed raw JSON. Type: {type(parsed)}")
                # Handle if it's wrapped in an object
                if isinstance(parsed, dict):
                    log_debug(f"DEBUG: Parsed as dict. Keys: {list(parsed.keys())}")
                    # Try to find a list value in the dict
                    for key, value in parsed.items():
                        if isinstance(value, list):
                            candidates_data = value
                            log_debug(f"DEBUG: Found list in dict key '{key}' with {len(value)} items")
                            break
                elif isinstance(parsed, list):
                    candidates_data = parsed
                    log_debug(f"DEBUG: Parsed as list with {len(parsed)} items")
                    
                if candidates_data:
                    log_debug(f"Successfully parsed raw JSON result - {len(candidates_data)} candidates")
            except json.JSONDecodeError as e:
                log_debug(f"Failed to parse raw JSON: {e}")
                log_debug(f"DEBUG: Error at position {e.pos}")
        
        # 3. Fallback: Try to find anything that looks like a JSON array
        if not candidates_data:
            log_debug("DEBUG: Attempting Method 3: Regex fallback for JSON array")
            array_match = re.search(r'\[\s*\{.*\}\s*\]', result_str, re.DOTALL)
            if array_match:
                log_debug(f"DEBUG: Found potential JSON array using regex")
                log_debug(f"DEBUG: Matched content (first 200 chars): {array_match.group(0)[:200]}")
                try:
                    candidates_data = json.loads(array_match.group(0))
                    log_debug(f"Successfully parsed JSON array using regex fallback - {len(candidates_data)} candidates")
                except json.JSONDecodeError as e:
                    log_debug(f"Failed regex fallback JSON parse: {e}")
                    log_debug(f"DEBUG: Error at position {e.pos}")
                    
                    # Manual Repair for Truncated JSON
                    log_debug("DEBUG: Attempting to repair truncated JSON...")
                    json_str = array_match.group(0)
                    
                    # Iterative Repair Strategy:
                    # Find all "}," occurrences. Try cutting at each one (from last to first)
                    # until we form valid JSON. This handles cases where the last "},"
                    # might be inside a nested object (like experience list) which would
                    # still result in invalid JSON if closed with just "]".
                    
                    possible_ends = []
                    start_pos = 0
                    while True:
                        idx = json_str.find('},', start_pos)
                        if idx == -1:
                            break
                        possible_ends.append(idx)
                        start_pos = idx + 1
                    
                    found_repair = False
                    if possible_ends:
                        log_debug(f"DEBUG: Found {len(possible_ends)} potential repair points")
                        for end_idx in reversed(possible_ends):
                            # Slice up to '}' (exclude comma) and add ']'
                            repaired_json = json_str[:end_idx+1] + ']'
                            try:
                                candidates_data = json.loads(repaired_json)
                                log_debug(f"✅ Successfully repaired and parsed JSON - {len(candidates_data)} candidates salvaged")
                                found_repair = True
                                break
                            except json.JSONDecodeError:
                                # This cut point didn't work (likely nested object), try next
                                continue
                    
                    if not found_repair:
                         log_debug("DEBUG: All repair attempts failed")
            else:
                log_debug("DEBUG: No JSON array pattern found via regex")
        
        
        # Process candidates if we have data
        if candidates_data and isinstance(candidates_data, list):
            log_debug(f"Processing {len(candidates_data)} candidate(s)...")
            for i, cand_data in enumerate(candidates_data):
                try:
                    if isinstance(cand_data, dict):
                        # Normalize field names to match CandidateProfile schema
                        # Some models return 'name' instead of 'full_name'
                        if 'name' in cand_data and 'full_name' not in cand_data:
                            cand_data['full_name'] = cand_data.pop('name')
                        
                        # Ensure id exists and is a string (some models omit it or return int)
                        if 'id' not in cand_data:
                            import uuid
                            cand_data['id'] = str(uuid.uuid4())
                        elif isinstance(cand_data['id'], int):
                            cand_data['id'] = str(cand_data['id'])
                        
                        # Add default values for required fields if missing
                        if 'summary' not in cand_data:
                            cand_data['summary'] = cand_data.get('bio', 'No summary available')
                        
                        # Ensure education is a list (some models return string)
                        if 'education' in cand_data and isinstance(cand_data['education'], str):
                            # Split if it's a comma-separated string, otherwise wrap in list
                            cand_data['education'] = [cand_data['education']]
                        elif 'education' not in cand_data:
                            cand_data['education'] = []
                        
                        # Fix experience fields mapping
                        if 'experience' in cand_data:
                            # Handle dict case - wrap in list
                            if isinstance(cand_data['experience'], dict):
                                cand_data['experience'] = [cand_data['experience']]
                            # Handle string case
                            elif isinstance(cand_data['experience'], str):
                                cand_data['experience'] = [{"description": cand_data['experience']}]
                        
                        if 'experience' in cand_data and isinstance(cand_data['experience'], list):
                            for exp in cand_data['experience']:
                                # Map 'role' to 'title'
                                if 'role' in exp and 'title' not in exp:
                                    exp['title'] = exp.pop('role')
                                
                                # Map 'duration' to 'start_date' and 'end_date'
                                if 'duration' in exp and ('start_date' not in exp or 'end_date' not in exp):
                                    duration = exp.pop('duration', '')
                                    parts = duration.split('-')
                                    if len(parts) >= 2:
                                        exp['start_date'] = parts[0].strip()
                                        exp['end_date'] = parts[1].strip()
                                    else:
                                        exp['start_date'] = duration
                                        exp['end_date'] = "Present"
                                
                                # Ensure required fields exist
                                if 'title' not in exp: exp['title'] = "Unknown Role"
                                if 'company' not in exp: exp['company'] = "Unknown Company"
                                if 'start_date' not in exp: exp['start_date'] = "Unknown"
                                if 'end_date' not in exp: exp['end_date'] = "Unknown"
                                
                                # Map achievements to description if description is missing
                                if 'description' not in exp:
                                    if 'achievements' in exp and isinstance(exp['achievements'], list):
                                        exp['description'] = "; ".join(exp['achievements'])
                                    else:
                                        exp['description'] = "No description provided"
                                
                                # Ensure key_achievements exists
                                if 'key_achievements' not in exp:
                                    if 'achievements' in exp:
                                        exp['key_achievements'] = exp.pop('achievements')
                                    else:
                                        exp['key_achievements'] = []

                        log_debug(f"  Creating candidate {i+1}/{len(candidates_data)}: {cand_data.get('full_name', 'Unknown')}")
                        
                        # Convert dict to CandidateProfile
                        profile = CandidateProfile(**cand_data)
                        
                        # Create Candidate object
                        candidate = Candidate(
                            id=profile.id,
                            name=profile.full_name,
                            resume_text=profile.resume_text,
                            role=self.state.query.split("-")[0] if "-" in self.state.query else "Executive",
                            profile=profile
                        )
                        
                        self.state.candidate_pool.append(candidate)
                        log_debug(f"Successfully added candidate: {candidate.name}")
                    else:
                        log_debug(f"Skipping non-dict candidate data: {type(cand_data)}")
                except Exception as e:
                    log_debug(f"Error creating candidate object: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            # Final Fallback: parse text output (original logic)
            log_debug("Failed all JSON parsing. Falling back to text parsing...")
            segments = result_str.split("CANDIDATE:")[1:] if "CANDIDATE:" in result_str else []
            
            for i, seg in enumerate(segments[:5]):
                lines = seg.strip().split("\n")
                name = lines[0].strip() if lines else f"Candidate {i+1}"
                
                candidate = Candidate(
                    id=str(uuid.uuid4())[:8],
                    name=name,
                    resume_text=seg.strip(),
                    role=self.state.query.split("-")[0] if "-" in self.state.query else "Executive"
                )
                
                self.state.candidate_pool.append(candidate)
        
        self.state.status = "Sourcing Complete"
        log_debug("="*80)
        log_debug("DEBUG: Sourcing Step Complete")
        log_debug("="*80)
        log_debug(f"DEBUG: Total candidates in pool: {len(self.state.candidate_pool)}")
        log_debug(f"DEBUG: Candidate names: {[c.name for c in self.state.candidate_pool]}")
        log_debug(f"DEBUG: candidates_data was: {'Found' if candidates_data else 'Not found'}")
        log_debug(f"DEBUG: Used fallback text parsing: {'Yes' if not candidates_data and 'CANDIDATE:' in result_str else 'No'}")
        log_debug("="*80)
        
        return self.state.candidate_pool
    
    @listen(sourcing_step)
    def vetting_step(self):
        """Vet each candidate using Vetting Crew"""
        print("Starting Vetting Crew...")
        self.state.status = "Vetting"
        
        # Determine role type for vetting rubric
        role_type = "Interim CFO"
        if "Healthcare" in self.state.query or "Ops" in self.state.query:
            role_type = "Healthcare Clinical Operations Lead"
        elif "Project Manager" in self.state.query or "PM" in self.state.query:
            role_type = "Elite Project Manager"
        
        # Vet each candidate - LIMIT TO TOP 5 TO AVOID RATE LIMITS
        import time
        max_vetting = 5
        candidates_to_vet = self.state.candidate_pool[:max_vetting]
        
        print(f"DEBUG: Vetting limited to top {len(candidates_to_vet)} of {len(self.state.candidate_pool)} candidates to avoid rate limits.")
        
        for i, candidate in enumerate(candidates_to_vet):
            print(f"Vetting candidate {i+1}/{len(candidates_to_vet)}: {candidate.name}")
            
            # Initialize Vetting Crew
            vetting_crew = VettingCrew(role_type=role_type).crew()
            
            # Retry logic for rate limits
            max_retries = 3
            retry_delay = 5
            result = None
            
            for attempt in range(max_retries):
                try:
                    # Add delay to avoid rate limits
                    if i > 0 or attempt > 0:
                        wait_time = 5 if attempt == 0 else retry_delay * (2 ** attempt)
                        print(f"Waiting {wait_time}s to respect rate limits...")
                        time.sleep(wait_time)
                    
                    # Kickoff vetting
                    print(f"  Attempt {attempt+1}/{max_retries}...")
                    result = vetting_crew.kickoff(inputs={
                        "resume": candidate.resume_text,
                        "role": role_type,
                        "requirements": json.dumps(self.state.client_requirements)
                    })
                    break # Success, exit retry loop
                except Exception as e:
                    print(f"Error vetting candidate {candidate.name} (Attempt {attempt+1}): {e}")
                    if attempt == max_retries - 1:
                        print(f"Skipping candidate {candidate.name} due to repeated errors.")
                        # Create a dummy result to allow graceful degradation
                        result = str({
                            "auditor_score": 70, 
                            "auditor_notes": "Vetting failed due to API limits.",
                            "domain_score": 70, 
                            "domain_notes": "Vetting failed due to API limits.",
                            "matchmaker_score": 70, 
                            "matchmaker_notes": "Automated vetting skipped.",
                            "final_recommendation": "Risk Flag",
                            "red_flags": ["Vetting incomplete"]
                        })
            
            if not result:
                continue

            # Parse vetting results - IMPROVED JSON PARSING
            try:
                # Try to extract JSON from result
                result_str = str(result)
                
                # DEBUG LOGGING
                try:
                    with open("d:/PRONEXUS/pronexus_agent/vetting_debug.log", "a", encoding="utf-8") as f:
                        f.write(f"\n{'='*50}\nCandidate: {candidate.name}\nResult String:\n{result_str}\n{'='*50}\n")
                except Exception as e:
                    print(f"Logging failed: {e}")

                # 1. Try to extract from markdown code blocks if present
                json_data = {}
                json_match = re.search(r'```\s*json\s*(.*?)\s*```', result_str, re.DOTALL | re.IGNORECASE)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(1))
                    except:
                        pass
                
                # 2. If no markdown or parse failed, try raw string
                if not json_data:
                    try:
                        json_data = json.loads(result_str)
                    except:
                        pass
                
                if json_data:
                    candidate.auditor_score = int(json_data.get('auditor_score', 75))
                    candidate.domain_score = int(json_data.get('domain_score', 75))
                    candidate.matchmaker_score = int(json_data.get('matchmaker_score', 75))
                    
                    candidate.auditor_notes = json_data.get('auditor_notes', "Notes not provided")
                    candidate.domain_notes = json_data.get('domain_notes', "Notes not provided")
                    candidate.matchmaker_notes = json_data.get('matchmaker_notes', "Notes not provided")
                    
                    # Handle final recommendation mapping
                    rec = json_data.get('final_recommendation', 'Hire')
                    candidate.final_fit = rec if rec in ["Strong Hire", "Hire", "Risk Flag", "Do Not Hire"] else "Hire"
                    
                    # Handle red flags
                    flags = json_data.get('red_flags', [])
                    if isinstance(flags, list):
                        candidate.red_flags.extend(flags)
                    elif isinstance(flags, str):
                        candidate.red_flags.append(flags)

                else:
                    # Fallback to regex/string searching if JSON parsing fails completely
                    # Look for JSON-like structures in the output
                    if "auditor_score" in result_str.lower():
                        # Extract scores (simplified parsing)
                        auditor_match = re.search(r'auditor[_\s]?score[:\s]+(\d+)', result_str, re.IGNORECASE)
                        domain_match = re.search(r'domain[_\s]?score[:\s]+(\d+)', result_str, re.IGNORECASE)
                        final_match = re.search(r'(?:final|matchmaker)[_\s]?score[:\s]+(\d+)', result_str, re.IGNORECASE)
                        
                        candidate.auditor_score = int(auditor_match.group(1)) if auditor_match else 70
                        candidate.domain_score = int(domain_match.group(1)) if domain_match else 70
                        candidate.matchmaker_score = int(final_match.group(1)) if final_match else 70
                    else:
                        # Default scores if parsing fails
                        candidate.auditor_score = 75
                        candidate.domain_score = 75
                        candidate.matchmaker_score = 75
                    
                    # Clean up notes - strip JSON artifacts if present at start/end
                    clean_str = result_str.strip()
                    if clean_str.startswith('```json'): clean_str = clean_str[7:]
                    if clean_str.endswith('```'): clean_str = clean_str[:-3]
                    if clean_str.startswith('{'): clean_str = clean_str[1:]
                    if clean_str.endswith('}'): clean_str = clean_str[:-1]
                    
                    candidate.matchmaker_notes = clean_str
                    candidate.auditor_notes = "See matchmaker notes"
                    candidate.domain_notes = "See matchmaker notes"
                    
                    # Extract red flags
                    if "red flag" in result_str.lower() or "risk" in result_str.lower():
                        candidate.red_flags.append("Risk identified in vetting")
                
                # Enforce consistency between scores and final recommendation
                avg_score = (candidate.auditor_score + candidate.domain_score + candidate.matchmaker_score) / 3
                if avg_score >= 90:
                    candidate.final_fit = "Strong Hire"
                elif avg_score >= 80:
                    candidate.final_fit = "Hire"
                elif avg_score >= 60 and candidate.final_fit not in ["Hire", "Strong Hire"]:
                    candidate.final_fit = "Risk Flag"
                elif avg_score < 60:
                    candidate.final_fit = "Do Not Hire"
            
            except Exception as e:
                print(f"Error parsing vetting result for {candidate.name}: {e}")
                candidate.final_fit = "Pending Review"
                candidate.matchmaker_notes = f"Error parsing result: {str(e)}"
            
            self.state.vetted_candidates.append(candidate)
        
        self.state.status = "Vetting Complete"
        print(f"Vetted {len(self.state.vetted_candidates)} candidates")
        
        self.state.status = "Vetting Complete"
        print(f"Vetted {len(self.state.vetted_candidates)} candidates")
        
        return self.state.vetted_candidates
    
    @listen(vetting_step)
    def generate_report(self):
        """Generate final markdown report"""
        print("Generating final report...")
        self.state.status = "Reporting"
        
        # Filter candidates by score threshold
        qualified_candidates = [
            c for c in self.state.vetted_candidates
            if c.matchmaker_score >= 60
        ]
        
        # Sort by score
        qualified_candidates.sort(key=lambda x: (x.auditor_score + x.domain_score + x.matchmaker_score) / 3, reverse=True)
        
        # Build markdown report
        report_lines = [
            "# ProNexus Executive Search Report",
            "",
            f"**Search Query:** {self.state.query}",
            f"**Candidates Evaluated:** {len(self.state.vetted_candidates)}",
            f"**Qualified Candidates:** {len(qualified_candidates)}",
            "",
            "---",
            ""
        ]
        
        for i, candidate in enumerate(qualified_candidates, 1):
            avg_score = int((candidate.auditor_score + candidate.domain_score + candidate.matchmaker_score) / 3)
            report_lines.extend([
                f"## {i}. {candidate.name}",
                "",
                f"**Final Recommendation:** {candidate.final_fit}",
                f"**Overall Score:** {avg_score}/100",
                "",
                "### Vetting Breakdown",
                f"- **Risk Assessment:** {candidate.auditor_score}/100",
                f"- **Domain Expertise:** {candidate.domain_score}/100",
                f"- **Fit Score:** {candidate.matchmaker_score}/100",
                ""
            ])
            
            if candidate.auditor_notes:
                report_lines.extend([
                    "### Risk Assessment Notes",
                    candidate.auditor_notes,
                    ""
                ])
            
            if candidate.domain_notes:
                report_lines.extend([
                    "### Domain Expertise Notes",
                    candidate.domain_notes,
                    ""
                ])
            
            if candidate.red_flags:
                report_lines.extend([
                    "### Red Flags",
                    "\n".join([f"- {flag}" for flag in candidate.red_flags]),
                    ""
                ])
            
            report_lines.append("---\n")
        
        self.state.final_report = "\n".join(report_lines)
        self.state.status = "Complete"
        
        return self.state.final_report
