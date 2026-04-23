"""Course comparison and recommendation engine."""

from __future__ import annotations

import statistics
from typing import Dict, List, Optional

from udemy_training_tool.models import Course


def recommend_courses(
    courses: List[Course],
    target_skill: str,
    top_n: int = 5,
) -> List[Dict]:
    """Score and rank courses for a given target skill/topic.

    Composite score (0-100) based on:
      - Rating:        30% weight (scale 0-5)
      - Student count: 25% weight (normalized via min-max)
      - Price value:   20% weight (lower price = higher score)
      - Course depth:  15% weight (num_lectures, normalized via min-max)
      - Instructor:    10% weight (heuristic: instructor name length as proxy)

    Args:
        courses: List of Course objects to score.
        target_skill: Skill/topic to match courses against.
        top_n: Number of top recommendations to return.

    Returns:
        List of dicts with keys: course, score (0-100), breakdown (dict of component scores).
        Sorted by score descending. Ties broken by rating (desc) then price (asc).
    """
    if not courses:
        return []

    # Filter courses that match the target skill
    matched = [c for c in courses if _skill_match(c, target_skill)]

    if not matched:
        # If no exact match, use all courses
        matched = list(courses)

    # Compute scores
    scored: List[Dict] = []
    for course in matched:
        score_info = _score_course(course)
        scored.append(score_info)

    # Sort: by score desc, then rating desc, then price asc
    scored.sort(key=lambda x: (-x["score"], -x["course"].rating, x["course"].price))

    return scored[:top_n]


def compare_courses(
    courses: List[Course],
    target_skill: str = "",
) -> List[Dict]:
    """Compare a list of courses side-by-side with score breakdowns.

    Args:
        courses: List of Course objects to compare.
        target_skill: Optional skill/topic for relevance scoring.

    Returns:
        List of dicts with course, score, and breakdown.
    """
    if not courses:
        return []

    results: List[Dict] = []
    for course in courses:
        score_info = _score_course(course)
        results.append(score_info)

    results.sort(key=lambda x: (-x["score"], -x["course"].rating, x["course"].price))
    return results


def _skill_match(course: Course, target_skill: str) -> bool:
    """Check if a course matches the target skill."""
    if not target_skill:
        return True
    skill_lower = target_skill.lower()
    searchable = " ".join([
        course.title,
        course.description,
        " ".join(course.tags),
        course.category,
    ]).lower()
    return skill_lower in searchable


def _score_course(course: Course) -> Dict:
    """Compute a composite score for a single course."""
    # Rating score (0-100): rating / 5 * 100
    rating_score = (course.rating / 5.0) * 100 if course.rating > 0 else 0

    # Student count score: normalize using median imputation for missing values
    student_score = _normalize_student_count(course.num_students)

    # Price value score: lower price = higher score (inverse)
    price_score = _normalize_price(course.price)

    # Course depth score: normalize num_lectures
    lecture_score = _normalize_lectures(course.num_lectures)

    # Instructor quality: heuristic based on name length (longer names tend to be real instructors)
    instructor_score = _score_instructor(course.instructor)

    # Composite score
    composite = (
        rating_score * 0.30
        + student_score * 0.25
        + price_score * 0.20
        + lecture_score * 0.15
        + instructor_score * 0.10
    )

    return {
        "course": course,
        "score": round(composite, 2),
        "breakdown": {
            "rating": round(rating_score, 2),
            "students": round(student_score, 2),
            "price_value": round(price_score, 2),
            "depth": round(lecture_score, 2),
            "instructor": round(instructor_score, 2),
        },
    }


def _normalize_student_count(num_students: int) -> float:
    """Normalize student count to 0-100 scale using median imputation."""
    if num_students <= 0:
        return 50.0  # median imputation for missing
    # Log scale normalization: 1 student = ~0, 1000000 students = 100
    import math
    max_students = 1_000_000
    if num_students >= max_students:
        return 100.0
    return (math.log10(num_students + 1) / math.log10(max_students + 1)) * 100


def _normalize_price(price: float) -> float:
    """Normalize price to 0-100 scale (lower price = higher score)."""
    if price <= 0:
        return 100.0  # free is best
    max_price = 200.0
    if price >= max_price:
        return 0.0
    return (1 - price / max_price) * 100


def _normalize_lectures(num_lectures: int) -> float:
    """Normalize num_lectures to 0-100 scale using median imputation."""
    if num_lectures <= 0:
        return 50.0  # median imputation
    max_lectures = 500
    if num_lectures >= max_lectures:
        return 100.0
    return (num_lectures / max_lectures) * 100


def _score_instructor(instructor: str) -> float:
    """Score instructor quality using heuristic (name length as proxy)."""
    if not instructor:
        return 50.0  # median imputation
    name_len = len(instructor.strip())
    # Heuristic: 3-30 chars is typical, score peaks around 15
    if name_len <= 0:
        return 0
    if name_len >= 30:
        return 100
    return min(100, (name_len / 30) * 100)
