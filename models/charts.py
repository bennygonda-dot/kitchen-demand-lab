"""Charting module using matplotlib.

Generates default-styled charts for drivers, panels, and price band mix.
"""

import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import polars as pl

logger = logging.getLogger(__name__)


def setup_chart_defaults() -> None:
    """Set matplotlib to use default styles (no custom colors)."""
    plt.style.use("default")
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["font.size"] = 10


def plot_drivers(
    completions_df: pl.DataFrame,
    rm_value_df: pl.DataFrame,
    hhfce_df: pl.DataFrame,
    output_dir: Path,
) -> None:
    """Plot key market drivers time series.

    Args:
        completions_df: House building completions (year, completions_annual)
        rm_value_df: Private housing R&M value (year, rm_value_annual)
        hhfce_df: HHFCE 05.3.1 (year, hhfce_05_3_1)
        output_dir: Output directory for charts
    """
    logger.info("Plotting market drivers...")

    setup_chart_defaults()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Completions
    fig, ax = plt.subplots(figsize=(10, 6))
    completions_annual = completions_df.group_by("year").agg(pl.sum("completions_uk"))
    ax.plot(completions_annual["year"], completions_annual["completions_uk"])
    ax.set_xlabel("Year")
    ax.set_ylabel("Completions (UK)")
    ax.set_title("UK House Building Completions")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "drivers_completions.png")
    plt.close()

    # R&M Value
    fig, ax = plt.subplots(figsize=(10, 6))
    rm_annual = rm_value_df.group_by("year").agg(pl.mean("rm_value"))
    ax.plot(rm_annual["year"], rm_annual["rm_value"])
    ax.set_xlabel("Year")
    ax.set_ylabel("R&M Value Index")
    ax.set_title("Private Housing Repair & Maintenance Value")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "drivers_rm_value.png")
    plt.close()

    # HHFCE
    fig, ax = plt.subplots(figsize=(10, 6))
    hhfce_annual = hhfce_df.group_by("year").agg(pl.sum("hhfce_05_3_1"))
    ax.plot(hhfce_annual["year"], hhfce_annual["hhfce_05_3_1"])
    ax.set_xlabel("Year")
    ax.set_ylabel("HHFCE 05.3.1 (£m)")
    ax.set_title("Household Expenditure on Major Appliances")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "drivers_hhfce.png")
    plt.close()

    logger.info("Market drivers charts saved")


def plot_income_decile_panel(
    income_panel: pl.DataFrame,
    output_dir: Path,
) -> None:
    """Plot cooking expenditure by income decile.

    Args:
        income_panel: Income decile panel (year, decile, cooking_spend)
        output_dir: Output directory for charts
    """
    logger.info("Plotting income decile panel...")

    setup_chart_defaults()

    # Stacked area chart by decile over time
    pivot = income_panel.pivot(
        values="cooking_spend",
        index="year",
        columns="decile"
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    years = pivot["year"].to_list()
    decile_cols = [c for c in pivot.columns if c != "year"]

    # Stacked area
    values = [pivot[col].to_list() for col in decile_cols]
    ax.stackplot(years, *values, labels=[f"D{c}" for c in decile_cols], alpha=0.8)

    ax.set_xlabel("Year")
    ax.set_ylabel("Cooking Spend (£m)")
    ax.set_title("Cooking Appliance Spend by Income Decile")
    ax.legend(loc="upper left", ncol=2, fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "income_decile_panel.png")
    plt.close()

    logger.info("Income decile panel chart saved")


def plot_price_decile_panels(
    nb_panel: pl.DataFrame,
    rr_panel: pl.DataFrame,
    output_dir: Path,
) -> None:
    """Plot cooking expenditure by home-price decile (NB and R&R).

    Args:
        nb_panel: New Build panel (year, decile, cooking_value_nb)
        rr_panel: R&R panel (year, decile, cooking_value_rr)
        output_dir: Output directory for charts
    """
    logger.info("Plotting price decile panels...")

    setup_chart_defaults()

    # New Build panel
    nb_pivot = nb_panel.pivot(
        values="cooking_value_nb",
        index="year",
        columns="decile"
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    years = nb_pivot["year"].to_list()
    decile_cols = [c for c in nb_pivot.columns if c != "year"]
    values = [nb_pivot[col].to_list() for col in decile_cols]
    ax.stackplot(years, *values, labels=[f"D{c}" for c in decile_cols], alpha=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cooking Value (£m)")
    ax.set_title("Cooking Appliance Value by Home-Price Decile (New Build)")
    ax.legend(loc="upper left", ncol=2, fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "newbuild_price_decile_panel.png")
    plt.close()

    # R&R panel
    rr_pivot = rr_panel.pivot(
        values="cooking_value_rr",
        index="year",
        columns="decile"
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    years = rr_pivot["year"].to_list()
    decile_cols = [c for c in rr_pivot.columns if c != "year"]
    values = [rr_pivot[col].to_list() for col in decile_cols]
    ax.stackplot(years, *values, labels=[f"D{c}" for c in decile_cols], alpha=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cooking Value (£m)")
    ax.set_title("Cooking Appliance Value by Home-Price Decile (R&R)")
    ax.legend(loc="upper left", ncol=2, fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "rr_price_decile_panel.png")
    plt.close()

    logger.info("Price decile panel charts saved")


def plot_range_share(
    range_share_df: pl.DataFrame,
    output_dir: Path,
) -> None:
    """Plot range cooker share over time.

    Args:
        range_share_df: Range share (year, range_share)
        output_dir: Output directory for charts
    """
    logger.info("Plotting range cooker share...")

    setup_chart_defaults()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range_share_df["year"], range_share_df["range_share"] * 100)
    ax.set_xlabel("Year")
    ax.set_ylabel("Range Share (%)")
    ax.set_title("Range Cooker Share within Cooking Appliances")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "range_share.png")
    plt.close()

    logger.info("Range share chart saved")


def plot_price_band_mix(
    band_summary_df: pl.DataFrame,
    panel_name: str,
    output_dir: Path,
) -> None:
    """Plot Luxury vs Mass-Premium mix over time.

    Args:
        band_summary_df: Price band summary (year, mass_premium_share, luxury_share)
        panel_name: Name of panel (for title)
        output_dir: Output directory for charts
    """
    logger.info(f"Plotting price band mix for {panel_name}...")

    setup_chart_defaults()

    # Aggregate by year
    by_year = band_summary_df.group_by("year").agg([
        pl.sum("total_mass_premium_value").alias("mass_premium"),
        pl.sum("total_luxury_value").alias("luxury"),
    ])

    by_year = by_year.with_columns([
        (pl.col("mass_premium") / (pl.col("mass_premium") + pl.col("luxury")) * 100).alias("mass_premium_pct"),
        (pl.col("luxury") / (pl.col("mass_premium") + pl.col("luxury")) * 100).alias("luxury_pct"),
    ])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(by_year["year"], by_year["luxury_pct"], label="Luxury", marker="o")
    ax.plot(by_year["year"], by_year["mass_premium_pct"], label="Mass-Premium", marker="s")
    ax.set_xlabel("Year")
    ax.set_ylabel("Share (%)")
    ax.set_title(f"Price Band Mix: {panel_name}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / f"price_band_mix_{panel_name.lower().replace(' ', '_')}.png")
    plt.close()

    logger.info(f"Price band mix chart for {panel_name} saved")
