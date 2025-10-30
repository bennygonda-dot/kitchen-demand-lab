"""HHFCE cooking-only extraction module.

Extracts cooking appliance expenditure from COICOP 05.3.1 using CPIH weights
to separate cooking from refrigeration, laundry, and dishwashers.
"""

import logging
from typing import Dict, Any

import polars as pl

logger = logging.getLogger(__name__)


def extract_cooking_only(
    hhfce_df: pl.DataFrame,
    weights_df: pl.DataFrame,
    config: Dict[str, Any],
) -> pl.DataFrame:
    """Extract cooking-only expenditure from total HHFCE 05.3.1.

    Applies CPIH weights to isolate cooking appliances (excluding refrigeration/laundry).

    Args:
        hhfce_df: HHFCE 05.3.1 time series (year, quarter, hhfce_05_3_1)
        weights_df: CPIH weights by year (year, weight_cookers, weight_total, etc.)
        config: Configuration dict

    Returns:
        DataFrame with columns: year, quarter, cooking_value (£m current prices)

    Formula:
        cooking_value_t = hhfce_05_3_1_t × (weight_cookers_t / weight_total_t)
    """
    logger.info("Extracting cooking-only expenditure from HHFCE 05.3.1...")

    # Compute cooking share within 05.3.1 from weights
    weights_df = weights_df.with_columns([
        (pl.col("weight_cookers") / pl.col("weight_total")).alias("cooking_share")
    ])

    # Join HHFCE with weights on year
    merged = hhfce_df.join(weights_df.select(["year", "cooking_share"]), on="year", how="left")

    # Forward-fill missing weights if needed (per ASSUMPTIONS.yaml carry_forward_max_years)
    merged = merged.with_columns([
        pl.col("cooking_share").fill_null(strategy="forward").alias("cooking_share")
    ])

    # Calculate cooking-only value
    merged = merged.with_columns([
        (pl.col("hhfce_05_3_1") * pl.col("cooking_share")).alias("cooking_value")
    ])

    result = merged.select(["year", "quarter", "cooking_value"])

    total_cooking = result.select(pl.sum("cooking_value")).item()
    logger.info(f"Total cooking expenditure extracted: £{total_cooking:,.0f}m over period")

    return result


def aggregate_to_annual(cooking_df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate quarterly cooking expenditure to annual.

    Args:
        cooking_df: Quarterly data (year, quarter, cooking_value)

    Returns:
        Annual data (year, cooking_value_annual)
    """
    logger.info("Aggregating cooking expenditure to annual frequency...")

    annual = cooking_df.group_by("year").agg([
        pl.sum("cooking_value").alias("cooking_value_annual")
    ]).sort("year")

    logger.info(f"Annual cooking expenditure: {len(annual)} years")
    return annual


def compute_cooking_volume_index(
    cooking_value_df: pl.DataFrame,
    rm_volume_df: pl.DataFrame,
    base_year: int = 2019,
) -> pl.DataFrame:
    """Compute cooking appliance volume index using R&M volume as proxy deflator.

    Args:
        cooking_value_df: Annual cooking value (year, cooking_value_annual)
        rm_volume_df: Private housing R&M volume index (year, rm_volume)
        base_year: Base year for index normalization (default 2019)

    Returns:
        DataFrame with year, cooking_value_annual, cooking_volume_index
    """
    logger.info(f"Computing cooking volume index (base year: {base_year})...")

    # Normalize R&M volume index to base year = 100
    rm_annual = rm_volume_df.group_by("year").agg([
        pl.mean("rm_volume").alias("rm_volume")
    ])

    base_volume = rm_annual.filter(pl.col("year") == base_year).select("rm_volume").item()
    rm_annual = rm_annual.with_columns([
        (pl.col("rm_volume") / base_volume * 100).alias("rm_volume_index")
    ])

    # Join and compute cooking volume
    merged = cooking_value_df.join(rm_annual.select(["year", "rm_volume_index"]), on="year", how="left")

    merged = merged.with_columns([
        (pl.col("cooking_value_annual") / pl.col("rm_volume_index") * 100).alias("cooking_volume_index")
    ])

    logger.info("Cooking volume index computed")
    return merged.select(["year", "cooking_value_annual", "cooking_volume_index"])
