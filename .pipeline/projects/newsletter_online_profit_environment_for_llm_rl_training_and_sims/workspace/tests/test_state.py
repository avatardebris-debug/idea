"""Tests for state module."""

import json
import pytest
from profit_env.state import NewsletterState


class TestNewsletterStateDefaults:
    """Test default state values."""
    
    def test_default_week(self):
        state = NewsletterState()
        assert state.week == 0
    
    def test_default_subscribers(self):
        state = NewsletterState()
        assert state.subscribers == 1000
    
    def test_default_revenue(self):
        state = NewsletterState()
        assert state.revenue == 0.0
    
    def test_default_costs(self):
        state = NewsletterState()
        assert state.costs == 0.0
    
    def test_default_profit(self):
        state = NewsletterState()
        assert state.profit == 0.0
    
    def test_default_cumulative_profit(self):
        state = NewsletterState()
        assert state.cumulative_profit == 0.0
    
    def test_default_engagement_score(self):
        state = NewsletterState()
        assert state.engagement_score == 0.75
    
    def test_default_sponsor_revenue(self):
        state = NewsletterState()
        assert state.sponsor_revenue == 0.0
    
    def test_default_ad_revenue(self):
        state = NewsletterState()
        assert state.ad_revenue == 0.0


class TestNewsletterStateSerialization:
    """Test state serialization and deserialization."""
    
    def test_to_dict(self):
        state = NewsletterState(
            week=10,
            subscribers=5000,
            revenue=10000.0,
            costs=5000.0,
            profit=5000.0
        )
        state_dict = state.to_dict()
        
        assert state_dict["week"] == 10
        assert state_dict["subscribers"] == 5000
        assert state_dict["revenue"] == 10000.0
        assert state_dict["costs"] == 5000.0
        assert state_dict["profit"] == 5000.0
    
    def test_from_dict(self):
        state_dict = {
            "week": 20,
            "subscribers": 10000,
            "revenue": 20000.0,
            "costs": 8000.0,
            "profit": 12000.0,
            "cumulative_profit": 50000.0,
            "churned": 500,
            "acquired": 1000,
            "engagement_score": 0.85,
            "sponsor_revenue": 2000.0,
            "ad_revenue": 1000.0
        }
        
        state = NewsletterState.from_dict(state_dict)
        
        assert state.week == 20
        assert state.subscribers == 10000
        assert state.revenue == 20000.0
        assert state.costs == 8000.0
        assert state.profit == 12000.0
        assert state.cumulative_profit == 50000.0
        assert state.churned == 500
        assert state.acquired == 1000
        assert state.engagement_score == 0.85
        assert state.sponsor_revenue == 2000.0
        assert state.ad_revenue == 1000.0
    
    def test_to_json(self):
        state = NewsletterState(week=5, subscribers=2000)
        json_str = state.to_json()
        
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["week"] == 5
        assert data["subscribers"] == 2000
    
    def test_from_json(self):
        json_str = json.dumps({
            "week": 15,
            "subscribers": 7500,
            "revenue": 15000.0,
            "costs": 6000.0,
            "profit": 9000.0,
            "cumulative_profit": 30000.0,
            "churned": 300,
            "acquired": 600,
            "engagement_score": 0.8,
            "sponsor_revenue": 1500.0,
            "ad_revenue": 750.0
        })
        
        state = NewsletterState.from_json(json_str)
        
        assert state.week == 15
        assert state.subscribers == 7500
        assert state.revenue == 15000.0
        assert state.costs == 6000.0
        assert state.profit == 9000.0


class TestNewsletterStateReset:
    """Test state reset functionality."""
    
    def test_reset(self):
        state = NewsletterState(
            week=50,
            subscribers=10000,
            revenue=50000.0,
            costs=20000.0,
            profit=30000.0,
            cumulative_profit=100000.0,
            churned=2000,
            acquired=3000,
            engagement_score=0.9,
            sponsor_revenue=5000.0,
            ad_revenue=2500.0
        )
        
        state.reset()
        
        assert state.week == 0
        assert state.subscribers == 1000
        assert state.revenue == 0.0
        assert state.costs == 0.0
        assert state.profit == 0.0
        assert state.cumulative_profit == 0.0
        assert state.churned == 0
        assert state.acquired == 0
        assert state.engagement_score == 0.75
        assert state.sponsor_revenue == 0.0
        assert state.ad_revenue == 0.0


class TestNewsletterStateValidation:
    """Test state validation."""
    
    def test_invalid_week(self):
        with pytest.raises(ValueError):
            NewsletterState(week=-1)
    
    def test_invalid_subscribers(self):
        with pytest.raises(ValueError):
            NewsletterState(subscribers=-100)
    
    def test_invalid_engagement_score(self):
        with pytest.raises(ValueError):
            NewsletterState(engagement_score=1.5)
    
    def test_invalid_engagement_score_negative(self):
        with pytest.raises(ValueError):
            NewsletterState(engagement_score=-0.1)
