"""Dispatcher module for handling email actions."""

import os
import shutil
from datetime import datetime
from typing import Optional, List
from email_tool.models import Email, Rule, RuleMatch, ActionType
from email_tool.path_builder import PathBuilder
from email_tool.formatter import Formatter


class Dispatcher:
    """
    Dispatcher for handling email actions (move, file, label).
    
    Actions:
    - MOVE: Move email to destination directory
    - FILE: Save email to file system
    - LABEL: Apply labels/tags to email (metadata only)
    """
    
    def __init__(
        self,
        base_path: str = "./archive",
        dry_run: bool = False,
        collision_strategy: str = "rename"
    ):
        """
        Initialize the dispatcher.
        
        Args:
            base_path: Base directory for all operations.
            dry_run: If True, only simulate actions without making changes.
            collision_strategy: Strategy for handling filename collisions:
                - "rename": Auto-rename with timestamp
                - "number": Add number suffix (file_1, file_2)
                - "overwrite": Overwrite existing file
        """
        self.base_path = os.path.abspath(base_path)
        self.dry_run = dry_run
        self.collision_strategy = collision_strategy
        self.path_builder = PathBuilder()
        self.operations_log: List[dict] = []
    
    def handle_action(
        self,
        email: Email,
        rule_match: RuleMatch,
        action: ActionType,
        action_params: Optional[dict] = None
    ) -> dict:
        """
        Handle a single action for an email.
        
        Args:
            email: The email to process.
            rule_match: The matched rule information.
            action: The action type to perform.
            action_params: Optional parameters for the action.
        
        Returns:
            Dictionary with operation results.
        """
        action_params = action_params or {}
        
        if action == ActionType.MOVE:
            return self._handle_move(email, rule_match, action_params)
        elif action == ActionType.FILE:
            return self._handle_file(email, rule_match, action_params)
        elif action == ActionType.LABEL:
            return self._handle_label(email, rule_match, action_params)
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action}"
            }
    
    def dispatch(
        self,
        email: Email,
        rule_match: RuleMatch,
        action: ActionType,
        action_params: Optional[dict] = None
    ) -> dict:
        """
        Dispatch an action for an email (alias for handle_action).
        
        Args:
            email: The email to process.
            rule_match: The matched rule information.
            action: The action type to perform.
            action_params: Optional parameters for the action.
        
        Returns:
            Dictionary with operation results.
        """
        return self.handle_action(email, rule_match, action, action_params)
    
    def _handle_move(
        self,
        email: Email,
        rule_match: RuleMatch,
        action_params: dict
    ) -> dict:
        """Handle MOVE action."""
        # Determine destination directory
        dest_dir = action_params.get("destination", self.base_path)
        
        # Build path
        path_builder = PathBuilder()
        filename = path_builder.build_filename(
            email,
            extension="eml",
            rule=rule_match.rule
        )
        
        dest_path = os.path.join(dest_dir, filename)
        
        # Check for collision
        if os.path.exists(dest_path):
            dest_path = self._resolve_collision(dest_path)
        
        # Perform move
        if self.dry_run:
            result = {
                "action": "MOVE",
                "email_id": email.id,
                "from": "source",
                "to": dest_path,
                "dry_run": True,
                "success": True
            }
        else:
            try:
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Move file
                shutil.move(str(email.source_path), dest_path)
                
                result = {
                    "action": "MOVE",
                    "email_id": email.id,
                    "from": str(email.source_path),
                    "to": dest_path,
                    "dry_run": False,
                    "success": True
                }
            except Exception as e:
                result = {
                    "action": "MOVE",
                    "email_id": email.id,
                    "error": str(e),
                    "success": False
                }
        
        self.operations_log.append(result)
        return result
    
    def _handle_file(
        self,
        email: Email,
        rule_match: RuleMatch,
        action_params: dict
    ) -> dict:
        """Handle FILE action."""
        # Determine output format
        output_format = action_params.get("format", "eml")
        
        # Build path
        path_builder = PathBuilder()
        filename = path_builder.build_filename(
            email,
            extension=output_format,
            rule=rule_match.rule
        )
        
        dest_path = os.path.join(self.base_path, filename)
        
        # Check for collision
        if os.path.exists(dest_path):
            dest_path = self._resolve_collision(dest_path)
        
        # Perform file operation
        if self.dry_run:
            result = {
                "action": "FILE",
                "email_id": email.id,
                "format": output_format,
                "to": dest_path,
                "dry_run": True,
                "success": True
            }
        else:
            try:
                # Ensure destination directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Create formatter and save
                formatter = Formatter(email)
                
                if output_format == "pdf":
                    formatter.to_pdf(dest_path)
                else:
                    content = formatter.format(output_format)
                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                result = {
                    "action": "FILE",
                    "email_id": email.id,
                    "format": output_format,
                    "to": dest_path,
                    "dry_run": False,
                    "success": True
                }
            except Exception as e:
                result = {
                    "action": "FILE",
                    "email_id": email.id,
                    "error": str(e),
                    "success": False
                }
        
        self.operations_log.append(result)
        return result
    
    def _handle_label(
        self,
        email: Email,
        rule_match: RuleMatch,
        action_params: dict
    ) -> dict:
        """Handle LABEL action (metadata only, no file operations)."""
        # Get labels from rule or action params
        labels = action_params.get("labels", [])
        
        # Apply labels to email metadata (merge with rule labels)
        all_labels = list(set(email.labels + labels + rule_match.labels))
        email.labels = all_labels
        
        result = {
            "action": "LABEL",
            "email_id": email.id,
            "labels": labels,
            "dry_run": self.dry_run,
            "success": True
        }
        
        self.operations_log.append(result)
        return result
    
    def _resolve_collision(self, existing_path: str) -> str:
        """
        Resolve filename collision based on strategy.
        
        Args:
            existing_path: Path of existing file.
        
        Returns:
            New path that doesn't conflict.
        """
        base, ext = os.path.splitext(existing_path)
        
        if self.collision_strategy == "overwrite":
            return existing_path
        
        elif self.collision_strategy == "number":
            counter = 1
            while True:
                new_path = f"{base}_{counter}{ext}"
                if not os.path.exists(new_path):
                    return new_path
                counter += 1
        
        elif self.collision_strategy == "rename":
            # Add timestamp after extension
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_path = f"{base}{ext}_{timestamp}{ext}"
            return new_path
        
        else:
            # Default to number strategy
            return self._resolve_collision(existing_path)
    
    def handle_multiple_actions(
        self,
        email: Email,
        rule_match: RuleMatch,
        actions: List[tuple]
    ) -> List[dict]:
        """
        Handle multiple actions for an email.
        
        Args:
            email: The email to process.
            rule_match: The matched rule information.
            actions: List of (action_type, action_params) tuples.
        
        Returns:
            List of operation results.
        """
        results = []
        
        for action_type, action_params in actions:
            result = self.handle_action(
                email=email,
                rule_match=rule_match,
                action=action_type,
                action_params=action_params
            )
            results.append(result)
        
        return results
    
    def get_operations_log(self) -> List[dict]:
        """
        Get the log of all operations performed.
        
        Returns:
            List of operation result dictionaries.
        """
        return self.operations_log.copy()
    
    def clear_operations_log(self):
        """Clear the operations log."""
        self.operations_log = []
    
    def get_summary(self) -> dict:
        """
        Get a summary of all operations.
        
        Returns:
            Dictionary with operation statistics.
        """
        summary = {
            "total_operations": len(self.operations_log),
            "successful_operations": 0,
            "failed_operations": 0,
            "dry_run": self.dry_run,
            "by_action": {},
            "by_email": {}
        }
        
        for op in self.operations_log:
            if op.get("success"):
                summary["successful_operations"] += 1
            else:
                summary["failed_operations"] += 1
            
            # Count by action type
            action = op.get("action", "UNKNOWN")
            summary["by_action"][action] = summary["by_action"].get(action, 0) + 1
            
            # Count by email
            email_id = op.get("email_id", "UNKNOWN")
            summary["by_email"][email_id] = summary["by_email"].get(email_id, 0) + 1
        
        return summary


class ActionBuilder:
    """
    Builder for constructing action configurations.
    """
    
    def __init__(self):
        """Initialize the action builder."""
        self.actions: List[tuple] = []
    
    def add_move(
        self,
        destination: str,
        priority: int = 1
    ) -> 'ActionBuilder':
        """
        Add a MOVE action.
        
        Args:
            destination: Destination directory path.
            priority: Action priority (higher = executed first).
        
        Returns:
            Self for chaining.
        """
        self.actions.append((ActionType.MOVE, {"destination": destination, "priority": priority}))
        return self
    
    def add_file(
        self,
        format: str = "eml",
        priority: int = 2
    ) -> 'ActionBuilder':
        """
        Add a FILE action.
        
        Args:
            format: Output format (eml, md, pdf).
            priority: Action priority.
        
        Returns:
            Self for chaining.
        """
        self.actions.append((ActionType.FILE, {"format": format, "priority": priority}))
        return self
    
    def add_label(
        self,
        labels: List[str],
        priority: int = 3
    ) -> 'ActionBuilder':
        """
        Add a LABEL action.
        
        Args:
            labels: List of label names to apply.
            priority: Action priority.
        
        Returns:
            Self for chaining.
        """
        self.actions.append((ActionType.LABEL, {"labels": labels, "priority": priority}))
        return self
    
    def build(self) -> List[tuple]:
        """
        Build the action list.
        
        Returns:
            List of (action_type, action_params) tuples.
        """
        # Sort by priority (higher first)
        self.actions.sort(key=lambda x: x[1].get("priority", 0), reverse=True)
        
        # Remove priority from params
        return [(action, {k: v for k, v in params.items() if k != "priority"})
                for action, params in self.actions]


# Alias for backward compatibility
ActionDispatcher = Dispatcher


class ActionExecutor:
    """
    Executes actions with error handling and retry logic.
    """
    
    def __init__(
        self,
        dispatcher: Dispatcher,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the action executor.
        
        Args:
            dispatcher: The dispatcher to use.
            max_retries: Maximum number of retry attempts.
            retry_delay: Delay between retries in seconds.
        """
        self.dispatcher = dispatcher
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def execute(
        self,
        email: Email,
        rule_match: RuleMatch,
        actions: List[tuple]
    ) -> List[dict]:
        """
        Execute actions with retry logic.
        
        Args:
            email: The email to process.
            rule_match: The matched rule information.
            actions: List of (action_type, action_params) tuples.
        
        Returns:
            List of operation results.
        """
        import time
        
        results = []
        
        for action_type, action_params in actions:
            attempt = 0
            last_error = None
            
            while attempt < self.max_retries:
                try:
                    result = self.dispatcher.handle_action(
                        email=email,
                        rule_match=rule_match,
                        action=action_type,
                        action_params=action_params
                    )
                    
                    if result.get("success"):
                        results.append(result)
                        break
                    else:
                        last_error = result.get("error")
                        attempt += 1
                        
                except Exception as e:
                    last_error = str(e)
                    attempt += 1
                
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
            
            if attempt >= self.max_retries:
                results.append({
                    "action": action_type.value,
                    "email_id": email.id,
                    "error": f"Failed after {self.max_retries} attempts: {last_error}",
                    "success": False
                })
        
        return results
