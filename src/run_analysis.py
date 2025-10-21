"""
Main Runner Script for Luxury Appliance Market Analysis
Executes the complete analysis pipeline from data collection to visualization
"""

import sys
import os
from datetime import datetime

# Ensure src directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def main():
    """Run complete analysis pipeline"""

    start_time = datetime.now()

    print("\n" + "=" * 80)
    print("  LUXURY APPLIANCE MARKET DEMAND ANALYSIS")
    print("  Complete Analysis Pipeline")
    print("=" * 80)
    print(f"\nStart Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTarget Brands: Viking, Wolf, Sub-Zero, Thermador")
    print("Analysis Period: 1990-Present")
    print("\n" + "=" * 80 + "\n")

    # ========================================================================
    # STEP 1: DATA COLLECTION
    # ========================================================================
    print_header("STEP 1 of 3: DATA COLLECTION")
    print("Collecting economic data from FRED...\n")

    try:
        from data_collector import LuxuryApplianceDataCollector

        collector = LuxuryApplianceDataCollector()
        df = collector.collect_all_data(start_date='1990-01-01')

        # Save in multiple frequencies
        monthly_df = collector.save_data('monthly_data.csv', frequency='monthly')
        quarterly_df = collector.save_data('quarterly_data.csv', frequency='quarterly')
        annual_df = collector.save_data('annual_data.csv', frequency='annual')

        # Print summary
        print("\n" + "-" * 80)
        print("Data Collection Summary:")
        print("-" * 80)
        summary = collector.get_data_summary()
        print(f"\nTotal Variables: {len(summary)}")
        print(f"Date Range: {df.index.min()} to {df.index.max()}")
        print(f"Observations (Monthly): {len(monthly_df)}")
        print(f"Observations (Quarterly): {len(quarterly_df)}")
        print(f"Observations (Annual): {len(annual_df)}")

        print("\n✓ Data collection complete!")

    except Exception as e:
        print(f"\n✗ Error in data collection: {e}")
        print("\nPlease ensure:")
        print("1. You have set FRED_API_KEY in .env file")
        print("2. You have internet connection")
        print("3. All dependencies are installed")
        sys.exit(1)

    # ========================================================================
    # STEP 2: REGRESSION ANALYSIS
    # ========================================================================
    print_header("STEP 2 of 3: REGRESSION ANALYSIS")
    print("Running multiple regression models...\n")

    try:
        from regression_analysis import LuxuryApplianceRegressionAnalysis

        analyzer = LuxuryApplianceRegressionAnalysis('data/quarterly_data.csv')

        # Run all models
        print("\nRunning Model 1: Income & Wealth...\n")
        analyzer.model_1_income_wealth()

        print("\nRunning Model 2: Housing Market...\n")
        analyzer.model_2_housing_market()

        print("\nRunning Model 3: Full Model...\n")
        analyzer.model_3_full_model()

        print("\nRunning Model 4: Time-Lagged Model...\n")
        analyzer.model_4_lagged_model()

        print("\nRunning Model 5: Growth Rate Model...\n")
        analyzer.model_5_growth_rates()

        # Elasticity analysis
        print("\nCalculating Elasticities...\n")
        elasticities = analyzer.elasticity_analysis()

        # Compare models
        print("\nComparing Models...\n")
        comparison = analyzer.compare_models()

        # Save results
        analyzer.save_results()

        # Plot regression results
        analyzer.plot_results()

        print("\n✓ Regression analysis complete!")

    except Exception as e:
        print(f"\n✗ Error in regression analysis: {e}")
        import traceback
        traceback.print_exc()
        print("\nContinuing to visualization step...")

    # ========================================================================
    # STEP 3: VISUALIZATION
    # ========================================================================
    print_header("STEP 3 of 3: VISUALIZATION")
    print("Generating visualizations...\n")

    try:
        from visualizations import LuxuryApplianceVisualizer

        viz = LuxuryApplianceVisualizer('data/quarterly_data.csv')
        viz.generate_all_visualizations()

        print("\n✓ Visualization complete!")

    except Exception as e:
        print(f"\n✗ Error in visualization: {e}")
        import traceback
        traceback.print_exc()

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 80)
    print("  ANALYSIS COMPLETE")
    print("=" * 80)

    print(f"\nEnd Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")

    print("\n" + "-" * 80)
    print("OUTPUTS GENERATED:")
    print("-" * 80)

    print("\n📊 Data Files (data/):")
    print("  ├── monthly_data.csv")
    print("  ├── quarterly_data.csv")
    print("  └── annual_data.csv")

    print("\n📈 Analysis Results (results/):")
    print("  ├── model_comparison.csv")
    print("  ├── regression_results.txt")
    print("  └── elasticities.csv")

    print("\n📉 Visualizations (figures/):")
    print("  ├── executive_dashboard.png")
    print("  ├── key_drivers_timeline.png")
    print("  ├── correlation_matrix.png")
    print("  ├── scatter_relationships.png")
    print("  ├── wealth_effect_analysis.png")
    print("  ├── housing_market_drivers.png")
    print("  ├── credit_conditions_impact.png")
    print("  ├── model_comparison.png")
    print("  └── elasticities.png")

    print("\n" + "-" * 80)
    print("NEXT STEPS:")
    print("-" * 80)
    print("\n1. Review results/model_comparison.csv for best model")
    print("2. Check results/regression_results.txt for detailed statistics")
    print("3. View figures/executive_dashboard.png for summary")
    print("4. Analyze results/elasticities.csv for driver sensitivity")
    print("5. Review driver_tree.md for framework and hypotheses")

    print("\n" + "=" * 80)
    print("  Thank you for using Luxury Appliance Market Analysis!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
