"""Repair & Remodel (R&R) anchor module.

Scales cooking appliance spend in existing homes using Private Housing R&M value indices
and distributes by home-price deciles.
"""

import logging
from typing import Dict, Any

import polars as pl

logger = logging.getLogger(__name__)


def compute_rr_scale_factor(
    rm_value_df: pl.DataFrame,
    base_year: int = 2019,
) -> pl.DataFrame:
    """Compute R&R scale factor from Private Housing R&M value index.

    Normalizes R&M value index to base year = 1.0.

    Args:
        rm_value_df: Private housing R&M value (year, quarter, rm_value)
        base_year: Base year for normalization

    Returns:
        DataFrame with columns: year, rm_scale_factor
    """
    logger.info(f"Computing R&R scale factor (base year: {base_year})...")

    # Aggregate to annual
    annual = rm_value_df.group_by("year").agg([
        pl.mean("rm_value").alias("rm_value_annual")
    ]).sort("year")

    # Normalize to base year
    base_value = annual.filter(pl.col("year") == base_year).select("rm_value_annual").item()

    annual = annual.with_columns([
        (pl.col("rm_value_annual") / base_value).alias("rm_scale_factor")
    ])

    logger.info("R&R scale factor computed")
    return annual.select(["year", "rm_scale_factor"])


def compute_rr_cooking_spend(
    cooking_annual_df: pl.DataFrame,
    rm_scale_df: pl.DataFrame,
    assumptions: Dict[str, Any],
) -> pl.DataFrame:
    """Compute total R&R cooking spend scaled by R&M growth.

    Args:
        cooking_annual_df: Total cooking value (year, cooking_value_annual)
        rm_scale_df: R&M scale factor (year, rm_scale_factor)
        assumptions: ASSUMPTIONS.yaml dict with kitchen_share_of_RM, appliance_share_of_kitchen

    Returns:
        DataFrame with columns: year, rr_cooking_spend (£m)

    Formula:
        rr_cooking_spend_t = cooking_value_annual_t × rm_scale_factor_t × kitchen_share × appliance_share
    """
    logger.info("Computing R&R cooking spend...")

    kitchen_share = assumptions.get("kitchen_share_of_RM", 0.27)
    appliance_share = assumptions.get("appliance_share_of_kitchen", 0.35)

    merged = cooking_annual_df.join(rm_scale_df, on="year", how="left")

    # R&R cooking spend is a portion of total, scaled by R&M growth
    merged = merged.with_columns([
        (pl.col("cooking_value_annual") * pl.col("rm_scale_factor") * kitchen_share * appliance_share).alias("rr_cooking_spend")
    ])

    result = merged.select(["year", "rr_cooking_spend"]).sort("year")

    total_rr = result.select(pl.sum("rr_cooking_spend")).item()
    logger.info(f"Total R&R cooking spend: £{total_rr:,.0f}m over period")

    return result


def distribute_rr_by_price_decile(
    rr_cooking_df: pl.DataFrame,
    price_deciles_ex: pl.DataFrame,
) -> pl.DataFrame:
    """Distribute R&R cooking spend by existing home price deciles.

    Args:
        rr_cooking_df: Annual R&R cooking spend (year, rr_cooking_spend)
        price_deciles_ex: Existing home price deciles (year, decile, share)

    Returns:
        DataFrame with columns: year, decile, cooking_value_rr (£m)

    Formula:
        cooking_value_rr_{q,t} = rr_cooking_spend_t × share_{q,t}
    """
    logger.info("Distributing R&R cooking spend by home-price decile (existing)...")

    merged = price_deciles_ex.join(rr_cooking_df, on="year", how="left")

    merged = merged.with_columns([
        (pl.col("rr_cooking_spend") * pl.col("share")).alias("cooking_value_rr")
    ])

    result = merged.select(["year", "decile", "cooking_value_rr"]).sort(["year", "decile"])

    # Validation
    validation = result.group_by("year").agg([
        pl.sum("cooking_value_rr").alias("sum_by_deciles")
    ])

    merged_val = validation.join(rr_cooking_df, on="year", how="left")
    merged_val = merged_val.with_columns([
        ((pl.col("sum_by_deciles") - pl.col("rr_cooking_spend")).abs() / pl.col("rr_cooking_spend") * 100).alias("error_pct")
    ])

    max_error = merged_val.select(pl.max("error_pct")).item()
    logger.info(f"R&R value by decile complete. Max error: {max_error:.2f}%")

    return result
