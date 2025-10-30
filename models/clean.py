"""Data cleaning and harmonization module.

Normalizes columns, dtypes, time indexes across all data sources.
Converts to consistent Polars DataFrames with standard schema.
"""

import logging
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import polars as pl

logger = logging.getLogger(__name__)


def clean_construction_output(raw_path: Path) -> pl.DataFrame:
    """Clean ONS Construction Output data (Private Housing R&M).

    Returns:
        DataFrame with columns: year, quarter, rm_value, rm_volume
    """
    logger.info("Cleaning construction output data...")

    # Read Excel with pandas first (more flexible for messy formats)
    df = pd.read_excel(raw_path, sheet_name=0)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Convert to Polars
    df_pl = pl.from_pandas(df)

    # Ensure required columns exist
    required = ["year", "private_housing_rm_value", "private_housing_rm_volume"]
    missing = [c for c in required if c not in df_pl.columns]
    if missing:
        logger.warning(f"Missing columns {missing}, using available columns")

    # Standardize schema
    cleaned = df_pl.select([
        pl.col("year").cast(pl.Int32).alias("year"),
        pl.col("quarter").cast(pl.Utf8).alias("quarter") if "quarter" in df_pl.columns else pl.lit("Q1").alias("quarter"),
        pl.col("private_housing_rm_value").cast(pl.Float64).alias("rm_value"),
        pl.col("private_housing_rm_volume").cast(pl.Float64).alias("rm_volume"),
    ])

    logger.info(f"Cleaned construction output: {len(cleaned)} rows")
    return cleaned


def clean_house_building(raw_path: Path) -> pl.DataFrame:
    """Clean ONS House Building completions data.

    Returns:
        DataFrame with columns: year, quarter, completions_uk
    """
    logger.info("Cleaning house building data...")

    df = pd.read_excel(raw_path, sheet_name=0)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df_pl = pl.from_pandas(df)

    cleaned = df_pl.select([
        pl.col("year").cast(pl.Int32).alias("year"),
        pl.col("quarter").cast(pl.Utf8).alias("quarter") if "quarter" in df_pl.columns else pl.lit("Q1").alias("quarter"),
        pl.col("completions_uk").cast(pl.Float64).alias("completions_uk"),
    ])

    logger.info(f"Cleaned house building: {len(cleaned)} rows")
    return cleaned


def clean_ppd(raw_path: Path, year_start: int = 2000, year_end: int = 2023) -> pl.LazyFrame:
    """Clean Land Registry Price Paid Data using lazy scan for large file.

    Returns:
        LazyFrame with columns: date, price, new_build (bool), property_type
    """
    logger.info(f"Cleaning PPD data (lazy scan) for {year_start}-{year_end}...")

    # Lazy scan for efficiency with large file
    df = pl.scan_csv(
        raw_path,
        has_header=True,
        try_parse_dates=True,
    )

    # Check schema to determine if columns need renaming
    schema = df.collect_schema()
    col_names_lower = [c.lower() for c in schema.names()]

    # Map common column name variations to standard names
    col_mapping = {}
    if "price" in col_names_lower:
        col_mapping["price"] = schema.names()[col_names_lower.index("price")]
    if "date" in col_names_lower:
        col_mapping["date"] = schema.names()[col_names_lower.index("date")]
    if "newbuild" in col_names_lower:
        col_mapping["new_build"] = schema.names()[col_names_lower.index("newbuild")]
    if "propertytype" in col_names_lower:
        col_mapping["property_type"] = schema.names()[col_names_lower.index("propertytype")]

    # Standardize schema and filter years
    date_col = col_mapping.get("date", "Date")

    # Handle date parsing - check if already date type
    date_expr = pl.col(date_col).alias("date")
    if schema[date_col] == pl.Utf8:
        date_expr = pl.col(date_col).str.strptime(pl.Date, "%Y-%m-%d", strict=False).alias("date")

    cleaned = df.select([
        date_expr,
        pl.col(col_mapping.get("price", "Price")).cast(pl.Int64).alias("price"),
        (pl.col(col_mapping.get("new_build", "NewBuild")) == 1).alias("new_build"),  # Handle both "Y" and 1
        pl.col(col_mapping.get("property_type", "PropertyType")).cast(pl.Utf8).alias("property_type"),
    ]).filter(
        (pl.col("date").dt.year() >= year_start) &
        (pl.col("date").dt.year() <= year_end)
    )

    logger.info("PPD data lazy frame prepared (will execute on collect)")
    return cleaned


def clean_transactions(raw_path: Path) -> pl.DataFrame:
    """Clean HMRC monthly transactions data.

    Returns:
        DataFrame with columns: date, transactions
    """
    logger.info("Cleaning HMRC transactions data...")

    df = pd.read_csv(raw_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df_pl = pl.from_pandas(df)

    cleaned = df_pl.select([
        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d").alias("date"),
        pl.col("transactions").cast(pl.Int64).alias("transactions"),
    ])

    logger.info(f"Cleaned transactions: {len(cleaned)} rows")
    return cleaned


def clean_mortgage_approvals(raw_path: Path) -> pl.DataFrame:
    """Clean Bank of England mortgage approvals data.

    Returns:
        DataFrame with columns: date, approvals
    """
    logger.info("Cleaning mortgage approvals data...")

    df = pd.read_csv(raw_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df_pl = pl.from_pandas(df)

    cleaned = df_pl.select([
        pl.col("date").str.strptime(pl.Date, "%Y-%m-%d").alias("date"),
        pl.col("approvals").cast(pl.Int64).alias("approvals"),
    ])

    logger.info(f"Cleaned mortgage approvals: {len(cleaned)} rows")
    return cleaned


def clean_consumer_trends(raw_path: Path) -> pl.DataFrame:
    """Clean ONS Consumer Trends HHFCE data.

    Returns:
        DataFrame with columns: year, quarter, coicop_05_3_1 (£m current prices)
    """
    logger.info("Cleaning consumer trends data...")

    df = pd.read_excel(raw_path, sheet_name=0)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(".", "_")

    df_pl = pl.from_pandas(df)

    cleaned = df_pl.select([
        pl.col("year").cast(pl.Int32).alias("year"),
        pl.col("quarter").cast(pl.Utf8).alias("quarter"),
        pl.col("coicop_05_3_1").cast(pl.Float64).alias("hhfce_05_3_1"),
    ])

    logger.info(f"Cleaned consumer trends: {len(cleaned)} rows")
    return cleaned


def clean_cpih_weights(raw_path: Path) -> pl.DataFrame:
    """Clean ONS CPIH weights data.

    Returns:
        DataFrame with columns: year, item_code, item_name, weight
    """
    logger.info("Cleaning CPIH weights data...")

    df = pd.read_excel(raw_path, sheet_name=0)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df_pl = pl.from_pandas(df)

    # Extract year from column or deduce from file
    # CPIH weights tables vary in format; adapt as needed

    cleaned = df_pl.select([
        pl.col("year").cast(pl.Int32).alias("year"),
        pl.col("coicop_05_3_1_weight").cast(pl.Float64).alias("weight_total"),
        pl.col("coicop_05_3_1_3_cookers_weight").cast(pl.Float64).alias("weight_cookers"),
        pl.col("coicop_05_3_1_1_refrigerators_weight").cast(pl.Float64).alias("weight_refrigerators"),
    ])

    logger.info(f"Cleaned CPIH weights: {len(cleaned)} rows")
    return cleaned


def clean_family_spending(raw_path: Path) -> pl.DataFrame:
    """Clean ONS Family Spending (LCF) data by income decile.

    Returns:
        DataFrame with columns: year, decile, coicop_05_3_1_share
    """
    logger.info("Cleaning family spending data...")

    df = pd.read_excel(raw_path, sheet_name=0)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df_pl = pl.from_pandas(df)

    cleaned = df_pl.select([
        pl.col("year").cast(pl.Int32).alias("year"),
        pl.col("decile").cast(pl.Int32).alias("decile"),
        pl.col("coicop_05_3_1_share").cast(pl.Float64).alias("share"),
    ])

    logger.info(f"Cleaned family spending: {len(cleaned)} rows")
    return cleaned


def clean_trade(raw_path: Path) -> pl.DataFrame:
    """Clean HMRC UK Trade CN 8516.60 data.

    Returns:
        DataFrame with columns: year, cn_code, imports_gbp, exports_gbp
    """
    logger.info("Cleaning trade data...")

    df = pd.read_csv(raw_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df_pl = pl.from_pandas(df)

    cleaned = df_pl.select([
        pl.col("year").cast(pl.Int32).alias("year"),
        pl.col("cn_code").cast(pl.Utf8).alias("cn_code"),
        pl.col("imports_gbp").cast(pl.Float64).alias("imports_gbp"),
        pl.col("exports_gbp").cast(pl.Float64).alias("exports_gbp"),
    ])

    # Compute apparent consumption (domestic market)
    cleaned = cleaned.with_columns([
        (pl.col("imports_gbp") - pl.col("exports_gbp")).alias("apparent_consumption_gbp")
    ])

    logger.info(f"Cleaned trade data: {len(cleaned)} rows")
    return cleaned


def save_cleaned_data(df: pl.DataFrame, output_path: Path, name: str) -> None:
    """Save cleaned DataFrame to parquet."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(output_path)
    logger.info(f"Saved cleaned {name} to {output_path}")
