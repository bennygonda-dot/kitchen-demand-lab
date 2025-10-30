"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def config():
    """Load and return config.yaml."""
    import yaml
    project_root = Path(__file__).parent.parent
    with open(project_root / "conf" / "config.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def assumptions():
    """Load and return ASSUMPTIONS.yaml."""
    import yaml
    project_root = Path(__file__).parent.parent
    with open(project_root / "conf" / "ASSUMPTIONS.yaml") as f:
        return yaml.safe_load(f)
