"""Smoke tests for basic functionality.

Quick tests that modules load and basic operations work.
"""

import pytest
from pathlib import Path


def test_imports():
    """Test that all model modules can be imported."""
    from models import (
        ingest,
        clean,
        hhfce,
        deciles_income,
        ppd_deciles,
        newbuild_pool,
        rr_anchor,
        range_share,
        price_bands,
        panels,
        charts,
    )

    assert ingest is not None
    assert clean is not None
    assert hhfce is not None


def test_config_files_exist():
    """Test that configuration files exist."""
    project_root = Path(__file__).parent.parent

    assert (project_root / "conf" / "config.yaml").exists()
    assert (project_root / "conf" / "ASSUMPTIONS.yaml").exists()


def test_config_yaml_valid():
    """Test that config YAML files are valid and parseable."""
    import yaml

    project_root = Path(__file__).parent.parent

    with open(project_root / "conf" / "config.yaml") as f:
        config = yaml.safe_load(f)

    assert "YEARS_START" in config
    assert "YEARS_END" in config
    assert "FREQUENCY" in config

    with open(project_root / "conf" / "ASSUMPTIONS.yaml") as f:
        assumptions = yaml.safe_load(f)

    assert "price_bands" in assumptions
    assert "attach_rates" in assumptions
    assert "ASPs" in assumptions


def test_data_directories_created():
    """Test that data directories exist."""
    project_root = Path(__file__).parent.parent

    assert (project_root / "data" / "raw").exists()
    assert (project_root / "data" / "processed").exists()
    assert (project_root / "outputs").exists()


def test_assumptions_have_required_keys():
    """Test that ASSUMPTIONS.yaml has all required parameters."""
    import yaml

    project_root = Path(__file__).parent.parent

    with open(project_root / "conf" / "ASSUMPTIONS.yaml") as f:
        assumptions = yaml.safe_load(f)

    # Check price bands
    assert "range_cookers" in assumptions["price_bands"]
    assert "mass_premium_min" in assumptions["price_bands"]["range_cookers"]
    assert "luxury_min" in assumptions["price_bands"]["range_cookers"]

    # Check ASPs
    assert "range_cookers" in assumptions["ASPs"]
    assert "mass_premium" in assumptions["ASPs"]["range_cookers"]
    assert "luxury" in assumptions["ASPs"]["range_cookers"]

    # Check shares
    assert "kitchen_share_of_RM" in assumptions
    assert "appliance_share_of_kitchen" in assumptions

    # Validate numeric ranges
    assert 0 < assumptions["kitchen_share_of_RM"] < 1
    assert 0 < assumptions["appliance_share_of_kitchen"] < 1


def test_pipeline_script_executable():
    """Test that run_all.py exists and is importable."""
    project_root = Path(__file__).parent.parent

    assert (project_root / "scripts" / "run_all.py").exists()

    # Test import
    import sys
    sys.path.insert(0, str(project_root))

    from scripts import run_all

    assert hasattr(run_all, "main")
    assert hasattr(run_all, "run_pipeline")
