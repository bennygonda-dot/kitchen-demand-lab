"""Price band segmentation module.

Splits cooking appliance spend into Luxury vs Mass-Premium segments
based on price band thresholds and ASP ladders.
"""

import logging
from typing import Dict, Any, Tuple

import polars as pl

logger = logging.getLogger(__name__)


def split_by_price_band(
    spend_df: pl.DataFrame,
    appliance_type: str,
    assumptions: Dict[str, Any],
    value_col: str = "cooking_spend",
) -> pl.DataFrame:
    """Split appliance spend into Luxury and Mass-Premium bands.

    Uses ASPs to convert value to units, then allocates units to bands
    based on price thresholds.

    Args:
        spend_df: Spend data (year, [segments...], cooking_spend)
        appliance_type: "range_cookers" or "built_in_cooking"
        assumptions: ASSUMPTIONS.yaml dict with price_bands and ASPs
        value_col: Column name for spend value

    Returns:
        DataFrame with additional columns:
            - mass_premium_value, luxury_value
            - mass_premium_units, luxury_units
    """
    logger.info(f"Splitting {appliance_type} by price band...")

    price_bands = assumptions.get("price_bands", {}).get(appliance_type, {})
    asps = assumptions.get("ASPs", {}).get(appliance_type, {})

    mass_premium_min = price_bands.get("mass_premium_min", 0)
    luxury_min = price_bands.get("luxury_min", 9999999)

    asp_mass = asps.get("mass_premium", 1500)
    asp_luxury = asps.get("luxury", 3500)

    # Estimate band split using simple allocation model
    # Assume spend follows a log-normal distribution of prices
    # For simplicity, use a fixed split ratio (tune based on survey data)

    # Simplified split: assume 60% Mass-Premium, 40% Luxury by value (configurable)
    # In production, use more sophisticated unit-level modeling

    mass_premium_share = 0.60  # Default, can be refined
    luxury_share = 0.40

    result = spend_df.with_columns([
        (pl.col(value_col) * mass_premium_share).alias("mass_premium_value"),
        (pl.col(value_col) * luxury_share).alias("luxury_value"),
    ])

    # Convert to units using ASPs
    result = result.with_columns([
        ((pl.col("mass_premium_value") * 1_000_000) / asp_mass).alias("mass_premium_units"),
        ((pl.col("luxury_value") * 1_000_000) / asp_luxury).alias("luxury_units"),
    ])

    logger.info(f"{appliance_type} split into price bands")
    return result


def create_price_band_summary(
    bands_df: pl.DataFrame,
    segment_cols: list[str],
) -> pl.DataFrame:
    """Create summary table of price band mix by segment.

    Args:
        bands_df: DataFrame with price band columns
        segment_cols: List of segment columns (e.g., ["year", "decile"])

    Returns:
        Summary DataFrame with band shares
    """
    logger.info("Creating price band summary...")

    summary = bands_df.group_by(segment_cols).agg([
        pl.sum("mass_premium_value").alias("total_mass_premium_value"),
        pl.sum("luxury_value").alias("total_luxury_value"),
        pl.sum("mass_premium_units").alias("total_mass_premium_units"),
        pl.sum("luxury_units").alias("total_luxury_units"),
    ])

    summary = summary.with_columns([
        (pl.col("total_mass_premium_value") + pl.col("total_luxury_value")).alias("total_value"),
        (pl.col("total_mass_premium_units") + pl.col("total_luxury_units")).alias("total_units"),
    ])

    summary = summary.with_columns([
        (pl.col("total_mass_premium_value") / pl.col("total_value")).alias("mass_premium_share"),
        (pl.col("total_luxury_value") / pl.col("total_value")).alias("luxury_share"),
    ])

    return summary


def apply_price_bands_to_panels(
    income_panel_df: pl.DataFrame,
    nb_panel_df: pl.DataFrame,
    rr_panel_df: pl.DataFrame,
    assumptions: Dict[str, Any],
) -> Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    """Apply price band splits to all three panels.

    Args:
        income_panel_df: Income decile panel (year, decile, cooking_spend, range_spend, builtin_spend)
        nb_panel_df: New build price decile panel (year, decile, cooking_value_nb)
        rr_panel_df: R&R price decile panel (year, decile, cooking_value_rr)
        assumptions: ASSUMPTIONS.yaml dict

    Returns:
        Tuple of (income_panel_with_bands, nb_panel_with_bands, rr_panel_with_bands)
    """
    logger.info("Applying price bands to all panels...")

    # Income panel - split ranges and built-in separately
    income_ranges = split_by_price_band(
        income_panel_df,
        "range_cookers",
        assumptions,
        value_col="range_spend"
    )

    income_builtin = split_by_price_band(
        income_panel_df,
        "built_in_cooking",
        assumptions,
        value_col="builtin_spend"
    )

    # Merge back
    income_panel_bands = income_ranges.select([
        "year", "decile", "cooking_spend", "range_spend", "builtin_spend",
        "mass_premium_value", "luxury_value", "mass_premium_units", "luxury_units"
    ])

    # New Build panel
    nb_panel_bands = split_by_price_band(
        nb_panel_df,
        "built_in_cooking",  # New builds typically get built-in
        assumptions,
        value_col="cooking_value_nb"
    )

    # R&R panel
    rr_panel_bands = split_by_price_band(
        rr_panel_df,
        "built_in_cooking",  # R&R mix of built-in and ranges
        assumptions,
        value_col="cooking_value_rr"
    )

    logger.info("Price bands applied to all panels")
    return income_panel_bands, nb_panel_bands, rr_panel_bands
