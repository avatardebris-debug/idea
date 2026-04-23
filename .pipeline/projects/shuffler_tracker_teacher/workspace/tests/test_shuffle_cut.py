"""
Test suite for ShuffleCut class.
"""

import json
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shuffler_tracker.models.shuffle_cut import ShuffleCut


class TestShuffleCutCreation:
    """Test cases for ShuffleCut creation."""
    
    def test_cut_creation_valid(self):
        """Test creating a valid ShuffleCut."""
        cut = ShuffleCut(left_half_size=26, right_half_size=26)
        assert cut.left_half_size == 26
        assert cut.right_half_size == 26
        assert cut.cut_ratio == 0.5
    
    def test_cut_creation_ideal(self):
        """Test creating ideal 26/26 cut."""
        cut = ShuffleCut(left_half_size=26, right_half_size=26)
        assert cut.total == 52
        assert cut.cut_ratio == 0.5
        assert cut.deviation_from_ideal == 0
    
    def test_cut_creation_variant(self):
        """Test creating variant cut."""
        cut = ShuffleCut(left_half_size=20, right_half_size=32)
        assert cut.left_half_size == 20
        assert cut.right_half_size == 32
        assert cut.cut_ratio == 20/32
        assert cut.total == 52
        assert cut.deviation_from_ideal == -6
    
    def test_cut_creation_invalid_zero(self):
        """Test that zero total raises ValueError."""
        with pytest.raises(ValueError):
            ShuffleCut(left_half_size=0, right_half_size=0)


class TestShuffleCutProperties:
    """Test cases for ShuffleCut properties."""
    
    def test_cut_ratio_calculation(self):
        """Test cut ratio calculation."""
        cut = ShuffleCut(left_half_size=20, right_half_size=32)
        assert cut.cut_ratio == 20/52
    
    def test_total_property(self):
        """Test total property."""
        cut = ShuffleCut(left_half_size=20, right_half_size=32)
        assert cut.total == 52
    
    def test_deviation_from_ideal(self):
        """Test deviation from ideal calculation."""
        cut_left26 = ShuffleCut(left_half_size=26, right_half_size=26)
        assert cut_left26.deviation_from_ideal == 0
        
        cut_left30 = ShuffleCut(left_half_size=30, right_half_size=22)
        assert cut_left30.deviation_from_ideal == 4
        
        cut_left20 = ShuffleCut(left_half_size=20, right_half_size=32)
        assert cut_left20.deviation_from_ideal == -6


class TestShuffleCutEquality:
    """Test cases for ShuffleCut equality."""
    
    def test_cut_equality_same(self):
        """Test equality for same cuts."""
        cut1 = ShuffleCut(left_half_size=26, right_half_size=26)
        cut2 = ShuffleCut(left_half_size=26, right_half_size=26)
        assert cut1 == cut2
    
    def test_cut_inequality_different(self):
        """Test inequality for different cuts."""
        cut1 = ShuffleCut(left_half_size=26, right_half_size=26)
        cut2 = ShuffleCut(left_half_size=20, right_half_size=32)
        assert cut1 != cut2
    
    def test_cut_inequality_different_type(self):
        """Test inequality with different type."""
        cut = ShuffleCut(left_half_size=26, right_half_size=26)
        assert cut != "ShuffleCut(left=26, right=26)"


class TestShuffleCutSerialization:
    """Test cases for ShuffleCut serialization."""
    
    def test_cut_to_dict(self):
        """Test ShuffleCut serialization to dictionary."""
        cut = ShuffleCut(left_half_size=20, right_half_size=32)
        data = cut.to_dict()
        
        assert data["left_half_size"] == 20
        assert data["right_half_size"] == 32
        assert abs(data["cut_ratio"] - (20/52)) < 0.0001
    
    def test_cut_to_json(self):
        """Test ShuffleCut serialization to JSON."""
        cut = ShuffleCut(left_half_size=20, right_half_size=32)
        json_str = cut.to_json()
        
        data = json.loads(json_str)
        assert data["left_half_size"] == 20
        assert data["right_half_size"] == 32
    
    def test_cut_from_dict(self):
        """Test creating ShuffleCut from dictionary."""
        data = {"left_half_size": 30, "right_half_size": 22}
        cut = ShuffleCut.from_dict(data)
        
        assert cut.left_half_size == 30
        assert cut.right_half_size == 22
        assert cut.total == 52
    
    def test_cut_from_json(self):
        """Test creating ShuffleCut from JSON string."""
        json_str = json.dumps({"left_half_size": 25, "right_half_size": 27})
        cut = ShuffleCut.from_json(json_str)
        
        assert cut.left_half_size == 25
        assert cut.right_half_size == 27


class TestShuffleCutStatistics:
    """Test cases for ShuffleCut statistics computation."""
    
    def test_statistics_computation(self):
        """Test statistics computation for multiple cuts."""
        cuts = [
            ShuffleCut(left_half_size=20, right_half_size=32),
            ShuffleCut(left_half_size=26, right_half_size=26),
            ShuffleCut(left_half_size=30, right_half_size=22),
        ]
        
        stats = ShuffleCut.compute_statistics(cuts)
        
        assert stats["mean"] == 0.5  # Mean should be exactly 0.5
        assert stats["left_half_mean"] == 25.333333333333332
    
    def test_statistics_empty_list(self):
        """Test statistics with empty list."""
        stats = ShuffleCut.compute_statistics([])
        
        assert stats["mean"] == 0.0
        assert stats["std"] == 0.0
        assert stats["min"] == 0.0
        assert stats["max"] == 0.0
        assert stats["median"] == 0.0
        assert stats["left_half_mean"] == 0.0
        assert stats["distribution"] == []


class TestShuffleCutStringRepresentation:
    """Test cases for ShuffleCut string representation."""
    
    def test_cut_str(self):
        """Test ShuffleCut string representation."""
        cut = ShuffleCut(left_half_size=20, right_half_size=32)
        str_repr = str(cut)
        
        assert "20" in str_repr
        assert "32" in str_repr
        assert "ratio" in str_repr
    
    def test_cut_repr(self):
        """Test ShuffleCut detailed representation."""
        cut = ShuffleCut(left_half_size=20, right_half_size=32)
        repr_str = repr(cut)
        
        assert "ShuffleCut" in repr_str
        assert "left_half_size=20" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
