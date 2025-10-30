"""
Competitor Analysis: Companies House Data for UK Range Cooker Manufacturers
Analyzes BSH UK, SMEG UK, and AGA Rangemaster with market context
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, Reference, BarChart

# Set style for visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def create_companies_house_data():
    """
    Compile Companies House financial data for UK competitors

    Data sources: Companies House filings and public financial reports
    All figures in £ millions
    """

    # BSH Home Appliances Limited (Company No. 01844007)
    # Includes Bosch, Neff, Siemens brands in UK
    bsh_data = {
        'Year': [2022, 2023],
        'Revenue': [810.0, 791.2],
        'Pre_Tax_Profit': [30.2, 24.0],
        'Unit_Sales': [2212200, 2011108],
        'Notes': ['Strong year', 'Inflationary pressures, weak consumer confidence']
    }

    # SMEG (UK) Limited (Company No. 02365886)
    smeg_data = {
        'Year': [2022, 2023],
        'Revenue': [48.5, 65.0],  # 2022 calculated from 34.12% growth
        'Gross_Profit': [None, 18.0],
        'EBITDA': [None, 0.851],
        'Notes': ['Estimated from growth rate', '34.12% revenue growth YoY']
    }

    # AGA Rangemaster Limited (Company No. 03872754)
    # Part of Middleby Corporation since 2015
    rangemaster_data = {
        'Year': [2018, 2019, 2020, 2021, 2022, 2023],
        'Revenue': [130.0, 126.2, 114.0, 144.5, 144.5, 115.5],
        'Pre_Tax_Profit': [None, 10.3, None, None, 27.0, 15.2],
        'Headcount': [None, None, None, 907, 836, 660],
        'Notes': [
            'Pre-pandemic baseline',
            'Slight decline',
            'Pandemic impact',
            'Strong recovery',
            'Peak performance',
            'Challenging market, 200 jobs cut'
        ]
    }

    return {
        'BSH': pd.DataFrame(bsh_data),
        'SMEG': pd.DataFrame(smeg_data),
        'Rangemaster': pd.DataFrame(rangemaster_data)
    }

def create_market_context_data():
    """
    UK Kitchen Appliances and Range Cooker Market Data

    Sources: Market research reports and industry analysis
    """

    market_data = {
        'Year': [2023, 2024, 2025, 2030],
        'UK_Kitchen_Appliances_Market_USD_Bn': [4.76, None, 10.68, 12.38],
        'UK_Home_Appliances_Market_USD_Bn': [None, None, 10.68, 12.38],
        'Global_Range_Cooker_Market_USD_Bn': [16.40, 17.67, None, 28.19],
        'Notes': [
            'UK kitchen appliances valued at $4.76bn',
            'Global range cooker market growing',
            'UK home appliances forecast',
            'Projected growth driven by premiumization'
        ]
    }

    return pd.DataFrame(market_data)

def create_combined_revenue_data():
    """
    Combine all revenue data for comparison
    """

    data = create_companies_house_data()

    # Create a unified timeline from 2018-2023
    years = list(range(2018, 2024))

    combined_data = {
        'Year': years,
        'BSH_UK_Revenue_£M': [None, None, None, None, 810.0, 791.2],
        'SMEG_UK_Revenue_£M': [None, None, None, None, 48.5, 65.0],
        'Rangemaster_Revenue_£M': [130.0, 126.2, 114.0, 144.5, 144.5, 115.5]
    }

    df = pd.DataFrame(combined_data)

    # Calculate total available market share (when all data available)
    df['Total_Revenue_£M'] = df[['BSH_UK_Revenue_£M', 'SMEG_UK_Revenue_£M', 'Rangemaster_Revenue_£M']].sum(axis=1)

    # Calculate market shares for years with complete data
    for company in ['BSH_UK', 'SMEG_UK', 'Rangemaster']:
        df[f'{company}_Share_%'] = (df[f'{company}_Revenue_£M'] / df['Total_Revenue_£M'] * 100).round(2)

    return df

def create_excel_report(output_filename='competitor_analysis_companies_house.xlsx'):
    """
    Create comprehensive Excel report with multiple sheets
    """

    print(f"Creating Excel report: {output_filename}")

    # Get all data
    companies_data = create_companies_house_data()
    market_data = create_market_context_data()
    combined_revenue = create_combined_revenue_data()

    # Create Excel writer
    with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:

        # Sheet 1: Combined Revenue Comparison
        combined_revenue.to_excel(writer, sheet_name='Revenue Comparison', index=False)

        # Sheet 2: BSH UK Details
        companies_data['BSH'].to_excel(writer, sheet_name='BSH UK Details', index=False)

        # Sheet 3: SMEG UK Details
        companies_data['SMEG'].to_excel(writer, sheet_name='SMEG UK Details', index=False)

        # Sheet 4: Rangemaster Details
        companies_data['Rangemaster'].to_excel(writer, sheet_name='Rangemaster Details', index=False)

        # Sheet 5: Market Context
        market_data.to_excel(writer, sheet_name='Market Context', index=False)

        # Sheet 6: Company Information
        company_info = pd.DataFrame({
            'Company': ['BSH Home Appliances Limited', 'SMEG (UK) Limited', 'AGA Rangemaster Limited'],
            'Companies_House_No': ['01844007', '02365886', '03872754'],
            'Incorporated': ['28 Aug 1984', '28 Mar 1989', 'Acquired 2015'],
            'Headquarters': [
                'Grand Union House, Milton Keynes, MK12 5PT',
                'The Magna Building, Abingdon, OX14 1DZ',
                'Nottingham'
            ],
            'Brands': [
                'Bosch, Neff, Siemens',
                'SMEG',
                'AGA, Rangemaster'
            ],
            'Parent_Company': [
                'BSH Hausgeräte GmbH (Germany)',
                'SMEG S.p.A. (Italy)',
                'Middleby Corporation (USA)'
            ],
            'Classification': ['Large', 'Large', 'Large'],
            'Key_Products': [
                'Full range of kitchen appliances',
                'Premium kitchen appliances, range cookers',
                'Range cookers, AGA cookers'
            ]
        })
        company_info.to_excel(writer, sheet_name='Company Information', index=False)

        # Sheet 7: Key Insights
        insights = pd.DataFrame({
            'Category': [
                'Market Leader',
                'Fastest Growth',
                'Market Dynamics',
                'BSH UK Trend',
                'SMEG UK Trend',
                'Rangemaster Trend',
                'Data Availability',
                'Market Size Context'
            ],
            'Insight': [
                'BSH UK is the dominant player with £791M revenue (2023), ~10x larger than competitors',
                'SMEG UK grew 34.12% from 2022 to 2023 (£48.5M to £65M)',
                'All companies faced challenging conditions in 2023 due to inflation and weak consumer confidence',
                'Slight decline from £810M (2022) to £791.2M (2023), -2.3% | Profit down 20.5%',
                'Strong growth trajectory, revenue up 34.12% year-over-year',
                'Significant decline from £144.5M (2022) to £115.5M (2023), -20.1% | 200 jobs cut',
                'Limited historical data available publicly. BSH and SMEG only have 2022-2023. Rangemaster has 2018-2023.',
                'UK kitchen appliances market valued at $4.76bn (2023). Global range cooker market: $16.4bn (2023)'
            ]
        })
        insights.to_excel(writer, sheet_name='Key Insights', index=False)

    print(f"✓ Excel report created successfully: {output_filename}")
    return output_filename

def create_visualizations():
    """
    Create comprehensive visualizations of competitor data
    """

    print("Creating visualizations...")

    companies_data = create_companies_house_data()
    combined_revenue = create_combined_revenue_data()

    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 12))

    # 1. Revenue Comparison Over Time
    ax1 = plt.subplot(2, 3, 1)
    for company, col in [('BSH UK', 'BSH_UK_Revenue_£M'),
                          ('SMEG UK', 'SMEG_UK_Revenue_£M'),
                          ('Rangemaster', 'Rangemaster_Revenue_£M')]:
        data = combined_revenue[combined_revenue[col].notna()]
        ax1.plot(data['Year'], data[col], marker='o', linewidth=2.5, markersize=8, label=company)

    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Revenue (£M)', fontsize=12, fontweight='bold')
    ax1.set_title('Revenue Comparison: UK Range Cooker Competitors\n(Companies House Data)',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(range(2018, 2024))

    # 2. 2023 Revenue Market Share
    ax2 = plt.subplot(2, 3, 2)
    revenue_2023 = combined_revenue[combined_revenue['Year'] == 2023][
        ['BSH_UK_Revenue_£M', 'SMEG_UK_Revenue_£M', 'Rangemaster_Revenue_£M']
    ].iloc[0]

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    wedges, texts, autotexts = ax2.pie(
        revenue_2023.values,
        labels=['BSH UK\n£791.2M', 'SMEG UK\n£65M', 'Rangemaster\n£115.5M'],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'}
    )
    ax2.set_title('2023 Market Share by Revenue\n(Based on Available Companies House Data)',
                  fontsize=14, fontweight='bold', pad=20)

    # 3. Year-over-Year Growth Rates (2022-2023)
    ax3 = plt.subplot(2, 3, 3)
    growth_rates = {
        'BSH UK': ((791.2 - 810.0) / 810.0) * 100,
        'SMEG UK': ((65.0 - 48.5) / 48.5) * 100,
        'Rangemaster': ((115.5 - 144.5) / 144.5) * 100
    }

    bars = ax3.bar(growth_rates.keys(), growth_rates.values(),
                   color=['red' if v < 0 else 'green' for v in growth_rates.values()],
                   alpha=0.7, edgecolor='black', linewidth=1.5)

    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax3.set_ylabel('YoY Growth Rate (%)', fontsize=12, fontweight='bold')
    ax3.set_title('Revenue Growth Rate 2022-2023\n(Companies House Data)',
                  fontsize=14, fontweight='bold', pad=20)
    ax3.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=11, fontweight='bold')

    # 4. Rangemaster Historical Performance
    ax4 = plt.subplot(2, 3, 4)
    rm_data = companies_data['Rangemaster']

    ax4_twin = ax4.twinx()

    line1 = ax4.plot(rm_data['Year'], rm_data['Revenue'],
                     marker='o', linewidth=2.5, markersize=8,
                     color='#45B7D1', label='Revenue')

    profit_data = rm_data[rm_data['Pre_Tax_Profit'].notna()]
    line2 = ax4_twin.plot(profit_data['Year'], profit_data['Pre_Tax_Profit'],
                          marker='s', linewidth=2.5, markersize=8,
                          color='#95E1D3', label='Pre-Tax Profit', linestyle='--')

    ax4.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Revenue (£M)', fontsize=12, fontweight='bold', color='#45B7D1')
    ax4_twin.set_ylabel('Pre-Tax Profit (£M)', fontsize=12, fontweight='bold', color='#95E1D3')
    ax4.set_title('AGA Rangemaster Historical Performance\n(Companies House Data 2018-2023)',
                  fontsize=14, fontweight='bold', pad=20)
    ax4.tick_params(axis='y', labelcolor='#45B7D1')
    ax4_twin.tick_params(axis='y', labelcolor='#95E1D3')
    ax4.grid(True, alpha=0.3)

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc='upper left', fontsize=10)

    # 5. BSH UK Performance 2022-2023
    ax5 = plt.subplot(2, 3, 5)
    bsh_data = companies_data['BSH']

    x = np.arange(len(bsh_data['Year']))
    width = 0.35

    bars1 = ax5.bar(x - width/2, bsh_data['Revenue'], width,
                    label='Revenue (£M)', color='#FF6B6B', alpha=0.8)
    bars2 = ax5.bar(x + width/2, bsh_data['Pre_Tax_Profit'], width,
                    label='Pre-Tax Profit (£M)', color='#FFD93D', alpha=0.8)

    ax5.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Amount (£M)', fontsize=12, fontweight='bold')
    ax5.set_title('BSH UK Revenue & Profit\n(Companies House Data)',
                  fontsize=14, fontweight='bold', pad=20)
    ax5.set_xticks(x)
    ax5.set_xticklabels(bsh_data['Year'])
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'£{height:.1f}M',
                    ha='center', va='bottom', fontsize=9)

    # 6. Relative Size Comparison (2023)
    ax6 = plt.subplot(2, 3, 6)

    companies = ['BSH UK', 'SMEG UK', 'Rangemaster']
    revenues_2023 = [791.2, 65.0, 115.5]

    bars = ax6.barh(companies, revenues_2023, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    ax6.set_xlabel('Revenue (£M)', fontsize=12, fontweight='bold')
    ax6.set_title('2023 Revenue Comparison\n(Companies House Data)',
                  fontsize=14, fontweight='bold', pad=20)
    ax6.grid(True, alpha=0.3, axis='x')

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, revenues_2023)):
        ax6.text(val + 20, bar.get_y() + bar.get_height()/2,
                f'£{val}M',
                ha='left', va='center', fontsize=11, fontweight='bold')

    plt.tight_layout(pad=3.0)

    # Save figure
    output_file = 'competitor_analysis_visualizations.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Visualizations saved: {output_file}")

    plt.show()

    return output_file

def create_market_context_chart():
    """
    Create a separate chart showing market context
    """

    print("Creating market context visualization...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # UK Market Size Projection
    years_uk = [2023, 2025, 2030]
    market_size = [4.76, 10.68, 12.38]

    ax1.plot(years_uk, market_size, marker='o', linewidth=3, markersize=10, color='#6C5CE7')
    ax1.fill_between(years_uk, market_size, alpha=0.3, color='#6C5CE7')

    for x, y in zip(years_uk, market_size):
        ax1.text(x, y + 0.3, f'${y:.2f}bn', ha='center', fontsize=11, fontweight='bold')

    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Market Size (USD Billions)', fontsize=12, fontweight='bold')
    ax1.set_title('UK Kitchen Appliances Market Size\n(USD Billions)',
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(years_uk)

    # Global Range Cooker Market
    years_global = [2023, 2024, 2030]
    global_market = [16.40, 17.67, 28.19]

    ax2.plot(years_global, global_market, marker='s', linewidth=3, markersize=10, color='#00B894')
    ax2.fill_between(years_global, global_market, alpha=0.3, color='#00B894')

    for x, y in zip(years_global, global_market):
        ax2.text(x, y + 0.8, f'${y:.2f}bn', ha='center', fontsize=11, fontweight='bold')

    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Market Size (USD Billions)', fontsize=12, fontweight='bold')
    ax2.set_title('Global Range Cooker Market Size\n(USD Billions)',
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(years_global)

    plt.tight_layout(pad=3.0)

    output_file = 'market_context_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Market context chart saved: {output_file}")

    plt.show()

    return output_file

def print_summary():
    """
    Print a text summary of key findings
    """

    print("\n" + "="*80)
    print("COMPETITOR ANALYSIS SUMMARY - UK RANGE COOKER MARKET")
    print("Companies House Data | BSH UK, SMEG UK, AGA Rangemaster")
    print("="*80 + "\n")

    print("📊 KEY FINDINGS:\n")

    print("1. MARKET DOMINANCE:")
    print("   • BSH UK leads with £791.2M revenue (2023)")
    print("   • Market share: BSH 81.4%, Rangemaster 11.9%, SMEG 6.7%")
    print("   • BSH is ~10x larger than Rangemaster, ~12x larger than SMEG\n")

    print("2. GROWTH DYNAMICS (2022-2023):")
    print("   • SMEG UK: +34.12% growth (£48.5M → £65M) - STRONG GROWTH")
    print("   • BSH UK: -2.3% decline (£810M → £791.2M) - SLIGHT DECLINE")
    print("   • Rangemaster: -20.1% decline (£144.5M → £115.5M) - SIGNIFICANT DECLINE\n")

    print("3. PROFITABILITY TRENDS:")
    print("   • BSH UK profit declined 20.5% (£30.2M → £24M)")
    print("   • Rangemaster profit declined 43.7% (£27M → £15.2M)")
    print("   • Both cited inflationary pressures and weak consumer confidence\n")

    print("4. OPERATIONAL CHANGES:")
    print("   • Rangemaster cut ~200 jobs (836 → 660 employees)")
    print("   • BSH unit sales dropped 9% (2.2M → 2.0M units)")
    print("   • Industry facing challenging market conditions\n")

    print("5. HISTORICAL CONTEXT (Rangemaster 2018-2023):")
    print("   • 2018-2020: Declining trend (£130M → £114M)")
    print("   • 2021-2022: Strong recovery to £144.5M")
    print("   • 2023: Sharp decline to £115.5M\n")

    print("6. MARKET CONTEXT:")
    print("   • UK kitchen appliances market: $4.76bn (2023)")
    print("   • Projected to reach $12.38bn by 2030")
    print("   • Global range cooker market: $16.4bn (2023) → $28.19bn (2030)\n")

    print("7. DATA LIMITATIONS:")
    print("   • BSH UK: Only 2022-2023 data publicly available")
    print("   • SMEG UK: Only 2022-2023 data publicly available")
    print("   • Rangemaster: 2018-2023 data available")
    print("   • More historical data requires direct Companies House account access\n")

    print("="*80)
    print("Data Sources: Companies House (UK), Market Research Reports")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("="*80 + "\n")

def main():
    """
    Main execution function
    """

    print("\n" + "="*80)
    print("GENERATING COMPETITOR ANALYSIS REPORT")
    print("Companies House Data: BSH UK, SMEG UK, AGA Rangemaster")
    print("="*80 + "\n")

    # Create Excel report
    excel_file = create_excel_report()

    # Create visualizations
    viz_file = create_visualizations()

    # Create market context chart
    market_file = create_market_context_chart()

    # Print summary
    print_summary()

    print("\n✅ ANALYSIS COMPLETE!\n")
    print(f"📁 Files created:")
    print(f"   • {excel_file}")
    print(f"   • {viz_file}")
    print(f"   • {market_file}\n")

if __name__ == "__main__":
    main()
