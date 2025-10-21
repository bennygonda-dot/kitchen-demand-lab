"""
Luxury Appliance Spending Regression Analysis
Analyzes drivers of premium appliance demand using multiple regression models
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.api import OLS, add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.stattools import adfuller, grangercausalitytests
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

import os

class LuxuryApplianceRegressionAnalysis:
    """Performs comprehensive regression analysis on luxury appliance drivers"""

    def __init__(self, data_path='data/quarterly_data.csv'):
        """
        Initialize with data

        Parameters:
        -----------
        data_path : str
            Path to the data CSV file
        """
        self.data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        self.results = {}

        # Proxy for luxury appliance spending (we'll use durable goods PCE as proxy)
        # In reality, you would want actual appliance sales data
        self.dependent_var = 'pce_durables'

        print(f"Data loaded: {len(self.data)} observations")
        print(f"Date range: {self.data.index.min()} to {self.data.index.max()}")
        print(f"Dependent variable (proxy): {self.dependent_var}")

    def check_stationarity(self, series_name):
        """Check if a time series is stationary using Augmented Dickey-Fuller test"""
        series = self.data[series_name].dropna()

        result = adfuller(series)

        print(f"\nStationarity Test for {series_name}:")
        print(f"  ADF Statistic: {result[0]:.4f}")
        print(f"  p-value: {result[1]:.4f}")

        if result[1] < 0.05:
            print(f"  ✓ Series is stationary (p < 0.05)")
            return True
        else:
            print(f"  ✗ Series is non-stationary (p >= 0.05)")
            return False

    def check_multicollinearity(self, X):
        """Calculate VIF (Variance Inflation Factor) to check for multicollinearity"""
        vif_data = pd.DataFrame()
        vif_data["Variable"] = X.columns
        vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

        print("\nMulticollinearity Check (VIF):")
        print(vif_data.to_string(index=False))
        print("\nInterpretation:")
        print("  VIF < 5: Low multicollinearity")
        print("  VIF 5-10: Moderate multicollinearity")
        print("  VIF > 10: High multicollinearity (consider removing)")

        return vif_data

    def model_1_income_wealth(self):
        """
        Model 1: Base Model (Income & Wealth)
        Luxury_Appliance_Spending = β₀ + β₁(Income) + β₂(Stock_Market) + β₃(Home_Prices) + ε
        """
        print("\n" + "=" * 80)
        print("MODEL 1: INCOME & WEALTH DRIVERS")
        print("=" * 80)

        # Select variables
        vars_needed = [self.dependent_var, 'disposable_income', 'sp500', 'home_price_index']
        df = self.data[vars_needed].dropna()

        # Dependent and independent variables
        y = df[self.dependent_var]
        X = df[['disposable_income', 'sp500', 'home_price_index']]
        X = add_constant(X)

        # Run regression
        model = OLS(y, X).fit()

        print(model.summary())

        # Check multicollinearity
        self.check_multicollinearity(df[['disposable_income', 'sp500', 'home_price_index']])

        # Store results
        self.results['model_1'] = {
            'model': model,
            'r2': model.rsquared,
            'adj_r2': model.rsquared_adj,
            'variables': list(X.columns)
        }

        return model

    def model_2_housing_market(self):
        """
        Model 2: Housing Market Model
        Luxury_Appliance_Spending = β₀ + β₁(New_Home_Sales) + β₂(Existing_Sales) + β₃(Home_Improvement) + ε
        """
        print("\n" + "=" * 80)
        print("MODEL 2: HOUSING MARKET DRIVERS")
        print("=" * 80)

        # Select variables
        vars_needed = [self.dependent_var, 'new_home_sales', 'existing_home_sales', 'hardware_store_sales']
        df = self.data[vars_needed].dropna()

        # Dependent and independent variables
        y = df[self.dependent_var]
        X = df[['new_home_sales', 'existing_home_sales', 'hardware_store_sales']]
        X = add_constant(X)

        # Run regression
        model = OLS(y, X).fit()

        print(model.summary())

        # Check multicollinearity
        self.check_multicollinearity(df[['new_home_sales', 'existing_home_sales', 'hardware_store_sales']])

        # Store results
        self.results['model_2'] = {
            'model': model,
            'r2': model.rsquared,
            'adj_r2': model.rsquared_adj,
            'variables': list(X.columns)
        }

        return model

    def model_3_full_model(self):
        """
        Model 3: Full Model
        Includes income, wealth, housing, credit conditions, and consumer confidence
        """
        print("\n" + "=" * 80)
        print("MODEL 3: FULL MODEL (ALL DRIVERS)")
        print("=" * 80)

        # Select variables
        vars_needed = [
            self.dependent_var,
            'disposable_income',
            'home_price_index',
            'sp500',
            'housing_starts_single',
            'mortgage_30y',
            'consumer_sentiment'
        ]

        df = self.data[vars_needed].dropna()

        # Dependent and independent variables
        y = df[self.dependent_var]
        X = df.drop(columns=[self.dependent_var])
        X = add_constant(X)

        # Run regression
        model = OLS(y, X).fit()

        print(model.summary())

        # Check multicollinearity
        self.check_multicollinearity(df.drop(columns=[self.dependent_var]))

        # Store results
        self.results['model_3'] = {
            'model': model,
            'r2': model.rsquared,
            'adj_r2': model.rsquared_adj,
            'variables': list(X.columns)
        }

        return model

    def model_4_lagged_model(self):
        """
        Model 4: Time-Lagged Model
        Tests hypothesis that appliance purchases lag home sales
        """
        print("\n" + "=" * 80)
        print("MODEL 4: TIME-LAGGED MODEL")
        print("=" * 80)

        # Create lagged variables
        df = self.data.copy()

        # Lag home sales by 6 months (2 quarters)
        df['home_sales_lag_2q'] = df['existing_home_sales'].shift(2)

        # Lag stock market by 1 quarter
        df['sp500_lag_1q'] = df['sp500'].shift(1)

        # Select variables
        vars_needed = [
            self.dependent_var,
            'disposable_income',
            'home_sales_lag_2q',
            'sp500_lag_1q'
        ]

        df = df[vars_needed].dropna()

        # Dependent and independent variables
        y = df[self.dependent_var]
        X = df.drop(columns=[self.dependent_var])
        X = add_constant(X)

        # Run regression
        model = OLS(y, X).fit()

        print(model.summary())

        # Store results
        self.results['model_4'] = {
            'model': model,
            'r2': model.rsquared,
            'adj_r2': model.rsquared_adj,
            'variables': list(X.columns)
        }

        return model

    def model_5_growth_rates(self):
        """
        Model 5: Growth Rate Model
        Uses percentage changes instead of levels to avoid non-stationarity
        """
        print("\n" + "=" * 80)
        print("MODEL 5: GROWTH RATE MODEL")
        print("=" * 80)

        # Calculate growth rates (quarter-over-quarter % change)
        df = self.data.copy()

        growth_vars = {
            'pce_durables_growth': 'pce_durables',
            'income_growth': 'disposable_income',
            'home_price_growth': 'home_price_index',
            'sp500_growth': 'sp500',
            'housing_starts_growth': 'housing_starts_single'
        }

        for new_var, original_var in growth_vars.items():
            df[new_var] = df[original_var].pct_change() * 100

        # Select variables
        vars_needed = [
            'pce_durables_growth',
            'income_growth',
            'home_price_growth',
            'sp500_growth',
            'housing_starts_growth'
        ]

        df = df[vars_needed].dropna()

        # Dependent and independent variables
        y = df['pce_durables_growth']
        X = df.drop(columns=['pce_durables_growth'])
        X = add_constant(X)

        # Run regression
        model = OLS(y, X).fit()

        print(model.summary())

        # Store results
        self.results['model_5'] = {
            'model': model,
            'r2': model.rsquared,
            'adj_r2': model.rsquared_adj,
            'variables': list(X.columns)
        }

        return model

    def elasticity_analysis(self):
        """
        Calculate elasticities: how much does luxury spending change
        when each driver changes by 1%?
        """
        print("\n" + "=" * 80)
        print("ELASTICITY ANALYSIS")
        print("=" * 80)

        # Use log-log model to get elasticities
        vars_needed = [
            self.dependent_var,
            'disposable_income',
            'sp500',
            'home_price_index',
            'existing_home_sales'
        ]

        df = self.data[vars_needed].dropna()

        # Take logs
        df_log = np.log(df)

        # Run regression on logs
        y = df_log[self.dependent_var]
        X = df_log.drop(columns=[self.dependent_var])
        X = add_constant(X)

        model = OLS(y, X).fit()

        print("\nLog-Log Model (Coefficients = Elasticities):")
        print(model.summary())

        print("\n" + "=" * 80)
        print("ELASTICITY INTERPRETATION")
        print("=" * 80)

        elasticities = model.params.drop('const')

        for var, elasticity in elasticities.items():
            print(f"\n{var}:")
            print(f"  Elasticity: {elasticity:.3f}")
            if abs(elasticity) > 1:
                print(f"  → Elastic: 1% increase in {var} → {elasticity:.2f}% change in luxury spending")
            else:
                print(f"  → Inelastic: 1% increase in {var} → {elasticity:.2f}% change in luxury spending")

        # Store results
        self.results['elasticities'] = elasticities.to_dict()

        return elasticities

    def compare_models(self):
        """Compare all models and identify the best fit"""
        print("\n" + "=" * 80)
        print("MODEL COMPARISON")
        print("=" * 80)

        comparison = pd.DataFrame({
            'Model': list(self.results.keys()),
            'R²': [self.results[m]['r2'] for m in self.results if 'r2' in self.results[m]],
            'Adj. R²': [self.results[m]['adj_r2'] for m in self.results if 'adj_r2' in self.results[m]],
            'Variables': [len(self.results[m]['variables']) for m in self.results if 'variables' in self.results[m]]
        })

        print("\n", comparison.to_string(index=False))

        # Best model
        best_model = comparison.loc[comparison['Adj. R²'].idxmax(), 'Model']
        best_r2 = comparison.loc[comparison['Adj. R²'].idxmax(), 'Adj. R²']

        print(f"\n✓ Best Model: {best_model} (Adj. R² = {best_r2:.4f})")

        return comparison

    def save_results(self, output_dir='results'):
        """Save all results to files"""
        os.makedirs(output_dir, exist_ok=True)

        # Save model comparison
        comparison = self.compare_models()
        comparison.to_csv(f'{output_dir}/model_comparison.csv', index=False)

        # Save detailed results for each model
        with open(f'{output_dir}/regression_results.txt', 'w') as f:
            for model_name, result in self.results.items():
                if 'model' in result:
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"{model_name.upper()}\n")
                    f.write(f"{'=' * 80}\n\n")
                    f.write(str(result['model'].summary()))
                    f.write("\n\n")

        # Save elasticities
        if 'elasticities' in self.results:
            pd.DataFrame.from_dict(
                self.results['elasticities'],
                orient='index',
                columns=['Elasticity']
            ).to_csv(f'{output_dir}/elasticities.csv')

        print(f"\n✓ Results saved to {output_dir}/")

    def plot_results(self):
        """Create visualizations of regression results"""
        import matplotlib.pyplot as plt
        import seaborn as sns

        sns.set_style("whitegrid")
        os.makedirs('figures', exist_ok=True)

        # 1. Model Comparison Plot
        comparison = pd.DataFrame({
            'Model': list(self.results.keys()),
            'R²': [self.results[m]['r2'] for m in self.results if 'r2' in self.results[m]],
            'Adj. R²': [self.results[m]['adj_r2'] for m in self.results if 'adj_r2' in self.results[m]],
        })

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(comparison))
        width = 0.35

        ax.bar(x - width/2, comparison['R²'], width, label='R²')
        ax.bar(x + width/2, comparison['Adj. R²'], width, label='Adj. R²')

        ax.set_xlabel('Model')
        ax.set_ylabel('R² Value')
        ax.set_title('Model Comparison: Goodness of Fit')
        ax.set_xticks(x)
        ax.set_xticklabels(comparison['Model'], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig('figures/model_comparison.png', dpi=300, bbox_inches='tight')
        print("✓ Saved figures/model_comparison.png")

        # 2. Elasticity Plot
        if 'elasticities' in self.results:
            elasticities = pd.Series(self.results['elasticities']).sort_values()

            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['red' if x < 0 else 'green' for x in elasticities]
            elasticities.plot(kind='barh', color=colors, ax=ax)

            ax.set_xlabel('Elasticity')
            ax.set_title('Income Elasticity of Luxury Appliance Spending')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            ax.axvline(x=1, color='gray', linestyle='--', linewidth=0.5, label='Unit Elastic')
            ax.axvline(x=-1, color='gray', linestyle='--', linewidth=0.5)
            ax.grid(axis='x', alpha=0.3)
            ax.legend()

            plt.tight_layout()
            plt.savefig('figures/elasticities.png', dpi=300, bbox_inches='tight')
            print("✓ Saved figures/elasticities.png")

        plt.close('all')


def main():
    """Main execution function"""

    print("=" * 80)
    print("LUXURY APPLIANCE SPENDING REGRESSION ANALYSIS")
    print("=" * 80)

    # Initialize analysis
    analyzer = LuxuryApplianceRegressionAnalysis('data/quarterly_data.csv')

    # Run all models
    print("\n\nRunning regression models...\n")

    analyzer.model_1_income_wealth()
    analyzer.model_2_housing_market()
    analyzer.model_3_full_model()
    analyzer.model_4_lagged_model()
    analyzer.model_5_growth_rates()

    # Elasticity analysis
    analyzer.elasticity_analysis()

    # Compare models
    analyzer.compare_models()

    # Save results
    analyzer.save_results()

    # Plot results
    analyzer.plot_results()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nOutputs:")
    print("  - results/model_comparison.csv")
    print("  - results/regression_results.txt")
    print("  - results/elasticities.csv")
    print("  - figures/model_comparison.png")
    print("  - figures/elasticities.png")


if __name__ == "__main__":
    main()
