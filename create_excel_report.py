"""
Create comprehensive Excel report with Cummins vs Caterpillar comparison
Includes historical data, LTM data, quarterly data, and embedded charts
"""

import pandas as pd
import xlsxwriter
from datetime import datetime

# Create Excel workbook
workbook = xlsxwriter.Workbook('/home/user/kitchen-demand-lab/Power_Systems_Comparison.xlsx')

# Add formats
header_format = workbook.add_format({
    'bold': True,
    'font_size': 12,
    'bg_color': '#4472C4',
    'font_color': 'white',
    'border': 1,
    'align': 'center',
    'valign': 'vcenter'
})

title_format = workbook.add_format({
    'bold': True,
    'font_size': 14,
    'bg_color': '#203864',
    'font_color': 'white',
    'align': 'center',
    'valign': 'vcenter'
})

number_format = workbook.add_format({'num_format': '#,##0'})
decimal_format = workbook.add_format({'num_format': '#,##0.0'})
percent_format = workbook.add_format({'num_format': '0.0%'})
currency_format = workbook.add_format({'num_format': '$#,##0'})

# ========================================
# SHEET 1: ANNUAL DATA (2019-2024)
# ========================================
worksheet1 = workbook.add_worksheet('Annual Data 2019-2024')
worksheet1.set_column('A:A', 10)
worksheet1.set_column('B:G', 18)

# Title
worksheet1.merge_range('A1:G1', 'Annual Financial Comparison: Cummins Power Systems vs Caterpillar Energy & Transportation (2019-2024)', title_format)

# Headers
worksheet1.write('A3', 'Year', header_format)
worksheet1.write('B3', 'Cummins Revenue ($M)', header_format)
worksheet1.write('C3', 'Cummins EBITDA ($M)', header_format)
worksheet1.write('D3', 'Cummins Margin (%)', header_format)
worksheet1.write('E3', 'CAT Revenue ($M)', header_format)
worksheet1.write('F3', 'CAT EBITDA ($M)', header_format)
worksheet1.write('G3', 'CAT Margin (%)', header_format)

# Annual data (Caterpillar EBITDA calculated with allocated D&A)
annual_data = [
    [2019, 4200, 220, 5.2, 20870, 3019, 14.5],
    [2020, 4100, 296, 7.2, 19231, 3159, 16.4],
    [2021, 4500, 390, 8.7, 22831, 3677, 16.1],
    [2022, 5030, 640, 12.7, 26330, 5225, 19.8],
    [2023, 5670, 1007, 17.8, 28000, 6205, 22.2],
    [2024, 6410, 1265, 19.7, 28850, 6708, 23.3]
]

row = 3
for data in annual_data:
    worksheet1.write(row, 0, data[0])
    worksheet1.write(row, 1, data[1], number_format)
    worksheet1.write(row, 2, data[2], number_format)
    worksheet1.write(row, 3, data[3]/100, percent_format)
    worksheet1.write(row, 4, data[4], number_format)
    worksheet1.write(row, 5, data[5], number_format)
    worksheet1.write(row, 6, data[6]/100, percent_format)
    row += 1

# ========================================
# SHEET 2: LTM DATA
# ========================================
worksheet2 = workbook.add_worksheet('LTM Data')
worksheet2.set_column('A:A', 25)
worksheet2.set_column('B:D', 18)

# Title
worksheet2.merge_range('A1:D1', 'Last Twelve Months (LTM) Financial Data', title_format)

# Cummins LTM (Q3 2024 - Q2 2025)
worksheet2.merge_range('A3:D3', 'Cummins Power Systems - LTM (Q3 2024 - Q2 2025)', header_format)
worksheet2.write('A4', 'Period', header_format)
worksheet2.write('B4', 'Revenue ($M)', header_format)
worksheet2.write('C4', 'EBITDA ($M)', header_format)
worksheet2.write('D4', 'EBITDA Margin (%)', header_format)

worksheet2.write('A5', 'LTM (Q3\'24-Q2\'25)')
worksheet2.write('B5', 6900, number_format)
worksheet2.write('C5', 1461, number_format)
worksheet2.write('D5', 0.212, percent_format)

# Caterpillar LTM (Q4 2024 - Q3 2025)
worksheet2.merge_range('A7:D7', 'Caterpillar Energy & Transportation - LTM (Q4 2024 - Q3 2025)', header_format)
worksheet2.write('A8', 'Period', header_format)
worksheet2.write('B8', 'Revenue ($M)', header_format)
worksheet2.write('C8', 'EBITDA ($M)', header_format)
worksheet2.write('D8', 'EBITDA Margin (%)', header_format)

worksheet2.write('A9', 'LTM (Q4\'24-Q3\'25)')
worksheet2.write('B9', 30450, number_format)
worksheet2.write('C9', 7046, number_format)
worksheet2.write('D9', 0.231, percent_format)

# Comparison
worksheet2.merge_range('A11:D11', 'LTM Comparison', header_format)
worksheet2.write('A12', 'Metric', header_format)
worksheet2.write('B12', 'Cummins', header_format)
worksheet2.write('C12', 'Caterpillar', header_format)
worksheet2.write('D12', 'CAT/Cummins Ratio', header_format)

worksheet2.write('A13', 'Revenue ($B)')
worksheet2.write('B13', 6.9, decimal_format)
worksheet2.write('C13', 30.5, decimal_format)
worksheet2.write('D13', 4.4, decimal_format)

worksheet2.write('A14', 'EBITDA ($B)')
worksheet2.write('B14', 1.46, decimal_format)
worksheet2.write('C14', 7.05, decimal_format)
worksheet2.write('D14', 4.8, decimal_format)

worksheet2.write('A15', 'EBITDA Margin (%)')
worksheet2.write('B15', 0.212, percent_format)
worksheet2.write('C15', 0.231, percent_format)
worksheet2.write('D15', '', percent_format)

# ========================================
# SHEET 3: QUARTERLY DATA - CUMMINS
# ========================================
worksheet3 = workbook.add_worksheet('Quarterly - Cummins')
worksheet3.set_column('A:A', 15)
worksheet3.set_column('B:D', 18)

worksheet3.merge_range('A1:D1', 'Cummins Power Systems - Quarterly Results', title_format)

worksheet3.write('A3', 'Quarter', header_format)
worksheet3.write('B3', 'Revenue ($M)', header_format)
worksheet3.write('C3', 'EBITDA ($M)', header_format)
worksheet3.write('D3', 'EBITDA Margin (%)', header_format)

cummins_quarterly = [
    ['Q3 2024', 1700, 328, 19.4],
    ['Q4 2024', 1700, 314, 18.0],
    ['Q1 2025', 1600, 389, 23.6],
    ['Q2 2025', 1900, 430, 22.8]
]

row = 3
for data in cummins_quarterly:
    worksheet3.write(row, 0, data[0])
    worksheet3.write(row, 1, data[1], number_format)
    worksheet3.write(row, 2, data[2], number_format)
    worksheet3.write(row, 3, data[3]/100, percent_format)
    row += 1

# ========================================
# SHEET 4: QUARTERLY DATA - CATERPILLAR
# ========================================
worksheet4 = workbook.add_worksheet('Quarterly - Caterpillar')
worksheet4.set_column('A:A', 15)
worksheet4.set_column('B:D', 18)

worksheet4.merge_range('A1:D1', 'Caterpillar Energy & Transportation - Quarterly Results', title_format)

worksheet4.write('A3', 'Quarter', header_format)
worksheet4.write('B3', 'Revenue ($M)', header_format)
worksheet4.write('C3', 'Operating Profit ($M)', header_format)
worksheet4.write('D3', 'Op. Margin (%)', header_format)

cat_quarterly = [
    ['Q4 2024', 7649, 1477, 19.3],
    ['Q1 2025', 6568, 1314, 20.0],
    ['Q2 2025', 7836, 1585, 20.2],
    ['Q3 2025', 8397, 1678, 20.0]
]

row = 3
for data in cat_quarterly:
    worksheet4.write(row, 0, data[0])
    worksheet4.write(row, 1, data[1], number_format)
    worksheet4.write(row, 2, data[2], number_format)
    worksheet4.write(row, 3, data[3]/100, percent_format)
    row += 1

# ========================================
# SHEET 5: KEY INSIGHTS
# ========================================
worksheet5 = workbook.add_worksheet('Key Insights')
worksheet5.set_column('A:B', 50)

worksheet5.merge_range('A1:B1', 'Key Insights & Analysis', title_format)

insights = [
    ['', ''],
    ['1. REVENUE SCALE (2024)', ''],
    ['   Caterpillar E&T Revenue', '$28.9 Billion'],
    ['   Cummins Power Systems Revenue', '$6.4 Billion'],
    ['   Size Ratio', '4.5x'],
    ['', ''],
    ['2. LTM REVENUE (Most Recent)', ''],
    ['   Caterpillar E&T LTM (Q4\'24-Q3\'25)', '$30.5 Billion'],
    ['   Cummins Power Systems LTM (Q3\'24-Q2\'25)', '$6.9 Billion'],
    ['   Size Ratio', '4.4x'],
    ['', ''],
    ['3. REVENUE GROWTH (2019-2024 CAGR)', ''],
    ['   Cummins Power Systems', '8.8%'],
    ['   Caterpillar E&T', '6.7%'],
    ['', ''],
    ['4. PROFITABILITY (2024 - Apples-to-Apples EBITDA)', ''],
    ['   Cummins EBITDA Margin', '19.7%'],
    ['   Caterpillar EBITDA Margin', '23.3%'],
    ['   Caterpillar leads', '+3.6 pts'],
    ['', ''],
    ['5. MARGIN EXPANSION (2019-2024)', ''],
    ['   Cummins Improvement', '+14.5 percentage points (5.2% → 19.7%)'],
    ['   Caterpillar Improvement', '+8.8 percentage points (14.5% → 23.3%)'],
    ['', ''],
    ['6. LTM PROFITABILITY (Most Recent - EBITDA)', ''],
    ['   Cummins LTM Margin', '21.2%'],
    ['   Caterpillar LTM EBITDA Margin', '23.1%'],
    ['   Caterpillar maintains lead', '+1.9 pts'],
    ['', ''],
    ['7. EBITDA DOLLARS (LTM)', ''],
    ['   Caterpillar EBITDA', '$7.05 Billion'],
    ['   Cummins EBITDA', '$1.46 Billion'],
    ['   Ratio', '4.8x'],
    ['', ''],
    ['8. KEY DRIVERS', ''],
    ['   - Data center power demand (AI/cloud)', ''],
    ['   - Strong pricing power', ''],
    ['   - Operational improvements', ''],
    ['   - Energy transition infrastructure', ''],
    ['', ''],
    ['9. COMPETITIVE POSITION', ''],
    ['   Caterpillar', 'Larger (4.4x), higher EBITDA margin leader'],
    ['   Cummins', 'Faster growth, rapidly closing margin gap'],
]

row = 1
bold_format = workbook.add_format({'bold': True})
for data in insights:
    if data[0].startswith('   '):
        worksheet5.write(row, 0, data[0])
        worksheet5.write(row, 1, data[1])
    else:
        worksheet5.write(row, 0, data[0], bold_format)
        worksheet5.write(row, 1, data[1], bold_format)
    row += 1

# ========================================
# SHEET 6: CHARTS SUMMARY
# ========================================
worksheet6 = workbook.add_worksheet('Charts')
worksheet6.set_column('A:A', 100)

worksheet6.merge_range('A1:A1', 'Visual Analysis', title_format)

# Revenue chart
chart_revenue = workbook.add_chart({'type': 'column'})
chart_revenue.add_series({
    'name': 'Cummins Power Systems',
    'categories': '=Annual Data 2019-2024!$A$4:$A$9',
    'values': '=Annual Data 2019-2024!$B$4:$B$9',
    'fill': {'color': '#F7B800'},
    'border': {'color': 'black'}
})
chart_revenue.add_series({
    'name': 'Caterpillar E&T',
    'categories': '=Annual Data 2019-2024!$A$4:$A$9',
    'values': '=Annual Data 2019-2024!$E$4:$E$9',
    'fill': {'color': '#FFCD11'},
    'border': {'color': 'black'}
})
chart_revenue.set_title({'name': 'Segment Revenue Comparison (2019-2024)'})
chart_revenue.set_x_axis({'name': 'Year'})
chart_revenue.set_y_axis({'name': 'Revenue ($M)'})
chart_revenue.set_size({'width': 720, 'height': 400})
chart_revenue.set_legend({'position': 'bottom'})
worksheet6.insert_chart('A3', chart_revenue)

# Margin chart
chart_margin = workbook.add_chart({'type': 'line'})
chart_margin.add_series({
    'name': 'Cummins EBITDA Margin',
    'categories': '=Annual Data 2019-2024!$A$4:$A$9',
    'values': '=Annual Data 2019-2024!$D$4:$D$9',
    'line': {'color': '#C41E3A', 'width': 3},
    'marker': {'type': 'circle', 'size': 8}
})
chart_margin.add_series({
    'name': 'Caterpillar EBITDA Margin',
    'categories': '=Annual Data 2019-2024!$A$4:$A$9',
    'values': '=Annual Data 2019-2024!$G$4:$G$9',
    'line': {'color': '#000000', 'width': 3},
    'marker': {'type': 'square', 'size': 8}
})
chart_margin.set_title({'name': 'EBITDA Margin Trends (2019-2024)'})
chart_margin.set_x_axis({'name': 'Year'})
chart_margin.set_y_axis({'name': 'Margin (%)', 'num_format': '0%'})
chart_margin.set_size({'width': 720, 'height': 400})
chart_margin.set_legend({'position': 'bottom'})
worksheet6.insert_chart('A25', chart_margin)

# Quarterly revenue chart - Cummins
chart_q_cummins = workbook.add_chart({'type': 'column'})
chart_q_cummins.add_series({
    'name': 'Cummins Revenue',
    'categories': '=Quarterly - Cummins!$A$4:$A$7',
    'values': '=Quarterly - Cummins!$B$4:$B$7',
    'fill': {'color': '#F7B800'},
    'border': {'color': 'black'}
})
chart_q_cummins.set_title({'name': 'Cummins Quarterly Revenue (Q3 2024 - Q2 2025)'})
chart_q_cummins.set_x_axis({'name': 'Quarter'})
chart_q_cummins.set_y_axis({'name': 'Revenue ($M)'})
chart_q_cummins.set_size({'width': 720, 'height': 400})
worksheet6.insert_chart('A47', chart_q_cummins)

# Add metadata
worksheet5.write('A45', 'Data Sources:', bold_format)
worksheet5.write('A46', '- Cummins Inc. Investor Relations (earnings releases 2019-2025)')
worksheet5.write('A47', '- Caterpillar Inc. Investor Relations (earnings releases 2019-2025)')
worksheet5.write('A48', f'- Report Generated: {datetime.now().strftime("%B %d, %Y")}')
worksheet5.write('A49', '- APPLES-TO-APPLES: Both showing EBITDA. CAT EBITDA = Op. Profit + allocated D&A')
worksheet5.write('A50', '- LTM periods differ due to reporting schedules')

workbook.close()

print("Excel report created successfully!")
print("File: Power_Systems_Comparison.xlsx")
print("\nSheets included:")
print("1. Annual Data 2019-2024")
print("2. LTM Data (Most Recent)")
print("3. Quarterly - Cummins")
print("4. Quarterly - Caterpillar")
print("5. Key Insights")
print("6. Charts (Revenue & Margin visualizations)")
