# notebooks/26_gldas_trend_analysis.py
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import json

print("📊 Analyzing GLDAS trends to infer groundwater changes...")

# Load GLDAS data
gldas_df = pd.read_csv('data/csv/pakistan_gldas_2018_2024_monthly.csv')
gldas_df['date'] = pd.to_datetime(gldas_df['date'])
gldas_df = gldas_df.sort_values('date')

# Calculate baseline (first year average)
baseline_period = gldas_df[gldas_df['date'].dt.year == 2018]
baseline_value = baseline_period['groundwater_cm'].mean()

print(f"📏 Baseline (2018 average): {baseline_value:.2f} kg/m²")

# Convert absolute values to anomalies (change from baseline)
gldas_df['anomaly_from_baseline'] = gldas_df['groundwater_cm'] - baseline_value

# Calculate year-over-year changes
gldas_df['year'] = gldas_df['date'].dt.year
yearly_means = gldas_df.groupby('year')['groundwater_cm'].mean()
yearly_changes = yearly_means.diff()

print("\n📈 Year-over-Year Changes:")
for year, change in yearly_changes.items():
    if not pd.isna(change):
        print(f"  {year}: {change:+.2f} kg/m² ({change/baseline_value*100:+.1f}%)")

# Perform trend analysis
x = np.arange(len(gldas_df))
y = gldas_df['groundwater_cm'].values
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

# Convert to monthly and annual rates
monthly_change = slope
annual_change = slope * 12
total_change = gldas_df['groundwater_cm'].iloc[-1] - gldas_df['groundwater_cm'].iloc[0]

print(f"\n📊 GLDAS Trend Analysis (2018-2024):")
print(f"  Monthly change: {monthly_change:+.3f} kg/m²/month")
print(f"  Annual change: {annual_change:+.3f} kg/m²/year")
print(f"  Total change: {total_change:+.2f} kg/m²")
print(f"  Relative change: {total_change/baseline_value*100:+.1f}%")
print(f"  Trend significance: p-value = {p_value:.6f}")

# Interpret the trend
if p_value < 0.05:
    if annual_change < -1:
        interpretation = "Significant declining trend - likely continued groundwater depletion"
    elif annual_change > 1:
        interpretation = "Significant increasing trend - possible groundwater recovery"
    else:
        interpretation = "Significant but small change - relatively stable"
else:
    interpretation = "No statistically significant trend - inconclusive"

print(f"\n🔍 Interpretation: {interpretation}")

# Create visualization
plt.figure(figsize=(12, 8))

# Subplot 1: Absolute values with trend
plt.subplot(2, 1, 1)
plt.plot(gldas_df['date'], gldas_df['groundwater_cm'], 'b-', label='GLDAS Soil Moisture', linewidth=2)
plt.plot(gldas_df['date'], intercept + slope * x, 'r--', label=f'Trend: {annual_change:+.1f} kg/m²/year', linewidth=2)
plt.axhline(y=baseline_value, color='green', linestyle=':', label='2018 Baseline')
plt.fill_between(gldas_df['date'], baseline_value, gldas_df['groundwater_cm'], 
                 where=(gldas_df['groundwater_cm'] < baseline_value), 
                 color='red', alpha=0.3, label='Below baseline')
plt.fill_between(gldas_df['date'], baseline_value, gldas_df['groundwater_cm'], 
                 where=(gldas_df['groundwater_cm'] >= baseline_value), 
                 color='green', alpha=0.3, label='Above baseline')
plt.xlabel('Date')
plt.ylabel('Soil Moisture (kg/m²)')
plt.title('GLDAS Deep Soil Moisture Trends (2018-2024)')
plt.legend()
plt.grid(True, alpha=0.3)

# Subplot 2: Anomalies from baseline
plt.subplot(2, 1, 2)
colors = ['red' if x < 0 else 'green' for x in gldas_df['anomaly_from_baseline']]
plt.bar(gldas_df['date'], gldas_df['anomaly_from_baseline'], color=colors, alpha=0.7, width=20)
plt.axhline(y=0, color='black', linewidth=1)
plt.xlabel('Date')
plt.ylabel('Change from 2018 Baseline (kg/m²)')
plt.title('Soil Moisture Anomalies - Indicator of Groundwater Changes')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/outputs/gldas_trend_analysis.png', dpi=300, bbox_inches='tight')
print("📊 Saved trend analysis plot")

# Compare with GRACE historical trend
grace_annual_change_cm = -0.808  # From GRACE analysis
# Rough conversion: 1 cm of water = 10 kg/m²
grace_annual_change_kg = grace_annual_change_cm * 10

print(f"\n🔄 Comparison with GRACE historical trend:")
print(f"  GRACE (2002-2017): {grace_annual_change_cm:.2f} cm/year ≈ {grace_annual_change_kg:.1f} kg/m²/year")
print(f"  GLDAS (2018-2024): {annual_change:.2f} kg/m²/year")

if annual_change < 0 and abs(annual_change) > 5:
    conclusion = "GLDAS data suggests groundwater depletion likely continued after 2017"
elif annual_change > 5:
    conclusion = "GLDAS data suggests possible groundwater recovery, but needs GRACE-FO validation"
else:
    conclusion = "GLDAS shows relatively stable conditions, but high uncertainty"

# Save analysis results
analysis_results = {
    "period": "2018-2024",
    "data_source": "GLDAS",
    "baseline_value": float(baseline_value),
    "total_change": float(total_change),
    "annual_change": float(annual_change),
    "monthly_change": float(monthly_change),
    "relative_change_percent": float(total_change/baseline_value*100),
    "trend_pvalue": float(p_value),
    "trend_significant": p_value < 0.05,
    "interpretation": interpretation,
    "conclusion": conclusion,
    "comparison_with_grace": {
        "grace_annual_change_cm": grace_annual_change_cm,
        "grace_annual_change_kg_estimate": grace_annual_change_kg,
        "gldas_annual_change_kg": float(annual_change)
    },
    "yearly_averages": yearly_means.to_dict(),
    "yearly_changes": yearly_changes.to_dict()
}

with open('data/processed/gldas_trend_analysis.json', 'w') as f:
    json.dump(analysis_results, f, indent=2)

print(f"\n✅ Analysis complete!")
print(f"📌 Final conclusion: {conclusion}")