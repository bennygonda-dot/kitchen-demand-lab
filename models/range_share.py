"""Range cooker share estimation module.

Estimates range cooker share within total cooking appliances using:
- Trade lens: CN 8516.60 apparent consumption
- Retail lens: SKU counts/filters for ≥90cm free-standing ranges
- Blended method combining both
"""

import logging
from typing import Dict, Any, Optional

import polars as pl

logger = logging.getLogger(__name__)


def estimate_range_share_from_trade(
    trade_df: pl.DataFrame,
    hhfce_cooking_df: pl.DataFrame,
) -> pl.DataFrame:
    """Estimate range cooker share from trade data (CN 8516.60).

    Assumes CN 8516.60 primarily captures range cookers (simplification).

    Args:
        trade_df: Trade data (year, apparent_consumption_gbp)
        hhfce_cooking_df: Total cooking value (year, cooking_value_annual in £m)

    Returns:
        DataFrame with columns: year, range_share_trade
    """
    logger.info("Estimating range share from trade data...")

    # Convert cooking value to £ (from £m)
    hhfce_cooking_df = hhfce_cooking_df.with_columns([
        (pl.col("cooking_value_annual") * 1_000_000).alias("cooking_value_gbp")
    ])

    merged = trade_df.join(
        hhfce_cooking_df.select(["year", "cooking_value_gbp"]),
        on="year",
        how="inner"
    )

    # Range share = apparent consumption / total cooking value
    merged = merged.with_columns([
        (pl.col("apparent_consumption_gbp") / pl.col("cooking_value_gbp")).alias("range_share_trade")
    ])

    # Clip to reasonable bounds (0-30%)
    merged = merged.with_columns([
        pl.col("range_share_trade").clip(0.0, 0.30).alias("range_share_trade")
    ])

    result = merged.select(["year", "range_share_trade"]).sort("year")

    mean_share = result.select(pl.mean("range_share_trade")).item()
    logger.info(f"Mean range share from trade: {mean_share:.2%}")

    return result


def estimate_range_share_from_retail(
    assumptions: Dict[str, Any],
) -> float:
    """Estimate range share from retail SKU analysis.

    In production, this would scrape/API major retailers to count SKUs ≥90cm.
    For now, returns a configured constant or estimates from assumptions.

    Args:
        assumptions: ASSUMPTIONS.yaml dict

    Returns:
        Range share as float (e.g., 0.12 = 12%)
    """
    logger.info("Estimating range share from retail SKU analysis...")

    # Placeholder: in production, implement web scraping/API calls to retailers
    # (Currys, AO, John Lewis, etc.) to count ranges vs built-in

    fallback_share = assumptions.get("range_share_within_cookers", {}).get("fallback_share", 0.12)

    logger.info(f"Using fallback retail range share: {fallback_share:.2%}")
    return fallback_share


def blend_range_shares(
    trade_share_df: pl.DataFrame,
    retail_share: float,
    assumptions: Dict[str, Any],
) -> pl.DataFrame:
    """Blend trade and retail range share estimates.

    Args:
        trade_share_df: Range share from trade (year, range_share_trade)
        retail_share: Range share from retail (scalar)
        assumptions: ASSUMPTIONS.yaml with blend weights

    Returns:
        DataFrame with columns: year, range_share_blended
    """
    logger.info("Blending trade and retail range share estimates...")

    config = assumptions.get("range_share_within_cookers", {})
    method = config.get("method", "blended")
    trade_weight = config.get("trade_weight", 0.6)
    retail_weight = config.get("retail_weight", 0.4)

    if method == "trade_only":
        result = trade_share_df.rename({"range_share_trade": "range_share"})
    elif method == "retail_only":
        result = trade_share_df.select("year").with_columns([
            pl.lit(retail_share).alias("range_share")
        ])
    else:  # blended
        result = trade_share_df.with_columns([
            (pl.col("range_share_trade") * trade_weight + retail_share * retail_weight).alias("range_share")
        ])

    mean_share = result.select(pl.mean("range_share")).item()
    logger.info(f"Blended range share (mean): {mean_share:.2%}")

    return result.select(["year", "range_share"])


def apply_range_share(
    cooking_by_segment_df: pl.DataFrame,
    range_share_df: pl.DataFrame,
    segment_cols: list[str],
) -> pl.DataFrame:
    """Apply range share to cooking expenditure by segment (income or price decile).

    Args:
        cooking_by_segment_df: Cooking spend by segment (year, segment, cooking_spend)
        range_share_df: Range share by year (year, range_share)
        segment_cols: List of segment column names (e.g., ["decile"] or ["income_decile"])

    Returns:
        DataFrame with additional columns: range_spend, builtin_spend
    """
    logger.info("Applying range share to segment data...")

    merged = cooking_by_segment_df.join(range_share_df, on="year", how="left")

    # Forward-fill missing range shares
    merged = merged.sort(["year"] + segment_cols)
    merged = merged.with_columns([
        pl.col("range_share").fill_null(strategy="forward").alias("range_share")
    ])

    # Split into range and built-in
    merged = merged.with_columns([
        (pl.col("cooking_spend") * pl.col("range_share")).alias("range_spend"),
        (pl.col("cooking_spend") * (1 - pl.col("range_share"))).alias("builtin_spend"),
    ])

    logger.info("Range share applied to segment data")
    return merged
