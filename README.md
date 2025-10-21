# Luxury Appliance Market Demand Analysis

A comprehensive data analysis project to understand the drivers of luxury/premium appliance spending for brands like Viking, Wolf, Sub-Zero, and Thermador.

## Overview

This project analyzes the economic and market factors that drive demand for luxury kitchen appliances (typically priced $3,000-$20,000+). Using public data from FRED, BLS, and other sources, we build a driver tree, collect relevant economic indicators, and perform multiple regression analyses to identify the key factors influencing luxury appliance purchases.

## Project Structure

```
kitchen-demand-lab/
│
├── driver_tree.md              # Comprehensive driver tree framework
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
│
├── src/
│   ├── data_collector.py      # FRED data collection script
│   ├── regression_analysis.py # Multiple regression models
│   ├── visualizations.py      # Data visualization scripts
│   └── run_analysis.py        # Main runner script
│
├── data/                      # Generated data files (CSV)
│   ├── monthly_data.csv
│   ├── quarterly_data.csv
│   └── annual_data.csv
│
├── results/                   # Regression results and reports
│   ├── model_comparison.csv
│   ├── regression_results.txt
│   └── elasticities.csv
│
└── figures/                   # Generated visualizations
    ├── executive_dashboard.png
    ├── key_drivers_timeline.png
    ├── correlation_matrix.png
    └── [more visualizations]
```

## Driver Tree Framework

The analysis is structured around six primary driver categories:

### 1. **Wealth & Income**
- Disposable Personal Income
- High-income household earnings
- Asset wealth (stocks, home equity)

### 2. **Housing Market Activity**
- New construction (housing starts, building permits)
- Existing home sales
- Home renovation/improvement spending

### 3. **Consumer Confidence & Sentiment**
- Consumer Confidence Index
- Consumer Sentiment
- Luxury spending indicators

### 4. **Credit Conditions**
- Mortgage rates (30-year)
- Federal funds rate
- Credit availability

### 5. **Demographics**
- Target age groups (35-65)
- High-income geographic markets
- Urban/coastal concentration

### 6. **Market Dynamics**
- Competition from mid-tier brands
- Import prices
- Consumer behavior trends

See [driver_tree.md](driver_tree.md) for the complete framework and hypotheses.

## Data Sources

### Primary: FRED (Federal Reserve Economic Data)
- **Income**: Personal income, disposable income, median household income
- **Wealth**: S&P 500, home price index, household net worth
- **Housing**: Housing starts, new/existing home sales, building permits
- **Confidence**: Consumer sentiment, consumer confidence
- **Credit**: Mortgage rates, federal funds rate, mortgage debt
- **Spending**: PCE durables, retail sales (furniture), building materials

### Secondary Sources
- Bureau of Labor Statistics (BLS) - Consumer Expenditure Survey
- Census Bureau - Housing and income data
- Case-Shiller Home Price Index

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get FRED API Key

1. Go to https://fred.stlouisfed.org/
2. Create a free account
3. Request an API key at: https://fred.stlouisfed.org/docs/api/api_key.html

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your FRED_API_KEY
```

## Usage

### Option 1: Run Complete Analysis

```bash
python src/run_analysis.py
```

This will:
1. Collect all data from FRED
2. Save data in multiple frequencies (monthly, quarterly, annual)
3. Run all regression models
4. Generate all visualizations
5. Save results to `results/` and `figures/`

### Option 2: Run Individual Components

**Collect Data Only:**
```bash
python src/data_collector.py
```

**Run Regression Analysis:**
```bash
python src/regression_analysis.py
```

**Generate Visualizations:**
```bash
python src/visualizations.py
```

## Regression Models

The analysis includes five complementary regression models:

### Model 1: Income & Wealth
Tests the relationship between luxury spending and wealth indicators.
```
Spending = f(Disposable_Income, S&P_500, Home_Prices)
```

### Model 2: Housing Market
Focuses on housing market activity as the primary driver.
```
Spending = f(New_Home_Sales, Existing_Home_Sales, Renovation_Activity)
```

### Model 3: Full Model
Comprehensive model including all major driver categories.
```
Spending = f(Income, Home_Prices, Stock_Market, Housing_Starts,
             Mortgage_Rates, Consumer_Confidence)
```

### Model 4: Time-Lagged Model
Tests hypothesis that appliance purchases lag home sales.
```
Spending_t = f(Home_Sales_t-6months, Stock_Market_t-3months, Income_t)
```

### Model 5: Growth Rate Model
Uses percentage changes to avoid non-stationarity issues.
```
Spending_Growth = f(Income_Growth, Home_Price_Growth, Stock_Market_Growth)
```

## Key Hypotheses

1. **High Income Elasticity**: Luxury appliances have income elasticity > 1.5
2. **Wealth Effect**: Home appreciation and stock gains drive luxury renovations
3. **New Construction**: New high-value homes are primary demand driver
4. **Interest Rate Sensitivity**: Lower mortgage rates → more renovations
5. **Lagged Effect**: Appliance purchases lag home sales by 6-12 months
6. **Geographic Concentration**: Coastal/high-value markets drive demand

## Output Files

### Data Files (`data/`)
- `monthly_data.csv` - All indicators at monthly frequency
- `quarterly_data.csv` - Quarterly aggregated data (recommended for regression)
- `annual_data.csv` - Annual aggregated data
- `*_metadata.txt` - Data documentation and variable lists

### Results (`results/`)
- `model_comparison.csv` - R² and Adj. R² for all models
- `regression_results.txt` - Full regression output with coefficients and p-values
- `elasticities.csv` - Income elasticity estimates

### Visualizations (`figures/`)
- `executive_dashboard.png` - Single-page summary dashboard
- `key_drivers_timeline.png` - Time series of all major drivers
- `correlation_matrix.png` - Correlation heatmap
- `scatter_relationships.png` - Bivariate relationships
- `wealth_effect_analysis.png` - Wealth indicators vs spending
- `housing_market_drivers.png` - Housing market analysis
- `credit_conditions_impact.png` - Interest rate effects
- `model_comparison.png` - Model R² comparison
- `elasticities.png` - Elasticity bar chart

## Interpreting Results

### R² (R-Squared)
- Measures how much variance in luxury spending is explained by the model
- Higher is better (0-1 scale)
- Adjusted R² accounts for number of variables

### Coefficients
- Sign (+/-) indicates direction of relationship
- Magnitude indicates strength of effect
- P-value < 0.05 indicates statistical significance

### Elasticities
- Measures % change in spending for 1% change in driver
- Elasticity > 1: "Elastic" - luxury goods are very responsive
- Elasticity < 1: "Inelastic" - less responsive
- Expected: Income elasticity for luxury appliances should be > 1.5

### VIF (Variance Inflation Factor)
- Checks for multicollinearity between variables
- VIF < 5: Low multicollinearity ✓
- VIF > 10: High multicollinearity (problematic)

## Target Market Insights

### Customer Profile
- **Income**: Top 20% of earners ($150k+ household income)
- **Age**: 35-65 (peak renovation age)
- **Geography**: Coastal markets, high-value suburbs
- **Home Value**: $500k+ properties
- **Behavior**: Status-conscious, value quality and brand

### Purchase Triggers
1. **New home purchase** (especially luxury segment)
2. **Major kitchen renovation** (avg. $50k+ projects)
3. **Home appreciation** → equity withdrawal
4. **Stock market gains** → wealth effect
5. **Low interest rates** → renovation financing

## Limitations & Caveats

1. **Proxy Variable**: We use PCE durable goods as a proxy. Actual luxury appliance sales data would be more precise.
2. **Brand-Level**: Analysis is market-level, not brand-specific (Viking vs. Thermador)
3. **Geographic**: National-level data. Regional analysis would provide more granular insights.
4. **Time Lag**: Exact timing between home sales and appliance purchases varies
5. **COVID-19**: 2020-2021 data may have unusual patterns

## Future Enhancements

- [ ] Add actual appliance sales data (if available)
- [ ] Regional panel regression (CA, NY, FL, TX separately)
- [ ] Quarterly forecasting model
- [ ] Brand-level market share analysis
- [ ] Competitive pricing analysis
- [ ] Consumer sentiment towards luxury goods specifically
- [ ] Integration with Google Trends data
- [ ] Builder/contractor survey data

## References

- FRED Economic Data: https://fred.stlouisfed.org/
- Bureau of Labor Statistics: https://www.bls.gov/
- Census Bureau Housing Data: https://www.census.gov/housing
- Case-Shiller Index: https://www.spglobal.com/spdji/en/index-family/indicators/sp-corelogic-case-shiller/

## License

This project is for analytical and research purposes. Data is sourced from public government databases (FRED, BLS, Census).

## Contact

For questions about methodology or results, please open an issue in this repository.

---

**Generated**: 2025
**Last Updated**: Check git log for latest changes
**Data Coverage**: 1990-Present (varies by indicator)
