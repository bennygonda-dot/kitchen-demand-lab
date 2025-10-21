"""
Generate sample data based on realistic economic trends
This is for demonstration when FRED API is not accessible
"""

import pandas as pd
import numpy as np
from datetime import datetime

def generate_sample_data():
    """Generate synthetic but realistic economic data"""

    # Create quarterly date range from 1990 to 2024
    dates = pd.date_range(start='1990-01-01', end='2024-09-30', freq='QE')
    n = len(dates)

    # Set random seed for reproducibility
    np.random.seed(42)

    # Create time trend
    t = np.arange(n)

    # Generate realistic economic indicators
    data = pd.DataFrame(index=dates)

    # INCOME & WEALTH (generally upward trends)
    data['disposable_income'] = 5000 + 50*t + np.random.normal(0, 100, n)
    data['personal_income'] = 6000 + 60*t + np.random.normal(0, 120, n)
    data['median_household_income'] = 40000 + 500*t + np.random.normal(0, 1000, n)

    # ASSET WEALTH (with boom/bust cycles)
    # S&P 500: dot-com boom, crash, recovery, 2008 crash, bull market
    sp500_base = 400
    sp500_trend = sp500_base * (1.07 ** (t/4))  # ~7% annual growth
    # Add recession shocks
    recession_2001 = np.where((dates.year >= 2000) & (dates.year <= 2002), -0.3, 0)
    recession_2008 = np.where((dates.year >= 2007) & (dates.year <= 2009), -0.4, 0)
    covid_2020 = np.where((dates.year == 2020) & (dates.quarter <= 2), -0.15, 0)
    data['sp500'] = sp500_trend * (1 + recession_2001 + recession_2008 + covid_2020) + np.random.normal(0, 50, n)

    # Home Price Index (with 2008 housing crisis)
    home_base = 100
    home_trend = home_base * (1.04 ** (t/4))  # ~4% annual growth
    housing_crash = np.where((dates.year >= 2007) & (dates.year <= 2011), -0.25, 0)
    data['home_price_index'] = home_trend * (1 + housing_crash) + np.random.normal(0, 5, n)

    # Household Net Worth
    data['household_net_worth'] = 25000 + 400*t + np.random.normal(0, 1000, n)

    # HOUSING MARKET
    # Housing starts (cyclical, hit hard in 2008)
    housing_base = 1200
    housing_cycle = 200 * np.sin(t / 8)  # Cyclical pattern
    housing_crash_effect = np.where((dates.year >= 2007) & (dates.year <= 2011), -600, 0)
    covid_boom = np.where((dates.year >= 2020) & (dates.year <= 2022), 200, 0)
    data['housing_starts'] = housing_base + housing_cycle + housing_crash_effect + covid_boom + np.random.normal(0, 50, n)
    data['housing_starts_single'] = data['housing_starts'] * 0.7 + np.random.normal(0, 30, n)

    # New home sales
    data['new_home_sales'] = 600 + 5*t + housing_cycle*0.5 + housing_crash_effect*0.6 + np.random.normal(0, 30, n)

    # Building permits
    data['building_permits'] = data['housing_starts'] * 1.1 + np.random.normal(0, 40, n)

    # Housing completed (lags starts slightly)
    data['housing_completed'] = data['housing_starts'].shift(2).fillna(data['housing_starts']) + np.random.normal(0, 30, n)

    # Existing home sales
    data['existing_home_sales'] = 4000 + 10*t + housing_crash_effect*2 + np.random.normal(0, 100, n)

    # Median sales price
    data['median_sales_price'] = 150000 + 3000*t + np.random.normal(0, 5000, n)

    # Home ownership rate
    data['home_ownership_rate'] = 64 + 2*np.sin(t/15) + np.random.normal(0, 0.5, n)

    # CONSUMER CONFIDENCE
    confidence_base = 85
    confidence_recessions = (recession_2001 + recession_2008 + covid_2020) * 30
    data['consumer_sentiment'] = confidence_base + 5*np.sin(t/6) + confidence_recessions + np.random.normal(0, 3, n)
    data['consumer_confidence'] = data['consumer_sentiment'] + np.random.normal(0, 2, n)

    # CREDIT CONDITIONS
    # Mortgage rates (high in 90s, low 2000s, spike 2022)
    rate_base = 8 - 0.04*t  # Declining trend
    rate_2022_spike = np.where(dates.year >= 2022, 2, 0)
    data['mortgage_30y'] = np.maximum(2.5, rate_base + rate_2022_spike + np.random.normal(0, 0.2, n))

    # Federal funds rate (follows similar pattern)
    data['federal_funds_rate'] = np.maximum(0, data['mortgage_30y'] - 2 + np.random.normal(0, 0.3, n))

    # Mortgage debt
    data['mortgage_debt'] = 3000 + 100*t + np.random.normal(0, 100, n)

    # CONSUMER SPENDING (our dependent variable proxy)
    # PCE Durables - should correlate with income, wealth, housing
    pce_base = 800
    income_effect = (data['disposable_income'] - data['disposable_income'].mean()) * 0.15
    wealth_effect = (data['sp500'] - data['sp500'].mean()) * 0.05
    home_effect = (data['home_price_index'] - data['home_price_index'].mean()) * 2
    housing_market_effect = (data['housing_starts_single'] - data['housing_starts_single'].mean()) * 0.1
    confidence_effect = (data['consumer_sentiment'] - data['consumer_sentiment'].mean()) * 2
    rate_effect = -(data['mortgage_30y'] - data['mortgage_30y'].mean()) * 20

    data['pce_durables'] = (pce_base + 10*t + income_effect + wealth_effect +
                            home_effect + housing_market_effect + confidence_effect +
                            rate_effect + np.random.normal(0, 30, n))

    # Retail sales
    data['retail_sales_furniture'] = 8000 + 100*t + housing_market_effect*10 + np.random.normal(0, 200, n)
    data['retail_sales_total'] = 200000 + 2000*t + np.random.normal(0, 5000, n)

    # DEMOGRAPHICS
    data['population'] = 250000 + 500*t + np.random.normal(0, 100, n)
    data['labor_force_participation'] = 66 - 0.01*t + np.random.normal(0, 0.3, n)

    # ECONOMIC INDICATORS
    data['gdp_real'] = 10000 + 100*t + confidence_recessions*100 + np.random.normal(0, 200, n)
    unemployment_base = 5.5
    unemployment_recessions = -1 * (recession_2001 + recession_2008 + covid_2020) * 15
    data['unemployment_rate'] = np.maximum(3.5, unemployment_base + unemployment_recessions + np.random.normal(0, 0.3, n))

    # CPI
    data['cpi'] = 140 + 3*t + np.random.normal(0, 2, n)
    data['cpi_housing'] = 150 + 3.5*t + np.random.normal(0, 2, n)
    data['cpi_durables'] = 100 - 0.5*t + np.random.normal(0, 1, n)  # Durables get cheaper over time

    # RENOVATION PROXIES
    data['home_improvement_spending'] = data['retail_sales_furniture'] * 1.2 + np.random.normal(0, 100, n)
    data['hardware_store_sales'] = 20000 + 200*t + housing_market_effect*20 + np.random.normal(0, 300, n)

    # Add time features
    data['year'] = dates.year
    data['quarter'] = dates.quarter
    data['month'] = dates.month

    # Ensure all values are positive
    for col in data.columns:
        if col not in ['year', 'quarter', 'month']:
            data[col] = np.maximum(data[col], 0)

    return data


def main():
    """Generate and save sample data"""
    print("=" * 70)
    print("GENERATING SAMPLE DATA")
    print("=" * 70)
    print("\nThis creates synthetic data based on realistic economic trends")
    print("Use this for testing when FRED API is not accessible\n")

    # Generate data
    df = generate_sample_data()

    # Save quarterly data
    df.to_csv('data/quarterly_data.csv')
    print(f"✓ Saved: data/quarterly_data.csv")
    print(f"  Shape: {df.shape}")
    print(f"  Date Range: {df.index.min()} to {df.index.max()}")

    # Create monthly data (interpolate quarterly)
    monthly_dates = pd.date_range(start='1990-01-01', end='2024-09-30', freq='ME')
    df_monthly = df.reindex(monthly_dates).interpolate(method='linear')
    df_monthly['year'] = df_monthly.index.year
    df_monthly['quarter'] = df_monthly.index.quarter
    df_monthly['month'] = df_monthly.index.month
    df_monthly.to_csv('data/monthly_data.csv')
    print(f"✓ Saved: data/monthly_data.csv")
    print(f"  Shape: {df_monthly.shape}")

    # Create annual data
    df_annual = df.resample('YE').mean()
    df_annual.to_csv('data/annual_data.csv')
    print(f"✓ Saved: data/annual_data.csv")
    print(f"  Shape: {df_annual.shape}")

    # Print summary stats
    print("\n" + "=" * 70)
    print("SAMPLE DATA SUMMARY")
    print("=" * 70)
    print("\nKey Statistics (Quarterly):")
    print(df[['pce_durables', 'disposable_income', 'sp500', 'home_price_index',
              'housing_starts_single', 'consumer_sentiment']].describe().round(2))

    print("\n✓ Sample data generation complete!")
    print("\nNote: This is synthetic data for demonstration.")
    print("For real analysis, use actual FRED data when API access is available.")


if __name__ == "__main__":
    main()
