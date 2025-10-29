# Census BPS Data Download Instructions

The Census Bureau blocks automated downloads (returns 403 Forbidden). **You must download files manually** using your web browser.

## Download URLs

### Modern CBSA Data (2019-11 to present) - **START HERE**

**Directory listing:** https://www2.census.gov/econ/bps/CBSA/

**Direct download links for recent months:**

- Oct 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202410.xlsx
- Sep 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202409.xlsx
- Aug 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202408.xlsx
- Jul 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202407.xlsx
- Jun 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202406.xlsx
- May 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202405.xlsx
- Apr 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202404.xlsx
- Mar 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202403.xlsx
- Feb 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202402.xlsx
- Jan 2024: https://www2.census.gov/econ/bps/CBSA/cbsa202401.xlsx

**Pattern:** `https://www2.census.gov/econ/bps/CBSA/cbsa[YYYY][MM].xlsx`

**Files needed:** cbsa201911.xlsx through cbsa202410.xlsx (62 files)

### Historical Metro Data (1995-01 to 2019-10)

**Directory listing:** https://www2.census.gov/econ/bps/Metro/

**Examples:**
- Oct 2019: https://www2.census.gov/econ/bps/Metro/ma201910t.txt
- Jan 2010: https://www2.census.gov/econ/bps/Metro/ma201001t.txt
- Jan 2000: https://www2.census.gov/econ/bps/Metro/ma200001t.txt
- Jan 1995: https://www2.census.gov/econ/bps/Metro/ma9501t.txt

**Pattern:** `https://www2.census.gov/econ/bps/Metro/ma[YYMM]t.txt` or `ma[YYYYMM]t.txt`

**Files needed:** Approximately 298 .txt files from 1995-01 through 2019-10

## Download Steps

### Option 1: Minimal Dataset (2020-2024 only - Recommended to start)

1. Open your web browser
2. Visit: https://www2.census.gov/econ/bps/CBSA/
3. Download these 60 files (Jan 2020 - Oct 2024):
   - cbsa202001.xlsx through cbsa202012.xlsx (2020)
   - cbsa202101.xlsx through cbsa202112.xlsx (2021)
   - cbsa202201.xlsx through cbsa202212.xlsx (2022)
   - cbsa202301.xlsx through cbsa202312.xlsx (2023)
   - cbsa202401.xlsx through cbsa202410.xlsx (2024)
4. Save them to: `bps_luxury_dataset/input_data/modern/`
5. Run: `python3 make_luxury_permits_dataset_local.py`

### Option 2: Full Historical Dataset (1995-2024)

1. Download modern files (step 3 above) + cbsa201911.xlsx and cbsa201912.xlsx
2. Visit: https://www2.census.gov/econ/bps/Metro/
3. Download all `.txt` files from 1995 through October 2019
4. Save them to: `bps_luxury_dataset/input_data/historical/`
5. Run: `python3 make_luxury_permits_dataset_local.py`

### Option 3: Bulk Download Tools

If clicking 360 files sounds tedious, try these tools:

**DownThemAll (Firefox/Chrome extension):**
1. Install DownThemAll extension
2. Visit https://www2.census.gov/econ/bps/CBSA/
3. Open DownThemAll, filter for `*.xlsx`
4. Download all to `input_data/modern/`

**wget (command line, may be blocked):**
```bash
wget -r -np -nd -A "cbsa*.xlsx" -P input_data/modern/ https://www2.census.gov/econ/bps/CBSA/
wget -r -np -nd -A "ma*.txt" -P input_data/historical/ https://www2.census.gov/econ/bps/Metro/
```

**curl (command line, may be blocked):**
See `download_census_files.sh` script

## After Downloading

Once you have files in `input_data/`, run:

```bash
python3 make_luxury_permits_dataset_local.py
```

This will:
1. Read all local Census files
2. Parse CBSA codes, names, SF units, SF valuations
3. Compute average valuation per unit for each CBSA-month
4. Flag top quintile (≥80th percentile) and top decile (≥90th percentile)
5. Generate national monthly aggregates
6. Output:
   - `out/luxury_sf_permits_by_cbsa_month.csv`
   - `out/national_luxury_sf_pipeline.csv`
   - `out/data_dictionary.json`

## Troubleshooting

**"403 Forbidden" errors:**
- Census blocks automated downloads
- Must use web browser to download manually
- Try different browser if one doesn't work

**"Directory listing disabled":**
- Use direct file URLs listed above
- Replace [YYYY] and [MM] with year and month

**Files won't download:**
- Census may have changed file structure
- Check main BPS page: https://www.census.gov/construction/bps/
- Look for "Metro/CBSA Monthly" data downloads

**Need help?**
- Census Bureau Help: https://ask.census.gov/
- Check if files moved or renamed
- Some older files may not exist (script will skip them)

## File Structure After Download

```
bps_luxury_dataset/
├── input_data/
│   ├── historical/
│   │   ├── ma9501t.txt
│   │   ├── ma9502t.txt
│   │   ├── ...
│   │   └── ma201910t.txt
│   └── modern/
│       ├── cbsa201911.xlsx
│       ├── cbsa201912.xlsx
│       ├── ...
│       └── cbsa202410.xlsx
├── out/
│   └── (output files will be created here)
├── make_luxury_permits_dataset_local.py
└── DOWNLOAD_INSTRUCTIONS.md (this file)
```
