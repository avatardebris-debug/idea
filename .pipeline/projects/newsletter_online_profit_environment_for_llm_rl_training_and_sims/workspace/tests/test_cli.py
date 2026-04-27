"""Tests for CLI module."""

import pytest
import json
import csv
import sys
import io
from pathlib import Path
from profit_env.cli import main, create_parser, run_simulation, run_stats, run_export


class TestCreateParser:
    """Test argument parser creation."""
    
    def test_parser_creation(self):
        parser = create_parser()
        
        assert parser is not None
        assert parser.description == "Newsletter Online Profit Environment - Simulation and Analysis Tool"
    
    def test_parser_has_sim_subcommand(self):
        parser = create_parser()
        
        # Parse to get the sim subparser
        args = parser.parse_args(["sim", "--help"])
        
        # Check that sim has subcommands
        assert hasattr(args, 'sim_command')
    
    def test_parser_sim_run_defaults(self):
        parser = create_parser()
        args = parser.parse_args(["sim", "run"])
        
        assert args.weeks == 52
        assert args.subscribers == 1000
        assert args.cpc == 2.50
        assert args.retention == 0.95
        assert args.arpu == 5.00


class TestRunSimulation:
    """Test simulation running functionality."""
    
    def test_run_default_simulation(self):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.95,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.1,
            "churn": 0.05,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 52,
        })()
        
        run_simulation(args)
    
    def test_run_custom_parameters(self):
        args = type('Args', (), {
            "subscribers": 5000,
            "cpc": 3.00,
            "retention": 0.98,
            "arpu": 10.00,
            "ad_rate": 1.00,
            "sponsor_rate": 200.00,
            "content_cost": 1000.00,
            "operational_cost": 500.00,
            "growth": 0.15,
            "churn": 0.02,
            "seasonal": 1.2,
            "competitors": 3,
            "saturation": 0.5,
            "conversion": 0.05,
            "engagement": 0.9,
            "sponsor_fill": 0.95,
            "refund": 0.005,
            "tax": 0.30,
            "discount": 0.15,
            "weeks": 26,
        })()
        
        run_simulation(args)
    
    def test_run_short_simulation(self):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.95,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.1,
            "churn": 0.05,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 4,
        })()
        
        run_simulation(args)
    
    def test_run_high_growth(self):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.95,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.25,
            "churn": 0.02,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 12,
        })()
        
        run_simulation(args)
    
    def test_run_low_churn(self):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.99,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.1,
            "churn": 0.01,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 12,
        })()
        
        run_simulation(args)


class TestRunStats:
    """Test statistics printing functionality."""
    
    def test_stats_default(self):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.95,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.1,
            "churn": 0.05,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 52,
        })()
        
        run_stats(args)
    
    def test_stats_custom(self):
        args = type('Args', (), {
            "subscribers": 5000,
            "cpc": 3.00,
            "retention": 0.98,
            "arpu": 10.00,
            "ad_rate": 1.00,
            "sponsor_rate": 200.00,
            "content_cost": 1000.00,
            "operational_cost": 500.00,
            "growth": 0.15,
            "churn": 0.02,
            "seasonal": 1.2,
            "competitors": 3,
            "saturation": 0.5,
            "conversion": 0.05,
            "engagement": 0.9,
            "sponsor_fill": 0.95,
            "refund": 0.005,
            "tax": 0.30,
            "discount": 0.15,
            "weeks": 26,
        })()
        
        run_stats(args)


class TestRunExport:
    """Test export functionality."""
    
    def test_export_json(self, tmp_path):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.95,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.1,
            "churn": 0.05,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 12,
            "output": str(tmp_path / "results.json"),
            "format": "json",
        })()
        
        run_export(args)
        
        assert (tmp_path / "results.json").exists()
        
        with open(tmp_path / "results.json") as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 12
        assert "subscribers" in data[0]
        assert "revenue" in data[0]
        assert "profit" in data[0]
    
    def test_export_csv(self, tmp_path):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.95,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.1,
            "churn": 0.05,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 12,
            "output": str(tmp_path / "results.csv"),
            "format": "csv",
        })()
        
        run_export(args)
        
        assert (tmp_path / "results.csv").exists()
        
        with open(tmp_path / "results.csv") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 12
        assert "subscribers" in rows[0]
        assert "revenue" in rows[0]
        assert "profit" in rows[0]
    
    def test_export_invalid_format(self, tmp_path):
        args = type('Args', (), {
            "subscribers": 1000,
            "cpc": 2.50,
            "retention": 0.95,
            "arpu": 5.00,
            "ad_rate": 0.50,
            "sponsor_rate": 100.00,
            "content_cost": 500.00,
            "operational_cost": 300.00,
            "growth": 0.1,
            "churn": 0.05,
            "seasonal": 1.0,
            "competitors": 5,
            "saturation": 0.3,
            "conversion": 0.02,
            "engagement": 0.75,
            "sponsor_fill": 0.8,
            "refund": 0.01,
            "tax": 0.25,
            "discount": 0.1,
            "weeks": 12,
            "output": str(tmp_path / "results.txt"),
            "format": "invalid",
        })()
        
        with pytest.raises(SystemExit):
            run_export(args)


class TestCLI:
    """Test CLI entry point."""
    
    def test_cli_no_command(self):
        """Test running CLI without arguments."""
        old_argv = sys.argv
        sys.argv = ["profit_env"]
        
        try:
            # When no command is provided, argparse shows help and exits
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with code 2 (argparse error)
            assert exc_info.value.code != 0
        finally:
            sys.argv = old_argv
    
    def test_cli_sim_run_command(self):
        """Test running simulation via CLI."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "run", "--weeks", "4"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
    
    def test_cli_sim_run_with_output(self, tmp_path):
        """Test running simulation with custom parameters."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "run", 
                   "--weeks", "4",
                   "--subscribers", "5000",
                   "--growth", "0.15",
                   "--churn", "0.02"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
    
    def test_cli_sim_stats_command(self):
        """Test running stats via CLI."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "stats", "--weeks", "4"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
    
    def test_cli_sim_export_json(self, tmp_path):
        """Test exporting results via CLI."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "4",
                   "--output", str(tmp_path / "results.json"),
                   "--format", "json"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
        
        assert (tmp_path / "results.json").exists()
        
        with open(tmp_path / "results.json") as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 4
    
    def test_cli_sim_export_csv(self, tmp_path):
        """Test exporting results via CLI."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "4",
                   "--output", str(tmp_path / "results.csv"),
                   "--format", "csv"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
        
        assert (tmp_path / "results.csv").exists()
        
        with open(tmp_path / "results.csv") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 4
    
    def test_cli_invalid_command(self):
        """Test running invalid command."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "invalid"]
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code != 0
        finally:
            sys.argv = old_argv
    
    def test_cli_help(self):
        """Test help output."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "--help"]
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 0
        finally:
            sys.argv = old_argv


class TestCLIVariations:
    """Test CLI with various parameter combinations."""
    
    def test_cli_high_growth(self, tmp_path):
        """Test CLI with high growth parameters."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "12",
                   "--subscribers", "10000",
                   "--growth", "0.15",
                   "--churn", "0.02",
                   "--output", str(tmp_path / "high_growth.json"),
                   "--format", "json"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
        
        assert (tmp_path / "high_growth.json").exists()
        
        with open(tmp_path / "high_growth.json") as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 12
        # First week should have fewer subscribers due to churn
        assert data[0]["subscribers"] < 10000
    
    def test_cli_low_churn(self, tmp_path):
        """Test CLI with low churn parameters."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "24",
                   "--churn", "0.005",
                   "--output", str(tmp_path / "low_churn.json"),
                   "--format", "json"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
        
        assert (tmp_path / "low_churn.json").exists()
    
    def test_cli_high_arpu(self, tmp_path):
        """Test CLI with high ARPU parameters."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "6",
                   "--arpu", "25.0",
                   "--output", str(tmp_path / "high_arpu.json"),
                   "--format", "json"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
        
        assert (tmp_path / "high_arpu.json").exists()
    
    def test_cli_seasonal(self, tmp_path):
        """Test CLI with seasonal parameters."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "12",
                   "--seasonal", "1.2",
                   "--output", str(tmp_path / "seasonal.json"),
                   "--format", "json"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
        
        assert (tmp_path / "seasonal.json").exists()


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_cli_invalid_growth(self):
        """Test CLI with invalid growth parameter."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "run", "--growth", "invalid"]
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code != 0
        finally:
            sys.argv = old_argv
    
    def test_cli_invalid_weeks(self):
        """Test CLI with invalid weeks parameter."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "run", "--weeks", "invalid"]
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code != 0
        finally:
            sys.argv = old_argv
    
    def test_cli_export_missing_output(self):
        """Test CLI export without output parameter."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "4",
                   "--format", "json"]
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code != 0
        finally:
            sys.argv = old_argv
    
    def test_cli_export_invalid_format(self, tmp_path):
        """Test CLI export with invalid format."""
        old_argv = sys.argv
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "4",
                   "--output", str(tmp_path / "results.txt"),
                   "--format", "invalid"]
        
        try:
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code != 0
        finally:
            sys.argv = old_argv


class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete workflow: run simulation, export results."""
        old_argv = sys.argv
        run_output = tmp_path / "simulation_results.json"
        
        sys.argv = ["profit_env", "sim", "export",
                   "--weeks", "12",
                   "--subscribers", "5000",
                   "--output", str(run_output),
                   "--format", "json"]
        
        try:
            main()
        finally:
            sys.argv = old_argv
        
        assert run_output.exists()
        
        with open(run_output) as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 12
        # First week should have fewer subscribers due to churn
        assert data[0]["subscribers"] < 5000
    
    def test_multiple_simulations(self, tmp_path):
        """Test running multiple simulations with different parameters."""
        old_argv = sys.argv
        
        scenarios = [
            {"subscribers": 1000, "growth": 0.05, "churn": 0.02},
            {"subscribers": 5000, "growth": 0.1, "churn": 0.01},
            {"subscribers": 10000, "growth": 0.15, "churn": 0.005},
        ]
        
        try:
            for i, scenario in enumerate(scenarios):
                output_path = tmp_path / f"scenario_{i}.json"
                sys.argv = ["profit_env", "sim", "export",
                           "--weeks", "6",
                           "--subscribers", str(scenario["subscribers"]),
                           "--growth", str(scenario["growth"]),
                           "--churn", str(scenario["churn"]),
                           "--output", str(output_path),
                           "--format", "json"]
                
                main()
                
                assert output_path.exists()
        finally:
            sys.argv = old_argv
    
    def test_cli_with_different_weeks(self, tmp_path):
        """Test that different weeks produce different results."""
        old_argv = sys.argv
        results = []
        
        try:
            for weeks in [4, 12, 24]:
                output_path = tmp_path / f"weeks_{weeks}.json"
                sys.argv = ["profit_env", "sim", "export",
                           "--weeks", str(weeks),
                           "--output", str(output_path),
                           "--format", "json"]
                
                main()
                
                with open(output_path) as f:
                    data = json.load(f)
                
                results.append(len(data))
        finally:
            sys.argv = old_argv
        
        # Results should be different
        assert len(set(results)) > 1
