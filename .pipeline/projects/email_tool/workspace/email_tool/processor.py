"""Processor module for the main email processing pipeline."""

import os
from datetime import datetime
from typing import List, Optional
from email_tool.models import Email, Rule, RuleMatch, ActionType
from email_tool.parser import EmailParser
from email_tool.matcher import RuleMatcher
from email_tool.dispatcher import Dispatcher, ActionBuilder, ActionExecutor


class EmailProcessor:
    """
    Main processor for email processing pipeline.
    
    Pipeline stages:
    1. Parse email from source
    2. Match against rules
    3. Dispatch actions based on matches
    """
    
    def __init__(
        self,
        base_path: str = "./archive",
        dry_run: bool = False,
        collision_strategy: str = "rename",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the email processor.
        
        Args:
            base_path: Base directory for all operations.
            dry_run: If True, only simulate actions without making changes.
            collision_strategy: Strategy for handling filename collisions.
            max_retries: Maximum retry attempts for actions.
            retry_delay: Delay between retries in seconds.
        """
        self.base_path = base_path
        self.dry_run = dry_run
        self.collision_strategy = collision_strategy
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize components
        self.parser = EmailParser()
        self.matcher = RuleMatcher()
        self.dispatcher = Dispatcher(
            base_path=self.base_path,
            dry_run=dry_run,
            collision_strategy=collision_strategy
        )
        self.executor = ActionExecutor(
            dispatcher=self.dispatcher,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        # Processing statistics
        self.stats = {
            "total_processed": 0,
            "total_matched": 0,
            "total_failed": 0,
            "by_rule": {},
            "by_action": {}
        }
        
        # Store rules and actions for monitoring
        self.rules: List[Rule] = []
        self.actions: List[tuple] = []
    
    def process_email(
        self,
        email_source: str,
        rules: List[Rule],
        actions: List[tuple]
    ) -> dict:
        """
        Process a single email through the pipeline.
        
        Args:
            email_source: Path to email file or email content.
            rules: List of rules to match against.
            actions: List of (action_type, action_params) tuples.
        
        Returns:
            Dictionary with processing results.
        """
        result = {
            "success": False,
            "email_id": None,
            "matches": [],
            "actions_performed": [],
            "errors": []
        }
        
        try:
            # Stage 1: Parse email
            email = self.parser.parse(email_source)
            result["email_id"] = email.id
            
            # Stage 2: Match against rules
            rule_matches = self.matcher.match(email, rules)
            result["matches"] = [
                {
                    "rule_name": m.rule_name,
                    "match_type": m.match_type,
                    "priority": m.priority
                }
                for m in rule_matches
            ]
            
            # Update statistics
            self.stats["total_processed"] += 1
            if rule_matches:
                self.stats["total_matched"] += 1
                for match in rule_matches:
                    rule_name = match.rule_name
                    self.stats["by_rule"][rule_name] = \
                        self.stats["by_rule"].get(rule_name, 0) + 1
            
            # Stage 3: Dispatch actions for each match
            for rule_match in rule_matches:
                action_results = self.executor.execute(
                    email=email,
                    rule_match=rule_match,
                    actions=actions
                )
                result["actions_performed"].extend(action_results)
                
                # Update action statistics
                for action_result in action_results:
                    action_type = action_result.get("action", "UNKNOWN")
                    self.stats["by_action"][action_type] = \
                        self.stats["by_action"].get(action_type, 0) + 1
            
            # Mark as successful if at least one action was performed
            if result["actions_performed"]:
                result["success"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
            self.stats["total_failed"] += 1
        
        return result
    
    def process_batch(
        self,
        email_sources: List[str],
        rules: List[Rule],
        actions: List[tuple]
    ) -> List[dict]:
        """
        Process multiple emails through the pipeline.
        
        Args:
            email_sources: List of email file paths or content.
            rules: List of rules to match against.
            actions: List of (action_type, action_params) tuples.
        
        Returns:
            List of processing results.
        """
        results = []
        
        for source in email_sources:
            result = self.process_email(source, rules, actions)
            results.append(result)
        
        return results
    
    def process_directory(
        self,
        source_dir: str,
        rules: List[Rule],
        actions: List[tuple],
        file_pattern: str = "*.eml"
    ) -> List[dict]:
        """
        Process all emails in a directory.
        
        Args:
            source_dir: Directory containing email files.
            rules: List of rules to match against.
            actions: List of (action_type, action_params) tuples.
            file_pattern: File pattern to match (e.g., "*.eml").
        
        Returns:
            List of processing results.
        """
        import glob
        
        email_files = glob.glob(os.path.join(source_dir, file_pattern))
        
        return self.process_batch(email_files, rules, actions)
    
    def get_stats(self) -> dict:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with processing statistics.
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = {
            "total_processed": 0,
            "total_matched": 0,
            "total_failed": 0,
            "by_rule": {},
            "by_action": {}
        }
    
    def get_dispatcher_log(self) -> List[dict]:
        """
        Get the dispatcher operation log.
        
        Returns:
            List of operation results.
        """
        return self.dispatcher.get_operations_log()
    
    def clear_dispatcher_log(self):
        """Clear the dispatcher operation log."""
        self.dispatcher.clear_operations_log()


class PipelineBuilder:
    """
    Builder for constructing email processing pipelines.
    """
    
    def __init__(self):
        """Initialize the pipeline builder."""
        self.base_path = "./archive"
        self.dry_run = False
        self.collision_strategy = "rename"
        self.max_retries = 3
        self.retry_delay = 1.0
        self.rules: List[Rule] = []
        self.actions: List[tuple] = []
    
    def set_base_path(self, path: str) -> 'PipelineBuilder':
        """Set the base path for operations."""
        self.base_path = path
        return self
    
    def set_base_path_absolute(self, path: str) -> 'PipelineBuilder':
        """Set the base path for operations (absolute path)."""
        import os
        self.base_path = os.path.abspath(path)
        return self
    
    def set_dry_run(self, dry_run: bool) -> 'PipelineBuilder':
        """Set dry run mode."""
        self.dry_run = dry_run
        return self
    
    def set_collision_strategy(self, strategy: str) -> 'PipelineBuilder':
        """Set collision handling strategy."""
        self.collision_strategy = strategy
        return self
    
    def set_retry_config(
        self,
        max_retries: int,
        retry_delay: float
    ) -> 'PipelineBuilder':
        """Set retry configuration."""
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        return self
    
    def add_rule(self, rule: Rule) -> 'PipelineBuilder':
        """Add a rule to the pipeline."""
        self.rules.append(rule)
        return self
    
    def add_rules(self, rules: List[Rule]) -> 'PipelineBuilder':
        """Add multiple rules to the pipeline."""
        self.rules.extend(rules)
        return self
    
    def add_action(
        self,
        action_type: ActionType,
        action_params: dict
    ) -> 'PipelineBuilder':
        """
        Add an action to the pipeline.
        
        Args:
            action_type: The type of action to perform.
            action_params: Parameters for the action.
        
        Returns:
            Self for chaining.
        """
        self.actions.append((action_type, action_params))
        return self
    
    def add_actions(self, actions: List[tuple]) -> 'PipelineBuilder':
        """Add multiple actions to the pipeline."""
        self.actions.extend(actions)
        return self
    
    def build(self) -> EmailProcessor:
        """
        Build the email processor.
        
        Returns:
            Configured EmailProcessor instance.
        """
        processor = EmailProcessor(
            base_path=self.base_path,
            dry_run=self.dry_run,
            collision_strategy=self.collision_strategy,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay
        )
        processor.rules = self.rules.copy()
        processor.actions = self.actions.copy()
        return processor


class PipelineExecutor:
    """
    Executes email processing pipelines with progress tracking.
    """
    
    def __init__(
        self,
        processor: EmailProcessor,
        progress_callback=None
    ):
        """
        Initialize the pipeline executor.
        
        Args:
            processor: The email processor to use.
            progress_callback: Optional callback function for progress updates.
        """
        self.processor = processor
        self.progress_callback = progress_callback
    
    def execute(
        self,
        email_sources: List[str],
        rules: List[Rule],
        actions: List[tuple]
    ) -> List[dict]:
        """
        Execute the pipeline with progress tracking.
        
        Args:
            email_sources: List of email sources to process.
            rules: List of rules to match against.
            actions: List of actions to perform.
        
        Returns:
            List of processing results.
        """
        results = []
        total = len(email_sources)
        
        for i, source in enumerate(email_sources):
            result = self.processor.process_email(source, rules, actions)
            results.append(result)
            
            # Call progress callback if provided
            if self.progress_callback:
                self.progress_callback(i + 1, total, result)
        
        return results
    
    def execute_directory(
        self,
        source_dir: str,
        rules: List[Rule],
        actions: List[tuple],
        file_pattern: str = "*.eml"
    ) -> List[dict]:
        """
        Execute the pipeline on a directory of emails.
        
        Args:
            source_dir: Directory containing email files.
            rules: List of rules to match against.
            actions: List of actions to perform.
            file_pattern: File pattern to match.
        
        Returns:
            List of processing results.
        """
        import glob
        
        email_files = glob.glob(os.path.join(source_dir, file_pattern))
        
        return self.execute(email_files, rules, actions)


class PipelineMonitor:
    """
    Monitors and reports on pipeline execution.
    """
    
    def __init__(self, processor: EmailProcessor):
        """
        Initialize the pipeline monitor.
        
        Args:
            processor: The email processor to monitor.
        """
        self.processor = processor
        self.stats = {}
    
    def update_stats(self):
        """Update statistics from the processor."""
        self.stats = self.processor.get_stats()
    
    def get_status(self) -> dict:
        """
        Get current pipeline status.
        
        Returns:
            Dictionary with status information.
        """
        self.update_stats()
        
        return {
            "total_processed": self.stats["total_processed"],
            "total_matched": self.stats["total_matched"],
            "total_failed": self.stats["total_failed"],
            "success_rate": self._calculate_success_rate(self.stats),
            "by_rule": self.stats["by_rule"],
            "by_action": self.stats["by_action"],
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_success_rate(self, stats: dict) -> float:
        """Calculate success rate from statistics."""
        total = stats["total_processed"]
        if total == 0:
            return 0.0
        return (stats["total_matched"] / total) * 100
    
    def get_rule_performance(self) -> dict:
        """
        Get performance metrics for each rule.
        
        Returns:
            Dictionary with rule performance metrics.
        """
        self.update_stats()
        
        performance = {}
        for rule_name, count in self.stats["by_rule"].items():
            performance[rule_name] = {
                "matches": count,
                "percentage": (count / max(self.stats["total_matched"], 1)) * 100
            }
        
        return performance
    
    def get_action_performance(self) -> dict:
        """
        Get performance metrics for each action type.
        
        Returns:
            Dictionary with action performance metrics.
        """
        self.update_stats()
        
        performance = {}
        for action_type, count in self.stats["by_action"].items():
            performance[action_type] = {
                "count": count,
                "percentage": (count / max(self.stats["total_matched"], 1)) * 100
            }
        
        return performance


class PipelineConfig:
    """
    Configuration for email processing pipeline.
    """
    
    def __init__(
        self,
        base_path: str = "./archive",
        dry_run: bool = False,
        collision_strategy: str = "rename",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize pipeline configuration.
        
        Args:
            base_path: Base directory for operations.
            dry_run: Enable dry run mode.
            collision_strategy: Strategy for filename collisions.
            max_retries: Maximum retry attempts.
            retry_delay: Delay between retries.
        """
        self.base_path = base_path
        self.dry_run = dry_run
        self.collision_strategy = collision_strategy
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def to_processor(self) -> EmailProcessor:
        """
        Convert configuration to EmailProcessor instance.
        
        Returns:
            Configured EmailProcessor.
        """
        return EmailProcessor(
            base_path=self.base_path,
            dry_run=self.dry_run,
            collision_strategy=self.collision_strategy,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay
        )
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'PipelineConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values.
        
        Returns:
            PipelineConfig instance.
        """
        return cls(
            base_path=config_dict.get("base_path", "./archive"),
            dry_run=config_dict.get("dry_run", False),
            collision_strategy=config_dict.get("collision_strategy", "rename"),
            max_retries=config_dict.get("max_retries", 3),
            retry_delay=config_dict.get("retry_delay", 1.0)
        )
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary with configuration values.
        """
        return {
            "base_path": self.base_path,
            "dry_run": self.dry_run,
            "collision_strategy": self.collision_strategy,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay
        }
