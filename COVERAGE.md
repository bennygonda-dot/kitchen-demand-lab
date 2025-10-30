# Data Coverage Report

Data availability and limitations by source and output panel.

**Note**: This is a template. Run the pipeline to generate actual `coverage.json` with specific first/last years.

## Overview

This document describes:
- Temporal coverage by data source
- Output panel availability
- Known gaps and imputation methods
- COICOP revision concordance

## Data Source Coverage

### ONS Consumer Trends (HHFCE 05.3.1)

**Typical Coverage**: 1997-Q1 to latest quarter (updated quarterly)

**Frequency**: Quarterly, seasonally adjusted and non-seasonally adjusted

**Revisions**: ONS revises back 5 years with each release. Use "consistent series" after revisions settle (~6 months post-reference period).

**Gaps**: None expected. ONS maintains continuous series.

**Access**: [ONS Consumer Trends](https://www.ons.gov.uk/economy/nationalaccounts/satelliteaccounts/datasets/consumertrends)

### ONS CPIH Weights

**Typical Coverage**: 2000-present (annual weights, published in February each year for prior year)

**Frequency**: Annual

**COICOP Revisions**:
- **2000-2015**: COICOP 1999 classification
- **2016-present**: COICOP 2018 classification (minor changes at 05.3.1 level)

**Concordance** (if needed):
- 05.3.1.3 "Cookers" stable across revisions
- 05.3.1.1 "Refrigerators" stable
- Check detailed reference tables for any sub-item reclassifications

**Gaps**: None expected.

**Access**: [ONS CPIH Detailed Reference Tables](https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/consumerpriceinflationdetailedreferencetables)

### ONS Family Spending (Living Costs & Food)

**Typical Coverage**: 2001/02-present (financial years, e.g., 2001/02 = April 2001-March 2002)

**Frequency**: Annual (sometimes biennial during austerity-related survey pauses)

**Gaps**:
- Survey suspended 2008-09 (financial crisis)
- Survey paused 2020-21 (COVID-19); resumed 2021-22

**Imputation**: If year missing, carry forward from nearest available year (max 2 years, per `ASSUMPTIONS.yaml`).

**Sample Size**: ~5,000-7,000 households; top income decile n~500, leading to higher variance.

**Access**: [ONS Family Spending](https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/datasets/detailedhouseholdexpenditurebyequivaliseddisposableincomedecilegroup)

### ONS Output in the Construction Industry

**Typical Coverage**: 2010-present (monthly and quarterly, published ~6 weeks after reference period)

**Frequency**: Monthly (seasonally adjusted), quarterly aggregates

**Private Housing R&M** (relevant series):
- Value index (current prices)
- Volume index (chained volume measure, base year 2019)

**Historical Data**: Pre-2010 data available from earlier ONS construction series (may require splicing).

**Gaps**: None in modern period.

**Access**: [ONS Construction Output](https://www.ons.gov.uk/businessindustryandtrade/constructionindustry/datasets/outputintheconstructionindustry)

### ONS/DLUHC House Building

**Typical Coverage**: 1946-present (completions), 1991-present (net additions)

**Frequency**: Quarterly (published ~8 weeks after quarter-end)

**Definitions**:
- **Completions**: Permanent dwellings completed (structural completion, ready for occupation)
- **Net Additions**: Completions + conversions - demolitions

**Use**: Completions are primary input for New Build attach pool.

**Gaps**: None.

**Access**: [DLUHC Live Tables on House Building](https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building)

### HM Land Registry Price Paid Data

**Typical Coverage**: January 1995-present (daily updates, typically 2-3 months lag)

**Frequency**: Transaction-level (aggregated to annual deciles in pipeline)

**Coverage Notes**:
- Excludes transactions <£40,000 (negligible impact for property market analysis)
- Includes freehold and leasehold sales
- Covers residential properties only
- **New Build flag** added April 2000; prior transactions lack NB/EX distinction

**Effective Coverage for This Pipeline**: 2000-present (due to NewBuild flag requirement)

**Sample Size**: ~1-1.5 million transactions/year (England & Wales); 100,000-150,000 New Build transactions/year.

**Gaps**: None after 2000.

**Access**: [HM Land Registry Open Data](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads)

### HMRC UK Transactions

**Typical Coverage**: 2005-present (monthly residential property transactions ≥£40k)

**Frequency**: Monthly, published ~3 weeks after month-end

**Use**: Flow indicator for R&R activity timing (not primary panel input).

**Gaps**: None.

**Access**: [HMRC Property Transactions Statistics](https://www.gov.uk/government/statistics/monthly-property-transactions-completed-in-the-uk-with-value-40000-or-above)

### Bank of England Mortgage Approvals

**Typical Coverage**: 1993-present (series LPMVQKR: Approvals for house purchase, NSA)

**Frequency**: Monthly

**Use**: Lead indicator (3-9 months) for R&R kitchen spend (discretionary home improvement follows mortgage-driven moves/refinances).

**Gaps**: None.

**Access**: [BoE Statistical Interactive Database](https://www.bankofengland.co.uk/boeapps/database/)

### HMRC UK Trade CN 8516.60

**Typical Coverage**: 1996-present (annual trade statistics)

**Frequency**: Annual (monthly data available but less stable for narrow commodity codes)

**Commodity Code**: CN 8516.60 - "Electric ovens, cookers, cooking plates, boiling rings, grillers and roasters (excluding microwave ovens)"

**Coverage Notes**:
- Includes all electric cooking appliances (ranges, built-in ovens, hobs)
- Excludes dual-fuel ranges (gas hob classified under different CN)
- Imports dominate (UK manufacturing minimal)

**Use**: Trade lens for range share estimation.

**Gaps**: None (but 2023+ may be provisional).

**Access**: [UK Trade Info](https://www.uktradeinfo.com/trade-data/)

## Output Panel Coverage

### Income Decile Panel

**Expected Coverage**: 2000-present

**Dependencies**:
- ONS Consumer Trends (HHFCE): 1997-present → ✅
- ONS CPIH Weights: 2000-present → ✅
- ONS Family Spending: 2001/02-present → ⚠️ Gaps in 2008-09, 2020-21

**Imputation**:
- Missing Family Spending years: Carry forward from nearest year (flagged in coverage.json)

**Confidence**: High (2002-present), Medium (2000-2001, limited LCF data)

### New Build Price Decile Panel

**Expected Coverage**: 2000-present

**Dependencies**:
- ONS House Building: 1946-present → ✅
- HM Land Registry PPD (New Build): 2000-present → ✅
- ASSUMPTIONS (attach rates, ASPs): Configurable → ✅

**Sample Size Check**: Require ≥10,000 New Build transactions/year for robust deciles.
- 2000-2005: ~80k-100k/year (Medium confidence)
- 2006-2007: ~150k/year (High confidence, housing boom)
- 2008-2012: ~60k-80k/year (Medium confidence, financial crisis)
- 2013-present: ~100k-150k/year (High confidence)

**Confidence**: Medium (2000-2005, 2008-2012), High (2006-2007, 2013-present)

### R&R Price Decile Panel

**Expected Coverage**: 2000-present (limited 2010-present for R&M volume index)

**Dependencies**:
- ONS Construction Output (R&M): 2010-present (volume index) → ⚠️ Historical gap
- HM Land Registry PPD (Existing): 2000-present → ✅
- ASSUMPTIONS (kitchen share, appliance share): Configurable → ✅

**Historical Extension**: For pre-2010 R&M, use earlier ONS construction series (requires splicing).

**Confidence**: Medium (2000-2009, spliced data), High (2010-present)

### Range Cooker Panels

**Expected Coverage**: 2000-present (with caveats)

**Dependencies**:
- HMRC Trade CN 8516.60: 1996-present → ✅
- Retail SKU analysis: Manual/scraped → ⚠️ Not automated in v1.0

**Estimation Method**: Blended trade + retail (retail component uses fallback share if scraping fails).

**Confidence**: Medium (relies on simplifying assumptions and blended methodology)

**Recommendation**: Update with retailer POS data when available.

### Price Band Panels (Luxury vs Mass-Premium)

**Expected Coverage**: 2000-present

**Dependencies**:
- Price band thresholds (ASSUMPTIONS.yaml): Configurable → ✅
- ASPs (ASSUMPTIONS.yaml): Configurable → ✅

**Method**: Simplified allocation (fixed shares); no micro-data.

**Confidence**: Low-Medium (simplified model; refine with transaction-level data)

## Known Gaps and Mitigations

| Gap | Years Affected | Mitigation | Flag in coverage.json |
|-----|----------------|------------|----------------------|
| Family Spending 2008-09 | 2008-2009 | Carry forward 2007/08 distribution | ✅ |
| Family Spending 2020-21 | 2020-2021 | Carry forward 2019/20 distribution | ✅ |
| R&M Volume pre-2010 | 2000-2009 | Splice with earlier ONS construction series | ✅ |
| New Build PPD low sample | 2000-2005, 2008-2012 | Flag as medium confidence; deciles less stable | ✅ |
| Retail range share | All years | Use fallback 12% if scraping fails | ℹ️ Note |

## COICOP Revision Concordance

### Relevant Items (05.3.1 Major Household Appliances)

| Old Code (COICOP 1999) | New Code (COICOP 2018) | Item | Change |
|------------------------|------------------------|------|--------|
| 05.3.1.3 | 05.3.1.3 | Cookers | No change |
| 05.3.1.1 | 05.3.1.1 | Refrigerators, freezers, fridge-freezers | No change |
| 05.3.1.2 | 05.3.1.2 | Washing machines, dryers, dishwashers | No change |

**Conclusion**: COICOP revisions at 05.3.1 level have minimal impact on cooking appliance extraction. Weights remain comparable across classifications.

## Quality Flags

Output files include quality flags in coverage.json:

- `high_confidence`: Full data availability, large sample sizes, minimal imputation
- `medium_confidence`: Minor gaps filled via interpolation/carry-forward, or smaller sample sizes
- `low_confidence`: Significant gaps or reliance on simplified assumptions (e.g., price band allocation)
- `note`: Additional context (e.g., retail share fallback used)

## Validation Checks

Pipeline performs automatic checks (see `tests/test_invariants.py`):

- ✅ Sum of deciles equals totals (within ±0.1%)
- ✅ Shares sum to 1.0
- ✅ Price decile cutpoints monotonic
- ✅ No negative values
- ✅ Only official public data sources used

## Future Improvements

**High Priority**:
1. Obtain retailer POS data → refine price band allocation and range share
2. Extend R&M volume index pre-2010 via ONS historical series
3. Add regional segmentation (requires regional HHFCE, PPD deciles)

**Medium Priority**:
4. Link PPD to EPC (Energy Performance Certificates) → appliance type proxy
5. Incorporate quarterly frequency where feasible (currently annual)
6. Add property-type segmentation (detached, semi, terrace, flat)

**Low Priority**:
7. Model seasonality explicitly (kitchen sales peak spring/summer)
8. Add brand-level segmentation (requires retailer partnerships)

## Reporting Issues

If you encounter data gaps or coverage issues:

1. Check `coverage.json` for specific first/last years achieved
2. Review `DATA_SOURCES.md` for source URLs and download timestamps
3. Consult `METHODOLOGY.md` for imputation methods
4. Open issue on GitHub with:
   - Affected panel/year
   - Error messages or unexpected results
   - Proposed mitigation

## References

- ONS (2023). *Methodology Guide for Consumer Trends*. Covers HHFCE COICOP classification.
- ONS (2023). *Living Costs and Food Survey Technical Report*. Details Family Spending methodology.
- HM Land Registry (2023). *Price Paid Data User Guidance*. Explains coverage and caveats.
- DLUHC (2023). *House Building Statistics Guidance Notes*. Definitions of completions vs net additions.

---

**Last Updated**: 2024 (Template; run pipeline to generate actual coverage)

**Generated**: See `coverage.json` for machine-readable version with specific years
