"""Proposal template engine for the Fiverr Job Automation Tool."""

import os
import re
from typing import Dict, List, Optional

import yaml

from .models import JobOpportunity


class ProposalEngine:
    """Template-based proposal generator that fills in job-specific variables
    into configurable proposal templates.

    Supported variables:
        {client_name}, {job_title}, {job_description}, {budget},
        {keywords}, {seller_name}, {custom_message}
    """

    DEFAULT_TEMPLATES = {
        "professional": (
            "Dear {client_name},\n\n"
            "I am writing to express my interest in your project: {job_title}.\n\n"
            "With my expertise in {keywords}, I am confident I can deliver "
            "high-quality results for your needs. I have reviewed your project "
            "description and believe my skills align well with what you are looking for.\n\n"
            "{job_description}\n\n"
            "Budget: {budget}\n\n"
            "{custom_message}\n\n"
            "I look forward to discussing how I can help you achieve your goals.\n\n"
            "Best regards,\n"
            "[Your Name]"
        ),
        "friendly": (
            "Hi {client_name}!\n\n"
            "I saw your project \"{job_title}\" and I'd love to help!\n\n"
            "I have experience with {keywords} and can deliver great results "
            "within your budget of {budget}.\n\n"
            "{job_description}\n\n"
            "{custom_message}\n\n"
            "Let's chat about how we can work together!\n\n"
            "Cheers,\n"
            "[Your Name]"
        ),
        "short": (
            "Hi {client_name},\n\n"
            "I can help with \"{job_title}\". "
            "Expertise in {keywords}. Budget: {budget}.\n\n"
            "{job_description}\n\n"
            "Best,\n"
            "[Your Name]"
        ),
    }

    def __init__(self, custom_templates: Optional[Dict[str, str]] = None):
        """Initialize the ProposalEngine.

        Args:
            custom_templates: Optional dictionary of custom templates.
        """
        self._templates = dict(self.DEFAULT_TEMPLATES)
        if custom_templates:
            self._templates.update(custom_templates)

    def load_templates(self, template_dict: Dict[str, str]) -> None:
        """Load or update templates from a dictionary.

        Args:
            template_dict: Mapping of template_name to template_string.
        """
        self._templates.update(template_dict)

    def load_templates_from_file(self, filepath: str) -> None:
        """Load templates from a YAML file.

        Args:
            filepath: Path to the YAML file containing templates.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file contains invalid YAML.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Template file not found: {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in template file: {e}")

        if not isinstance(data, dict) or "templates" not in data:
            raise ValueError("Invalid YAML format: expected 'templates' key")

        self._templates.update(data["templates"])

    def get_available_templates(self) -> List[str]:
        """Return a list of available template names.

        Returns:
            List of template names.
        """
        return list(self._templates.keys())

    def generate(
        self,
        job: JobOpportunity,
        template_name: str,
        custom_message: str = "",
        seller_name: str = "",
    ) -> str:
        """Generate a proposal using the specified template.

        Args:
            job: The job opportunity to generate a proposal for.
            template_name: Name of the template to use.
            custom_message: Optional custom message to include.
            seller_name: Optional seller name to include.

        Returns:
            Generated proposal string.

        Raises:
            ValueError: If the template name is not found.
        """
        if template_name not in self._templates:
            raise ValueError(f"Unknown template: {template_name}")

        template = self._templates[template_name]

        # Prepare variables
        client_name = job.buyer_name or "Client"
        job_title = job.title or "Untitled Project"
        job_description = job.description or "No description provided"
        budget = f"{job.budget_min} - {job.budget_max}" if job.has_budget else "Negotiable"
        keywords = ", ".join(job.keywords) if job.has_keywords else "relevant skills"
        custom_msg = custom_message or "I look forward to discussing this project with you."

        # Replace variables in template
        variables = {
            "client_name": client_name,
            "job_title": job_title,
            "job_description": job_description,
            "budget": budget,
            "keywords": keywords,
            "custom_message": custom_msg,
            "seller_name": seller_name,
        }

        proposal = template
        for var_name, var_value in variables.items():
            placeholder = "{" + var_name + "}"
            proposal = proposal.replace(placeholder, str(var_value))

        return proposal

    def validate_template(self, template_name: str) -> bool:
        """Validate that a template exists and is properly formatted.

        Args:
            template_name: Name of the template to validate.

        Returns:
            True if the template is valid, False otherwise.
        """
        if template_name not in self._templates:
            return False

        template = self._templates[template_name]
        # Check for unclosed braces
        if template.count("{") != template.count("}"):
            return False

        return True
