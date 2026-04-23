"""Job Automation Tool — parse job descriptions, match candidates, automate workflows."""

__version__ = "0.1.0"

from job_automation_tool.profile import Profile
from job_automation_tool.parser import parse_job_description
from job_automation_tool.matcher import match_profiles

__all__ = ["Profile", "parse_job_description", "match_profiles"]
