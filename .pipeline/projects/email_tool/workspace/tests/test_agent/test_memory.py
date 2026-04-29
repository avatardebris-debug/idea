"""Tests for the memory module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from email_tool.agent.memory import MemoryManager
from email_tool.agent.base import AgentResult


class TestMemoryManager:
    """Test cases for MemoryManager."""
    
    def test_init_default_path(self):
        """Test initialization with default path."""
        with patch.object(Path, 'home', return_value=Path('/home/user')):
            manager = MemoryManager()
            
            assert manager.storage_path == Path('/home/user/.email_tool/memory')
            assert manager.storage_path.exists()
            assert manager.storage_path.is_dir()
    
    def test_init_custom_path(self):
        """Test initialization with custom path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            assert manager.storage_path == Path(tmpdir)
            assert manager.storage_path.exists()
            assert manager.storage_path.is_dir()
    
    def test_store_and_retrieve(self):
        """Test storing and retrieving values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            result = manager.store("test_key", "test_value")
            
            assert result.success is True
            assert result.data["key"] == "test_key"
            assert result.data["value"] == "test_value"
            
            value = manager.retrieve("test_key")
            assert value == "test_value"
    
    def test_store_with_complex_value(self):
        """Test storing complex data structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            complex_data = {
                "user_id": 123,
                "preferences": {"theme": "dark", "notifications": True},
                "tags": ["work", "important"]
            }
            
            result = manager.store("user_data", complex_data)
            
            assert result.success is True
            
            retrieved = manager.retrieve("user_data")
            assert retrieved == complex_data
    
    def test_retrieve_with_default(self):
        """Test retrieving with default value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            value = manager.retrieve("nonexistent_key", default="default_value")
            
            assert value == "default_value"
    
    def test_retrieve_none_default(self):
        """Test retrieving with None default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            value = manager.retrieve("nonexistent_key")
            
            assert value is None
    
    def test_delete_existing_key(self):
        """Test deleting an existing key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("test_key", "test_value")
            
            result = manager.delete("test_key")
            
            assert result.success is True
            assert result.data["key"] == "test_key"
            
            value = manager.retrieve("test_key")
            assert value is None
    
    def test_delete_nonexistent_key(self):
        """Test deleting a non-existent key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            result = manager.delete("nonexistent_key")
            
            assert result.success is False
            assert "not found" in result.error_message.lower()
    
    def test_add_history_entry(self):
        """Test adding an entry to history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            entry = {
                "action": "test_action",
                "data": {"key": "value"}
            }
            
            result = manager.add_history_entry(entry)
            
            assert result.success is True
            assert result.data["action"] == "test_action"
            assert "timestamp" in result.data
    
    def test_get_history(self):
        """Test getting history entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            for i in range(5):
                manager.add_history_entry({"action": f"action_{i}"})
            
            history = manager.get_history()
            
            assert len(history) == 5
            assert history[0]["action"] == "action_0"
            assert history[-1]["action"] == "action_4"
    
    def test_get_history_with_limit(self):
        """Test getting history with limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            for i in range(10):
                manager.add_history_entry({"action": f"action_{i}"})
            
            history = manager.get_history(limit=3)
            
            assert len(history) == 3
            assert history[0]["action"] == "action_7"
            assert history[-1]["action"] == "action_9"
    
    def test_clear_history(self):
        """Test clearing history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            for i in range(5):
                manager.add_history_entry({"action": f"action_{i}"})
            
            result = manager.clear_history()
            
            assert result.success is True
            assert result.metadata["operation"] == "clear_history"
            
            history = manager.get_history()
            assert len(history) == 0
    
    def test_get_all_memory(self):
        """Test getting all memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("key1", "value1")
            manager.store("key2", "value2")
            
            all_memory = manager.get_all_memory()
            
            assert len(all_memory) == 2
            assert all_memory["key1"] == "value1"
            assert all_memory["key2"] == "value2"
    
    def test_clear_memory(self):
        """Test clearing all memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("key1", "value1")
            manager.store("key2", "value2")
            
            result = manager.clear_memory()
            
            assert result.success is True
            assert result.metadata["operation"] == "clear_memory"
            
            all_memory = manager.get_all_memory()
            assert len(all_memory) == 0
    
    def test_get_status(self):
        """Test getting memory status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("key1", "value1")
            manager.add_history_entry({"action": "test"})
            
            status = manager.get_status()
            
            assert "storage_path" in status
            assert "memory_keys" in status
            assert "memory_count" in status
            assert "history_count" in status
            assert status["memory_count"] == 1
            assert status["history_count"] == 1
    
    def test_store_overwrites_existing_key(self):
        """Test that storing overwrites existing key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("test_key", "value1")
            manager.store("test_key", "value2")
            
            value = manager.retrieve("test_key")
            assert value == "value2"
    
    def test_memory_persistence(self):
        """Test that memory persists across sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First session
            manager1 = MemoryManager(storage_path=tmpdir)
            manager1.store("test_key", "test_value")
            
            # Second session - should load existing memory
            manager2 = MemoryManager(storage_path=tmpdir)
            
            value = manager2.retrieve("test_key")
            assert value == "test_value"
    
    def test_history_persistence(self):
        """Test that history persists across sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # First session
            manager1 = MemoryManager(storage_path=tmpdir)
            manager1.add_history_entry({"action": "test_action"})
            
            # Second session - should load existing history
            manager2 = MemoryManager(storage_path=tmpdir)
            
            history = manager2.get_history()
            assert len(history) == 1
            assert history[0]["action"] == "test_action"
    
    def test_store_with_none_value(self):
        """Test storing None value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            result = manager.store("none_key", None)
            
            assert result.success is True
            
            value = manager.retrieve("none_key")
            assert value is None
    
    def test_store_with_empty_string(self):
        """Test storing empty string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            result = manager.store("empty_key", "")
            
            assert result.success is True
            
            value = manager.retrieve("empty_key")
            assert value == ""
    
    def test_store_with_empty_list(self):
        """Test storing empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            result = manager.store("list_key", [])
            
            assert result.success is True
            
            value = manager.retrieve("list_key")
            assert value == []
    
    def test_store_with_empty_dict(self):
        """Test storing empty dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            result = manager.store("dict_key", {})
            
            assert result.success is True
            
            value = manager.retrieve("dict_key")
            assert value == {}
    
    def test_get_status_with_empty_memory(self):
        """Test getting status with empty memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            status = manager.get_status()
            
            assert status["memory_count"] == 0
            assert status["history_count"] == 0
            assert status["memory_keys"] == []
    
    def test_delete_removes_from_memory(self):
        """Test that delete removes key from memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("test_key", "test_value")
            manager.delete("test_key")
            
            all_memory = manager.get_all_memory()
            assert "test_key" not in all_memory
    
    def test_add_history_entry_with_complex_data(self):
        """Test adding history entry with complex data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            entry = {
                "action": "complex_action",
                "data": {
                    "user_id": 123,
                    "items": ["item1", "item2"],
                    "metadata": {"timestamp": "2024-01-01"}
                }
            }
            
            result = manager.add_history_entry(entry)
            
            assert result.success is True
            assert result.data["action"] == "complex_action"
            assert result.data["data"]["user_id"] == 123
    
    def test_get_history_empty(self):
        """Test getting history when empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            history = manager.get_history()
            
            assert history == []
    
    def test_clear_history_empty(self):
        """Test clearing empty history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            result = manager.clear_history()
            
            assert result.success is True
    
    def test_memory_file_created(self):
        """Test that memory file is created after storing data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            # File should not exist initially
            assert not manager.memory_file.exists()
            
            # Store some data
            manager.store("test_key", "test_value")
            
            # File should exist after storing data
            assert manager.memory_file.exists()
            assert manager.memory_file.is_file()
    
    def test_history_file_created(self):
        """Test that history file is created after adding history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            # File should not exist initially
            assert not manager.history_file.exists()
            
            # Add some history
            manager.add_history_entry({"action": "test"})
            
            # File should exist after adding history
            assert manager.history_file.exists()
            assert manager.history_file.is_file()
    
    def test_storage_path_created(self):
        """Test that storage path is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "new" / "storage" / "path"
            
            manager = MemoryManager(storage_path=str(storage_path))
            
            assert storage_path.exists()
            assert storage_path.is_dir()
    
    def test_store_with_special_characters(self):
        """Test storing values with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            special_value = "Value with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
            
            result = manager.store("special_key", special_value)
            
            assert result.success is True
            
            retrieved = manager.retrieve("special_key")
            assert retrieved == special_value
    
    def test_store_with_unicode_characters(self):
        """Test storing values with unicode characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            unicode_value = "Value with unicode: 你好 🌍 مرحبا"
            
            result = manager.store("unicode_key", unicode_value)
            
            assert result.success is True
            
            retrieved = manager.retrieve("unicode_key")
            assert retrieved == unicode_value
    
    def test_store_with_long_value(self):
        """Test storing long values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            long_value = "x" * 10000
            
            result = manager.store("long_key", long_value)
            
            assert result.success is True
            
            retrieved = manager.retrieve("long_key")
            assert retrieved == long_value
    
    def test_store_with_nested_structure(self):
        """Test storing deeply nested structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            nested_value = {
                "level1": {
                    "level2": {
                        "level3": {
                            "level4": {
                                "value": "deep"
                            }
                        }
                    }
                }
            }
            
            result = manager.store("nested_key", nested_value)
            
            assert result.success is True
            
            retrieved = manager.retrieve("nested_key")
            assert retrieved == nested_value
    
    def test_retrieve_nonexistent_with_none_default(self):
        """Test retrieving non-existent key with None default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            value = manager.retrieve("nonexistent_key", default=None)
            
            assert value is None
    
    def test_get_status_with_large_memory(self):
        """Test getting status with large memory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            for i in range(100):
                manager.store(f"key_{i}", f"value_{i}")
            
            status = manager.get_status()
            
            assert status["memory_count"] == 100
            assert len(status["memory_keys"]) == 100
    
    def test_get_status_with_large_history(self):
        """Test getting status with large history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            for i in range(100):
                manager.add_history_entry({"action": f"action_{i}"})
            
            status = manager.get_status()
            
            assert status["history_count"] == 100
    
    def test_store_and_delete_multiple_keys(self):
        """Test storing and deleting multiple keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            keys = ["key1", "key2", "key3", "key4", "key5"]
            
            for key in keys:
                manager.store(key, f"value_{key}")
            
            for key in keys:
                manager.delete(key)
            
            all_memory = manager.get_all_memory()
            assert len(all_memory) == 0
    
    def test_history_order_preserved(self):
        """Test that history order is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            for i in range(10):
                manager.add_history_entry({"action": f"action_{i}"})
            
            history = manager.get_history()
            
            for i, entry in enumerate(history):
                assert entry["action"] == f"action_{i}"
    
    def test_history_limit_respected(self):
        """Test that history limit is respected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            for i in range(20):
                manager.add_history_entry({"action": f"action_{i}"})
            
            history = manager.get_history(limit=5)
            
            assert len(history) == 5
            assert history[0]["action"] == "action_15"
            assert history[-1]["action"] == "action_19"
    
    def test_clear_memory_and_history(self):
        """Test clearing both memory and history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("key1", "value1")
            manager.add_history_entry({"action": "test"})
            
            manager.clear_memory()
            manager.clear_history()
            
            assert len(manager.get_all_memory()) == 0
            assert len(manager.get_history()) == 0
    
    def test_store_with_boolean_values(self):
        """Test storing boolean values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("bool_true", True)
            manager.store("bool_false", False)
            
            assert manager.retrieve("bool_true") is True
            assert manager.retrieve("bool_false") is False
    
    def test_store_with_integer_values(self):
        """Test storing integer values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("int_positive", 42)
            manager.store("int_negative", -42)
            manager.store("int_zero", 0)
            
            assert manager.retrieve("int_positive") == 42
            assert manager.retrieve("int_negative") == -42
            assert manager.retrieve("int_zero") == 0
    
    def test_store_with_float_values(self):
        """Test storing float values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = MemoryManager(storage_path=tmpdir)
            
            manager.store("float_positive", 3.14)
            manager.store("float_negative", -3.14)
            manager.store("float_zero", 0.0)
            
            assert manager.retrieve("float_positive") == 3.14
            assert manager.retrieve("float_negative") == -3.14
            assert manager.retrieve("float_zero") == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
