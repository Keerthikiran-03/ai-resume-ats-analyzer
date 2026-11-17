import re
import math
from typing import Dict, List, Any, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .skills_db import SKILLS_TAXONOMY, STRONG_ACTION_VERBS, WEAK_ACTION_VERBS, SECTION_PATTERNS

class ATSEngine:
    def __init__(self):
        pass

    def analyze(self, resume_text: str, jd_text: str = "") -> Dict[str, Any]:
        """Performs full ATS and multi-dimensional resume evaluation against a JD or standalone."""
        clean_resume = resume_text.lower()
        clean_jd = (jd_text or "").lower().strip()
        has_jd = len(clean_jd) >= 20

        # 1. Contact Information Extraction
        contact_info = self._extract_contact_info(resume_text)

        # 2. Section Completeness Check
        sections_found, missing_sections = self._check_sections(clean_resume)

        # 3. Skills Gap Analysis
        skills_analysis = self._analyze_skills(clean_resume, clean_jd, has_jd)

        # 4. TF-IDF & Semantic Similarity Score
        tfidf_score, top_jd_keywords = self._compute_tfidf_match(resume_text, jd_text, has_jd)

        # 5. Impact & Action Verbs Analysis
        impact_analysis = self._analyze_impact_and_verbs(resume_text)

        # 6. Readability & Formatting Checks
        readability = self._analyze_readability(resume_text)

        # 7. Overall Composite ATS Score Calculation
        overall_score, component_scores = self._calculate_overall_score(
            tfidf_score=tfidf_score,
            skills_coverage_score=skills_analysis["coverage_score"],
            impact_score=impact_analysis["impact_score"],
            section_score=self._calc_section_score(sections_found, contact_info),
            readability_score=readability["readability_score"],
            has_jd=has_jd
        )

        # 8. Actionable Insights & Recommendations
        recommendations = self._generate_recommendations(
            overall_score=overall_score,
            skills_analysis=skills_analysis,
            impact_analysis=impact_analysis,
            contact_info=contact_info,
            missing_sections=missing_sections,
            readability=readability,
            has_jd=has_jd
        )

        return {
            "overall_score": overall_score,
            "has_target_job": has_jd,
            "rating_tier": self._get_rating_tier(overall_score, has_jd),
            "component_scores": component_scores,
            "skills_analysis": skills_analysis,
            "impact_analysis": impact_analysis,
            "contact_info": contact_info,
            "sections": {
                "found": sections_found,
                "missing": missing_sections
            },
            "readability": readability,
            "top_jd_keywords": top_jd_keywords,
            "recommendations": recommendations
        }

    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
        github_match = re.search(r'github\.com/[a-zA-Z0-9_-]+', text, re.IGNORECASE)

        return {
            "has_email": bool(email_match),
            "email": email_match.group(0) if email_match else None,
            "has_phone": bool(phone_match),
            "phone": phone_match.group(0) if phone_match else None,
            "has_linkedin": bool(linkedin_match),
            "linkedin": linkedin_match.group(0) if linkedin_match else None,
            "has_github_or_portfolio": bool(github_match),
            "github": github_match.group(0) if github_match else None,
        }

    def _check_sections(self, clean_resume: str) -> Tuple[List[str], List[str]]:
        found = []
        missing = []
        for section, patterns in SECTION_PATTERNS.items():
            if any(re.search(pat, clean_resume) for pat in patterns):
                found.append(section.capitalize())
            else:
                missing.append(section.capitalize())
        return found, missing

    def _analyze_skills(self, clean_resume: str, clean_jd: str, has_jd: bool) -> Dict[str, Any]:
        """Extracts and compares skills between JD and Resume."""
        jd_skills = {}
        resume_skills = {}

        for skill, category in SKILLS_TAXONOMY.items():
            pattern = r'\b' + re.escape(skill) + r'\b'
            if has_jd and re.search(pattern, clean_jd):
                jd_skills[skill] = category
            if re.search(pattern, clean_resume):
                resume_skills[skill] = category

        # Separate resume skills into technical vs soft
        all_resume_hard = [s for s, cat in resume_skills.items() if cat != "Soft Skills"]
        all_resume_soft = [s for s, cat in resume_skills.items() if cat == "Soft Skills"]

        if not has_jd:
            # Standalone Resume Audit: all detected resume skills are displayed as matched
            num_skills = len(all_resume_hard)
            coverage_score = min(95, max(45, 50 + (num_skills * 3)))
            return {
                "coverage_score": coverage_score,
                "matched_hard_skills": sorted(all_resume_hard),
                "missing_hard_skills": [],
                "matched_soft_skills": sorted(all_resume_soft),
                "missing_soft_skills": [],
                "additional_resume_skills": [],
                "total_jd_skills_found": 0,
                "total_matched": len(resume_skills)
            }

        # Targeted JD Mode: Categorize matches against JD
        matched_hard = []
        missing_hard = []
        matched_soft = []
        missing_soft = []

        for skill, category in jd_skills.items():
            is_soft = (category == "Soft Skills")
            if skill in resume_skills:
                if is_soft:
                    matched_soft.append(skill)
                else:
                    matched_hard.append(skill)
            else:
                if is_soft:
                    missing_soft.append(skill)
                else:
                    missing_hard.append(skill)

        additional_skills = [
            skill for skill in resume_skills if skill not in jd_skills
        ]

        total_jd_skills = len(jd_skills)
        matched_count = len(matched_hard) + len(matched_soft)

        if total_jd_skills > 0:
            coverage_score = round((matched_count / total_jd_skills) * 100)
        else:
            coverage_score = 75

        return {
            "coverage_score": min(100, coverage_score),
            "matched_hard_skills": sorted(matched_hard),
            "missing_hard_skills": sorted(missing_hard),
            "matched_soft_skills": sorted(matched_soft),
            "missing_soft_skills": sorted(missing_soft),
            "additional_resume_skills": sorted(additional_skills)[:15],
            "total_jd_skills_found": total_jd_skills,
            "total_matched": matched_count
        }

    def _compute_tfidf_match(self, resume_text: str, jd_text: str, has_jd: bool) -> Tuple[int, List[Dict[str, Any]]]:
        """Computes TF-IDF similarity if JD provided, or keyword richness if standalone."""
        if not resume_text.strip():
            return 40, []

        try:
            if not has_jd:
                # Standalone mode: extract top keywords from resume
                vec = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=30)
                tfidf = vec.fit_transform([resume_text])
                feature_names = vec.get_feature_names_out()
                scores = tfidf.toarray()[0]
                top_indices = scores.argsort()[::-1][:15]
                top_keywords = []
                for idx in top_indices:
                    word = feature_names[idx]
                    if len(word) > 2 and scores[idx] > 0.05:
                        top_keywords.append({
                            "keyword": word,
                            "weight": round(float(scores[idx]), 3),
                            "present_in_resume": True
                        })
                # Baseline keyword richness score
                richness_score = min(92, max(55, len(top_keywords) * 6))
                return richness_score, top_keywords

            # Targeted JD Mode: Cosine similarity
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=100
            )
            tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            scaled_score = min(100, int(similarity * 140))
            if similarity > 0.05 and scaled_score < 40:
                scaled_score = 40 + int(similarity * 60)

            feature_names = vectorizer.get_feature_names_out()
            jd_scores = tfidf_matrix[0].toarray()[0]
            resume_scores = tfidf_matrix[1].toarray()[0]

            top_indices = jd_scores.argsort()[::-1][:15]
            top_keywords = []
            for idx in top_indices:
                word = feature_names[idx]
                if len(word) > 2 and jd_scores[idx] > 0.05:
                    top_keywords.append({
                        "keyword": word,
                        "weight": round(float(jd_scores[idx]), 3),
                        "present_in_resume": bool(resume_scores[idx] > 0)
                    })

            return max(20, min(98, scaled_score)), top_keywords
        except Exception:
            return 60, []

    def _analyze_impact_and_verbs(self, text: str) -> Dict[str, Any]:
        """Analyzes use of measurable metrics, strong action verbs, and identifies weak verbs."""
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 15]
        bullets = [line for line in lines if line.startswith(('-', '•', '*', '–')) or len(line) < 200]

        metric_pattern = re.compile(
            r'(\b\d+(\.\d+)?%|\$\d+(\.\d+)?(k|m|b)?|\b\d+\s?(k|m|b)\b|\b\d+x\b|\bincreased by \d+|\breduced by \d+|\bsaved \d+)',
            re.IGNORECASE
        )

        measurable_bullets = []
        bullets_needing_metrics = []

        for b in bullets[:25]:
            clean_b = b.lstrip('-•*– ').strip()
            if metric_pattern.search(clean_b):
                measurable_bullets.append(clean_b)
            elif len(clean_b) > 30:
                bullets_needing_metrics.append(clean_b)

        words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
        found_strong_verbs = list(words.intersection(STRONG_ACTION_VERBS))
        found_weak_verbs = [
            phrase for phrase in WEAK_ACTION_VERBS if phrase in text.lower()
        ]

        total_bullets = len(measurable_bullets) + len(bullets_needing_metrics)
        metrics_ratio = (len(measurable_bullets) / max(1, total_bullets)) if total_bullets > 0 else 0.4
        
        impact_score = int(
            (metrics_ratio * 50) + 
            (min(len(found_strong_verbs), 8) / 8.0 * 35) + 
            (15 if len(found_weak_verbs) == 0 else max(0, 15 - len(found_weak_verbs) * 3))
        )

        return {
            "impact_score": min(100, max(20, impact_score)),
            "metrics_count": len(measurable_bullets),
            "total_evaluated_bullets": total_bullets,
            "metrics_ratio_pct": round(metrics_ratio * 100),
            "strong_verbs_count": len(found_strong_verbs),
            "strong_verbs_found": sorted(found_strong_verbs),
            "weak_verbs_found": sorted(found_weak_verbs),
            "sample_measurable_bullets": measurable_bullets[:5],
            "bullets_needing_metrics": bullets_needing_metrics[:5]
        }

    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Evaluates resume word count, page density, and text flow."""
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        if 400 <= word_count <= 850:
            status = "Optimal (1-2 pages recommended length)"
            score = 95
        elif 300 <= word_count < 400:
            status = "Slightly Short (Consider expanding on key achievements)"
            score = 75
        elif 850 < word_count <= 1200:
            status = "A bit long (Ensure every bullet is high impact)"
            score = 80
        elif word_count < 300:
            status = "Too Brief (Lacks sufficient detail for ATS parsing)"
            score = 45
        else:
            status = "Too Long (Exceeds typical 2-page ATS standard)"
            score = 60

        est_pages = max(1, math.ceil(word_count / 450))

        return {
            "word_count": word_count,
            "estimated_pages": est_pages,
            "length_status": status,
            "readability_score": score
        }

    def _calc_section_score(self, sections_found: List[str], contact_info: Dict[str, Any]) -> int:
        score = 0
        score += min(len(sections_found) * 12, 60)
        if contact_info.get("has_email"): score += 10
        if contact_info.get("has_phone"): score += 10
        if contact_info.get("has_linkedin"): score += 10
        if contact_info.get("has_github_or_portfolio"): score += 10
        return min(100, score)

    def _calculate_overall_score(self, tfidf_score: int, skills_coverage_score: int,
                                 impact_score: int, section_score: int, readability_score: int,
                                 has_jd: bool = True) -> Tuple[int, Dict[str, int]]:
        if has_jd:
            composite = (
                tfidf_score * 0.35 +
                skills_coverage_score * 0.25 +
                impact_score * 0.20 +
                section_score * 0.10 +
                readability_score * 0.10
            )
        else:
            # Standalone Resume ATS Health weights:
            # Impact & Metrics: 30%, Skills Taxonomy: 25%, Structure & Contact: 20%, Readability: 15%, Keyword Richness: 10%
            composite = (
                impact_score * 0.30 +
                skills_coverage_score * 0.25 +
                section_score * 0.20 +
                readability_score * 0.15 +
                tfidf_score * 0.10
            )
        
        overall = int(round(composite))
        components = {
            "keyword_match": tfidf_score,
            "skills_coverage": skills_coverage_score,
            "impact_metrics": impact_score,
            "structure_contact": section_score,
            "formatting_readability": readability_score
        }
        return overall, components

    def _get_rating_tier(self, score: int, has_jd: bool = True) -> Dict[str, str]:
        suffix = "Target Match" if has_jd else "ATS Health"
        if score >= 85:
            return {"label": f"Exceptional {suffix}", "color": "emerald", "badge": "Top 5% Candidate"}
        elif score >= 70:
            return {"label": f"Competitive {suffix}", "color": "blue", "badge": "Strong Contender"}
        elif score >= 55:
            return {"label": f"Moderate {suffix}", "color": "amber", "badge": "Needs Optimization"}
        else:
            return {"label": f"Low {suffix}", "color": "rose", "badge": "Critical Fixes Needed"}

    def _generate_recommendations(self, overall_score: int, skills_analysis: Dict[str, Any],
                                  impact_analysis: Dict[str, Any], contact_info: Dict[str, Any],
                                  missing_sections: List[str], readability: Dict[str, Any],
                                  has_jd: bool = True) -> List[Dict[str, Any]]:
        recs = []

        if not has_jd:
            recs.append({
                "type": "suggestion",
                "category": "Targeted Optimization",
                "title": "Compare Against a Specific Job Description",
                "description": "This is a General ATS Health Audit. To see your exact keyword match percentage and missing technical skills for a specific role, paste the Job Description into the right panel and click Analyze."
            })

        missing_hard = skills_analysis.get("missing_hard_skills", [])
        if missing_hard and has_jd:
            top_missing = missing_hard[:5]
            recs.append({
                "type": "critical",
                "category": "Skills Gap",
                "title": f"Integrate {len(missing_hard)} Missing High-Demand Skills",
                "description": f"The job description specifically looks for: {', '.join(top_missing)}. Add these into your Technical Skills section and work history if you have experience with them."
            })

        if impact_analysis.get("metrics_ratio_pct", 0) < 40:
            recs.append({
                "type": "warning",
                "category": "Quantifiable Impact",
                "title": "Add Measurable Metrics to Your Bullet Points",
                "description": "Recruiters and ATS favor the Google XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'. Incorporate exact %, $, time saved, or scale numbers in at least 50% of your experience bullets."
            })

        weak_verbs = impact_analysis.get("weak_verbs_found", [])
        if weak_verbs:
            recs.append({
                "type": "warning",
                "category": "Action Verbs",
                "title": f"Replace {len(weak_verbs)} Passive/Weak Verbs",
                "description": f"Found passive phrases like: {', '.join(weak_verbs)}. Replace them with assertive leadership verbs such as 'Spearheaded', 'Architected', 'Streamlined', or 'Orchestrated'."
            })

        if not contact_info.get("has_linkedin"):
            recs.append({
                "type": "suggestion",
                "category": "Contact Details",
                "title": "Include a Custom LinkedIn URL",
                "description": "Over 87% of recruiters cross-reference LinkedIn profiles during ATS reviews. Add your customized LinkedIn handle to your header."
            })

        if "Summary" in missing_sections:
            recs.append({
                "type": "suggestion",
                "category": "Structure",
                "title": "Add a Tailored Professional Summary",
                "description": "A 3-4 sentence summary at the top highlights your career identity and immediately seeds high-value keywords for ATS parsing."
            })

        if readability.get("word_count", 0) < 350:
            recs.append({
                "type": "critical",
                "category": "Length",
                "title": "Expand Resume Depth (Currently Under 350 Words)",
                "description": "Your resume is too brief. Provide more detailed project bullet points, tools utilized, and specific outcomes."
            })

        return recs
