"""
Luxury Appliance Market Data Collector
Pulls data from FRED and other sources for regression analysis
"""

import os
import pandas as pd
import numpy as np
from fredapi import Fred
from datetime import datetime
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class LuxuryApplianceDataCollector:
    """Collects economic data for luxury appliance spending analysis"""

    def __init__(self, api_key=None):
        """Initialize with FRED API key"""
        if api_key is None:
            api_key = os.getenv('FRED_API_KEY')

        if not api_key:
            raise ValueError(
                "FRED API key required. Set FRED_API_KEY in .env file or pass as parameter.\n"
                "Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html"
            )

        self.fred = Fred(api_key=api_key)
        self.data = {}

        # Define all data series we want to collect
        self.series_map = {
            # INCOME & WEALTH
            'disposable_income': 'DSPIC96',  # Real Disposable Personal Income
            'personal_income': 'PI',  # Personal Income
            'median_household_income': 'MEHOINUSA672N',  # Median Household Income

            # ASSET WEALTH
            'sp500': 'SP500',  # S&P 500
            'home_price_index': 'CSUSHPISA',  # Case-Shiller Home Price Index
            'household_net_worth': 'TNWBSHNO',  # Households and Nonprofit Net Worth

            # HOUSING MARKET - NEW CONSTRUCTION
            'housing_starts': 'HOUST',  # Housing Starts
            'housing_starts_single': 'HOUST1F',  # Single-Family Housing Starts
            'new_home_sales': 'HSN1F',  # New Single-Family Home Sales
            'building_permits': 'PERMIT',  # Building Permits
            'housing_completed': 'COMPUTSA',  # Housing Units Completed

            # HOUSING MARKET - EXISTING SALES
            'existing_home_sales': 'EXHOSLUSM495S',  # Existing Home Sales
            'median_sales_price': 'MSPUS',  # Median Sales Price of Houses Sold
            'home_ownership_rate': 'RHORUSQ156N',  # Homeownership Rate

            # CONSUMER CONFIDENCE
            'consumer_sentiment': 'UMCSENT',  # U Michigan Consumer Sentiment
            'consumer_confidence': 'CSCICP03USM665S',  # OECD Consumer Confidence

            # CREDIT CONDITIONS
            'mortgage_30y': 'MORTGAGE30US',  # 30-Year Mortgage Rate
            'federal_funds_rate': 'FEDFUNDS',  # Federal Funds Rate
            'mortgage_debt': 'HHMSDODNS',  # Household Mortgage Debt

            # CONSUMER SPENDING
            'pce_durables': 'PCDG',  # Personal Consumption: Durable Goods
            'retail_sales_furniture': 'RSFHFS',  # Retail Sales: Furniture
            'retail_sales_total': 'RSXFS',  # Retail Sales (ex Auto & Gas)

            # DEMOGRAPHICS
            'population': 'POPTHM',  # Population
            'labor_force_participation': 'CIVPART',  # Labor Force Participation

            # ECONOMIC INDICATORS
            'gdp_real': 'GDPC1',  # Real GDP
            'unemployment_rate': 'UNRATE',  # Unemployment Rate
            'cpi': 'CPIAUCSL',  # Consumer Price Index
            'cpi_housing': 'CUUR0000SAH',  # CPI: Housing
            'cpi_durables': 'CUSR0000SAD',  # CPI: Durables

            # RENOVATION PROXIES
            'home_improvement_spending': 'TLHIRESCONS',  # Home Improvement Retail Sales
            'hardware_store_sales': 'RSBMGESD',  # Building Materials Sales
        }

    def collect_all_data(self, start_date='1990-01-01', end_date=None):
        """
        Collect all data series from FRED

        Parameters:
        -----------
        start_date : str
            Start date in YYYY-MM-DD format
        end_date : str
            End date in YYYY-MM-DD format (defaults to today)

        Returns:
        --------
        pd.DataFrame : All data series merged
        """
        print(f"Collecting data from {start_date} to {end_date or 'present'}...")
        print(f"Total series to collect: {len(self.series_map)}\n")

        all_series = []
        failed_series = []

        for name, series_id in self.series_map.items():
            try:
                print(f"Fetching {name} ({series_id})...", end=' ')
                series = self.fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
                series.name = name
                all_series.append(series)
                print(f"✓ ({len(series)} obs)")
            except Exception as e:
                print(f"✗ Failed: {e}")
                failed_series.append((name, series_id, str(e)))

        if failed_series:
            print(f"\n⚠ Warning: {len(failed_series)} series failed to download:")
            for name, series_id, error in failed_series:
                print(f"  - {name} ({series_id}): {error}")

        # Merge all series into one DataFrame
        print("\nMerging data series...")
        df = pd.concat(all_series, axis=1)

        # Add time features
        df['year'] = df.index.year
        df['quarter'] = df.index.quarter
        df['month'] = df.index.month

        print(f"\nData collection complete!")
        print(f"Date range: {df.index.min()} to {df.index.max()}")
        print(f"Total observations: {len(df)}")
        print(f"Total variables: {len(df.columns)}")

        self.data = df
        return df

    def get_quarterly_data(self):
        """Resample data to quarterly frequency"""
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data collected yet. Run collect_all_data() first.")

        # Resample to quarterly, taking the mean for each quarter
        quarterly = self.data.resample('QE').mean()
        return quarterly

    def get_annual_data(self):
        """Resample data to annual frequency"""
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data collected yet. Run collect_all_data() first.")

        # Resample to annual, taking the mean for each year
        annual = self.data.resample('YE').mean()
        return annual

    def create_derived_variables(self, df):
        """Create derived variables for analysis"""
        df = df.copy()

        # Growth rates (year-over-year % change)
        if 'disposable_income' in df.columns:
            df['income_growth_yoy'] = df['disposable_income'].pct_change(12) * 100

        if 'sp500' in df.columns:
            df['sp500_return_yoy'] = df['sp500'].pct_change(12) * 100

        if 'home_price_index' in df.columns:
            df['home_price_growth_yoy'] = df['home_price_index'].pct_change(12) * 100

        # Lagged variables (for time-series regression)
        if 'existing_home_sales' in df.columns:
            df['home_sales_lag3m'] = df['existing_home_sales'].shift(3)
            df['home_sales_lag6m'] = df['existing_home_sales'].shift(6)
            df['home_sales_lag12m'] = df['existing_home_sales'].shift(12)

        if 'new_home_sales' in df.columns:
            df['new_home_sales_lag6m'] = df['new_home_sales'].shift(6)

        # Wealth proxy (combination of stock market and home prices)
        if 'sp500' in df.columns and 'home_price_index' in df.columns:
            # Normalize both to 0-1 scale
            sp500_norm = (df['sp500'] - df['sp500'].min()) / (df['sp500'].max() - df['sp500'].min())
            home_norm = (df['home_price_index'] - df['home_price_index'].min()) / (df['home_price_index'].max() - df['home_price_index'].min())
            df['wealth_index'] = (sp500_norm + home_norm) / 2

        # Affordability index (income relative to home prices)
        if 'disposable_income' in df.columns and 'median_sales_price' in df.columns:
            df['affordability_index'] = df['disposable_income'] / df['median_sales_price']

        # Credit conditions index (lower is easier credit)
        if 'mortgage_30y' in df.columns and 'federal_funds_rate' in df.columns:
            df['credit_conditions_index'] = (df['mortgage_30y'] + df['federal_funds_rate']) / 2

        return df

    def save_data(self, filename='luxury_appliance_data.csv', frequency='monthly'):
        """Save collected data to CSV"""
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data collected yet. Run collect_all_data() first.")

        if frequency == 'quarterly':
            df = self.get_quarterly_data()
        elif frequency == 'annual':
            df = self.get_annual_data()
        else:
            df = self.data

        # Add derived variables
        df = self.create_derived_variables(df)

        # Save to CSV
        filepath = os.path.join('data', filename)
        df.to_csv(filepath)
        print(f"\nData saved to {filepath}")
        print(f"Shape: {df.shape}")

        # Save metadata
        meta_filepath = os.path.join('data', filename.replace('.csv', '_metadata.txt'))
        with open(meta_filepath, 'w') as f:
            f.write(f"Luxury Appliance Market Data\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Frequency: {frequency}\n")
            f.write(f"Date Range: {df.index.min()} to {df.index.max()}\n")
            f.write(f"Observations: {len(df)}\n")
            f.write(f"Variables: {len(df.columns)}\n\n")
            f.write(f"Variables:\n")
            for col in df.columns:
                f.write(f"  - {col}\n")

        print(f"Metadata saved to {meta_filepath}")

        return df

    def get_data_summary(self):
        """Get summary statistics of collected data"""
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data collected yet. Run collect_all_data() first.")

        summary = pd.DataFrame({
            'count': self.data.count(),
            'missing': self.data.isna().sum(),
            'missing_pct': (self.data.isna().sum() / len(self.data) * 100).round(2),
            'min': self.data.min(),
            'max': self.data.max(),
            'mean': self.data.mean(),
            'std': self.data.std(),
        })

        return summary


def main():
    """Main execution function"""

    # Initialize collector
    print("=" * 70)
    print("LUXURY APPLIANCE MARKET DATA COLLECTION")
    print("=" * 70)
    print()

    collector = LuxuryApplianceDataCollector()

    # Collect data from 1990 onwards
    df = collector.collect_all_data(start_date='1990-01-01')

    # Save in multiple frequencies
    print("\n" + "=" * 70)
    print("SAVING DATA")
    print("=" * 70)

    # Monthly data
    monthly_df = collector.save_data('monthly_data.csv', frequency='monthly')

    # Quarterly data
    quarterly_df = collector.save_data('quarterly_data.csv', frequency='quarterly')

    # Annual data
    annual_df = collector.save_data('annual_data.csv', frequency='annual')

    # Print summary
    print("\n" + "=" * 70)
    print("DATA SUMMARY")
    print("=" * 70)
    summary = collector.get_data_summary()
    print("\nMissing Data Analysis:")
    print(summary[['count', 'missing', 'missing_pct']].sort_values('missing_pct', ascending=False))

    print("\n" + "=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review data in data/monthly_data.csv")
    print("2. Check data quality and missing values")
    print("3. Run regression analysis (see src/regression_analysis.py)")


if __name__ == "__main__":
    main()
