"""Tests for the processor module."""

import os
import pytest
from datetime import datetime
from email_tool.models import Email, Rule, RuleType, RuleMatch, ActionType
from email_tool.processor import (
    EmailProcessor,
    PipelineBuilder,
    PipelineExecutor,
    PipelineMonitor,
    PipelineConfig
)
from email_tool.parser import EmailParser


class TestEmailProcessor:
    """Test cases for EmailProcessor class."""
    
    @pytest.fixture
    def sample_email(self):
        """Create a sample email for testing."""
        return Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@test.com"],
            subject="Test Email",
            date=datetime(2024, 3, 15, 10, 30, 0),
            body_plain="This is a test email body.",
            attachments=[],
            raw_headers={},
            labels=[],
            source_path="/tmp/test.eml"
        )
    
    @pytest.fixture
    def sample_rules(self):
        """Create sample rules for testing."""
        return [
            Rule(
                id="test_rule_001",
                name="test_rule_1",
                rule_type=RuleType.SUBJECT_EXACT,
                pattern="test",
                priority=50,
                category="general",
                labels=["important"]
            ),
            Rule(
                id="test_rule_001",
                name="test_rule_2",
                rule_type=RuleType.FROM_EXACT,
                pattern="sender@example.com",
                priority=40,
                category="sender",
                labels=["trusted"]
            )
        ]
    
    @pytest.fixture
    def sample_actions(self):
        """Create sample actions for testing."""
        return [
            (ActionType.MOVE, {"destination": "/tmp/archive"}),
            (ActionType.FILE, {"format": "md"}),
            (ActionType.LABEL, {"labels": ["processed"]})
        ]
    
    @pytest.fixture
    def processor(self, tmp_path):
        """Create a configured processor for testing."""
        return EmailProcessor(
            base_path=str(tmp_path),
            dry_run=True
        )
    
    def test_process_email_success(self, processor, sample_email, sample_rules, sample_actions):
        """Test successful email processing."""
        # Save email to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            result = processor.process_email(temp_file, sample_rules, sample_actions)
            
            assert result["success"] is True
            assert result["email_id"] == sample_email.id
            assert len(result["matches"]) == 2
            assert len(result["actions_performed"]) == 3
        finally:
            os.unlink(temp_file)
    
    def test_process_email_no_matches(self, processor, sample_email, sample_actions):
        """Test email processing with no rule matches."""
        # Save email to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            # Use a rule that won't match
            no_match_rules = [
                Rule(
                    id="test_rule_001",
                name="no_match_rule",
                    rule_type=RuleType.SUBJECT_EXACT,
                    pattern="nonexistent",
                    priority=50,
                    category="general",
                    labels=[]
                )
            ]
            
            result = processor.process_email(temp_file, no_match_rules, sample_actions)
            
            assert result["success"] is False
            assert len(result["matches"]) == 0
            assert len(result["actions_performed"]) == 0
        finally:
            os.unlink(temp_file)
    
    def test_process_email_parsing_error(self, processor, sample_rules, sample_actions):
        """Test email processing with parsing error."""
        # Use invalid email content
        result = processor.process_email("invalid email content", sample_rules, sample_actions)
        
        assert result["success"] is False
        assert len(result["errors"]) > 0
    
    def test_process_batch(self, processor, sample_email, sample_rules, sample_actions):
        """Test processing multiple emails."""
        # Save emails to temp files
        temp_files = []
        for i in range(3):
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
                f.write(sample_email.to_eml())
                temp_files.append(f.name)
        
        try:
            results = processor.process_batch(temp_files, sample_rules, sample_actions)
            
            assert len(results) == 3
            assert all(r["success"] for r in results)
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_process_directory(self, processor, sample_email, sample_rules, sample_actions, tmp_path):
        """Test processing emails from a directory."""
        # Create test directory with emails
        test_dir = tmp_path / "test_emails"
        test_dir.mkdir()
        
        for i in range(3):
            email_file = test_dir / f"email_{i}.eml"
            email_file.write_text(sample_email.to_eml())
        
        results = processor.process_directory(
            str(test_dir),
            sample_rules,
            sample_actions
        )
        
        assert len(results) == 3
        assert all(r["success"] for r in results)
    
    def test_get_stats(self, processor, sample_email, sample_rules, sample_actions):
        """Test getting processing statistics."""
        # Save email to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            processor.process_email(temp_file, sample_rules, sample_actions)
            
            stats = processor.get_stats()
            
            assert stats["total_processed"] == 1
            assert stats["total_matched"] == 1
            assert stats["total_failed"] == 0
            assert "test_rule_1" in stats["by_rule"]
            assert "MOVE" in stats["by_action"]
        finally:
            os.unlink(temp_file)
    
    def test_reset_stats(self, processor, sample_email, sample_rules, sample_actions):
        """Test resetting statistics."""
        # Process an email
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            processor.process_email(temp_file, sample_rules, sample_actions)
            
            # Reset stats
            processor.reset_stats()
            
            stats = processor.get_stats()
            assert stats["total_processed"] == 0
            assert stats["total_matched"] == 0
        finally:
            os.unlink(temp_file)
    
    def test_get_dispatcher_log(self, processor, sample_email, sample_rules, sample_actions):
        """Test getting dispatcher operation log."""
        # Save email to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            processor.process_email(temp_file, sample_rules, sample_actions)
            
            log = processor.get_dispatcher_log()
            
            assert len(log) > 0
            assert log[0]["action"] in ["MOVE", "FILE", "LABEL"]
        finally:
            os.unlink(temp_file)
    
    def test_clear_dispatcher_log(self, processor, sample_email, sample_rules, sample_actions):
        """Test clearing dispatcher operation log."""
        # Save email to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            processor.process_email(temp_file, sample_rules, sample_actions)
            
            # Clear log
            processor.clear_dispatcher_log()
            
            log = processor.get_dispatcher_log()
            assert len(log) == 0
        finally:
            os.unlink(temp_file)


class TestPipelineBuilder:
    """Test cases for PipelineBuilder class."""
    
    def test_build_default_config(self):
        """Test building processor with default configuration."""
        builder = PipelineBuilder()
        processor = builder.build()
        
        assert processor.base_path == "./archive"
        assert processor.dry_run is False
        assert processor.collision_strategy == "rename"
        assert processor.max_retries == 3
        assert processor.retry_delay == 1.0
    
    def test_build_custom_config(self):
        """Test building processor with custom configuration."""
        builder = PipelineBuilder()
        processor = builder.set_base_path("/custom/path") \
            .set_dry_run(True) \
            .set_collision_strategy("number") \
            .set_retry_config(max_retries=5, retry_delay=2.0) \
            .build()
        
        assert processor.base_path == "/custom/path"
        assert processor.dry_run is True
        assert processor.collision_strategy == "number"
        assert processor.max_retries == 5
        assert processor.retry_delay == 2.0
    
    def test_add_rule(self):
        """Test adding rules to pipeline."""
        builder = PipelineBuilder()
        rule = Rule(
            id="test_rule_001",
                name="test_rule",
            rule_type=RuleType.SUBJECT_EXACT,
            pattern="test",
            priority=50,
            category="general",
            labels=[]
        )
        
        builder.add_rule(rule)
        processor = builder.build()
        
        # Rules are stored in builder, not processor
        # This test verifies the builder pattern works
        assert builder.rules == [rule]
    
    def test_add_rules(self):
        """Test adding multiple rules to pipeline."""
        builder = PipelineBuilder()
        rules = [
            Rule(
                id="test_rule_001",
                name="rule_1",
                rule_type=RuleType.SUBJECT_EXACT,
                pattern="test1",
                priority=50,
                category="general",
                labels=[]
            ),
            Rule(
                id="test_rule_001",
                name="rule_2",
                rule_type=RuleType.SUBJECT_EXACT,
                pattern="test2",
                priority=40,
                category="general",
                labels=[]
            )
        ]
        
        builder.add_rules(rules)
        assert len(builder.rules) == 2
    
    def test_add_action(self):
        """Test adding actions to pipeline."""
        builder = PipelineBuilder()
        builder.add_action(ActionType.MOVE, {"destination": "/tmp/archive"})
        
        assert len(builder.actions) == 1
        assert builder.actions[0] == (ActionType.MOVE, {"destination": "/tmp/archive"})
    
    def test_add_actions(self):
        """Test adding multiple actions to pipeline."""
        builder = PipelineBuilder()
        actions = [
            (ActionType.MOVE, {"destination": "/tmp/archive"}),
            (ActionType.FILE, {"format": "md"})
        ]
        
        builder.add_actions(actions)
        assert len(builder.actions) == 2
    
    def test_chaining(self):
        """Test method chaining."""
        builder = PipelineBuilder()
        processor = builder \
            .set_base_path("/test") \
            .set_dry_run(True) \
            .add_rule(Rule(
                id="test_rule_001",
                name="test",
                rule_type=RuleType.SUBJECT_EXACT,
                pattern="test",
                priority=50,
                category="general",
                labels=[]
            )) \
            .add_action(ActionType.MOVE, {"destination": "/tmp"}) \
            .build()
        
        assert processor is not None


class TestPipelineExecutor:
    """Test cases for PipelineExecutor class."""
    
    @pytest.fixture
    def processor(self, tmp_path):
        """Create a processor for testing."""
        return EmailProcessor(
            base_path=str(tmp_path),
            dry_run=True
        )
    
    @pytest.fixture
    def sample_email(self):
        """Create a sample email."""
        return Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@test.com"],
            subject="Test Email",
            date=datetime(2024, 3, 15, 10, 30, 0),
            body_plain="Test body",
            attachments=[],
            raw_headers={},
            labels=[],
            source_path="/tmp/test.eml"
        )
    
    def test_execute_with_callback(self, processor, sample_email, tmp_path):
        """Test execution with progress callback."""
        callback_calls = []
        
        def progress_callback(current, total, result):
            callback_calls.append((current, total, result))
        
        executor = PipelineExecutor(processor, progress_callback=progress_callback)
        
        # Save email to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            rules = [
                Rule(
                    id="test_rule_001",
                name="test_rule",
                    rule_type=RuleType.SUBJECT_EXACT,
                    pattern="test",
                    priority=50,
                    category="general",
                    labels=[]
                )
            ]
            
            actions = [(ActionType.MOVE, {"destination": "/tmp/archive"})]
            
            results = executor.execute([temp_file], rules, actions)
            
            assert len(results) == 1
            assert len(callback_calls) == 1
            assert callback_calls[0][0] == 1
            assert callback_calls[0][1] == 1
        finally:
            os.unlink(temp_file)
    
    def test_execute_without_callback(self, processor, sample_email, tmp_path):
        """Test execution without progress callback."""
        executor = PipelineExecutor(processor)
        
        # Save email to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            rules = [
                Rule(
                    id="test_rule_001",
                name="test_rule",
                    rule_type=RuleType.SUBJECT_EXACT,
                    pattern="test",
                    priority=50,
                    category="general",
                    labels=[]
                )
            ]
            
            actions = [(ActionType.MOVE, {"destination": "/tmp/archive"})]
            
            results = executor.execute([temp_file], rules, actions)
            
            assert len(results) == 1
        finally:
            os.unlink(temp_file)
    
    def test_execute_directory(self, processor, sample_email, tmp_path):
        """Test executing on directory."""
        # Create test directory with emails
        test_dir = tmp_path / "test_emails"
        test_dir.mkdir()
        
        for i in range(3):
            email_file = test_dir / f"email_{i}.eml"
            email_file.write_text(sample_email.to_eml())
        
        executor = PipelineExecutor(processor)
        
        rules = [
            Rule(
                id="test_rule_001",
                name="test_rule",
                rule_type=RuleType.SUBJECT_EXACT,
                pattern="test",
                priority=50,
                category="general",
                labels=[]
            )
        ]
        
        actions = [(ActionType.MOVE, {"destination": "/tmp/archive"})]
        
        results = executor.execute_directory(str(test_dir), rules, actions)
        
        assert len(results) == 3


class TestPipelineMonitor:
    """Test cases for PipelineMonitor class."""
    
    @pytest.fixture
    def processor(self, tmp_path):
        """Create a processor for testing."""
        return EmailProcessor(
            base_path=str(tmp_path),
            dry_run=True
        )
    
    @pytest.fixture
    def sample_email(self):
        """Create a sample email."""
        return Email(
            from_addr="sender@example.com",
            to_addrs=["recipient@test.com"],
            subject="Test Email",
            date=datetime(2024, 3, 15, 10, 30, 0),
            body_plain="Test body",
            attachments=[],
            raw_headers={},
            labels=[],
            source_path="/tmp/test.eml"
        )
    
    def test_get_status(self, processor, sample_email, tmp_path):
        """Test getting pipeline status."""
        # Process an email
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            rules = [
                Rule(
                    id="test_rule_001",
                name="test_rule",
                    rule_type=RuleType.SUBJECT_EXACT,
                    pattern="test",
                    priority=50,
                    category="general",
                    labels=[]
                )
            ]
            
            actions = [(ActionType.MOVE, {"destination": "/tmp/archive"})]
            
            processor.process_email(temp_file, rules, actions)
            
            monitor = PipelineMonitor(processor)
            status = monitor.get_status()
            
            assert status["total_processed"] == 1
            assert status["total_matched"] == 1
            assert status["total_failed"] == 0
            assert status["success_rate"] == 100.0
            assert "last_updated" in status
        finally:
            os.unlink(temp_file)
    
    def test_get_rule_performance(self, processor, sample_email, tmp_path):
        """Test getting rule performance metrics."""
        # Process an email
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            rules = [
                Rule(
                    id="test_rule_001",
                name="test_rule",
                    rule_type=RuleType.SUBJECT_EXACT,
                    pattern="test",
                    priority=50,
                    category="general",
                    labels=[]
                )
            ]
            
            actions = [(ActionType.MOVE, {"destination": "/tmp/archive"})]
            
            processor.process_email(temp_file, rules, actions)
            
            monitor = PipelineMonitor(processor)
            performance = monitor.get_rule_performance()
            
            assert "test_rule" in performance
            assert performance["test_rule"]["matches"] == 1
            assert "percentage" in performance["test_rule"]
        finally:
            os.unlink(temp_file)
    
    def test_get_action_performance(self, processor, sample_email, tmp_path):
        """Test getting action performance metrics."""
        # Process an email
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(sample_email.to_eml())
            temp_file = f.name
        
        try:
            rules = [
                Rule(
                    id="test_rule_001",
                name="test_rule",
                    rule_type=RuleType.SUBJECT_EXACT,
                    pattern="test",
                    priority=50,
                    category="general",
                    labels=[]
                )
            ]
            
            actions = [(ActionType.MOVE, {"destination": "/tmp/archive"})]
            
            processor.process_email(temp_file, rules, actions)
            
            monitor = PipelineMonitor(processor)
            performance = monitor.get_action_performance()
            
            assert "MOVE" in performance
            assert performance["MOVE"]["count"] == 1
            assert "percentage" in performance["MOVE"]
        finally:
            os.unlink(temp_file)
    
    def test_get_status_no_processing(self, processor):
        """Test getting status with no processing."""
        monitor = PipelineMonitor(processor)
        status = monitor.get_status()
        
        assert status["total_processed"] == 0
        assert status["total_matched"] == 0
        assert status["success_rate"] == 0.0


class TestPipelineConfig:
    """Test cases for PipelineConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineConfig()
        
        assert config.base_path == "./archive"
        assert config.dry_run is False
        assert config.collision_strategy == "rename"
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = PipelineConfig(
            base_path="/custom/path",
            dry_run=True,
            collision_strategy="number",
            max_retries=5,
            retry_delay=2.0
        )
        
        assert config.base_path == "/custom/path"
        assert config.dry_run is True
        assert config.collision_strategy == "number"
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
    
    def test_to_processor(self):
        """Test converting config to processor."""
        config = PipelineConfig(
            base_path="/test/path",
            dry_run=True,
            collision_strategy="number"
        )
        
        processor = config.to_processor()
        
        assert processor.base_path == "/test/path"
        assert processor.dry_run is True
        assert processor.collision_strategy == "number"
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "base_path": "/custom/path",
            "dry_run": True,
            "collision_strategy": "number",
            "max_retries": 5,
            "retry_delay": 2.0
        }
        
        config = PipelineConfig.from_dict(config_dict)
        
        assert config.base_path == "/custom/path"
        assert config.dry_run is True
        assert config.collision_strategy == "number"
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
    
    def test_from_dict_defaults(self):
        """Test creating config from dictionary with defaults."""
        config_dict = {}
        
        config = PipelineConfig.from_dict(config_dict)
        
        assert config.base_path == "./archive"
        assert config.dry_run is False
        assert config.collision_strategy == "rename"
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = PipelineConfig(
            base_path="/test/path",
            dry_run=True,
            collision_strategy="number",
            max_retries=5,
            retry_delay=2.0
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["base_path"] == "/test/path"
        assert config_dict["dry_run"] is True
        assert config_dict["collision_strategy"] == "number"
        assert config_dict["max_retries"] == 5
        assert config_dict["retry_delay"] == 2.0
    
    def test_round_trip(self):
        """Test round-trip conversion."""
        original_config = PipelineConfig(
            base_path="/test/path",
            dry_run=True,
            collision_strategy="number",
            max_retries=5,
            retry_delay=2.0
        )
        
        config_dict = original_config.to_dict()
        restored_config = PipelineConfig.from_dict(config_dict)
        
        assert restored_config.base_path == original_config.base_path
        assert restored_config.dry_run == original_config.dry_run
        assert restored_config.collision_strategy == original_config.collision_strategy
        assert restored_config.max_retries == original_config.max_retries
        assert restored_config.retry_delay == original_config.retry_delay


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
