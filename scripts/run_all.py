#!/usr/bin/env python3
"""Main pipeline runner for UK cooking appliance datasets.

Orchestrates data ingestion, cleaning, transformation, and output generation.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    ingest,
    clean,
    hhfce,
    deciles_income,
    ppd_deciles,
    newbuild_pool,
    rr_anchor,
    range_share,
    price_bands,
    panels,
    charts,
)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for pipeline."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_config(config_path: Path, assumptions_path: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load configuration and assumptions YAML files."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    with open(assumptions_path) as f:
        assumptions = yaml.safe_load(f)

    return config, assumptions


def run_pipeline(
    config: Dict[str, Any],
    assumptions: Dict[str, Any],
    project_root: Path,
) -> None:
    """Execute full pipeline from data ingestion to output generation.

    Args:
        config: config.yaml dict
        assumptions: ASSUMPTIONS.yaml dict
        project_root: Project root directory
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("UK COOKING APPLIANCE DATASETS PIPELINE")
    logger.info("=" * 80)

    # Paths
    raw_data_dir = project_root / "data" / "raw"
    processed_data_dir = project_root / "data" / "processed"
    output_dir = project_root / "outputs" / "tables"
    figures_dir = project_root / "outputs" / "figures"

    raw_data_dir.mkdir(parents=True, exist_ok=True)
    processed_data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # ====================
    # STEP 1: Data Ingestion
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 1: Data Ingestion")
    logger.info("=" * 80)

    ingester = ingest.DataIngester(
        raw_data_dir=raw_data_dir,
        config=config,
        cache_downloads=config.get("processing", {}).get("cache_downloads", True),
    )

    sources = ingester.fetch_all()

    # ====================
    # STEP 2: Data Cleaning
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: Data Cleaning")
    logger.info("=" * 80)

    # Clean each source
    construction_clean = clean.clean_construction_output(sources["construction_output"])
    clean.save_cleaned_data(construction_clean, processed_data_dir / "construction_output.parquet", "construction_output")

    house_building_clean = clean.clean_house_building(sources["house_building"])
    clean.save_cleaned_data(house_building_clean, processed_data_dir / "house_building.parquet", "house_building")

    year_start = config.get("YEARS_START", 2000)
    if year_start == "min":
        year_start = 2000  # Default minimum

    year_end = config.get("YEARS_END", "latest")
    if year_end == "latest":
        year_end = 2023  # Current default

    ppd_clean_lazy = clean.clean_ppd(sources["ppd"], year_start, year_end)

    transactions_clean = clean.clean_transactions(sources["transactions"])
    clean.save_cleaned_data(transactions_clean, processed_data_dir / "transactions.parquet", "transactions")

    mortgage_clean = clean.clean_mortgage_approvals(sources["mortgage_approvals"])
    clean.save_cleaned_data(mortgage_clean, processed_data_dir / "mortgage_approvals.parquet", "mortgage_approvals")

    consumer_trends_clean = clean.clean_consumer_trends(sources["consumer_trends"])
    clean.save_cleaned_data(consumer_trends_clean, processed_data_dir / "consumer_trends.parquet", "consumer_trends")

    cpih_weights_clean = clean.clean_cpih_weights(sources["cpih_weights"])
    clean.save_cleaned_data(cpih_weights_clean, processed_data_dir / "cpih_weights.parquet", "cpih_weights")

    family_spending_clean = clean.clean_family_spending(sources["family_spending"])
    clean.save_cleaned_data(family_spending_clean, processed_data_dir / "family_spending.parquet", "family_spending")

    trade_clean = clean.clean_trade(sources["trade"])
    clean.save_cleaned_data(trade_clean, processed_data_dir / "trade.parquet", "trade")

    # ====================
    # STEP 3: Extract Cooking-Only from HHFCE
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: Extract Cooking-Only Expenditure")
    logger.info("=" * 80)

    cooking_quarterly = hhfce.extract_cooking_only(
        consumer_trends_clean,
        cpih_weights_clean,
        config,
    )

    cooking_annual = hhfce.aggregate_to_annual(cooking_quarterly)
    clean.save_cleaned_data(cooking_annual, processed_data_dir / "cooking_annual.parquet", "cooking_annual")

    cooking_volume = hhfce.compute_cooking_volume_index(
        cooking_annual,
        construction_clean,
        base_year=config.get("INDEX_BASE_YEAR", 2019),
    )
    clean.save_cleaned_data(cooking_volume, processed_data_dir / "cooking_volume.parquet", "cooking_volume")

    # ====================
    # STEP 4: Distribute by Income Decile
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: Distribute by Income Decile")
    logger.info("=" * 80)

    cooking_by_income_decile = deciles_income.distribute_by_income_decile(
        cooking_annual,
        family_spending_clean,
        config,
    )

    # ====================
    # STEP 5: Compute PPD Price Deciles
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 5: Compute Home-Price Deciles")
    logger.info("=" * 80)

    nb_deciles, ex_deciles = ppd_deciles.compute_ppd_deciles_both(ppd_clean_lazy)

    # Apply premium uplift to top deciles
    nb_deciles = ppd_deciles.apply_premium_uplift(
        nb_deciles,
        top_deciles=[9, 10],
        uplift_factor=1.0 + assumptions.get("premium_uplift_newbuild_top_deciles", 0.10),
    )

    clean.save_cleaned_data(nb_deciles, processed_data_dir / "ppd_nb_deciles.parquet", "ppd_nb_deciles")
    clean.save_cleaned_data(ex_deciles, processed_data_dir / "ppd_ex_deciles.parquet", "ppd_ex_deciles")

    # ====================
    # STEP 6: New Build Attach Pool
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 6: Compute New Build Attach Pool")
    logger.info("=" * 80)

    attach_pool = newbuild_pool.compute_newbuild_attach_pool(
        house_building_clean,
        assumptions,
    )

    # Base cooking set value (from ASPs)
    base_set_value = assumptions.get("ASPs", {}).get("built_in_sets", {}).get("mass_premium", 1600)

    nb_value_by_decile = newbuild_pool.compute_newbuild_value_by_decile(
        attach_pool,
        nb_deciles,
        base_set_value,
        assumptions,
    )

    # ====================
    # STEP 7: R&R Anchor and Distribution
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 7: Compute R&R Cooking Spend")
    logger.info("=" * 80)

    rm_scale = rr_anchor.compute_rr_scale_factor(
        construction_clean,
        base_year=config.get("INDEX_BASE_YEAR", 2019),
    )

    rr_cooking = rr_anchor.compute_rr_cooking_spend(
        cooking_annual,
        rm_scale,
        assumptions,
    )

    rr_value_by_decile = rr_anchor.distribute_rr_by_price_decile(
        rr_cooking,
        ex_deciles,
    )

    # ====================
    # STEP 8: Range Cooker Share Estimation
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 8: Estimate Range Cooker Share")
    logger.info("=" * 80)

    range_share_trade = range_share.estimate_range_share_from_trade(
        trade_clean,
        cooking_annual,
    )

    range_share_retail = range_share.estimate_range_share_from_retail(assumptions)

    range_share_blended = range_share.blend_range_shares(
        range_share_trade,
        range_share_retail,
        assumptions,
    )

    clean.save_cleaned_data(range_share_blended, processed_data_dir / "range_share.parquet", "range_share")

    # ====================
    # STEP 9: Assemble Panels
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 9: Assemble Final Panels")
    logger.info("=" * 80)

    income_panel = panels.assemble_income_panel(
        cooking_by_income_decile,
        range_share_blended,
        assumptions,
    )

    nb_panel, rr_panel = panels.assemble_price_decile_panels(
        nb_value_by_decile,
        rr_value_by_decile,
    )

    # ====================
    # STEP 10: Apply Price Bands
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 10: Apply Luxury vs Mass-Premium Price Bands")
    logger.info("=" * 80)

    income_panel_bands, nb_panel_bands, rr_panel_bands = price_bands.apply_price_bands_to_panels(
        income_panel,
        nb_panel,
        rr_panel,
        assumptions,
    )

    # ====================
    # STEP 11: Save Outputs
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("STEP 11: Save Output Tables")
    logger.info("=" * 80)

    # Save panels for all years
    panels.save_panels(income_panel, nb_panel, rr_panel, output_dir, year="all")

    # Save price band mix
    panels.save_price_band_mix(income_panel_bands, nb_panel_bands, rr_panel_bands, output_dir, year="all")

    # Generate coverage report
    coverage = panels.generate_coverage_report(
        income_panel,
        nb_panel,
        rr_panel,
        project_root / "coverage.json",
    )

    # ====================
    # STEP 12: Generate Charts
    # ====================
    if config.get("outputs", {}).get("generate_charts", True):
        logger.info("\n" + "=" * 80)
        logger.info("STEP 12: Generate Charts")
        logger.info("=" * 80)

        charts.plot_drivers(
            house_building_clean,
            construction_clean,
            consumer_trends_clean,
            figures_dir,
        )

        charts.plot_income_decile_panel(income_panel, figures_dir)
        charts.plot_price_decile_panels(nb_panel, rr_panel, figures_dir)
        charts.plot_range_share(range_share_blended, figures_dir)

        # Price band mix charts
        from models.price_bands import create_price_band_summary

        income_summary = create_price_band_summary(income_panel_bands, ["year", "decile"])
        charts.plot_price_band_mix(income_summary, "Income Decile", figures_dir)

    # ====================
    # Pipeline Complete
    # ====================
    logger.info("\n" + "=" * 80)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Outputs saved to: {output_dir}")
    logger.info(f"Charts saved to: {figures_dir}")
    logger.info(f"Coverage report: {project_root / 'coverage.json'}")
    logger.info("\nCoverage Summary:")
    logger.info(f"  Income decile panel: {coverage['income_decile_panel']['first_year']}-{coverage['income_decile_panel']['last_year']}")
    logger.info(f"  New Build panel: {coverage['newbuild_price_decile_panel']['first_year']}-{coverage['newbuild_price_decile_panel']['last_year']}")
    logger.info(f"  R&R panel: {coverage['rr_price_decile_panel']['first_year']}-{coverage['rr_price_decile_panel']['last_year']}")


def main() -> None:
    """Main entry point for pipeline CLI."""
    parser = argparse.ArgumentParser(
        description="UK Cooking Appliance Datasets Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default config (2000 to latest)
  python -m scripts.run_all

  # Specify year range
  python -m scripts.run_all --years-start 2010 --years-end 2022

  # Start from earliest available data
  python -m scripts.run_all --years-start min

  # Change frequency to quarterly (where available)
  python -m scripts.run_all --frequency quarterly

  # Set log level
  python -m scripts.run_all --log-level DEBUG
        """,
    )

    parser.add_argument(
        "--years-start",
        type=str,
        default=None,
        help="Start year (YYYY) or 'min' for earliest available (default: from config)",
    )

    parser.add_argument(
        "--years-end",
        type=str,
        default=None,
        help="End year (YYYY) or 'latest' for most recent (default: from config)",
    )

    parser.add_argument(
        "--frequency",
        type=str,
        choices=["annual", "quarterly"],
        default=None,
        help="Time series frequency (default: from config)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.yaml (default: conf/config.yaml)",
    )

    parser.add_argument(
        "--assumptions",
        type=Path,
        default=None,
        help="Path to ASSUMPTIONS.yaml (default: conf/ASSUMPTIONS.yaml)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Determine project root
    project_root = Path(__file__).parent.parent

    # Load configuration
    config_path = args.config or project_root / "conf" / "config.yaml"
    assumptions_path = args.assumptions or project_root / "conf" / "ASSUMPTIONS.yaml"

    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    if not assumptions_path.exists():
        logger.error(f"Assumptions file not found: {assumptions_path}")
        sys.exit(1)

    config, assumptions = load_config(config_path, assumptions_path)

    # Override config with CLI arguments
    if args.years_start:
        config["YEARS_START"] = args.years_start if args.years_start != "min" else "min"

    if args.years_end:
        config["YEARS_END"] = args.years_end

    if args.frequency:
        config["FREQUENCY"] = args.frequency

    # Set log level in config
    config.setdefault("processing", {})["log_level"] = args.log_level

    # Run pipeline
    try:
        run_pipeline(config, assumptions, project_root)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
