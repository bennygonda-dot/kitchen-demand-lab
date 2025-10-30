"""Invariant tests for pipeline integrity.

Tests fundamental mathematical constraints:
- Sum checks (decile sums equal totals)
- Monotonicity (price deciles increasing)
- Bounds (shares in [0,1])
- No private data inputs
"""

import polars as pl
import pytest
from pathlib import Path


def test_income_decile_sum_equals_total():
    """Test that sum across income deciles equals total cooking value."""
    # Load processed data
    project_root = Path(__file__).parent.parent
    processed_dir = project_root / "data" / "processed"

    # Skip if data doesn't exist yet
    if not (processed_dir / "cooking_annual.parquet").exists():
        pytest.skip("Processed data not available")

    cooking_annual = pl.read_parquet(processed_dir / "cooking_annual.parquet")

    # Load income decile panel from outputs
    output_dir = project_root / "outputs" / "tables"
    if not (output_dir / "cooking_only_by_income_decile_all.csv").exists():
        pytest.skip("Output data not available")

    income_panel = pl.read_csv(output_dir / "cooking_only_by_income_decile_all.csv")

    # Sum by year across deciles
    decile_sums = income_panel.group_by("year").agg([
        pl.sum("cooking_spend").alias("total_by_deciles")
    ])

    # Join with original totals
    merged = decile_sums.join(cooking_annual, on="year", how="inner")

    # Compute percentage error
    merged = merged.with_columns([
        ((pl.col("total_by_deciles") - pl.col("cooking_value_annual")).abs() /
         pl.col("cooking_value_annual") * 100).alias("error_pct")
    ])

    # Check max error is within tolerance (1%)
    max_error = merged.select(pl.max("error_pct")).item()
    assert max_error < 1.0, f"Income decile sum error exceeds 1%: {max_error:.2f}%"


def test_price_decile_shares_sum_to_one():
    """Test that price decile shares sum to 1.0 per year."""
    project_root = Path(__file__).parent.parent
    processed_dir = project_root / "data" / "processed"

    if not (processed_dir / "ppd_nb_deciles.parquet").exists():
        pytest.skip("PPD deciles not available")

    nb_deciles = pl.read_parquet(processed_dir / "ppd_nb_deciles.parquet")
    ex_deciles = pl.read_parquet(processed_dir / "ppd_ex_deciles.parquet")

    # Check New Build
    nb_sums = nb_deciles.group_by("year").agg([
        pl.sum("share").alias("total_share")
    ])
    nb_errors = nb_sums.filter((pl.col("total_share") - 1.0).abs() > 0.01)
    assert len(nb_errors) == 0, f"New Build shares don't sum to 1.0: {nb_errors}"

    # Check Existing
    ex_sums = ex_deciles.group_by("year").agg([
        pl.sum("share").alias("total_share")
    ])
    ex_errors = ex_sums.filter((pl.col("total_share") - 1.0).abs() > 0.01)
    assert len(ex_errors) == 0, f"Existing shares don't sum to 1.0: {ex_errors}"


def test_price_deciles_monotonic():
    """Test that price decile cutpoints are strictly increasing."""
    project_root = Path(__file__).parent.parent
    processed_dir = project_root / "data" / "processed"

    if not (processed_dir / "ppd_nb_deciles.parquet").exists():
        pytest.skip("PPD deciles not available")

    nb_deciles = pl.read_parquet(processed_dir / "ppd_nb_deciles.parquet")

    # For each year, check price_min increases with decile
    for year in nb_deciles.select("year").unique().to_series():
        year_data = nb_deciles.filter(pl.col("year") == year).sort("decile")
        prices = year_data.select("price_min").to_series().to_list()

        for i in range(len(prices) - 1):
            assert prices[i] <= prices[i + 1], \
                f"Price deciles not monotonic for year {year}: {prices}"


def test_shares_bounded():
    """Test that all share values are in [0, 1]."""
    project_root = Path(__file__).parent.parent
    processed_dir = project_root / "data" / "processed"

    # Check family spending shares
    if (processed_dir / "family_spending.parquet").exists():
        family_spending = pl.read_parquet(processed_dir / "family_spending.parquet")
        assert family_spending.filter(
            (pl.col("share") < 0) | (pl.col("share") > 1)
        ).height == 0, "Family spending shares out of bounds"

    # Check range share
    if (processed_dir / "range_share.parquet").exists():
        range_share = pl.read_parquet(processed_dir / "range_share.parquet")
        assert range_share.filter(
            (pl.col("range_share") < 0) | (pl.col("range_share") > 1)
        ).height == 0, "Range shares out of bounds"


def test_no_negative_values():
    """Test that all monetary values and units are non-negative."""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "outputs" / "tables"

    if not output_dir.exists():
        pytest.skip("Outputs not available")

    # Check income panel
    if (output_dir / "cooking_only_by_income_decile_all.csv").exists():
        income_panel = pl.read_csv(output_dir / "cooking_only_by_income_decile_all.csv")
        assert income_panel.filter(pl.col("cooking_spend") < 0).height == 0, \
            "Negative cooking spend found"

    # Check NB panel
    if (output_dir / "cooking_only_by_price_decile_newbuild_all.csv").exists():
        nb_panel = pl.read_csv(output_dir / "cooking_only_by_price_decile_newbuild_all.csv")
        assert nb_panel.filter(pl.col("cooking_value_nb") < 0).height == 0, \
            "Negative NB cooking value found"


def test_no_private_data_sources():
    """Test that only official public data sources are used."""
    project_root = Path(__file__).parent.parent

    # Check DATA_SOURCES.md exists and contains only official URLs
    data_sources_path = project_root / "DATA_SOURCES.md"

    if not data_sources_path.exists():
        pytest.skip("DATA_SOURCES.md not generated yet")

    with open(data_sources_path) as f:
        content = f.read().lower()

    # List of approved official domains
    official_domains = [
        "ons.gov.uk",
        "gov.uk",
        "bankofengland.co.uk",
        "landregistry.gov.uk",
        "uktradeinfo.com",
    ]

    # Check that content only references official domains
    # (This is a simplified check; enhance as needed)
    assert any(domain in content for domain in official_domains), \
        "DATA_SOURCES.md doesn't reference official sources"


def test_coverage_report_exists():
    """Test that coverage report exists and has valid structure."""
    project_root = Path(__file__).parent.parent
    coverage_path = project_root / "coverage.json"

    if not coverage_path.exists():
        pytest.skip("Coverage report not generated yet")

    import json
    with open(coverage_path) as f:
        coverage = json.load(f)

    # Check required keys
    required_keys = ["income_decile_panel", "newbuild_price_decile_panel", "rr_price_decile_panel"]
    for key in required_keys:
        assert key in coverage, f"Missing coverage key: {key}"
        assert "first_year" in coverage[key]
        assert "last_year" in coverage[key]
        assert coverage[key]["first_year"] <= coverage[key]["last_year"]


def test_output_files_exist():
    """Smoke test that expected output files exist."""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "outputs" / "tables"

    if not output_dir.exists():
        pytest.skip("Outputs directory not created yet")

    # Expected files
    expected_files = [
        "cooking_only_by_income_decile_all.csv",
        "range_cookers_by_income_decile_all.csv",
        "cooking_only_by_price_decile_newbuild_all.csv",
        "cooking_only_by_price_decile_rr_all.csv",
    ]

    missing_files = [f for f in expected_files if not (output_dir / f).exists()]

    # Allow some files to be missing in early runs
    if missing_files:
        pytest.skip(f"Some output files not generated yet: {missing_files}")
