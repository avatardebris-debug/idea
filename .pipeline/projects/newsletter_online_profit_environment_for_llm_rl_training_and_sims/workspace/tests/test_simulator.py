"""Tests for simulator module."""

import pytest
from profit_env.config import SimConfig
from profit_env.simulator import NewsletterSimulator


class TestNewsletterSimulatorInitialization:
    """Test simulator initialization."""
    
    def test_simulator_creation(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        assert simulator.config == config
        assert simulator.state.week == 0
        assert simulator.state.subscribers == 1000
        assert len(simulator.history) == 0
    
    def test_simulator_with_custom_config(self):
        config = SimConfig(
            subscriber_count=5000,
            cpc=5.00,
            arpu=10.00
        )
        simulator = NewsletterSimulator(config)
        
        assert simulator.state.subscribers == 5000


class TestNewsletterSimulatorWeekExecution:
    """Test weekly simulation execution."""
    
    def test_run_week_advances_time(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_week()
        
        assert simulator.state.week == 1
    
    def test_run_week_updates_subscribers(self):
        config = SimConfig(
            subscriber_count=1000,
            churn_rate=0.1,
            growth_rate=0.2
        )
        simulator = NewsletterSimulator(config)
        
        initial_subscribers = simulator.state.subscribers
        simulator.run_week()
        
        assert simulator.state.subscribers != initial_subscribers
        assert simulator.state.subscribers >= 0
    
    def test_run_week_calculates_revenue(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_week()
        
        assert simulator.state.revenue > 0
        assert simulator.state.sponsor_revenue >= 0
        assert simulator.state.ad_revenue >= 0
    
    def test_run_week_calculates_costs(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_week()
        
        assert simulator.state.costs > 0
    
    def test_run_week_calculates_profit(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_week()
        
        assert simulator.state.profit == simulator.state.revenue - simulator.state.costs
    
    def test_run_week_updates_cumulative_profit(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_week()
        first_profit = simulator.state.profit
        
        simulator.run_week()
        
        assert simulator.state.cumulative_profit >= first_profit
    
    def test_run_week_updates_engagement(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_week()
        
        assert 0.0 <= simulator.state.engagement_score <= 1.0


class TestNewsletterSimulatorSimulation:
    """Test complete simulation execution."""
    
    def test_run_simulation(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        history = simulator.run_simulation(10)
        
        assert len(history) == 10
        assert simulator.state.week == 10
    
    def test_run_simulation_records_history(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_simulation(5)
        
        assert len(simulator.history) == 5
        assert simulator.history[0]["week"] == 0
        assert simulator.history[4]["week"] == 4
    
    def test_run_simulation_returns_history(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        history = simulator.run_simulation(3)
        
        assert len(history) == 3
        assert all("week" in record for record in history)
        assert all("subscribers" in record for record in history)
        assert all("revenue" in record for record in history)
        assert all("costs" in record for record in history)
        assert all("profit" in record for record in history)


class TestNewsletterSimulatorStatistics:
    """Test statistics calculation."""
    
    def test_get_statistics(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_simulation(10)
        
        stats = simulator.get_statistics()
        
        assert "total_revenue" in stats
        assert "total_costs" in stats
        assert "net_profit" in stats
        assert "avg_subscribers" in stats
        assert "final_subscribers" in stats
        assert "final_cumulative_profit" in stats
        assert "avg_churn_rate" in stats
        assert "total_acquired" in stats
    
    def test_statistics_accuracy(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_simulation(5)
        
        stats = simulator.get_statistics()
        
        assert stats["net_profit"] == stats["total_revenue"] - stats["total_costs"]
        assert stats["final_cumulative_profit"] == simulator.state.cumulative_profit
        assert stats["final_subscribers"] == simulator.state.subscribers


class TestNewsletterSimulatorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_run_simulation_zero_weeks(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        history = simulator.run_simulation(0)
        
        assert len(history) == 0
        assert simulator.state.week == 0
    
    def test_run_simulation_with_zero_subscribers(self):
        config = SimConfig(subscriber_count=0)
        simulator = NewsletterSimulator(config)
        
        history = simulator.run_simulation(5)
        
        assert len(history) == 5
        assert simulator.state.subscribers >= 0
    
    def test_run_simulation_with_high_churn(self):
        config = SimConfig(
            subscriber_count=1000,
            churn_rate=0.9
        )
        simulator = NewsletterSimulator(config)
        
        history = simulator.run_simulation(5)
        
        assert len(history) == 5
        assert simulator.state.subscribers >= 0
    
    def test_run_simulation_with_high_growth(self):
        config = SimConfig(
            subscriber_count=1000,
            growth_rate=1.0
        )
        simulator = NewsletterSimulator(config)
        
        history = simulator.run_simulation(5)
        
        assert len(history) == 5
        assert simulator.state.subscribers >= 1000


class TestNewsletterSimulatorReset:
    """Test simulator reset functionality."""
    
    def test_reset(self):
        config = SimConfig()
        simulator = NewsletterSimulator(config)
        
        simulator.run_simulation(10)
        
        simulator.reset()
        
        assert simulator.state.week == 0
        assert simulator.state.subscribers == 1000
        assert simulator.state.cumulative_profit == 0.0
        assert len(simulator.history) == 0
