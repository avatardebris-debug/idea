"""Profile matcher — scores how well a candidate matches a job profile."""

from __future__ import annotations


def match_profiles(
    candidate_skills: list[str],
    candidate_experience: str,
    job_profile: dict,
) -> dict:
    """Score how well a candidate matches a job profile.

    Args:
        candidate_skills: List of candidate's skills.
        candidate_experience: Candidate's experience level (e.g. "senior", "mid-level").
        job_profile: Dict with keys matching parse_job_description output.

    Returns:
        Dict with keys:
            score (int 0-100): Overall match score.
            matched_skills (list[str]): Skills the candidate has that the job needs.
            missing_skills (list[str]): Skills the job needs that the candidate lacks.
            salary_match (bool): Whether salary expectations align.
    """
    # Normalize inputs
    candidate_skills_set = set(s.lower().strip() for s in candidate_skills)
    job_skills = [s.lower().strip() for s in job_profile.get("skills", [])]
    job_skills_set = set(job_skills)

    # --- Skill overlap (Jaccard similarity scaled to 0-60 points) ---
    if not job_skills_set and not candidate_skills_set:
        skill_score = 60  # No skills required, candidate has none — neutral
        matched_skills: list[str] = []
        missing_skills: list[str] = []
    elif not job_skills_set:
        skill_score = 60  # No skills required — full credit
        matched_skills = []
        missing_skills = []
    elif not candidate_skills_set:
        skill_score = 0
        matched_skills = []
        missing_skills = list(job_profile.get("skills", []))
    else:
        intersection = candidate_skills_set & job_skills_set
        union = candidate_skills_set | job_skills_set
        jaccard = len(intersection) / len(union) if union else 0.0
        skill_score = int(jaccard * 60)
        matched_skills = [s for s in job_profile.get("skills", []) if s.lower().strip() in intersection]
        missing_skills = [s for s in job_profile.get("skills", []) if s.lower().strip() not in intersection]

    # --- Experience level compatibility (0-25 points) ---
    exp_score = _score_experience(candidate_experience, job_profile.get("experience_level"))

    # --- Salary alignment (0-15 points) ---
    salary_match = _score_salary(candidate_skills, job_profile)

    # --- Total score (capped at 100) ---
    total = min(skill_score + exp_score + salary_match, 100)

    return {
        "score": total,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "salary_match": salary_match > 0,
    }


def _score_experience(candidate_exp: str, job_exp: str | None) -> int:
    """Score experience level compatibility (0-25 points)."""
    if not job_exp:
        return 25  # No experience requirement — full credit

    # Define experience hierarchy
    exp_levels = {
        "entry": 1,
        "junior": 1,
        "entry-level": 1,
        "mid": 2,
        "mid-level": 2,
        "senior": 3,
        "lead": 4,
        "principal": 5,
        "staff": 5,
        "director": 6,
        "vp": 7,
        "c-suite": 8,
    }

    candidate_level = exp_levels.get(candidate_exp.lower().strip(), 0)
    job_level = exp_levels.get(job_exp.lower().strip(), 0)

    if candidate_level >= job_level:
        return 25  # Candidate meets or exceeds requirement
    elif candidate_level >= job_level - 1:
        return 15  # Close match
    else:
        return 5   # Far below requirement


def _score_salary(candidate_skills: list[str], job_profile: dict) -> int:
    """Score salary alignment (0-15 points).

    If the job has a salary range, we check if the candidate's expected
    salary (derived from skills/experience) falls within it.
    """
    salary_min = job_profile.get("salary_min")
    salary_max = job_profile.get("salary_max")

    if not salary_min or not salary_max:
        return 15  # No salary info — assume match

    # Estimate candidate's expected salary based on skills and experience
    # This is a simplified heuristic
    base_salary = 50000  # Base salary
    skill_bonus = len(candidate_skills) * 5000  # $5k per skill
    expected_salary = base_salary + skill_bonus

    if salary_min <= expected_salary <= salary_max:
        return 15  # Within range
    elif expected_salary < salary_min:
        return 10  # Below range but close
    else:
        return 5   # Above range
