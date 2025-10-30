"""
Revenue and EBITDA Comparison: Cummins Power Systems vs Caterpillar Energy & Transportation

Data sources:
- Cummins investor relations earnings releases (2019-2024)
- Caterpillar investor relations earnings releases (2019-2024)

Note: Caterpillar reports "segment profit" (operating profit) rather than EBITDA.
Full-year segment data compiled from quarterly earnings releases and 10-K filings.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cummins Power Systems Data (in millions USD)
# Source: Cummins earnings releases and segment reporting
cummins_data = {
    'Year': [2019, 2020, 2021, 2022, 2023, 2024, 'LTM\nQ3\'24-\nQ2\'25'],
    'Revenue': [4200, 4100, 4500, 5030, 5670, 6410, 6900],  # Millions USD
    'EBITDA': [220, 296, 390, 640, 1007, 1265, 1461],  # Estimated from quarterly data
    'EBITDA_Margin': [5.2, 7.2, 8.7, 12.7, 17.8, 19.7, 21.2]  # Percent
}

# Caterpillar Energy & Transportation Data (in millions USD)
# Source: Caterpillar earnings releases and segment reporting
# Note: "Segment Profit" used as proxy for EBITDA
caterpillar_data = {
    'Year': [2019, 2020, 2021, 2022, 2023, 2024, 'LTM\nQ4\'24-\nQ3\'25'],
    'Revenue': [20870, 19231, 22831, 26330, 28000, 28850, 30450],  # Millions USD
    'Operating_Profit': [2088, 2100, 2623, 4184, 5310, 5750, 6054],  # Segment profit
    'EBITDA_Margin': [10.0, 10.9, 11.5, 15.9, 19.0, 19.9, 19.9]  # Percent
}

df_cummins = pd.DataFrame(cummins_data)
df_cat = pd.DataFrame(caterpillar_data)

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Cummins Power Systems vs Caterpillar Energy & Transportation\nFinancial Comparison (2019-2024 + LTM)',
             fontsize=16, fontweight='bold')

# Color scheme
cummins_color = '#F7B800'  # Cummins yellow/gold
cat_color = '#FFCD11'  # Caterpillar yellow
cummins_secondary = '#C41E3A'  # Cummins red
cat_secondary = '#000000'  # Caterpillar black

# 1. Revenue Comparison (in Billions)
ax1 = axes[0, 0]
x = np.arange(len(df_cummins['Year']))
width = 0.35

bars1 = ax1.bar(x - width/2, df_cummins['Revenue']/1000, width, label='Cummins Power Systems',
                color=cummins_color, edgecolor='black', linewidth=1.2)
bars2 = ax1.bar(x + width/2, df_cat['Revenue']/1000, width, label='Caterpillar Energy & Transportation',
                color=cat_color, edgecolor='black', linewidth=1.2)

ax1.set_xlabel('Period', fontsize=12, fontweight='bold')
ax1.set_ylabel('Revenue ($ Billions)', fontsize=12, fontweight='bold')
ax1.set_title('Segment Revenue Comparison', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(df_cummins['Year'], fontsize=8)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_axisbelow(True)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.1f}B',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

# 2. EBITDA/Operating Profit Comparison (in Billions)
ax2 = axes[0, 1]
bars3 = ax2.bar(x - width/2, df_cummins['EBITDA']/1000, width, label='Cummins EBITDA',
                color=cummins_secondary, edgecolor='black', linewidth=1.2)
bars4 = ax2.bar(x + width/2, df_cat['Operating_Profit']/1000, width, label='Caterpillar Operating Profit',
                color=cat_secondary, edgecolor='black', linewidth=1.2)

ax2.set_xlabel('Period', fontsize=12, fontweight='bold')
ax2.set_ylabel('EBITDA / Operating Profit ($ Billions)', fontsize=12, fontweight='bold')
ax2.set_title('EBITDA / Operating Profit Comparison', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(df_cummins['Year'], fontsize=8)
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_axisbelow(True)

# Add value labels on bars
for bars in [bars3, bars4]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.2f}B',
                ha='center', va='bottom', fontsize=9, fontweight='bold')

# 3. EBITDA Margins Comparison
ax3 = axes[1, 0]
x_margin = np.arange(len(df_cummins['Year']))
ax3.plot(x_margin, df_cummins['EBITDA_Margin'], marker='o', linewidth=3,
         markersize=10, label='Cummins Power Systems', color=cummins_secondary)
ax3.plot(x_margin, df_cat['EBITDA_Margin'], marker='s', linewidth=3,
         markersize=10, label='Caterpillar Energy & Transportation', color=cat_secondary)

ax3.set_xlabel('Period', fontsize=12, fontweight='bold')
ax3.set_ylabel('EBITDA Margin (%)', fontsize=12, fontweight='bold')
ax3.set_title('EBITDA Margin Trends', fontsize=14, fontweight='bold')
ax3.set_xticks(x_margin)
ax3.set_xticklabels(df_cummins['Year'], fontsize=8)
ax3.legend(loc='upper left', fontsize=10)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.set_axisbelow(True)

# Add value labels on points
for i, margin in enumerate(df_cummins['EBITDA_Margin']):
    ax3.text(i, margin + 0.5, f'{margin:.1f}%', ha='center', va='bottom',
             fontsize=8, fontweight='bold', color=cummins_secondary)

for i, margin in enumerate(df_cat['EBITDA_Margin']):
    ax3.text(i, margin - 1.2, f'{margin:.1f}%', ha='center', va='top',
             fontsize=8, fontweight='bold', color=cat_secondary)

# 4. Revenue Growth Rate Comparison
ax4 = axes[1, 1]

# Calculate year-over-year growth rates
cummins_growth = [0] + [((df_cummins['Revenue'][i] - df_cummins['Revenue'][i-1]) /
                         df_cummins['Revenue'][i-1] * 100) for i in range(1, len(df_cummins['Revenue']))]
cat_growth = [0] + [((df_cat['Revenue'][i] - df_cat['Revenue'][i-1]) /
                     df_cat['Revenue'][i-1] * 100) for i in range(1, len(df_cat['Revenue']))]

bars5 = ax4.bar(x - width/2, cummins_growth, width, label='Cummins Power Systems',
                color=cummins_color, edgecolor='black', linewidth=1.2)
bars6 = ax4.bar(x + width/2, cat_growth, width, label='Caterpillar Energy & Transportation',
                color=cat_color, edgecolor='black', linewidth=1.2)

ax4.set_xlabel('Period', fontsize=12, fontweight='bold')
ax4.set_ylabel('Revenue Growth Rate (%)', fontsize=12, fontweight='bold')
ax4.set_title('Period-over-Period Revenue Growth', fontsize=14, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(df_cummins['Year'], fontsize=8)
ax4.legend(loc='upper left', fontsize=10)
ax4.grid(True, alpha=0.3, linestyle='--')
ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax4.set_axisbelow(True)

# Add value labels on bars
for bars in [bars5, bars6]:
    for bar in bars:
        height = bar.get_height()
        if height != 0:  # Skip 2019 baseline
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/user/kitchen-demand-lab/revenue_ebitda_comparison.png', dpi=300, bbox_inches='tight')
print("Chart saved: revenue_ebitda_comparison.png")

# Create summary table
print("\n" + "="*80)
print("SUMMARY COMPARISON TABLE")
print("="*80)

summary_df = pd.DataFrame({
    'Year': df_cummins['Year'],
    'Cummins Revenue ($B)': df_cummins['Revenue'] / 1000,
    'Cummins EBITDA ($M)': df_cummins['EBITDA'],
    'Cummins Margin (%)': df_cummins['EBITDA_Margin'],
    'CAT Revenue ($B)': df_cat['Revenue'] / 1000,
    'CAT Op. Profit ($M)': df_cat['Operating_Profit'],
    'CAT Margin (%)': df_cat['EBITDA_Margin']
})

print(summary_df.to_string(index=False))
print("="*80)

# Key insights
print("\nKEY INSIGHTS:")
print("-" * 80)
print(f"1. Revenue Scale (LTM):")
print(f"   - Caterpillar E&T is ~{df_cat['Revenue'].iloc[-1]/df_cummins['Revenue'].iloc[-1]:.1f}x larger than Cummins Power Systems")
print(f"   - CAT LTM: ${df_cat['Revenue'].iloc[-1]/1000:.1f}B | Cummins LTM: ${df_cummins['Revenue'].iloc[-1]/1000:.1f}B")

print(f"\n2. Profitability (LTM - Most Recent):")
print(f"   - Cummins EBITDA Margin: {df_cummins['EBITDA_Margin'].iloc[-1]:.1f}%")
print(f"   - Caterpillar Op. Margin: {df_cat['EBITDA_Margin'].iloc[-1]:.1f}%")
print(f"   - Cummins now leads by {df_cummins['EBITDA_Margin'].iloc[-1] - df_cat['EBITDA_Margin'].iloc[-1]:.1f} percentage points")

cummins_cagr = ((df_cummins['Revenue'].iloc[-2] / df_cummins['Revenue'].iloc[0]) ** (1/5) - 1) * 100
cat_cagr = ((df_cat['Revenue'].iloc[-2] / df_cat['Revenue'].iloc[0]) ** (1/5) - 1) * 100
print(f"\n3. Revenue CAGR (2019-2024):")
print(f"   - Cummins: {cummins_cagr:.1f}%")
print(f"   - Caterpillar: {cat_cagr:.1f}%")

print(f"\n4. Margin Improvement (2019 to LTM):")
print(f"   - Cummins: {df_cummins['EBITDA_Margin'].iloc[0]:.1f}% → {df_cummins['EBITDA_Margin'].iloc[-1]:.1f}% (+{df_cummins['EBITDA_Margin'].iloc[-1] - df_cummins['EBITDA_Margin'].iloc[0]:.1f} pts)")
print(f"   - Caterpillar: {df_cat['EBITDA_Margin'].iloc[0]:.1f}% → {df_cat['EBITDA_Margin'].iloc[-1]:.1f}% (+{df_cat['EBITDA_Margin'].iloc[-1] - df_cat['EBITDA_Margin'].iloc[0]:.1f} pts)")
print("-" * 80)

print(f"\n5. Latest LTM Performance:")
print(f"   - Cummins LTM Revenue: ${df_cummins['Revenue'].iloc[-1]/1000:.1f}B (Q3'24-Q2'25)")
print(f"   - Cummins LTM EBITDA: ${df_cummins['EBITDA'].iloc[-1]/1000:.2f}B")
print(f"   - Cummins LTM Margin: {df_cummins['EBITDA_Margin'].iloc[-1]:.1f}%")
print(f"   - Caterpillar LTM Revenue: ${df_cat['Revenue'].iloc[-1]/1000:.1f}B (Q4'24-Q3'25)")
print(f"   - Caterpillar LTM Op. Profit: ${df_cat['Operating_Profit'].iloc[-1]/1000:.2f}B")
print(f"   - Caterpillar LTM Margin: {df_cat['EBITDA_Margin'].iloc[-1]:.1f}%")
print(f"   - Cummins now leads in margin by {df_cummins['EBITDA_Margin'].iloc[-1] - df_cat['EBITDA_Margin'].iloc[-1]:.1f} pts!")
print("-" * 80)

print("\nNOTE: Data compiled from public filings and earnings releases.")
print("Caterpillar figures represent segment operating profit; Cummins figures represent EBITDA.")
print("Some 2019-2021 values estimated from quarterly data and segment reporting.")
print("LTM = Last Twelve Months (most recent rolling 12-month period)")
