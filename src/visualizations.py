"""
Data Visualization for Luxury Appliance Market Analysis
Creates charts and graphs to explore the data and driver relationships
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

sns.set_style("whitegrid")
sns.set_palette("husl")


class LuxuryApplianceVisualizer:
    """Creates visualizations for luxury appliance market analysis"""

    def __init__(self, data_path='data/quarterly_data.csv'):
        """Initialize with data"""
        self.data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        self.output_dir = 'figures'
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"Data loaded: {len(self.data)} observations")
        print(f"Date range: {self.data.index.min()} to {self.data.index.max()}")

    def plot_key_drivers_over_time(self):
        """Plot main driver variables over time"""

        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Luxury Appliance Market Key Drivers (1990-Present)', fontsize=16, fontweight='bold')

        # 1. Disposable Income
        ax = axes[0, 0]
        ax.plot(self.data.index, self.data['disposable_income'], linewidth=2, color='#2E86AB')
        ax.set_title('Real Disposable Personal Income', fontweight='bold')
        ax.set_ylabel('Billions of 2012 Dollars')
        ax.grid(alpha=0.3)

        # 2. S&P 500
        ax = axes[0, 1]
        ax.plot(self.data.index, self.data['sp500'], linewidth=2, color='#A23B72')
        ax.set_title('S&P 500 Index', fontweight='bold')
        ax.set_ylabel('Index Value')
        ax.grid(alpha=0.3)

        # 3. Home Prices
        ax = axes[1, 0]
        ax.plot(self.data.index, self.data['home_price_index'], linewidth=2, color='#F18F01')
        ax.set_title('Case-Shiller Home Price Index', fontweight='bold')
        ax.set_ylabel('Index Value')
        ax.grid(alpha=0.3)

        # 4. Housing Starts
        ax = axes[1, 1]
        ax.plot(self.data.index, self.data['housing_starts_single'], linewidth=2, color='#C73E1D')
        ax.set_title('Single-Family Housing Starts', fontweight='bold')
        ax.set_ylabel('Thousands of Units')
        ax.grid(alpha=0.3)

        # 5. Consumer Sentiment
        ax = axes[2, 0]
        ax.plot(self.data.index, self.data['consumer_sentiment'], linewidth=2, color='#6A994E')
        ax.set_title('Consumer Sentiment Index', fontweight='bold')
        ax.set_ylabel('Index Value')
        ax.grid(alpha=0.3)

        # 6. Mortgage Rates
        ax = axes[2, 1]
        ax.plot(self.data.index, self.data['mortgage_30y'], linewidth=2, color='#BC4B51')
        ax.set_title('30-Year Mortgage Rate', fontweight='bold')
        ax.set_ylabel('Percent')
        ax.grid(alpha=0.3)

        # Shade recessions (approximate)
        recession_periods = [
            ('2001-03-01', '2001-11-01'),  # Dot-com bust
            ('2007-12-01', '2009-06-01'),  # Great Recession
            ('2020-02-01', '2020-04-01'),  # COVID-19
        ]

        for ax_row in axes:
            for ax in ax_row:
                for start, end in recession_periods:
                    ax.axvspan(pd.to_datetime(start), pd.to_datetime(end),
                              alpha=0.2, color='gray', label='Recession' if ax == axes[0, 0] else '')

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, 'key_drivers_timeline.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved {filepath}")
        plt.close()

    def plot_correlation_matrix(self):
        """Create correlation heatmap of all driver variables"""

        # Select key variables
        key_vars = [
            'pce_durables',
            'disposable_income',
            'sp500',
            'home_price_index',
            'housing_starts_single',
            'new_home_sales',
            'existing_home_sales',
            'consumer_sentiment',
            'mortgage_30y',
            'retail_sales_furniture'
        ]

        df = self.data[key_vars].dropna()

        # Calculate correlation matrix
        corr = df.corr()

        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)

        ax.set_title('Correlation Matrix: Luxury Appliance Market Drivers', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, 'correlation_matrix.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved {filepath}")
        plt.close()

    def plot_scatter_relationships(self):
        """Create scatter plots showing relationships between key variables"""

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Relationship: Durable Goods Spending vs. Key Drivers', fontsize=16, fontweight='bold')

        relationships = [
            ('disposable_income', 'Disposable Income'),
            ('sp500', 'S&P 500'),
            ('home_price_index', 'Home Price Index'),
            ('new_home_sales', 'New Home Sales'),
            ('consumer_sentiment', 'Consumer Sentiment'),
            ('household_net_worth', 'Household Net Worth')
        ]

        for idx, (var, title) in enumerate(relationships):
            row = idx // 3
            col = idx % 3
            ax = axes[row, col]

            if var in self.data.columns:
                df = self.data[['pce_durables', var]].dropna()

                # Scatter plot
                ax.scatter(df[var], df['pce_durables'], alpha=0.5, s=30)

                # Add trend line
                z = np.polyfit(df[var], df['pce_durables'], 1)
                p = np.poly1d(z)
                ax.plot(df[var], p(df[var]), "r--", linewidth=2, alpha=0.8)

                # Calculate R²
                correlation = df[var].corr(df['pce_durables'])
                r_squared = correlation ** 2

                ax.set_xlabel(title)
                ax.set_ylabel('PCE: Durable Goods')
                ax.set_title(f'{title}\n(R² = {r_squared:.3f})', fontweight='bold')
                ax.grid(alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, 'scatter_relationships.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved {filepath}")
        plt.close()

    def plot_wealth_vs_spending(self):
        """Create detailed wealth effect analysis"""

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Wealth Effect on Luxury Appliance Spending', fontsize=16, fontweight='bold')

        # 1. Stock Market vs Spending
        ax = axes[0, 0]
        df = self.data[['sp500', 'pce_durables']].dropna()
        ax.scatter(df['sp500'], df['pce_durables'], alpha=0.5, c=range(len(df)), cmap='viridis', s=30)
        z = np.polyfit(df['sp500'], df['pce_durables'], 1)
        p = np.poly1d(z)
        ax.plot(df['sp500'], p(df['sp500']), "r--", linewidth=2)
        ax.set_xlabel('S&P 500')
        ax.set_ylabel('Durable Goods Spending')
        ax.set_title('Stock Market Wealth Effect')
        ax.grid(alpha=0.3)

        # 2. Home Prices vs Spending
        ax = axes[0, 1]
        df = self.data[['home_price_index', 'pce_durables']].dropna()
        ax.scatter(df['home_price_index'], df['pce_durables'], alpha=0.5, c=range(len(df)), cmap='plasma', s=30)
        z = np.polyfit(df['home_price_index'], df['pce_durables'], 1)
        p = np.poly1d(z)
        ax.plot(df['home_price_index'], p(df['home_price_index']), "r--", linewidth=2)
        ax.set_xlabel('Home Price Index')
        ax.set_ylabel('Durable Goods Spending')
        ax.set_title('Home Equity Wealth Effect')
        ax.grid(alpha=0.3)

        # 3. Combined Wealth Index
        ax = axes[1, 0]
        df = self.data[['household_net_worth', 'pce_durables']].dropna()
        ax.scatter(df['household_net_worth'], df['pce_durables'], alpha=0.5, c=range(len(df)), cmap='coolwarm', s=30)
        z = np.polyfit(df['household_net_worth'], df['pce_durables'], 1)
        p = np.poly1d(z)
        ax.plot(df['household_net_worth'], p(df['household_net_worth']), "r--", linewidth=2)
        ax.set_xlabel('Household Net Worth')
        ax.set_ylabel('Durable Goods Spending')
        ax.set_title('Total Wealth Effect')
        ax.grid(alpha=0.3)

        # 4. Time series comparison
        ax = axes[1, 1]
        # Normalize to 100 at start
        sp500_norm = (self.data['sp500'] / self.data['sp500'].iloc[0]) * 100
        home_norm = (self.data['home_price_index'] / self.data['home_price_index'].iloc[0]) * 100
        spending_norm = (self.data['pce_durables'] / self.data['pce_durables'].iloc[0]) * 100

        ax.plot(self.data.index, sp500_norm, label='S&P 500', linewidth=2)
        ax.plot(self.data.index, home_norm, label='Home Prices', linewidth=2)
        ax.plot(self.data.index, spending_norm, label='Durable Spending', linewidth=2, linestyle='--')
        ax.set_ylabel('Index (First Observation = 100)')
        ax.set_title('Wealth & Spending Growth Comparison')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, 'wealth_effect_analysis.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved {filepath}")
        plt.close()

    def plot_housing_market_drivers(self):
        """Analyze housing market impact on appliance spending"""

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Housing Market Drivers of Luxury Appliance Demand', fontsize=16, fontweight='bold')

        # 1. New vs Existing Home Sales
        ax = axes[0, 0]
        ax2 = ax.twinx()
        ax.plot(self.data.index, self.data['new_home_sales'], label='New Home Sales', color='#2E86AB', linewidth=2)
        ax2.plot(self.data.index, self.data['existing_home_sales'], label='Existing Home Sales', color='#A23B72', linewidth=2)
        ax.set_ylabel('New Home Sales (Thousands)', color='#2E86AB')
        ax2.set_ylabel('Existing Home Sales (Thousands)', color='#A23B72')
        ax.set_title('New vs Existing Home Sales')
        ax.tick_params(axis='y', labelcolor='#2E86AB')
        ax2.tick_params(axis='y', labelcolor='#A23B72')
        ax.grid(alpha=0.3)

        # 2. Housing Starts vs Spending
        ax = axes[0, 1]
        df = self.data[['housing_starts_single', 'pce_durables']].dropna()
        ax.scatter(df['housing_starts_single'], df['pce_durables'], alpha=0.5, s=30)
        z = np.polyfit(df['housing_starts_single'], df['pce_durables'], 1)
        p = np.poly1d(z)
        ax.plot(df['housing_starts_single'], p(df['housing_starts_single']), "r--", linewidth=2)
        corr = df['housing_starts_single'].corr(df['pce_durables'])
        ax.set_xlabel('Housing Starts (Single-Family)')
        ax.set_ylabel('Durable Goods Spending')
        ax.set_title(f'New Construction Effect (r={corr:.3f})')
        ax.grid(alpha=0.3)

        # 3. Home Sales Volume Trend
        ax = axes[1, 0]
        # Calculate total sales volume (new + existing)
        total_sales = self.data['new_home_sales'].fillna(0) + (self.data['existing_home_sales'].fillna(0) / 1000)
        ax.plot(self.data.index, total_sales, linewidth=2, color='#F18F01')
        ax.set_ylabel('Total Home Sales Volume')
        ax.set_title('Total Housing Market Activity')
        ax.grid(alpha=0.3)

        # 4. Renovation Proxy (Hardware/Building Materials)
        ax = axes[1, 1]
        df = self.data[['hardware_store_sales', 'pce_durables']].dropna()
        ax.scatter(df['hardware_store_sales'], df['pce_durables'], alpha=0.5, s=30, color='#6A994E')
        z = np.polyfit(df['hardware_store_sales'], df['pce_durables'], 1)
        p = np.poly1d(z)
        ax.plot(df['hardware_store_sales'], p(df['hardware_store_sales']), "r--", linewidth=2)
        corr = df['hardware_store_sales'].corr(df['pce_durables'])
        ax.set_xlabel('Building Materials Sales')
        ax.set_ylabel('Durable Goods Spending')
        ax.set_title(f'Renovation Activity Effect (r={corr:.3f})')
        ax.grid(alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, 'housing_market_drivers.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved {filepath}")
        plt.close()

    def plot_credit_conditions_impact(self):
        """Analyze impact of credit conditions on luxury purchases"""

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Credit Conditions & Luxury Appliance Demand', fontsize=16, fontweight='bold')

        # 1. Mortgage Rates Over Time
        ax = axes[0, 0]
        ax.plot(self.data.index, self.data['mortgage_30y'], linewidth=2, color='#BC4B51')
        ax.fill_between(self.data.index, self.data['mortgage_30y'], alpha=0.3, color='#BC4B51')
        ax.set_ylabel('Percent')
        ax.set_title('30-Year Mortgage Rates')
        ax.grid(alpha=0.3)

        # 2. Mortgage Rates vs Spending (Inverse Relationship Expected)
        ax = axes[0, 1]
        df = self.data[['mortgage_30y', 'pce_durables']].dropna()
        ax.scatter(df['mortgage_30y'], df['pce_durables'], alpha=0.5, s=30, c=range(len(df)), cmap='RdYlGn_r')
        z = np.polyfit(df['mortgage_30y'], df['pce_durables'], 1)
        p = np.poly1d(z)
        ax.plot(df['mortgage_30y'], p(df['mortgage_30y']), "r--", linewidth=2)
        corr = df['mortgage_30y'].corr(df['pce_durables'])
        ax.set_xlabel('Mortgage Rate (%)')
        ax.set_ylabel('Durable Goods Spending')
        ax.set_title(f'Interest Rate Effect (r={corr:.3f})')
        ax.grid(alpha=0.3)

        # 3. Fed Funds Rate
        ax = axes[1, 0]
        ax.plot(self.data.index, self.data['federal_funds_rate'], linewidth=2, color='#2E86AB')
        ax.set_ylabel('Percent')
        ax.set_title('Federal Funds Rate')
        ax.grid(alpha=0.3)

        # 4. Combined Credit Conditions
        ax = axes[1, 1]
        ax2 = ax.twinx()
        ax.plot(self.data.index, self.data['mortgage_30y'], label='Mortgage Rate', color='#BC4B51', linewidth=2)
        ax2.plot(self.data.index, self.data['pce_durables'], label='Durable Spending', color='#6A994E', linewidth=2, linestyle='--')
        ax.set_ylabel('Mortgage Rate (%)', color='#BC4B51')
        ax2.set_ylabel('Durable Spending', color='#6A994E')
        ax.set_title('Credit Conditions vs Spending')
        ax.tick_params(axis='y', labelcolor='#BC4B51')
        ax2.tick_params(axis='y', labelcolor='#6A994E')
        ax.grid(alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, 'credit_conditions_impact.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved {filepath}")
        plt.close()

    def create_executive_dashboard(self):
        """Create a single-page executive summary dashboard"""

        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        fig.suptitle('Luxury Appliance Market: Executive Dashboard', fontsize=18, fontweight='bold', y=0.98)

        # Main chart: Durable Goods Spending Over Time
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.data.index, self.data['pce_durables'], linewidth=3, color='#2E86AB')
        ax1.fill_between(self.data.index, self.data['pce_durables'], alpha=0.2, color='#2E86AB')
        ax1.set_title('Durable Goods Personal Consumption (Luxury Appliance Proxy)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Billions of Dollars')
        ax1.grid(alpha=0.3)

        # Key metrics
        key_vars = [
            ('disposable_income', 'Income', '#A23B72'),
            ('sp500', 'Stock Market', '#F18F01'),
            ('home_price_index', 'Home Prices', '#C73E1D'),
            ('housing_starts_single', 'Housing Starts', '#6A994E'),
            ('consumer_sentiment', 'Sentiment', '#BC4B51'),
            ('mortgage_30y', 'Mortgage Rate', '#7209B7')
        ]

        for idx, (var, title, color) in enumerate(key_vars):
            row = (idx // 3) + 1
            col = idx % 3
            ax = fig.add_subplot(gs[row, col])

            # Normalize to 100 at start for comparison
            normalized = (self.data[var] / self.data[var].iloc[0]) * 100

            ax.plot(self.data.index, normalized, linewidth=2, color=color)
            ax.fill_between(self.data.index, normalized, alpha=0.2, color=color)
            ax.set_title(title, fontweight='bold')
            ax.set_ylabel('Index (Start = 100)')
            ax.grid(alpha=0.3)

            # Add latest value annotation
            latest = normalized.iloc[-1]
            ax.text(0.02, 0.98, f'Current: {latest:.0f}',
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, 'executive_dashboard.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✓ Saved {filepath}")
        plt.close()

    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("\n" + "=" * 80)
        print("GENERATING VISUALIZATIONS")
        print("=" * 80 + "\n")

        self.plot_key_drivers_over_time()
        self.plot_correlation_matrix()
        self.plot_scatter_relationships()
        self.plot_wealth_vs_spending()
        self.plot_housing_market_drivers()
        self.plot_credit_conditions_impact()
        self.create_executive_dashboard()

        print("\n" + "=" * 80)
        print("VISUALIZATION GENERATION COMPLETE")
        print("=" * 80)
        print(f"\nAll figures saved to {self.output_dir}/")


def main():
    """Main execution function"""
    viz = LuxuryApplianceVisualizer('data/quarterly_data.csv')
    viz.generate_all_visualizations()


if __name__ == "__main__":
    main()
