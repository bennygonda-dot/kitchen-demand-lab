#!/usr/bin/env python3
"""
BPS Luxury Single-Family Permits Dataset Builder - LOCAL FILE VERSION

Reads U.S. Census Building Permits Survey (BPS) data from locally downloaded files,
combines single-family units and valuations, computes average valuation per unit,
and flags top quintile (80th) and top decile (90th) luxury markets each month.

SETUP:
1. Download Census BPS files using download_census_files.sh
2. Or manually download files to:
   - input_data/historical/ (text files: ma*.txt from 1995-2019-10)
   - input_data/modern/ (Excel files: cbsa*.xlsx from 2019-11-present)

Outputs:
  - luxury_sf_permits_by_cbsa_month.csv (CBSA-month panel)
  - national_luxury_sf_pipeline.csv (national monthly aggregates)
  - data_dictionary.json (column descriptions)
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np


# Configuration
INPUT_DIR_HISTORICAL = Path("input_data/historical")
INPUT_DIR_MODERN = Path("input_data/modern")
OUTPUT_DIR = Path("out")
OUTPUT_DIR.mkdir(exist_ok=True)

# Date ranges
HISTORICAL_START = (1995, 1)
HISTORICAL_END = (2019, 10)
MODERN_START = (2019, 11)
MODERN_END = (datetime.now().year, datetime.now().month)


def generate_month_range(start_year_month, end_year_month):
    """Generate list of (year, month) tuples."""
    start_year, start_month = start_year_month
    end_year, end_month = end_year_month

    months = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        months.append((year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def fetch_historical_metro_data(year, month):
    """
    Read historical Metro text tables from local files (1995-2019-10).
    Returns DataFrame with columns: year, month, cbsa_code, cbsa_name, sf_units, sf_val
    """
    month_str = f"{month:02d}"
    year_short = f"{year % 100:02d}"

    # Try different filename patterns
    patterns = [
        f"ma{year}{month_str}t.txt",
        f"ma{year_short}{month_str}t.txt",
    ]

    for filename in patterns:
        filepath = INPUT_DIR_HISTORICAL / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    text = f.read()
                return parse_historical_text(text, year, month)
            except Exception as e:
                continue

    return None


def parse_historical_text(text, year, month):
    """
    Parse historical BPS Metro text file.
    These files contain metro area data with CBSA codes, names, units, and valuations.

    Format varies by year, but generally:
    - Fixed-width or tab-delimited
    - CBSA code (4-5 digits) | CBSA name | ... | SF units | SF valuation | ...
    """
    lines = text.strip().split('\n')
    records = []

    # Skip header lines and find data start
    data_start = 0
    for i, line in enumerate(lines):
        # Look for line with column headers
        if re.search(r'(CBSA|MSA|Area|Code)', line, re.IGNORECASE) and re.search(r'(Unit|Permit)', line, re.IGNORECASE):
            data_start = i + 1
            break
        # Or first line with CBSA code pattern
        if re.match(r'^\s*\d{4,5}\s+', line):
            data_start = i
            break

    for line in lines[data_start:]:
        # Skip empty lines and footers
        if not line.strip() or re.match(r'^\s*(Note|Source|---)', line, re.IGNORECASE):
            continue

        # Match: CBSA code (4-5 digits) + Name + data columns
        # Example: "10420   Akron, OH              850    185000"
        match = re.match(r'^\s*(\d{4,5})\s+([A-Za-z\s,\-\.\/\(\)]+?)\s+([\d\s,]+)$', line)

        if match:
            cbsa_code = match.group(1)
            cbsa_name = match.group(2).strip()
            numbers_str = match.group(3)

            # Extract all numbers (remove commas)
            numbers = [int(x.replace(',', '')) for x in re.findall(r'[\d,]+', numbers_str) if x.replace(',', '').isdigit()]

            if len(numbers) >= 2:
                # Heuristic: Usually columns are structured as
                # [Total Units, SF Units, MF Units, Total Val, SF Val, MF Val]
                # Or simpler: [SF Units, SF Val]
                # We want SF units and SF valuation

                # Strategy: Look for columns that make sense
                # SF units usually 10-10000 per metro per month
                # SF val usually in thousands or millions

                sf_units = 0
                sf_val = 0

                # If only 2 numbers: assume [units, val]
                if len(numbers) == 2:
                    sf_units = numbers[0]
                    sf_val = numbers[1] * 1000  # Values often in thousands

                # If more numbers, use heuristics
                elif len(numbers) >= 4:
                    # Common pattern: Total units, SF units, ..., Total val, SF val
                    # Or: SF units, MF units, SF val, MF val
                    # Pick second-smallest as units, largest/second-largest as valuation
                    sf_units = numbers[0] if numbers[0] < 10000 else numbers[1]
                    sf_val = max(numbers) if max(numbers) > 10000 else max(numbers) * 1000

                if sf_units > 0:
                    records.append({
                        'year': year,
                        'month': month,
                        'cbsa_code': cbsa_code,
                        'cbsa_name': cbsa_name,
                        'sf_units': sf_units,
                        'sf_val': sf_val
                    })

    if records:
        return pd.DataFrame(records)
    return None


def fetch_modern_cbsa_data(year, month):
    """
    Read modern CBSA Excel files from local directory (2019-11 onwards).
    Returns DataFrame with columns: year, month, cbsa_code, cbsa_name, sf_units, sf_val
    """
    month_str = f"{month:02d}"
    filename = f"cbsa{year}{month_str}.xlsx"
    filepath = INPUT_DIR_MODERN / filename

    if filepath.exists():
        try:
            return parse_modern_excel(filepath, year, month)
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            return None

    return None


def parse_modern_excel(filepath, year, month):
    """
    Parse modern BPS CBSA Excel file.
    Format: Excel workbook with CBSA data including units and valuations.
    """
    try:
        # Read Excel file - usually first sheet has the data
        excel_file = pd.ExcelFile(filepath)
        sheet_name = excel_file.sheet_names[0]
        df = pd.read_excel(filepath, sheet_name=sheet_name)

        # Find the header row (may not be first row)
        header_row = 0
        for i in range(min(20, len(df))):
            row_str = ' '.join([str(x).lower() for x in df.iloc[i] if pd.notna(x)])
            if 'cbsa' in row_str and ('unit' in row_str or 'permit' in row_str):
                header_row = i
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_row)
                break

        # Identify columns
        code_col = None
        name_col = None
        units_col = None
        val_col = None

        for col in df.columns:
            col_lower = str(col).lower()

            if 'cbsa' in col_lower and 'code' in col_lower:
                code_col = col
            elif 'cbsa' in col_lower and ('name' in col_lower or 'title' in col_lower or 'area' in col_lower):
                name_col = col
            elif '1-unit' in col_lower or '1 unit' in col_lower or ('single' in col_lower and 'unit' in col_lower):
                units_col = col
            elif '1-unit' in col_lower and ('val' in col_lower or 'construction' in col_lower):
                val_col = col
            elif 'single' in col_lower and 'family' in col_lower:
                if 'unit' in col_lower and not units_col:
                    units_col = col
                elif ('val' in col_lower or 'construction' in col_lower) and not val_col:
                    val_col = col

        # If not found, try positional approach
        if not code_col or not name_col:
            cols = list(df.columns)
            for i, col in enumerate(cols[:5]):
                if not code_col and df[col].dtype in [np.int64, np.float64]:
                    # Check if looks like CBSA codes (5-digit numbers)
                    sample = df[col].dropna().head(10)
                    if len(sample) > 0 and all(10000 <= x < 99999 for x in sample if pd.notna(x)):
                        code_col = col
                        if i + 1 < len(cols):
                            name_col = cols[i + 1]
                        break

        # Find units and valuation columns by scanning data columns
        if not units_col or not val_col:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col == code_col:
                    continue
                sample = df[col].dropna()
                if len(sample) == 0:
                    continue

                # Units typically 0-5000 range
                # Valuations typically 100000+ (millions)
                if not units_col and sample.median() < 5000:
                    units_col = col
                elif not val_col and sample.median() > 10000:
                    val_col = col

        if all([code_col, name_col, units_col, val_col]):
            result = df[[code_col, name_col, units_col, val_col]].copy()
            result.columns = ['cbsa_code', 'cbsa_name', 'sf_units', 'sf_val']

            # Clean data
            result['cbsa_code'] = pd.to_numeric(result['cbsa_code'], errors='coerce')
            result['cbsa_name'] = result['cbsa_name'].astype(str)
            result['sf_units'] = pd.to_numeric(result['sf_units'], errors='coerce').fillna(0).astype(int)
            result['sf_val'] = pd.to_numeric(result['sf_val'], errors='coerce').fillna(0).astype(int)

            # Filter out invalid rows
            result = result[result['cbsa_code'].notna()].copy()
            result = result[result['cbsa_code'] > 10000].copy()  # Valid CBSA codes are 5 digits

            result['year'] = year
            result['month'] = month

            return result[['year', 'month', 'cbsa_code', 'cbsa_name', 'sf_units', 'sf_val']]

    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

    return None


def compute_luxury_flags(df):
    """
    For each month, compute average valuation per unit and flag top quintile/decile.
    """
    results = []

    for (year, month), group in df.groupby(['year', 'month']):
        # Compute average valuation per unit
        group = group.copy()
        group['sf_avg_val_per_unit'] = np.where(
            group['sf_units'] > 0,
            group['sf_val'] / group['sf_units'],
            np.nan
        )

        # Filter to CBSAs with valid data for percentile calculation
        valid = group[group['sf_avg_val_per_unit'].notna() & (group['sf_avg_val_per_unit'] > 0)].copy()

        if len(valid) > 0:
            # Calculate percentiles
            p80 = valid['sf_avg_val_per_unit'].quantile(0.80)
            p90 = valid['sf_avg_val_per_unit'].quantile(0.90)

            # Flag luxury markets
            group['is_top_quintile'] = (group['sf_avg_val_per_unit'] >= p80).astype(int)
            group['is_top_decile'] = (group['sf_avg_val_per_unit'] >= p90).astype(int)
            group['p80_threshold'] = p80
            group['p90_threshold'] = p90
        else:
            group['is_top_quintile'] = 0
            group['is_top_decile'] = 0
            group['p80_threshold'] = np.nan
            group['p90_threshold'] = np.nan

        results.append(group)

    return pd.concat(results, ignore_index=True)


def aggregate_national(df):
    """
    Aggregate to national monthly totals.
    """
    national = df.groupby(['year', 'month']).apply(
        lambda x: pd.Series({
            'sf_units': x['sf_units'].sum(),
            'sf_val': x['sf_val'].sum(),
            'top_quintile_units': (x['is_top_quintile'] * x['sf_units']).sum(),
            'top_decile_units': (x['is_top_decile'] * x['sf_units']).sum(),
        })
    ).reset_index()

    # Compute shares
    national['top_quintile_share'] = national['top_quintile_units'] / national['sf_units']
    national['top_decile_share'] = national['top_decile_units'] / national['sf_units']
    national['national_avg_val_per_unit'] = national['sf_val'] / national['sf_units']

    # Create date column
    national['date'] = pd.to_datetime(national[['year', 'month']].assign(day=1))

    # Select and order columns
    return national[['date', 'year', 'month', 'sf_units', 'sf_val',
                     'national_avg_val_per_unit', 'top_quintile_units', 'top_quintile_share',
                     'top_decile_units', 'top_decile_share']]


def create_data_dictionary():
    """Create data dictionary for outputs."""
    dictionary = {
        "luxury_sf_permits_by_cbsa_month.csv": {
            "description": "CBSA-month panel of single-family building permits with luxury market flags",
            "columns": {
                "date": "Date (first day of month)",
                "year": "Year",
                "month": "Month (1-12)",
                "cbsa_code": "CBSA/Metro area code",
                "cbsa_name": "CBSA/Metro area name",
                "sf_units": "Number of single-family units permitted",
                "sf_val": "Total valuation of single-family permits ($)",
                "sf_avg_val_per_unit": "Average valuation per single-family unit ($)",
                "is_top_quintile": "1 if CBSA is in top quintile (≥80th percentile) for this month, 0 otherwise",
                "is_top_decile": "1 if CBSA is in top decile (≥90th percentile) for this month, 0 otherwise",
                "p80_threshold": "80th percentile threshold for average valuation this month ($)",
                "p90_threshold": "90th percentile threshold for average valuation this month ($)"
            }
        },
        "national_luxury_sf_pipeline.csv": {
            "description": "National monthly aggregates of single-family building permits and luxury shares",
            "columns": {
                "date": "Date (first day of month)",
                "year": "Year",
                "month": "Month (1-12)",
                "sf_units": "Total single-family units permitted nationally",
                "sf_val": "Total valuation of single-family permits nationally ($)",
                "national_avg_val_per_unit": "National average valuation per unit ($)",
                "top_quintile_units": "Number of SF units in CBSAs flagged as top quintile",
                "top_quintile_share": "Share of SF units in top quintile CBSAs",
                "top_decile_units": "Number of SF units in CBSAs flagged as top decile",
                "top_decile_share": "Share of SF units in top decile CBSAs"
            }
        }
    }
    return dictionary


def main():
    """Main execution function."""
    print("=" * 80)
    print("BPS Luxury Single-Family Permits Dataset Builder")
    print("LOCAL FILE VERSION")
    print("=" * 80)
    print()

    # Check for input directories
    if not INPUT_DIR_HISTORICAL.exists() and not INPUT_DIR_MODERN.exists():
        print("ERROR: Input data directories not found!")
        print()
        print("Please create input_data/ directory and download Census BPS files:")
        print("  1. Run: ./download_census_files.sh")
        print("  2. Or manually download files to:")
        print(f"     - {INPUT_DIR_HISTORICAL}/ (text files from 1995-2019)")
        print(f"     - {INPUT_DIR_MODERN}/ (Excel files from 2019-11 onwards)")
        print()
        return

    all_data = []
    months_processed = []
    months_skipped = []

    # Process historical data (1995-2019-10)
    print("Processing historical Metro data (1995-2019-10)...")
    historical_months = generate_month_range(HISTORICAL_START, HISTORICAL_END)

    for year, month in historical_months:
        print(f"  {year}-{month:02d}...", end=" ")
        data = fetch_historical_metro_data(year, month)

        if data is not None and len(data) > 0:
            all_data.append(data)
            months_processed.append((year, month))
            print(f"✓ ({len(data)} CBSAs)")
        else:
            months_skipped.append((year, month))
            print("✗ (not found or empty)")

    # Process modern CBSA data (2019-11 onwards)
    print("\nProcessing modern CBSA data (2019-11 onwards)...")
    modern_months = generate_month_range(MODERN_START, MODERN_END)

    for year, month in modern_months:
        print(f"  {year}-{month:02d}...", end=" ")
        data = fetch_modern_cbsa_data(year, month)

        if data is not None and len(data) > 0:
            all_data.append(data)
            months_processed.append((year, month))
            print(f"✓ ({len(data)} CBSAs)")
        else:
            months_skipped.append((year, month))
            print("✗ (not found or empty)")

    # Combine all data
    print("\nCombining data...")
    if not all_data:
        print("ERROR: No data was successfully loaded!")
        print()
        print("Please ensure Census BPS files are downloaded to input_data/ directories.")
        return

    combined = pd.concat(all_data, ignore_index=True)
    print(f"Total records: {len(combined):,}")

    # Compute luxury flags
    print("\nComputing luxury market flags (top quintile/decile per month)...")
    luxury_panel = compute_luxury_flags(combined)

    # Add date column
    luxury_panel['date'] = pd.to_datetime(luxury_panel[['year', 'month']].assign(day=1))

    # Sort and reorder columns
    luxury_panel = luxury_panel.sort_values(['date', 'cbsa_code']).reset_index(drop=True)
    luxury_panel['cbsa_code'] = luxury_panel['cbsa_code'].astype(int)
    luxury_panel = luxury_panel[['date', 'year', 'month', 'cbsa_code', 'cbsa_name',
                                 'sf_units', 'sf_val', 'sf_avg_val_per_unit',
                                 'is_top_quintile', 'is_top_decile',
                                 'p80_threshold', 'p90_threshold']]

    # Aggregate national
    print("Aggregating national totals...")
    national = aggregate_national(luxury_panel)

    # Save outputs
    print("\nSaving outputs...")
    cbsa_output = OUTPUT_DIR / "luxury_sf_permits_by_cbsa_month.csv"
    national_output = OUTPUT_DIR / "national_luxury_sf_pipeline.csv"
    dict_output = OUTPUT_DIR / "data_dictionary.json"

    luxury_panel.to_csv(cbsa_output, index=False)
    print(f"  ✓ {cbsa_output}")

    national.to_csv(national_output, index=False)
    print(f"  ✓ {national_output}")

    data_dict = create_data_dictionary()
    with open(dict_output, 'w') as f:
        json.dump(data_dict, f, indent=2)
    print(f"  ✓ {dict_output}")

    # Print summary
    print("\n" + "=" * 80)
    print("RUN SUMMARY")
    print("=" * 80)

    if months_processed:
        date_range = f"{months_processed[0][0]}-{months_processed[0][1]:02d} to {months_processed[-1][0]}-{months_processed[-1][1]:02d}"
    else:
        date_range = "N/A"

    print(f"Date range covered: {date_range}")
    print(f"Months successfully parsed: {len(months_processed)}")
    print(f"Months skipped: {len(months_skipped)}")
    print(f"Total CBSA-month observations: {len(luxury_panel):,}")
    print(f"Unique CBSAs: {luxury_panel['cbsa_code'].nunique():,}")

    # Preview outputs
    print("\n" + "-" * 80)
    print("PREVIEW: luxury_sf_permits_by_cbsa_month.csv (last 6 lines)")
    print("-" * 80)
    print(luxury_panel.tail(6).to_string(index=False))

    print("\n" + "-" * 80)
    print("PREVIEW: national_luxury_sf_pipeline.csv (last 6 lines)")
    print("-" * 80)
    print(national.tail(6).to_string(index=False))

    print("\n" + "=" * 80)
    print("COMPLETE! Outputs saved to 'out/' directory.")
    print("=" * 80)


if __name__ == "__main__":
    main()
