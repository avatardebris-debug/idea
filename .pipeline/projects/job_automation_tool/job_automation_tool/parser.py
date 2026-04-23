"""Job description parser — extracts structured fields from raw text."""

from __future__ import annotations

import re
from typing import Optional


def parse_job_description(text: str) -> Optional[dict]:
    """Parse a raw job description text into structured fields.

    Returns a dict with keys:
        title, company, skills (list[str]), experience_level (str or None),
        salary_min (int or None), salary_max (int or None),
        location (str or None), responsibilities (list[str])

    Returns None if the input is empty or whitespace-only.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # --- Title ---
    title = _extract_title(text)

    # --- Company ---
    company = _extract_company(text)

    # --- Skills ---
    skills = _extract_skills(text)

    # --- Experience level ---
    experience_level = _extract_experience(text)

    # --- Salary range ---
    salary_min, salary_max = _extract_salary(text)

    # --- Location ---
    location = _extract_location(text)

    # --- Responsibilities ---
    responsibilities = _extract_responsibilities(text)

    return {
        "title": title,
        "company": company,
        "skills": skills,
        "experience_level": experience_level,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "location": location,
        "responsibilities": responsibilities,
    }


def _extract_title(text: str) -> str:
    """Extract the job title from the text."""
    # Look for "Job Title:" or "Position:" or "Role:" patterns
    patterns = [
        r"(?:job\s*title|position|role)\s*[:]\s*(.+)",
        r"^(.+?)\s*$",  # first line as fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return ""


def _extract_company(text: str) -> str:
    """Extract the company name from the text."""
    patterns = [
        r"(?:company|at|by)\s*[:]\s*(.+)",
        r"(?:company|at|by)\s+(.+?)(?:\s*[,;]|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _extract_skills(text: str) -> list[str]:
    """Extract skills from the text using section headers and patterns."""
    skills: list[str] = []

    # Look for skills/requirements/must-have sections
    section_patterns = [
        r"(?:skills|requirements|must\s*have|qualifications)\s*[:]\s*\n?(.*?)(?=\n\s*\n|\n\s*[A-Z][a-z]+:|$)",
    ]
    for pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            section = match.group(1)
            # Extract comma-separated or line-separated items
            items = re.split(r"[,\n;]", section)
            for item in items:
                item = item.strip().strip("-").strip("*").strip()
                if item and len(item) > 1:
                    skills.append(item)

    # If no skills found in sections, try to find capitalized words after skill keywords
    if not skills:
        keyword_patterns = [
            r"(?:skills|requirements|must\s*have)\s*[:]\s*(.+)",
        ]
        for pattern in keyword_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                line = match.group(1)
                # Extract capitalized words
                words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", line)
                skills.extend(words)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_skills: list[str] = []
    for skill in skills:
        lower = skill.lower()
        if lower not in seen:
            seen.add(lower)
            unique_skills.append(skill)

    return unique_skills


def _extract_experience(text: str) -> Optional[str]:
    """Extract experience level from the text."""
    patterns = [
        r"(?:experience|years?\s*of)\s*[:]\s*(.+?)(?:\s*[,;]|$)",
        r"(\d+\+?\s*(?:years?|yrs?))",
        r"(entry\s*[- ]?level|junior|mid\s*[- ]?level|senior|lead|principal|staff|director|vp|c\s*[- ]?suite)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
    return None


def _extract_salary(text: str) -> tuple[Optional[int], Optional[int]]:
    """Extract salary range from the text."""
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None

    # Pattern for "$Xk-$Yk" or "$Xk - $Yk"
    range_pattern = r"\$([\d,]+)k?\s*[-–]\s*\$?([\d,]+)k?"
    match = re.search(range_pattern, text)
    if match:
        low = match.group(1).replace(",", "")
        high = match.group(2).replace(",", "")
        # If values are < 1000, assume they're in thousands
        if int(low) < 1000 and int(high) < 1000:
            salary_min = int(low) * 1000
            salary_max = int(high) * 1000
        else:
            salary_min = int(low)
            salary_max = int(high)
        return salary_min, salary_max

    # Pattern for "$X,XXX" or "$XXXXX"
    single_pattern = r"\$([\d,]+)"
    match = re.search(single_pattern, text)
    if match:
        value = int(match.group(1).replace(",", ""))
        if value > 1000:
            salary_min = value
            salary_max = value
        return salary_min, salary_max

    return None, None


def _extract_location(text: str) -> Optional[str]:
    """Extract location from the text."""
    patterns = [
        r"(?:location|place|where)\s*[:]\s*(.+?)(?:\s*[,;]|$)",
        r"(remote|onsite|hybrid)\s*(?:work)?",
        r"([A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+)+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_responsibilities(text: str) -> list[str]:
    """Extract responsibilities from the text."""
    responsibilities: list[str] = []

    # Look for "Responsibilities:" or "What you'll do:" sections
    section_patterns = [
        r"(?:responsibilities|what\s*you'll?\s*do|key\s*responsibilities)\s*[:]\s*\n?(.*?)(?=\n\s*\n|\n\s*[A-Z][a-z]+:|$)",
    ]
    for pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            section = match.group(1)
            # Split by bullet points or newlines
            items = re.split(r"[\n•*•]", section)
            for item in items:
                item = item.strip().strip("-").strip("*").strip()
                if item and len(item) > 10:
                    responsibilities.append(item)

    return responsibilities
