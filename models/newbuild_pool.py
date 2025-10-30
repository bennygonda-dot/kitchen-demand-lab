"""New build attach pool module.

Computes cooking appliance attach pool from new dwelling completions,
assuming one cooking set (hob + oven + hood) per new home.
"""

import logging
from typing import Dict, Any

import polars as pl

logger = logging.getLogger(__name__)


def compute_newbuild_attach_pool(
    completions_df: pl.DataFrame,
    assumptions: Dict[str, Any],
) -> pl.DataFrame:
    """Compute new build cooking appliance attach pool.

    Args:
        completions_df: House building completions (year, quarter, completions_uk)
        assumptions: ASSUMPTIONS.yaml dict with attach_rates

    Returns:
        DataFrame with columns: year, completions_annual, cooking_sets
    """
    logger.info("Computing new build cooking appliance attach pool...")

    attach_rate = assumptions.get("attach_rates", {}).get("new_build_base_set", 1.0)

    # Aggregate to annual
    annual = completions_df.group_by("year").agg([
        pl.sum("completions_uk").alias("completions_annual")
    ]).sort("year")

    # Compute cooking sets (1 per dwelling)
    annual = annual.with_columns([
        (pl.col("completions_annual") * attach_rate).alias("cooking_sets")
    ])

    total_sets = annual.select(pl.sum("cooking_sets")).item()
    logger.info(f"Total new build cooking sets: {total_sets:,.0f} over period")

    return annual


def compute_newbuild_value_by_decile(
    attach_pool_df: pl.DataFrame,
    price_deciles_nb: pl.DataFrame,
    base_set_value: float,
    assumptions: Dict[str, Any],
) -> pl.DataFrame:
    """Compute new build cooking value distributed by home-price decile.

    Args:
        attach_pool_df: Annual attach pool (year, cooking_sets)
        price_deciles_nb: New build price deciles (year, decile, share, value_multiplier)
        base_set_value: Base cooking set value (£, hob+oven+hood)
        assumptions: ASSUMPTIONS.yaml dict

    Returns:
        DataFrame with columns: year, decile, cooking_value_nb (£m)

    Formula:
        cooking_value_nb_{q,t} = cooking_sets_t × base_set_value × share_{q,t} × value_multiplier_{q,t}
    """
    logger.info("Computing new build cooking value by home-price decile...")

    # Compute total pool value per year
    attach_pool_df = attach_pool_df.with_columns([
        (pl.col("cooking_sets") * base_set_value).alias("total_value")
    ])

    # Join with deciles
    merged = price_deciles_nb.join(attach_pool_df.select(["year", "total_value"]), on="year", how="left")

    # Compute value by decile
    merged = merged.with_columns([
        (pl.col("total_value") * pl.col("share") * pl.col("value_multiplier") / 1_000_000).alias("cooking_value_nb")
    ])

    result = merged.select(["year", "decile", "cooking_value_nb"]).sort(["year", "decile"])

    # Validation: sum should equal total pool value (within rounding)
    validation = result.group_by("year").agg([
        pl.sum("cooking_value_nb").alias("sum_by_deciles")
    ])

    merged_val = validation.join(
        attach_pool_df.select([
            "year",
            (pl.col("total_value") / 1_000_000).alias("total_value_m")
        ]),
        on="year",
        how="left"
    )

    merged_val = merged_val.with_columns([
        ((pl.col("sum_by_deciles") - pl.col("total_value_m")).abs() / pl.col("total_value_m") * 100).alias("error_pct")
    ])

    max_error = merged_val.select(pl.max("error_pct")).item()
    logger.info(f"New build value by decile complete. Max error: {max_error:.2f}%")

    return result
