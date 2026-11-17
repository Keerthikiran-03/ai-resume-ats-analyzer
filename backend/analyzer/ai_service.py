import json
import os
import re
from typing import Dict, Any, List, Optional
import requests

class AIService:
    def __init__(self):
        # Check system env for API key fallback
        self.default_gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def _call_gemini(self, prompt: str, api_key: Optional[str] = None, system_instruction: str = "") -> Optional[str]:
        """Calls Gemini API directly using REST API."""
        key = api_key or self.default_gemini_key
        if not key:
            return None

        # Models to try: gemini-2.5-flash, gemini-1.5-flash
        models = ["gemini-2.5-flash", "gemini-1.5-flash"]
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_instruction}\n\n{prompt}" if system_instruction else prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 2048,
                }
            }
            try:
                resp = requests.post(url, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            except Exception as e:
                print(f"Gemini API request failed for {model}: {e}")
                continue

        return None

    def generate_deep_review(self, resume_text: str, jd_text: str, ats_data: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generates an executive-level recruiter review of the resume."""
        prompt = f"""
You are an elite Fortune 500 Executive Recruiter and ATS Specialist.
Perform an in-depth review of this Candidate Resume against the Job Description.

JOB DESCRIPTION:
{jd_text[:2000]}

CANDIDATE RESUME:
{resume_text[:2500]}

ATS ANALYSIS DATA:
- ATS Score: {ats_data.get('overall_score')}%
- Matched Hard Skills: {', '.join(ats_data.get('skills_analysis', {}).get('matched_hard_skills', [])[:10])}
- Missing Hard Skills: {', '.join(ats_data.get('skills_analysis', {}).get('missing_hard_skills', [])[:10])}

Return a valid, pure JSON object with these keys:
{{
  "recruiter_verdict": "A sharp 2-3 sentence summary of how a recruiter views this candidate in the first 6 seconds.",
  "top_strengths": ["Strength 1 with detail", "Strength 2 with detail", "Strength 3 with detail"],
  "critical_blindspots": ["Blindspot 1 with fix", "Blindspot 2 with fix", "Blindspot 3 with fix"],
  "tailoring_advice": ["Specific tactical action 1", "Specific tactical action 2", "Specific tactical action 3"],
  "salary_market_positioning": "Brief note on candidate positioning for this tier of role"
}}
Do NOT wrap in markdown fences if possible, return strictly parseable JSON.
"""
        response_text = self._call_gemini(prompt, api_key=api_key)
        if response_text:
            try:
                # Clean potential markdown fences
                clean_json = re.sub(r'```json\s*|\s*```', '', response_text).strip()
                return json.loads(clean_json)
            except Exception:
                pass

        # Offline Algorithmic Fallback
        matched = ats_data.get("skills_analysis", {}).get("matched_hard_skills", [])
        missing = ats_data.get("skills_analysis", {}).get("missing_hard_skills", [])
        score = ats_data.get("overall_score", 70)

        return {
            "recruiter_verdict": f"The candidate presents a {ats_data.get('rating_tier', {}).get('label', 'Competent Profile')} for this position. While core foundations in {', '.join(matched[:3]) if matched else 'the discipline'} are demonstrated, addressing the {len(missing)} missing key competencies will significantly boost interview conversion.",
            "top_strengths": [
                f"Demonstrated proficiency in relevant core technologies ({', '.join(matched[:4]) if matched else 'Foundational domain skills'}).",
                f"Resume structure features {len(ats_data.get('sections', {}).get('found', []))} standard ATS-recognized sections.",
                f"Contains {ats_data.get('impact_analysis', {}).get('metrics_count', 0)} quantified performance bullets with tangible metrics."
            ],
            "critical_blindspots": [
                f"Missing high-priority keywords from Job Description: {', '.join(missing[:4]) if missing else 'None detected; consider deepening architecture-level descriptions'}.",
                "Some bullet points lack the Google XYZ impact formula (Accomplished X by doing Y measured by Z).",
                "Ensure skills are demonstrated inside recent job bullets rather than just listed in a static skills cloud."
            ],
            "tailoring_advice": [
                f"Incorporate missing skills ({', '.join(missing[:3]) if missing else 'domain keywords'}) into the most recent 2 role descriptions.",
                "Elevate verbs: replace passive phrases with leadership actions (Engineered, Spearheaded, Accelerated).",
                "Craft a targeted 3-line summary specifically echoing the job title and top required tools."
            ],
            "salary_market_positioning": f"Profile matches approximately {score}% of target requirements. Bridging identified gaps positions the candidate in the upper quartile compensation bracket for this role."
        }

    def rewrite_bullet(self, bullet: str, jd_text: str = "", target_skill: str = "", api_key: Optional[str] = None) -> Dict[str, Any]:
        """Rewrites a resume bullet point into 3 high-impact variations."""
        prompt = f"""
You are a master executive resume writer specializing in the Google XYZ resume formula:
"Accomplished [X] as measured by [Y], by doing [Z]"

Original Bullet: "{bullet}"
Target Skill / Focus: "{target_skill or 'Impact & Engineering'}"
Job Context: "{jd_text[:600] if jd_text else 'Standard high-performance industry role'}"

Provide 3 distinct rewritten variations:
1. Metrics & Quantifiable Impact (emphasizing measurable business/engineering results)
2. Technical Depth & Modern Tooling (emphasizing technical architecture and modern practices)
3. Leadership & Cross-Functional Execution (emphasizing ownership, mentorship, and delivery)

Return pure JSON:
{{
  "metrics_focused": "Rewritten bullet emphasizing numbers, %, and quantifiable outcomes",
  "technical_focused": "Rewritten bullet highlighting deep technical implementation and tools",
  "leadership_focused": "Rewritten bullet highlighting ownership, team impact, and velocity",
  "key_improvements_made": ["improvement 1", "improvement 2"]
}}
"""
        response_text = self._call_gemini(prompt, api_key=api_key)
        if response_text:
            try:
                clean_json = re.sub(r'```json\s*|\s*```', '', response_text).strip()
                return json.loads(clean_json)
            except Exception:
                pass

        # Offline Algorithmic Rewrite Generator
        clean_bullet = bullet.lstrip('-•*– ').strip()
        skill_insert = f" utilizing {target_skill}" if target_skill else ""

        return {
            "metrics_focused": f"Spearheaded {clean_bullet.lower()}{skill_insert}, achieving a 35% reduction in latency and improving operational efficiency across 50,000+ monthly active users.",
            "technical_focused": f"Architected and deployed {clean_bullet.lower()}{skill_insert}, implementing modular microservices and automated CI/CD pipelines to ensure 99.9% uptime.",
            "leadership_focused": f"Orchestrated cross-functional collaboration to deliver {clean_bullet.lower()}{skill_insert}, mentoring junior engineers and accelerating project delivery 3 weeks ahead of schedule.",
            "key_improvements_made": [
                "Replaced passive wording with strong power verbs (Spearheaded, Architected, Orchestrated).",
                "Incorporated quantifiable metrics and business impact.",
                "Structured following the Google XYZ achievement formula."
            ]
        }

    def generate_cover_letter(self, resume_text: str, jd_text: str, candidate_name: str = "",
                              company_name: str = "", role_title: str = "", api_key: Optional[str] = None) -> str:
        """Generates a tailored, ATS-friendly cover letter."""
        prompt = f"""
Write a compelling, professional, and authentic cover letter.
Candidate Name: {candidate_name or 'The Candidate'}
Company Name: {company_name or 'Hiring Team'}
Target Role: {role_title or 'Target Role'}

Candidate Resume Experience:
{resume_text[:2000]}

Job Description Requirements:
{jd_text[:2000]}

Guidelines:
- 3 to 4 paragraphs.
- Enthusiastic, confident, and specific to the candidate's actual projects and the job requirements.
- Avoid clichés like "I am writing to express my interest". Start with an engaging hook.
- Connect 2-3 specific accomplishments from the resume to the company's pain points.
- Professional closing.
"""
        response_text = self._call_gemini(prompt, api_key=api_key)
        if response_text:
            return response_text.strip()

        # Offline Algorithmic Generator
        cand = candidate_name or "[Your Name]"
        comp = company_name or "[Company Name]"
        role = role_title or "[Target Role]"

        return f"""Dear Hiring Team at {comp},

I am writing to enthusiastically present my qualifications for the {role} position. Having closely followed {comp}'s recent growth and industry initiatives, I am eager to leverage my hands-on background in scalable development, technical problem-solving, and continuous optimization to drive immediate value for your engineering team.

In my recent experience, I have spearheaded initiatives that directly parallel the core priorities outlined in your job description. By architecting resilient solutions, optimizing workflows, and applying modern development best practices, I consistently deliver solutions that balance rapid execution with high code quality and measurable business impact.

What particularly excites me about {comp} is your commitment to technical excellence and user-centric innovation. I look forward to contributing my technical skills, collaborative drive, and proactive problem-solving mindset to your upcoming milestones.

Thank you for your time and consideration. I would welcome the opportunity to discuss how my experience and passion align with your team's vision.

Sincerely,
{cand}"""

    def generate_interview_prep(self, resume_text: str, jd_text: str, skills_data: Dict[str, Any], api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generates tailored interview questions (Technical, STAR Behavioral, System Design/Situational)."""
        prompt = f"""
Generate 6 highly tailored interview questions for this candidate based on their resume and the job description.
Focus on:
1. Technical questions targeting their claimed stack AND missing skills ({', '.join(skills_data.get('missing_hard_skills', [])[:4])}).
2. Behavioral questions using the STAR framework (Situation, Task, Action, Result).
3. Situational/Architectural problem solving.

Resume: {resume_text[:1800]}
Job: {jd_text[:1800]}

Return pure JSON array of objects:
[
  {{
    "type": "Technical" | "Behavioral (STAR)" | "Situational",
    "question": "The exact interview question",
    "why_asked": "Why the recruiter/interviewer asks this",
    "ideal_strategy": "Concrete advice and talking points on how to answer effectively"
  }}
]
"""
        response_text = self._call_gemini(prompt, api_key=api_key)
        if response_text:
            try:
                clean_json = re.sub(r'```json\s*|\s*```', '', response_text).strip()
                parsed = json.loads(clean_json)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

        # Offline Algorithmic Generator
        missing = skills_data.get("missing_hard_skills", [])
        matched = skills_data.get("matched_hard_skills", [])
        focus_tech = missing[0] if missing else (matched[0] if matched else "System Architecture")

        return [
            {
                "type": "Technical",
                "question": f"How have you approached designing scalable solutions using {focus_tech}, and what architectural trade-offs did you consider?",
                "why_asked": f"Evaluates your practical depth in {focus_tech}, a core requirement highlighted in the job description.",
                "ideal_strategy": "Discuss a real project where you handled scale or latency. Contrast 2 architectural options (e.g. caching vs async queues) and explain why your choice was optimal."
            },
            {
                "type": "Behavioral (STAR)",
                "question": "Tell me about a time a critical production bug occurred or a project deadline was at risk. How did you handle it?",
                "why_asked": "Assesses resilience, root cause analysis, accountability, and communication under high pressure.",
                "ideal_strategy": "Use STAR: Situation (high-stakes bug), Task (restore service & isolate issue), Action (systematic debugging & stakeholder updates), Result (quick recovery, post-mortem, and automated safeguards added)."
            },
            {
                "type": "Technical",
                "question": f"Can you walk me through how you optimize database queries and backend APIs for sub-100ms response times?",
                "why_asked": "Tests backend engineering maturity, caching strategies (Redis), indexing, and performance profiling.",
                "ideal_strategy": "Highlight profiling tools (EXPLAIN plans, APM), indexing strategies, connection pooling, and how you prevent N+1 query bottlenecks."
            },
            {
                "type": "Behavioral (STAR)",
                "question": "Describe an instance where you disagreed with a product manager or team lead on a technical approach. How was it resolved?",
                "why_asked": "Evaluates teamwork, negotiation, empathy, and data-driven decision making.",
                "ideal_strategy": "Frame the disagreement around objective metrics/user outcomes rather than ego. Explain how you ran a quick proof-of-concept or benchmark to reach consensus."
            },
            {
                "type": "Situational",
                "question": "If tasked with migrating a legacy monolithic service into decoupled microservices with zero downtime, how would you phase the project?",
                "why_asked": "Assesses large-scale architecture thinking, risk management, and the Strangler Fig migration pattern.",
                "ideal_strategy": "Detail the Strangler Fig pattern: establish an API gateway, route specific read traffic first, use dual-write/event streaming, and decommission the old module once validated."
            }
        ]
