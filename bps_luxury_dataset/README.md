# BPS Luxury Single-Family Permits — Builder

This project pulls U.S. Census **Building Permits Survey (BPS)** metro/CBSA data, merges single-family **units** and **valuation**, computes **average valuation per SF unit**, and flags each CBSA–month as in the **top quintile (80th)** and **top decile (90th)** within that month. It also produces a national aggregate.

**Outputs**
- `luxury_sf_permits_by_cbsa_month.csv` — CBSA–month panel with flags for top decile/quintile.
- `national_luxury_sf_pipeline.csv` — national monthly totals & shares of SF units in top decile/quintile.
- `data_dictionary.json` — column descriptions.

**Coverage**
- 1995–2019-10: Historical metro **text** tables (units & valuation).
- 2019-11–present: Monthly **CBSA** Excel files.

**Luxury definition**
For each month: `sf_avg_val_per_unit = sf_val / sf_units`.
Compute percentiles across CBSAs for that month; flag:
- **Top quintile**: ≥ 80th percentile
- **Top decile**: ≥ 90th percentile

> You can switch to a fixed $ cutoff later (e.g., `$1,000,000 per unit`) by editing the code section marked "OPTIONAL: fixed $ cutoff".

**Run**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python make_luxury_permits_dataset.py
```

**Data Sources**
- Historical (1995–2019-10): https://www2.census.gov/econ/bps/Metro/
- Modern (2019-11–present): https://www2.census.gov/econ/bps/CBSA/

**Notes**
- The script gracefully skips missing months or malformed files.
- CBSAs with zero SF units or valuation are excluded from percentile calculations.
- National aggregates sum all CBSAs for each month.
