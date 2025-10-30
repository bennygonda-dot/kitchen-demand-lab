# Methodology

Comprehensive mathematical specification for UK cooking appliance datasets construction.

## Table of Contents

1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [Core Transformations](#core-transformations)
4. [Segmentation Logic](#segmentation-logic)
5. [Validation & Invariants](#validation--invariants)
6. [Limitations & Assumptions](#limitations--assumptions)

## Overview

This pipeline constructs long-run (2000-present) datasets for the UK cooking appliance market by:

1. Extracting cooking appliance expenditure from broader household expenditure
2. Segmenting by income deciles and home-price deciles
3. Separating new build vs repair & remodel (R&R) channels
4. Isolating range cookers within cooking appliances
5. Splitting into Luxury vs Mass-Premium price bands

All operations maintain mathematical consistency with sum and share constraints.

## Data Sources

### Primary Sources

| Source | Code | Description | Frequency |
|--------|------|-------------|-----------|
| ONS Consumer Trends | HHFCE | COICOP 05.3.1 "Major household appliances" | Quarterly |
| ONS CPIH Weights | CPIH | Item weights at COICOP5 level | Annual |
| ONS Family Spending | LCF | Expenditure by income decile | Annual |
| ONS Construction Output | CO | Private Housing R&M value & volume | Quarterly |
| ONS/DLUHC House Building | HB | Dwelling completions | Quarterly |
| HM Land Registry PPD | PPD | Property transactions with prices | Daily (aggregated annually) |
| HMRC Transactions | TX | Residential transactions ≥£40k | Monthly |
| Bank of England | BoE | Mortgage approvals (house purchase) | Monthly |
| HMRC UK Trade | CN8516.60 | Electric ovens/cookers/ranges import/export | Annual |

### Data Provenance Rules

- **Official only**: All data from gov.uk, ons.gov.uk, bankofengland.co.uk domains
- **Public access**: No paywalled or proprietary sources
- **Audit trail**: All downloads logged with URL, timestamp, SHA256 hash
- **Version control**: Source file names include access date where possible

## Core Transformations

### 1. Cooking-Only Extraction from HHFCE

**Objective**: Isolate cooking appliance expenditure from COICOP 05.3.1 "Major household appliances"

**Method**: Use CPIH weights to separate cooking from refrigeration, laundry, dishwashers.

**Formula**:

```
C_t = H_t × w_t^cook
```

Where:
- `C_t` = Cooking appliance value at time t (£m, current prices)
- `H_t` = HHFCE 05.3.1 total (£m, current prices)
- `w_t^cook` = Cooking weight share = (weight_05.3.1.3_cookers) / (weight_05.3.1_total)

**COICOP Structure**:
- 05.3.1 Major household appliances
  - 05.3.1.1 Refrigerators, freezers, fridge-freezers (EXCLUDE)
  - 05.3.1.2 Washing machines, dryers, dishwashers (EXCLUDE)
  - 05.3.1.3 Cookers (INCLUDE)
  - 05.3.1.4 Other major appliances (case-by-case)

**Handling COICOP Revisions**: If ONS changes classification, maintain concordance table mapping old → new codes.

**Validation**:
```
0 < w_t^cook < 1 for all t
C_t < H_t for all t
```

### 2. Income Decile Distribution

**Objective**: Distribute national cooking expenditure across household income deciles.

**Data Source**: ONS Family Spending (Living Costs & Food) Workbook 1 - expenditure by equivalised disposable income decile.

**Formula**:

```
CookingSpend_{d,t} = C_t × π_{d,t}
```

Where:
- `CookingSpend_{d,t}` = Cooking spend for decile d in year t (£m)
- `π_{d,t}` = Share of total expenditure in decile d (normalized to sum to 1)
- `d ∈ {1, 2, ..., 10}` where 1 = lowest income, 10 = highest

**Normalization**:

```
π_{d,t} = share_{d,t}^raw / Σ_d share_{d,t}^raw

Such that: Σ_{d=1}^{10} π_{d,t} = 1.0
```

**Missing Years**: If Family Spending data unavailable for year t, carry forward nearest available year:

```
π_{d,t} = π_{d,t*} where t* = argmin_{t'} |t - t'| and data exists for t'
```

Maximum carry-forward: 2 years (configurable in ASSUMPTIONS.yaml).

**Validation**:
```
Σ_{d=1}^{10} CookingSpend_{d,t} = C_t  (within ±0.1% rounding error)
```

### 3. Home-Price Decile Computation (PPD)

**Objective**: Compute annual decile cutpoints and transaction shares from Price Paid Data, separately for New Build vs Existing.

**Method**: For each year, compute price quantiles (P10, P20, ..., P90, P100) for transactions where:
- New Build: `NewBuild = 'Y'`
- Existing: `NewBuild = 'N'`

**Decile Cutpoints**:

```
For decile q ∈ {1, 2, ..., 10}:
price_min_q = Quantile((q-1)/10, prices)
price_max_q = Quantile(q/10, prices)
```

**Transaction Shares**:

```
σ_{q,t} = (Count of transactions in decile q) / (Total transactions in year t)

By construction: Σ_{q=1}^{10} σ_{q,t} = 1.0
```

**Minimum Sample Size**: Require ≥10,000 transactions per year per type (NB/EX) for robust deciles. If below threshold, flag as low-confidence.

**Monotonicity Check**:
```
price_min_1 ≤ price_max_1 ≤ price_min_2 ≤ ... ≤ price_max_10
```

### 4. New Build Cooking Value Panel

**Objective**: Distribute cooking appliance value across new build home-price deciles.

**Attach Pool Formula**:

```
AttachPool_t = Completions_t × AttachRate × CookingSetValue
```

Where:
- `Completions_t` = UK dwelling completions in year t
- `AttachRate` = Cooking sets per dwelling (default 1.0)
- `CookingSetValue` = Base value of hob + oven + hood (£)

**Distribution by Decile**:

```
NB_CookingSpend_{q,t} = AttachPool_t × σ_{q,t}^NB × μ_{q,t}
```

Where:
- `σ_{q,t}^NB` = New Build PPD decile share
- `μ_{q,t}` = Value multiplier for decile q (captures premium appliances in expensive homes)

**Value Multiplier**:

```
μ_{q,t} = {
    1.0 + ε     if q ∈ {9, 10}  (top 2 deciles)
    1.0         otherwise
}
```

Where `ε` = premium_uplift_newbuild_top_deciles (default 0.10 = +10%).

**Rationale**: High-price new builds (top deciles) typically receive higher-spec appliances (double ovens, premium brands).

**Validation**:
```
Σ_{q=1}^{10} NB_CookingSpend_{q,t} = AttachPool_t  (within ±0.1%)
```

### 5. Repair & Remodel (R&R) Cooking Value Panel

**Objective**: Distribute cooking spend in existing homes (R&R channel) by home-price deciles.

**R&R Scale Factor**:

```
α_t^RM = RM_Value_t / RM_Value_{base}
```

Where:
- `RM_Value_t` = Private Housing Repair & Maintenance value index (from ONS Construction Output)
- `RM_Value_{base}` = R&M value in base year (default 2019)

**R&R Cooking Spend**:

```
RR_CookingSpend_t = C_t × α_t^RM × κ × α
```

Where:
- `κ` = kitchen_share_of_RM (default 0.27 = 27% of R&M is kitchens)
- `α` = appliance_share_of_kitchen (default 0.35 = 35% of kitchen value is appliances)

**Distribution by Decile**:

```
RM_CookingSpend_{q,t} = RR_CookingSpend_t × σ_{q,t}^EX
```

Where `σ_{q,t}^EX` = Existing home PPD decile share.

**Validation**:
```
Σ_{q=1}^{10} RM_CookingSpend_{q,t} = RR_CookingSpend_t  (within ±0.1%)
```

### 6. Range Cooker Share Estimation

**Objective**: Estimate range cooker share within total cooking appliances.

**Definition**: Range cookers = free-standing cookers ≥90cm width (typically dual-fuel or all-electric, 5+ burners).

**Method**: Blend trade data with retail analysis.

#### A. Trade Lens

Uses HMRC UK Trade data for CN 8516.60 "Electric ovens and cookers (excluding microwaves)".

```
ApparentConsumption_t = Imports_t - Exports_t

ρ_t^trade = ApparentConsumption_t / (C_t × 10^6)
```

**Caveats**:
- CN 8516.60 includes all electric cookers/ovens, not just ranges
- Dual-fuel ranges (gas hob + electric oven) classified under different CN codes
- Requires adjustment factor based on range vs built-in mix in trade

#### B. Retail Lens

Count SKUs ≥90cm across major retailers (Currys, AO, John Lewis, etc.) as proxy for range share.

```
ρ_t^retail = (Count of range SKUs) / (Total cooking SKUs)
```

Weighted by ASPs if sales volume data available.

**Caveats**:
- SKU counts ≠ sales volumes
- Online retailers may not reflect full market (trade channels, independent retailers)

#### C. Blended Estimate

```
ρ_t = w^trade × ρ_t^trade + w^retail × ρ_t^retail
```

Default weights: w^trade = 0.6, w^retail = 0.4 (configurable).

**Fallback**: If data unavailable, use ρ_t = 0.12 (12%, industry estimate).

**Bounds**: Clip ρ_t ∈ [0.05, 0.30] to prevent outliers.

**Application to Panels**:

```
RangeSpend_{d,t} = CookingSpend_{d,t} × ρ_t
BuiltInSpend_{d,t} = CookingSpend_{d,t} × (1 - ρ_t)
```

### 7. Luxury vs Mass-Premium Price Bands

**Objective**: Split cooking and range spend into Luxury and Mass-Premium segments.

**Price Band Definitions** (from ASSUMPTIONS.yaml):

| Product | Mass-Premium Min | Luxury Min |
|---------|------------------|------------|
| Range Cookers | £1,400 | £3,500 |
| Built-In Sets (oven+hob+hood) | £800 | £2,000 |

**Simplified Allocation Model**:

Assume log-normal price distribution within segment. Split by fixed shares (refined via survey data):

```
LuxuryValue = TotalValue × λ_luxury
MassPremiumValue = TotalValue × (1 - λ_luxury)
```

Default λ_luxury = 0.40 (40% of value in Luxury segment).

**Unit Conversion**:

```
LuxuryUnits = (LuxuryValue × 10^6) / ASP_luxury
MassPremiumUnits = (MassPremiumValue × 10^6) / ASP_mass_premium
```

**ASP Ladders** (from ASSUMPTIONS.yaml):

| Product | Mass-Premium ASP | Luxury ASP |
|---------|------------------|------------|
| Range Cookers | £2,200 | £4,200 |
| Built-In Sets | £1,600 | £3,200 |

**Note**: This is a simplified model. Production version should use micro-data (retailer transaction logs) for precise unit-level allocation.

## Segmentation Logic

### Three Panel Structure

1. **Income Decile Panel**: National cooking spend distributed by household income
   - Basis: ONS Family Spending survey
   - Reflects ability to pay across income distribution

2. **New Build Price Decile Panel**: Cooking appliance value in new homes by property price
   - Basis: New dwelling completions × attach rate, distributed by PPD New Build prices
   - Reflects specification choices in new construction

3. **R&R Price Decile Panel**: Cooking appliance spend in existing homes by property price
   - Basis: Total cooking spend scaled by R&M growth, distributed by PPD Existing prices
   - Reflects replacement and renovation cycles

### Why Separate NB and R&R?

- **Different drivers**: NB driven by completions; R&R driven by existing stock maintenance cycles
- **Different price points**: NB may have higher spec (developer choices), R&R replacement may seek value
- **Policy relevance**: New Build standards (energy efficiency) vs retrofit incentives

### Decile vs Other Segmentations

**Income Deciles**:
- Pros: Captures ability to pay; policy-relevant (progressive consumption patterns)
- Cons: Survey data lags; potential non-response bias in top decile

**Home-Price Deciles**:
- Pros: Property value is observable (PPD); captures wealth effects beyond current income
- Cons: Price ≠ quality/size (regional variation); new build prices may include location premium

**Alternative segmentations** (future extensions):
- Regional (England, Scotland, Wales, NI)
- Property type (detached, semi, terrace, flat)
- Tenure (owner-occupied, private rental, social)

## Validation & Invariants

### Sum Constraints

1. **Income Decile Sum**:
   ```
   Σ_{d=1}^{10} CookingSpend_{d,t} = C_t  (±0.1%)
   ```

2. **New Build Price Decile Sum**:
   ```
   Σ_{q=1}^{10} NB_CookingSpend_{q,t} = AttachPool_t  (±0.1%)
   ```

3. **R&R Price Decile Sum**:
   ```
   Σ_{q=1}^{10} RM_CookingSpend_{q,t} = RR_CookingSpend_t  (±0.1%)
   ```

4. **Range + Built-In Sum**:
   ```
   RangeSpend_{segment,t} + BuiltInSpend_{segment,t} = CookingSpend_{segment,t}  (±0.1%)
   ```

### Share Constraints

1. **Decile Shares**:
   ```
   Σ_{d=1}^{10} π_{d,t} = 1.0
   Σ_{q=1}^{10} σ_{q,t} = 1.0
   ```

2. **Price Band Shares**:
   ```
   λ_luxury + λ_mass_premium = 1.0
   ```

3. **Range Share**:
   ```
   0 ≤ ρ_t ≤ 1
   ```

### Monotonicity

1. **Price Decile Cutpoints**:
   ```
   price_min_q ≤ price_max_q ≤ price_min_{q+1}  for all q
   ```

2. **Income Deciles** (generally, but not strict):
   ```
   CookingSpend_{d,t} ≤ CookingSpend_{d+1,t}  (higher income → higher spend)
   ```
   *Note*: Violations possible due to household composition, life-cycle effects.

### Non-Negativity

All monetary values, units, shares ≥ 0.

## Limitations & Assumptions

### Data Limitations

1. **HHFCE COICOP granularity**: 05.3.1 lumps all major appliances; must use weights to separate cooking.
2. **Family Spending sample size**: Top income decile has high variance; consider merging D9+D10 for robustness.
3. **PPD coverage**: Excludes transactions <£40k (negligible for cooking appliances, relevant for property distribution).
4. **Trade data lags**: UK Trade data published with 2-3 month delay; latest year may be incomplete.
5. **No micro-data**: Lack of retailer transaction data forces simplified price band allocation.

### Key Assumptions

1. **kitchen_share_of_RM = 0.27**: Industry estimate; varies by project scope. Sensitivity: ±5 percentage points.
2. **appliance_share_of_kitchen = 0.35**: Assumes 35% of kitchen value is appliances (vs cabinetry, labor). Sensitivity: ±5 pp.
3. **Range share ρ_t ≈ 12%**: Blended estimate; actual varies by channel (higher in trade, lower in retail self-select).
4. **Luxury share λ = 40%**: Fixed allocation; should be refined with sales data.
5. **ASPs**: Represent mid-market averages; regional/temporal variation exists.
6. **Attach rate = 1.0**: Assumes one cooking set per new dwelling; some may have two (e.g., large homes with second kitchen).

### Simplifications

1. **No regional variation**: National panels; regional patterns may differ (e.g., higher range share in rural areas).
2. **No seasonality**: Annual aggregation smooths quarterly patterns (e.g., kitchen sales peak in spring/summer).
3. **No product-level detail**: Hobs, ovens, hoods aggregated into "cooking set"; cannot separate induction vs gas, for example.
4. **No brand segmentation**: Luxury defined by price, not brand (some mass-premium brands may overlap with luxury prices).

### Recommendations for Future Refinement

1. **Obtain retailer micro-data**: For precise unit-level price band allocation.
2. **Commission targeted survey**: On kitchen renovation spend by decile (validate κ and α assumptions).
3. **Extend to quarterly**: Where data allows, for seasonal analysis.
4. **Add regional dimension**: Especially for range share (urban vs rural).
5. **Incorporate energy efficiency**: Split by energy rating (policy evaluation).

## References

- ONS (2023). *Consumer Trends*. Series ABJR (HHFCE COICOP 05.3).
- ONS (2023). *Consumer Price Inflation*. Detailed reference tables (CPIH weights).
- ONS (2023). *Family Spending*. Workbook 1: Detailed household expenditure by income decile.
- ONS (2023). *Output in the Construction Industry*. Private Housing Repair & Maintenance.
- DLUHC (2023). *House Building Statistics*. Permanent dwellings completed.
- HM Land Registry (2023). *Price Paid Data*. Open data on property transactions.
- HMRC (2023). *UK Trade in Goods Statistics*. CN 8516.60.
- Bank of England (2023). *Statistical Interactive Database*. Series LPMVQKR (Mortgage Approvals).
