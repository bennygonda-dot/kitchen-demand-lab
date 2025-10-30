"""Final panel assembly module.

Assembles final output panels:
- Income decile panel (cooking-only and range cookers)
- New Build price decile panel
- R&R price decile panel
"""

import logging
from pathlib import Path
from typing import Dict, Any, Tuple

import polars as pl

logger = logging.getLogger(__name__)


def assemble_income_panel(
    cooking_by_decile: pl.DataFrame,
    range_share_df: pl.DataFrame,
    assumptions: Dict[str, Any],
) -> pl.DataFrame:
    """Assemble final income decile panel with cooking and range splits.

    Args:
        cooking_by_decile: Cooking spend by income decile (year, decile, cooking_spend)
        range_share_df: Range share (year, range_share)
        assumptions: ASSUMPTIONS.yaml dict

    Returns:
        DataFrame with columns: year, decile, cooking_spend, range_spend, builtin_spend
    """
    logger.info("Assembling income decile panel...")

    from .range_share import apply_range_share

    panel = apply_range_share(
        cooking_by_decile,
        range_share_df,
        segment_cols=["decile"]
    )

    panel = panel.select([
        "year", "decile", "cooking_spend", "range_spend", "builtin_spend"
    ]).sort(["year", "decile"])

    logger.info(f"Income panel assembled: {len(panel)} rows")
    return panel


def assemble_price_decile_panels(
    nb_value_df: pl.DataFrame,
    rr_value_df: pl.DataFrame,
) -> Tuple[pl.DataFrame, pl.DataFrame]:
    """Assemble New Build and R&R price decile panels.

    Args:
        nb_value_df: New build cooking value by price decile (year, decile, cooking_value_nb)
        rr_value_df: R&R cooking value by price decile (year, decile, cooking_value_rr)

    Returns:
        Tuple of (nb_panel, rr_panel)
    """
    logger.info("Assembling price decile panels...")

    nb_panel = nb_value_df.sort(["year", "decile"])
    rr_panel = rr_value_df.sort(["year", "decile"])

    logger.info(f"Price decile panels assembled: NB={len(nb_panel)}, R&R={len(rr_panel)} rows")
    return nb_panel, rr_panel


def save_panels(
    income_panel: pl.DataFrame,
    nb_panel: pl.DataFrame,
    rr_panel: pl.DataFrame,
    output_dir: Path,
    year: int,
) -> None:
    """Save final panels to CSV files.

    Args:
        income_panel: Income decile panel
        nb_panel: New Build price decile panel
        rr_panel: R&R price decile panel
        output_dir: Output directory for CSVs
        year: Year for filename (or "all" for multi-year)
    """
    logger.info(f"Saving panels for year {year}...")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Income panels
    income_panel.write_csv(output_dir / f"cooking_only_by_income_decile_{year}.csv")
    logger.info(f"Saved: cooking_only_by_income_decile_{year}.csv")

    # Extract range cookers subset
    range_panel = income_panel.select([
        "year", "decile",
        pl.col("range_spend").alias("range_cooker_spend")
    ])
    range_panel.write_csv(output_dir / f"range_cookers_by_income_decile_{year}.csv")
    logger.info(f"Saved: range_cookers_by_income_decile_{year}.csv")

    # Price decile panels
    nb_panel.write_csv(output_dir / f"cooking_only_by_price_decile_newbuild_{year}.csv")
    logger.info(f"Saved: cooking_only_by_price_decile_newbuild_{year}.csv")

    rr_panel.write_csv(output_dir / f"cooking_only_by_price_decile_rr_{year}.csv")
    logger.info(f"Saved: cooking_only_by_price_decile_rr_{year}.csv")


def save_price_band_mix(
    income_panel_bands: pl.DataFrame,
    nb_panel_bands: pl.DataFrame,
    rr_panel_bands: pl.DataFrame,
    output_dir: Path,
    year: int,
) -> None:
    """Save price band mix summaries.

    Args:
        income_panel_bands: Income panel with price bands
        nb_panel_bands: New Build panel with price bands
        rr_panel_bands: R&R panel with price bands
        output_dir: Output directory
        year: Year for filename
    """
    logger.info(f"Saving price band mix for year {year}...")

    from .price_bands import create_price_band_summary

    # Income panel summary
    income_summary = create_price_band_summary(income_panel_bands, ["year", "decile"])
    income_summary.write_csv(output_dir / f"price_bands_mix_income_{year}.csv")

    # NB panel summary
    nb_summary = create_price_band_summary(nb_panel_bands, ["year", "decile"])
    nb_summary.write_csv(output_dir / f"price_bands_mix_newbuild_{year}.csv")

    # RR panel summary
    rr_summary = create_price_band_summary(rr_panel_bands, ["year", "decile"])
    rr_summary.write_csv(output_dir / f"price_bands_mix_rr_{year}.csv")

    logger.info("Price band mix summaries saved")


def generate_coverage_report(
    income_panel: pl.DataFrame,
    nb_panel: pl.DataFrame,
    rr_panel: pl.DataFrame,
    coverage_path: Path,
) -> Dict[str, Any]:
    """Generate coverage report documenting data availability.

    Args:
        income_panel: Income decile panel
        nb_panel: New Build panel
        rr_panel: R&R panel
        coverage_path: Path to save coverage.json

    Returns:
        Coverage dict
    """
    logger.info("Generating coverage report...")

    coverage = {
        "income_decile_panel": {
            "first_year": int(income_panel.select(pl.min("year")).item()),
            "last_year": int(income_panel.select(pl.max("year")).item()),
            "total_rows": len(income_panel),
            "gaps": [],  # TODO: detect gaps in time series
        },
        "newbuild_price_decile_panel": {
            "first_year": int(nb_panel.select(pl.min("year")).item()),
            "last_year": int(nb_panel.select(pl.max("year")).item()),
            "total_rows": len(nb_panel),
            "gaps": [],
        },
        "rr_price_decile_panel": {
            "first_year": int(rr_panel.select(pl.min("year")).item()),
            "last_year": int(rr_panel.select(pl.max("year")).item()),
            "total_rows": len(rr_panel),
            "gaps": [],
        },
    }

    # Save to JSON
    import json
    with open(coverage_path, "w") as f:
        json.dump(coverage, f, indent=2)

    logger.info(f"Coverage report saved to {coverage_path}")
    return coverage
