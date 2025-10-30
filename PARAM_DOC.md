# Parameter Documentation

Complete guide to editable assumptions in `conf/ASSUMPTIONS.yaml` and their impact on outputs.

## Overview

The `ASSUMPTIONS.yaml` file contains market parameters that can be tuned without modifying code. This document explains:

- What each parameter represents
- How it affects outputs
- Recommended ranges and sensitivity
- Sources for validation

## Price Bands

### `price_bands.range_cookers.mass_premium_min`

**Default**: 1400 (£)

**Description**: Minimum price threshold for Mass-Premium range cookers. Products below this are considered "economy" and excluded from analysis (focus is on Mass-Premium and Luxury only).

**Impact**:
- Determines split between economy and Mass-Premium segments
- Affects luxury_share calculations (indirectly)
- Influences unit counts (via ASP ladders)

**Sensitivity**: ±£200 changes Mass-Premium unit estimates by ~10-15%

**Validation**: Cross-reference with retailer listings (e.g., Currys, AO). Check median price of ≥90cm ranges.

### `price_bands.range_cookers.luxury_min`

**Default**: 3500 (£)

**Description**: Minimum price for Luxury range cookers. Above this threshold, products classified as Luxury.

**Impact**:
- Primary driver of Luxury vs Mass-Premium split
- Affects both value and unit distributions
- Influences average ASPs if calculated dynamically

**Sensitivity**: ±£500 changes Luxury share by ~5-8 percentage points

**Validation**: Industry benchmarks (e.g., Rangemaster, AGA entry-level luxury models start ~£3,000-4,000).

### `price_bands.built_in_cooking.mass_premium_min` & `luxury_min`

**Defaults**: 800 / 2000 (£)

**Description**: Equivalent thresholds for built-in cooking sets (oven + hob + hood basket).

**Impact**: Similar to range cookers, but applies to New Build and R&R built-in appliances.

**Note**: Built-in prices are for complete set, not individual items.

## Attach Rates

### `attach_rates.new_build_base_set`

**Default**: 1.0

**Description**: Number of cooking sets (hob + oven + hood) per new dwelling completion.

**Impact**:
- Scales entire New Build panel proportionally
- Multiplies with completions to determine attach pool

**Sensitivity**: Highly linear—change by 10% → 10% change in NB panel values.

**Validation**: Assume 1.0 for standard homes. Large properties (5+ beds) may have 1.2-1.5 (second kitchen, utility kitchen).

**Recommendation**: Keep at 1.0 for baseline; add segmentation by dwelling size for advanced analysis.

### `attach_rates.luxury_extra_ovens_factor`

**Default**: 1.15

**Description**: Value multiplier for top home-price deciles (9-10) in New Build, reflecting higher-spec appliances (e.g., double ovens, steam ovens, premium brands).

**Impact**:
- Increases cooking value in top 2 deciles by 15%
- Does not affect lower deciles
- Redistributes value within constant total pool (sum still equals completions × base set value)

**Sensitivity**: Change to 1.0 (no uplift) → reduces top-decile share by ~10-12 percentage points.

**Validation**: Developer specifications for premium developments; compare standard vs luxury new build kitchens.

## Kitchen and Appliance Shares (R&R Channel)

### `kitchen_share_of_RM`

**Default**: 0.27 (27%)

**Description**: Percentage of Private Housing Repair & Maintenance (R&M) expenditure attributable to kitchen projects.

**Rationale**:
- R&M includes all home improvement (bathrooms, extensions, roofing, etc.)
- Kitchens represent significant but not dominant share
- Industry surveys (NKBA, KBB) suggest 20-30% range

**Impact**:
- Scales R&R cooking spend proportionally
- If increased to 0.32 (+5 pp), R&R panel values rise 18.5%

**Sensitivity**: High—this is a primary lever for R&R panel magnitude.

**Validation**:
- NKBA Kitchen & Bath Market Outlook (US-based, but structural patterns similar)
- UK Office for National Statistics household spending surveys
- Trade association estimates (e.g., kbbreview.com industry reports)

**Recommendation**: Conduct sensitivity analysis with ±0.05 (22%-32% range).

### `appliance_share_of_kitchen`

**Default**: 0.35 (35%)

**Description**: Percentage of kitchen project value that is appliances (vs cabinetry, countertops, flooring, labor).

**Rationale**:
- Typical kitchen breakdown: 30-40% appliances, 30-35% cabinetry, 15-20% labor, 10-15% countertops/backsplash
- Varies by project scope (appliance-only replacement vs full renovation)

**Impact**:
- Scales R&R cooking appliance spend within kitchen projects
- If increased to 0.40 (+5 pp), appliance values rise 14.3%

**Sensitivity**: Moderate—multiplies with kitchen_share_of_RM, so combined effect is significant.

**Validation**:
- Kitchen industry cost breakdowns (e.g., Homeowners Alliance, Which? kitchen cost guides)
- Retailer/installer quotes for typical kitchen projects

**Recommendation**: 0.30-0.40 range is realistic; luxury kitchens may skew higher (0.40-0.45).

## Range Share Estimation

### `range_share_within_cookers.method`

**Options**: `trade_only`, `retail_only`, `blended`

**Default**: `blended`

**Description**: Method for estimating range cooker share within total cooking appliances.

**Methods**:
- `trade_only`: Uses HMRC UK Trade CN 8516.60 apparent consumption
- `retail_only`: Uses retail SKU counts/filters (≥90cm free-standing)
- `blended`: Weighted average of trade and retail

**Impact**:
- Determines split between range_spend and builtin_spend in all panels
- Changes unit estimates for range vs built-in products

**Recommendation**: Use `blended` for robustness; compare all three methods for validation.

### `range_share_within_cookers.trade_weight` & `retail_weight`

**Defaults**: 0.6 / 0.4

**Description**: Weights for blending trade and retail range share estimates.

**Rationale**:
- Trade data (CN 8516.60) more comprehensive (captures all imports)
- Retail data (SKU counts) may over-represent online visibility
- 60/40 split gives primacy to trade while incorporating retail signal

**Impact**:
- Trade weight ↑ → range share moves toward trade estimate (typically lower)
- Retail weight ↑ → range share moves toward retail estimate (typically higher)

**Sensitivity**: Moderate—10 pp shift in weights → ~1-2 pp change in blended range share.

**Validation**: Compare blended estimate with industry benchmarks (e.g., GfK market research if available).

### `range_share_within_cookers.fallback_share`

**Default**: 0.12 (12%)

**Description**: Fallback range share if trade/retail data unavailable for a given year.

**Source**: Industry estimate based on:
- Historical GfK data (pre-2015)
- AMDEA (Association of Manufacturers of Domestic Appliances) reports
- Retailer category splits

**Impact**: Only used when data is missing; forward-fills from nearest available year first.

**Recommendation**: Update periodically based on latest available data.

## Average Selling Prices (ASPs)

### `ASPs.range_cookers.mass_premium` & `luxury`

**Defaults**: 2200 / 4200 (£)

**Description**: Average selling prices for Mass-Premium and Luxury range cookers, used to convert value to unit estimates.

**Calculation**: ASPs should represent volume-weighted averages within each segment, not simple arithmetic means.

**Impact**:
- Directly determines unit counts: Units = Value / ASP
- If ASP too low → overestimates units; too high → underestimates units

**Sensitivity**: ±10% in ASP → ±10% in unit estimates (linear).

**Validation**:
- Scrape major retailers (Currys, AO, John Lewis) and compute weighted averages
- Use POS data if available (retailer partnerships)
- Compare with industry reports (e.g., AMDEA average transaction values)

**Recommendation**: Update ASPs annually using retailer price indices.

### `ASPs.built_in_sets.mass_premium` & `luxury`

**Defaults**: 1600 / 3200 (£)

**Description**: ASPs for built-in cooking sets (oven + hob + hood).

**Note**: This is a **basket** price, not individual item. Example breakdown:
- Mass-Premium: £600 oven + £400 hob + £600 hood = £1,600
- Luxury: £1,200 oven + £800 hob + £1,200 hood = £3,200

**Impact**: Affects New Build and R&R built-in unit estimates.

**Validation**: Sum prices of typical combinations from retailer catalogs.

## Premium Uplift (New Build)

### `premium_uplift_newbuild_top_deciles`

**Default**: 0.10 (+10%)

**Description**: Value uplift factor for top 2 home-price deciles (9-10) in New Build panel, capturing higher appliance specifications in expensive new homes.

**Rationale**:
- Developer specifications vary by market segment
- Premium developments (top deciles) typically include upgraded appliances as standard
- Examples: Bosch vs Neff; single oven vs double oven; gas vs induction hob

**Impact**:
- Redistributes ~5-7% of total New Build value from lower deciles to top 2 deciles
- Does not change total pool (sum constraint maintained)

**Sensitivity**: Set to 0.0 (no uplift) → top decile share drops ~10 pp; set to 0.20 (+20%) → top decile share rises ~10 pp.

**Validation**:
- Compare developer specifications for entry-level vs premium new builds
- Analyze PPD new build prices combined with EPC appliance data (if linked)

**Recommendation**: 0.05-0.15 range (5-15% uplift) is realistic.

## Data Quality Rules

### `data_quality.min_sample_size_ppd`

**Default**: 10000

**Description**: Minimum number of transactions per year (per type: New Build / Existing) required for robust price decile computation.

**Impact**: If year has fewer transactions, flag as low-confidence in coverage.json.

**Recommendation**: Keep at 10,000 for national-level deciles; increase to 50,000+ if adding regional segmentation.

### `data_quality.interpolation_method`

**Default**: `linear`

**Description**: Method for filling small gaps (1-2 years) in time series.

**Options**: `linear`, `forward_fill`, `backward_fill`, `polynomial`

**Recommendation**: Use `linear` for smooth transitions; avoid `polynomial` (can create spurious trends).

### `data_quality.carry_forward_max_years`

**Default**: 2

**Description**: Maximum number of years to carry forward Family Spending decile distributions if data is missing.

**Impact**: If Family Spending skips 3+ years, pipeline will warn and use last available distribution, flagging uncertainty in coverage.json.

**Recommendation**: Keep at 2; ONS Family Spending typically annual or biennial.

## Regional Analysis (Future)

### `regional.enabled`

**Default**: `false`

**Description**: Enable regional segmentation (England, Scotland, Wales, Northern Ireland).

**Impact**: Multiplies panel outputs by number of regions; requires regional HHFCE, PPD, and completions data.

**Status**: Not implemented in initial version; planned for future extension.

## Parameter Interaction Matrix

| Parameter | Affects | Interaction with |
|-----------|---------|------------------|
| kitchen_share_of_RM | R&R panel | appliance_share_of_kitchen (multiplicative) |
| appliance_share_of_kitchen | R&R panel | kitchen_share_of_RM (multiplicative) |
| range_share | All panels | ASPs (determines range vs built-in units) |
| ASPs | Unit estimates | Price bands (defines segment boundaries) |
| premium_uplift | NB top deciles | attach_rate (multiplicative) |
| price_bands | Luxury/Mass split | ASPs (must be consistent: luxury_min < ASP_luxury < luxury_max) |

## Sensitivity Analysis Recommendations

**High Priority** (run scenarios):
1. kitchen_share_of_RM: [0.22, 0.27, 0.32]
2. appliance_share_of_kitchen: [0.30, 0.35, 0.40]
3. range_share: [0.10, 0.12, 0.15]

**Medium Priority**:
4. ASPs: ±15% across all segments
5. premium_uplift: [0.05, 0.10, 0.15]

**Low Priority** (usually stable):
6. Price band thresholds: ±10%
7. Attach rates: Keep at 1.0 unless dwelling-type segmentation added

## Updating Assumptions

### Annual Review Checklist

□ Update ASPs from retailer price scrapes
□ Validate range_share against latest trade data
□ Check kitchen_share and appliance_share against industry reports
□ Review price_band thresholds for inflation adjustment
□ Confirm premium_uplift with developer specifications

### When to Recalibrate

- **Major market shift**: e.g., induction hobs surge (changes ASPs, range share)
- **Regulatory change**: e.g., new energy efficiency standards (affects product mix)
- **Data source revision**: e.g., ONS reclassifies COICOP items
- **New data available**: e.g., obtain retailer POS data → refine ASPs and price bands

## Support

For questions on parameter selection:
- Consult METHODOLOGY.md for underlying equations
- See COVERAGE.md for data availability by parameter
- Review test_invariants.py for validation checks

For industry benchmarks:
- AMDEA (UK appliance manufacturers association)
- kbbreview.com (kitchen & bathroom trade publication)
- Euromonitor / GfK market research (if accessible)
