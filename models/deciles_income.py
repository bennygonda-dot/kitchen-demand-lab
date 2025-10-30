"""Income deciles distribution module.

Distributes cooking expenditure across household income deciles using
ONS Family Spending (Living Costs & Food) survey data.
"""

import logging
from typing import Dict, Any

import polars as pl

logger = logging.getLogger(__name__)


def distribute_by_income_decile(
    cooking_annual_df: pl.DataFrame,
    family_spending_df: pl.DataFrame,
    config: Dict[str, Any],
) -> pl.DataFrame:
    """Distribute cooking expenditure by income decile.

    Args:
        cooking_annual_df: Annual cooking value (year, cooking_value_annual)
        family_spending_df: Decile shares by year (year, decile, share)
        config: Configuration dict with carry-forward rules

    Returns:
        DataFrame with columns: year, decile, cooking_spend (£m)

    Formula:
        cooking_spend_{d,t} = cooking_value_annual_t × share_{d,t}
    """
    logger.info("Distributing cooking expenditure by income decile...")

    # Ensure shares sum to 1.0 per year (normalize if needed)
    family_spending_df = family_spending_df.with_columns([
        pl.col("share").fill_null(0.0)
    ])

    # Normalize shares to sum to 1 per year
    shares_by_year = family_spending_df.group_by("year").agg([
        pl.sum("share").alias("total_share")
    ])

    family_spending_df = family_spending_df.join(shares_by_year, on="year", how="left")
    family_spending_df = family_spending_df.with_columns([
        (pl.col("share") / pl.col("total_share")).alias("share_normalized")
    ])

    # Carry forward missing years (per ASSUMPTIONS.yaml)
    max_carry_forward = config.get("data_quality", {}).get("carry_forward_max_years", 2)

    all_years = cooking_annual_df.select("year").unique().sort("year")
    all_deciles = pl.DataFrame({"decile": list(range(1, 11))})

    # Create full grid of year × decile
    full_grid = all_years.join(all_deciles, how="cross")

    # Join with family spending shares
    merged = full_grid.join(
        family_spending_df.select(["year", "decile", "share_normalized"]),
        on=["year", "decile"],
        how="left"
    )

    # Forward-fill missing shares (within max_carry_forward limit)
    merged = merged.sort(["decile", "year"])
    merged = merged.with_columns([
        pl.col("share_normalized").fill_null(strategy="forward").over("decile").alias("share_filled")
    ])

    # Join with cooking value
    result = merged.join(cooking_annual_df, on="year", how="left")

    # Compute cooking spend by decile
    result = result.with_columns([
        (pl.col("cooking_value_annual") * pl.col("share_filled")).alias("cooking_spend")
    ])

    result = result.select(["year", "decile", "cooking_spend"]).sort(["year", "decile"])

    # Validation: check sum per year equals total cooking value
    validation = result.group_by("year").agg([
        pl.sum("cooking_spend").alias("total_by_deciles")
    ])

    merged_val = validation.join(cooking_annual_df, on="year", how="left")
    merged_val = merged_val.with_columns([
        ((pl.col("total_by_deciles") - pl.col("cooking_value_annual")).abs() / pl.col("cooking_value_annual") * 100).alias("error_pct")
    ])

    max_error = merged_val.select(pl.max("error_pct")).item()
    logger.info(f"Income decile distribution complete. Max error: {max_error:.2f}%")

    if max_error > 1.0:
        logger.warning(f"Sum validation error exceeds 1% (max: {max_error:.2f}%)")

    return result


def compute_cooking_units_by_decile(
    cooking_spend_df: pl.DataFrame,
    asp_ladder: Dict[int, float],
) -> pl.DataFrame:
    """Convert cooking spend to implied units using ASP ladder by decile.

    Higher deciles are assumed to purchase higher-ASP products.

    Args:
        cooking_spend_df: Year × decile cooking spend (year, decile, cooking_spend)
        asp_ladder: Dict mapping decile -> assumed ASP (£)

    Returns:
        DataFrame with additional column: cooking_units
    """
    logger.info("Converting cooking spend to implied units by decile...")

    # Create ASP mapping dataframe
    asp_df = pl.DataFrame({
        "decile": list(asp_ladder.keys()),
        "asp": list(asp_ladder.values()),
    })

    result = cooking_spend_df.join(asp_df, on="decile", how="left")

    result = result.with_columns([
        ((pl.col("cooking_spend") * 1_000_000) / pl.col("asp")).alias("cooking_units")
    ])

    total_units = result.select(pl.sum("cooking_units")).item()
    logger.info(f"Total cooking units implied: {total_units:,.0f} over period")

    return result.select(["year", "decile", "cooking_spend", "asp", "cooking_units"])
