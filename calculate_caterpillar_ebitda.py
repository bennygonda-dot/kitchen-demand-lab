"""
Calculate Caterpillar Energy & Transportation EBITDA
using D&A allocation based on segment revenue proportion

Methodology:
- Caterpillar reports Operating Profit at segment level
- EBITDA = Operating Profit + D&A
- Allocate total company D&A to segment proportionally based on revenue
"""

import pandas as pd

# Caterpillar Total Company Data (from MacroTrends and company reports)
cat_total = {
    'Year': [2019, 2020, 2021, 2022, 2023, 2024],
    'Total_Revenue': [53800, 41748, 50971, 59427, 67060, 64809],  # Millions USD
    'Total_DA': [2400, 2300, 2352, 2350, 2144, 2153]  # Estimated D&A in millions (conservative estimates)
}

# Energy & Transportation Segment Data
# Revenue and Operating Profit from our previous research
energy_transport = {
    'Year': [2019, 2020, 2021, 2022, 2023, 2024, 'LTM Q4\'24-Q3\'25'],
    'Revenue': [20870, 19231, 22831, 26330, 28000, 28850, 30450],  # Millions USD
    'Operating_Profit': [2088, 2100, 2623, 4184, 5310, 5750, 6054]  # Millions USD
}

# Calculate segment revenue as % of total for 2019-2024
df_total = pd.DataFrame(cat_total)
df_segment = pd.DataFrame(energy_transport)

# Calculate allocated D&A for each year
allocated_da = []
for i in range(6):  # 2019-2024
    revenue_pct = df_segment['Revenue'][i] / df_total['Total_Revenue'][i]
    segment_da = df_total['Total_DA'][i] * revenue_pct
    allocated_da.append(segment_da)

# For LTM, use average D&A rate from 2023-2024
ltm_revenue_pct = (df_segment['Revenue'][6] / ((df_total['Total_Revenue'][5] + df_total['Total_Revenue'][4])/2))
ltm_da = ((df_total['Total_DA'][4] + df_total['Total_DA'][5])/2) * ltm_revenue_pct
allocated_da.append(ltm_da)

# Calculate EBITDA
df_segment['Allocated_DA'] = allocated_da
df_segment['EBITDA'] = df_segment['Operating_Profit'] + df_segment['Allocated_DA']
df_segment['EBITDA_Margin'] = (df_segment['EBITDA'] / df_segment['Revenue'] * 100).round(1)
df_segment['Op_Margin'] = (df_segment['Operating_Profit'] / df_segment['Revenue'] * 100).round(1)

print("="*100)
print("CATERPILLAR ENERGY & TRANSPORTATION - EBITDA CALCULATION")
print("="*100)
print("\nMethodology: Allocated D&A based on segment revenue as % of total company revenue")
print(f"Average D&A allocation to Energy & Transportation: ~{df_segment['Allocated_DA'][:6].mean():.0f}M per year")
print("\n" + "="*100)

# Display results
summary = df_segment[['Year', 'Revenue', 'Operating_Profit', 'Allocated_DA', 'EBITDA', 'Op_Margin', 'EBITDA_Margin']].copy()
summary.columns = ['Year', 'Revenue ($M)', 'Op. Profit ($M)', 'D&A ($M)', 'EBITDA ($M)', 'Op. Margin (%)', 'EBITDA Margin (%)']

print(summary.to_string(index=False))
print("="*100)

print("\n" + "="*100)
print("KEY FINDINGS - APPLES-TO-APPLES EBITDA MARGIN COMPARISON")
print("="*100)
print(f"\n2024 EBITDA Margins:")
print(f"  Cummins Power Systems: 19.7%")
print(f"  Caterpillar E&T (adjusted): {df_segment['EBITDA_Margin'][5]:.1f}%")
print(f"  Difference: {19.7 - df_segment['EBITDA_Margin'][5]:.1f} percentage points")

print(f"\nLTM EBITDA Margins:")
print(f"  Cummins Power Systems: 21.2%")
print(f"  Caterpillar E&T (adjusted): {df_segment['EBITDA_Margin'][6]:.1f}%")
print(f"  Cummins advantage: {21.2 - df_segment['EBITDA_Margin'][6]:.1f} percentage points")

print(f"\nEBITDA Margin Improvement (2019 to LTM):")
print(f"  Cummins: 5.2% → 21.2% (+16.0 pts)")
print(f"  Caterpillar E&T: {df_segment['EBITDA_Margin'][0]:.1f}% → {df_segment['EBITDA_Margin'][6]:.1f}% ({df_segment['EBITDA_Margin'][6] - df_segment['EBITDA_Margin'][0]:.1f} pts)")

print("\n" + "="*100)
print("Note: D&A allocated proportionally based on segment revenue as % of total company revenue")
print("This is a standard method when segment-level D&A is not disclosed")
print("="*100)

# Save for use in visualization
df_segment.to_csv('/home/user/kitchen-demand-lab/caterpillar_ebitda_calculated.csv', index=False)
print("\nData saved to: caterpillar_ebitda_calculated.csv")
