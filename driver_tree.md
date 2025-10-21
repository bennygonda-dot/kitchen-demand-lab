# Luxury Appliance Spending Driver Tree

## Target Brands: Viking, Wolf/Sub-Zero, Thermador
**Price Point**: $3,000-$20,000+ per appliance
**Target Market**: High-income households, luxury home renovations

---

## Level 1: Primary Drivers

### 1. WEALTH & INCOME
- **High-Income Households** (Top 20% income)
  - Disposable Personal Income (DPI)
  - Median Household Income (upper quintile)
  - Wage growth in high-income sectors
- **Asset Wealth**
  - Stock market performance (S&P 500)
  - Home equity values
  - Net worth of top 10%

### 2. HOUSING MARKET ACTIVITY
- **New Construction**
  - New housing starts (single-family)
  - Housing units completed
  - Building permits (high-value areas)
- **Existing Home Sales**
  - Home sales (especially $500k+)
  - Home turnover rate
  - Median home sale prices
- **Renovation Activity**
  - Home improvement spending
  - Kitchen renovation index
  - Home equity withdrawals

### 3. CONSUMER CONFIDENCE & SENTIMENT
- **Confidence Indices**
  - Consumer Confidence Index
  - Consumer Sentiment (U Michigan)
  - Economic Policy Uncertainty Index
- **Luxury Spending Indicators**
  - Retail sales: furniture & home furnishings
  - Durable goods orders
  - Personal consumption expenditures (durables)

### 4. CREDIT CONDITIONS
- **Interest Rates**
  - 30-year mortgage rates
  - Home equity loan rates
  - Federal funds rate
- **Credit Availability**
  - Bank lending standards
  - HELOC originations
  - Consumer credit conditions

### 5. DEMOGRAPHIC FACTORS
- **Target Demographics**
  - Population aged 35-65 (prime renovation age)
  - High-income households by region
  - Coastal/urban concentration
- **Geographic Factors**
  - High-value housing markets (CA, NY, FL, TX)
  - Urban vs suburban trends
  - Second home market

### 6. COMPETITIVE/SUBSTITUTE FACTORS
- **Market Dynamics**
  - Mid-tier appliance pricing (competition)
  - Import prices for appliances
  - Luxury goods inflation
- **Consumer Behavior**
  - Shift to premium products (trading up)
  - Kitchen as status symbol trend
  - Professional-grade home cooking trend

---

## Level 2: Data Sources Mapping

### FRED (Federal Reserve Economic Data)
- Personal Income (DSPIC96)
- Disposable Personal Income (DPI)
- Consumer Confidence (UMCSENT)
- S&P 500 (SP500)
- Housing Starts (HOUST)
- New Home Sales (HSN1F)
- Existing Home Sales (EXHOSLUSM495S)
- 30-Year Mortgage Rate (MORTGAGE30US)
- Consumer Price Index
- Home Price Index (CSUSHPISA)

### BLS (Bureau of Labor Statistics)
- Consumer Expenditure Survey (high-income households)
- Employment Cost Index (high-income sectors)
- CPI for household furnishings and operations
- Producer Price Index for appliances

### Census Bureau
- New Residential Construction
- Median Home Prices by Region
- Housing Vacancies and Homeownership
- Income and Poverty data (quintiles)

### Additional Sources
- Case-Shiller Home Price Index
- National Association of Home Builders (NAHB) indices
- American Housing Survey
- Remodeling Market Index

---

## Level 3: Hypotheses for Regression Analysis

### Primary Hypotheses
1. **Income Elasticity**: Luxury appliance spending has high income elasticity (>1.5)
2. **Housing Wealth Effect**: Home value appreciation drives luxury renovations
3. **New Construction**: New high-value homes are primary demand driver
4. **Interest Rate Sensitivity**: Lower mortgage rates → more renovations → appliance purchases
5. **Stock Market Wealth**: Equity gains correlate with luxury durable purchases
6. **Age Demographics**: Peak spending in 45-60 age range

### Secondary Hypotheses
7. **Geographic Concentration**: Coastal high-value markets drive disproportionate demand
8. **Consumer Confidence**: Luxury purchases require strong confidence (discretionary)
9. **Trading Up Trend**: Shift from mid-tier to premium over time
10. **Lagged Housing Effect**: Appliance purchases lag home sales by 6-12 months

---

## Level 4: Regression Model Specifications

### Model 1: Base Model (Income & Wealth)
```
Luxury_Appliance_Spending = β₀ + β₁(Top20%_Income) + β₂(Stock_Market) + β₃(Home_Prices) + ε
```

### Model 2: Housing Market Model
```
Luxury_Appliance_Spending = β₀ + β₁(New_Home_Sales_High_Value) + β₂(Existing_Home_Sales) + β₃(Renovation_Spending) + ε
```

### Model 3: Full Model
```
Luxury_Appliance_Spending = β₀ + β₁(Disposable_Income) + β₂(Home_Prices) + β₃(Stock_Market)
                           + β₄(New_Housing_Starts) + β₅(Mortgage_Rates) + β₆(Consumer_Confidence)
                           + β₇(Demographics) + ε
```

### Model 4: Time-Lagged Model
```
Luxury_Appliance_Spending_t = β₀ + β₁(Home_Sales_t-2) + β₂(Stock_Market_t-1) + β₃(Income_t) + ε
```

### Model 5: Regional Panel Model
```
Luxury_Appliance_Spending_i,t = α_i + β₁(Regional_Income) + β₂(Regional_Home_Prices) + δ_t + ε_i,t
```

---

## Expected Timeline
- Data availability: 1990-2024 (FRED has longest history)
- Focus period: 2000-2024 (better data quality, includes multiple cycles)
- Quarterly data preferred (monthly for some series)
- Regional breakdown where available

## Key Metrics to Track
1. **R-squared**: Explanatory power of each model
2. **Coefficient significance**: Which drivers matter most
3. **Elasticities**: How sensitive is luxury spending to each driver
4. **Forecast accuracy**: Can we predict future demand?
