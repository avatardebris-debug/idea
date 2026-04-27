"""Tests for configuration module."""

import pytest
from profit_env.config import SimConfig


class TestSimConfigDefaults:
    """Test default configuration values."""
    
    def test_default_subscriber_count(self):
        config = SimConfig()
        assert config.subscriber_count == 1000
    
    def test_default_cpc(self):
        config = SimConfig()
        assert config.cpc == 2.50
    
    def test_default_retention_rate(self):
        config = SimConfig()
        assert config.retention_rate == 0.95
    
    def test_default_arpu(self):
        config = SimConfig()
        assert config.arpu == 5.00
    
    def test_default_ad_rate(self):
        config = SimConfig()
        assert config.ad_rate == 0.50
    
    def test_default_sponsor_rate(self):
        config = SimConfig()
        assert config.sponsor_rate == 100.00
    
    def test_default_content_cost(self):
        config = SimConfig()
        assert config.content_cost == 500.00
    
    def test_default_operational_cost(self):
        config = SimConfig()
        assert config.operational_cost == 300.00
    
    def test_default_growth_rate(self):
        config = SimConfig()
        assert config.growth_rate == 0.1
    
    def test_default_churn_rate(self):
        config = SimConfig()
        assert config.churn_rate == 0.05
    
    def test_default_seasonal_factor(self):
        config = SimConfig()
        assert config.seasonal_factor == 1.0
    
    def test_default_competitor_count(self):
        config = SimConfig()
        assert config.competitor_count == 5
    
    def test_default_market_saturation(self):
        config = SimConfig()
        assert config.market_saturation == 0.3
    
    def test_default_conversion_rate(self):
        config = SimConfig()
        assert config.conversion_rate == 0.02
    
    def test_default_engagement_rate(self):
        config = SimConfig()
        assert config.engagement_rate == 0.75
    
    def test_default_sponsorship_fill_rate(self):
        config = SimConfig()
        assert config.sponsorship_fill_rate == 0.8
    
    def test_default_refund_rate(self):
        config = SimConfig()
        assert config.refund_rate == 0.01
    
    def test_default_tax_rate(self):
        config = SimConfig()
        assert config.tax_rate == 0.25
    
    def test_default_discount_rate(self):
        config = SimConfig()
        assert config.discount_rate == 0.1
    
    def test_default_acquisition_channel_mix(self):
        config = SimConfig()
        assert config.acquisition_channel_mix == {
            "organic": 0.4,
            "paid": 0.3,
            "social": 0.2,
            "referral": 0.1
        }


class TestSimConfigValidation:
    """Test configuration validation."""
    
    def test_invalid_subscriber_count(self):
        with pytest.raises(ValueError):
            SimConfig(subscriber_count=-100)
    
    def test_invalid_retention_rate(self):
        with pytest.raises(ValueError):
            SimConfig(retention_rate=1.5)
    
    def test_invalid_churn_rate(self):
        with pytest.raises(ValueError):
            SimConfig(churn_rate=-0.1)
    
    def test_invalid_cpc(self):
        with pytest.raises(ValueError):
            SimConfig(cpc=-1.0)
    
    def test_invalid_arpu(self):
        with pytest.raises(ValueError):
            SimConfig(arpu=-1.0)
    
    def test_invalid_content_cost(self):
        with pytest.raises(ValueError):
            SimConfig(content_cost=-100.0)
    
    def test_invalid_operational_cost(self):
        with pytest.raises(ValueError):
            SimConfig(operational_cost=-100.0)
    
    def test_invalid_tax_rate(self):
        with pytest.raises(ValueError):
            SimConfig(tax_rate=1.5)
    
    def test_churn_retention_sum(self):
        with pytest.raises(ValueError):
            SimConfig(churn_rate=0.6, retention_rate=0.6)
    
    def test_growth_with_zero_subscribers(self):
        with pytest.raises(ValueError):
            SimConfig(subscriber_count=0, growth_rate=0.1)


class TestSimConfigCustomValues:
    """Test custom configuration values."""
    
    def test_custom_subscriber_count(self):
        config = SimConfig(subscriber_count=5000)
        assert config.subscriber_count == 5000
    
    def test_custom_cpc(self):
        config = SimConfig(cpc=5.00)
        assert config.cpc == 5.00
    
    def test_custom_arpu(self):
        config = SimConfig(arpu=10.00)
        assert config.arpu == 10.00
    
    def test_custom_rates(self):
        config = SimConfig(
            churn_rate=0.1,
            retention_rate=0.9,
            growth_rate=0.2
        )
        assert config.churn_rate == 0.1
        assert config.retention_rate == 0.9
        assert config.growth_rate == 0.2
