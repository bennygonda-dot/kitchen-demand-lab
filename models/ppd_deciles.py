"""Price Paid Data deciles module.

Computes home-price decile cutpoints and transaction shares from Land Registry PPD,
separately for New Build vs Existing properties.
"""

import logging
from typing import Tuple

import polars as pl

logger = logging.getLogger(__name__)


def compute_price_deciles(
    ppd_lazy: pl.LazyFrame,
    new_build: bool,
) -> pl.DataFrame:
    """Compute price decile cutpoints and transaction shares for given property type.

    Args:
        ppd_lazy: LazyFrame of PPD transactions (date, price, new_build, property_type)
        new_build: If True, filter for NewBuild=True; else NewBuild=False

    Returns:
        DataFrame with columns: year, decile, price_min, price_max, share
    """
    logger.info(f"Computing price deciles for {'New Build' if new_build else 'Existing'} properties...")

    # Filter by new build status
    filtered = ppd_lazy.filter(pl.col("new_build") == new_build)

    # Extract year
    filtered = filtered.with_columns([
        pl.col("date").dt.year().alias("year")
    ])

    # Collect for quantile computation (required for deciles)
    df = filtered.select(["year", "price"]).collect()

    # Compute deciles per year
    deciles_list = []

    for year in df.select("year").unique().sort("year").to_series():
        year_data = df.filter(pl.col("year") == year)
        prices = year_data.select("price").to_series().to_list()

        if len(prices) < 100:
            logger.warning(f"Year {year} has only {len(prices)} transactions for {'NB' if new_build else 'EX'}, skipping")
            continue

        # Compute decile boundaries
        quantiles = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        price_sorted = sorted(prices)
        n = len(price_sorted)

        for i in range(10):
            decile = i + 1
            lower_idx = int(quantiles[i] * (n - 1))
            upper_idx = int(quantiles[i + 1] * (n - 1))

            price_min = price_sorted[lower_idx]
            price_max = price_sorted[upper_idx]

            # Share is uniform (10% per decile by construction)
            share = 0.10

            deciles_list.append({
                "year": year,
                "decile": decile,
                "price_min": price_min,
                "price_max": price_max,
                "share": share,
            })

    result = pl.DataFrame(deciles_list)

    logger.info(f"Price deciles computed: {len(result)} year-decile combinations")
    return result


def compute_ppd_deciles_both(
    ppd_lazy: pl.LazyFrame,
) -> Tuple[pl.DataFrame, pl.DataFrame]:
    """Compute price deciles for both New Build and Existing properties.

    Args:
        ppd_lazy: LazyFrame of PPD transactions

    Returns:
        Tuple of (new_build_deciles, existing_deciles)
    """
    logger.info("Computing price deciles for New Build and Existing properties...")

    nb_deciles = compute_price_deciles(ppd_lazy, new_build=True)
    ex_deciles = compute_price_deciles(ppd_lazy, new_build=False)

    return nb_deciles, ex_deciles


def apply_premium_uplift(
    deciles_df: pl.DataFrame,
    top_deciles: list[int],
    uplift_factor: float,
) -> pl.DataFrame:
    """Apply premium uplift to top home-price deciles.

    Args:
        deciles_df: Price deciles (year, decile, ...)
        top_deciles: List of decile numbers to apply uplift (e.g., [9, 10])
        uplift_factor: Multiplicative uplift (e.g., 1.10 for +10%)

    Returns:
        DataFrame with additional column: value_multiplier
    """
    logger.info(f"Applying {uplift_factor:.2%} premium uplift to deciles {top_deciles}...")

    deciles_df = deciles_df.with_columns([
        pl.when(pl.col("decile").is_in(top_deciles))
        .then(pl.lit(uplift_factor))
        .otherwise(pl.lit(1.0))
        .alias("value_multiplier")
    ])

    return deciles_df
