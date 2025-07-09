# notebooks/23_historical_grace_analysis.py
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler

print("📊 Historical Groundwater Analysis (2002-2017)")

def analyze_grace_historical():
    """Comprehensive analysis of GRACE historical data"""
    
    # Load GRACE data
    grace_df = pd.read_csv('data/csv/pakistan_grace_2002_2017_complete.csv')
    grace_df['date'] = pd.to_datetime(grace_df['date'])
    grace_df = grace_df.sort_values('date')
    
    print(f"📅 Historical Period: {grace_df['date'].min()} to {grace_df['date'].max()}")
    print(f"📊 Data Points: {len(grace_df)}")
    
    # Basic statistics
    stats_summary = {
        'mean_groundwater_cm': grace_df['groundwater_cm'].mean(),
        'std_groundwater_cm': grace_df['groundwater_cm'].std(),
        'min_groundwater_cm': grace_df['groundwater_cm'].min(),
        'max_groundwater_cm': grace_df['groundwater_cm'].max(),
        'total_change': grace_df['groundwater_cm'].iloc[-1] - grace_df['groundwater_cm'].iloc[0]
    }
    
    print(f"\n📊 Historical Statistics (2002-2017):")
    print(f"   Mean Anomaly: {stats_summary['mean_groundwater_cm']:.2f} cm")
    print(f"   Standard Deviation: {stats_summary['std_groundwater_cm']:.2f} cm")
    print(f"   Range: {stats_summary['min_groundwater_cm']:.2f} to {stats_summary['max_groundwater_cm']:.2f} cm")
    print(f"   Total Change: {stats_summary['total_change']:.2f} cm over 15 years")
    
    # Trend analysis
    x_vals = np.arange(len(grace_df))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, grace_df['groundwater_cm'])
    
    trend_stats = {
        'slope_cm_per_month': slope,
        'slope_cm_per_year': slope * 12,
        'r_squared': r_value**2,
        'p_value': p_value,
        'trend_significance': 'Significant' if p_value < 0.05 else 'Not Significant'
    }
    
    print(f"\n📈 Trend Analysis:")
    print(f"   Slope: {trend_stats['slope_cm_per_year']:.3f} cm/year")
    print(f"   R²: {trend_stats['r_squared']:.3f}")
    print(f"   P-value: {trend_stats['p_value']:.6f}")
    print(f"   Trend: {trend_stats['trend_significance']}")
    
    # Seasonal analysis
    grace_df['month'] = grace_df['date'].dt.month
    grace_df['year'] = grace_df['date'].dt.year
    
    seasonal_stats = grace_df.groupby('month')['groundwater_cm'].agg(['mean', 'std']).round(3)
    
    # Visualizations
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Time series with trend
    axes[0, 0].plot(grace_df['date'], grace_df['groundwater_cm'], 'b-', alpha=0.7, linewidth=1)
    trend_line = intercept + slope * x_vals
    axes[0, 0].plot(grace_df['date'], trend_line, 'r--', linewidth=2, 
                    label=f'Trend: {trend_stats["slope_cm_per_year"]:.3f} cm/year')
    axes[0, 0].set_title('Pakistan Groundwater Anomaly (2002-2017)', fontweight='bold')
    axes[0, 0].set_ylabel('Groundwater Anomaly (cm)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Annual averages
    annual_stats = grace_df.groupby('year')['groundwater_cm'].mean()
    axes[0, 1].bar(annual_stats.index, annual_stats.values, color='skyblue', alpha=0.8)
    axes[0, 1].set_title('Annual Average Groundwater Anomaly', fontweight='bold')
    axes[0, 1].set_ylabel('Average Anomaly (cm)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Seasonal patterns
    axes[1, 0].plot(seasonal_stats.index, seasonal_stats['mean'], 'go-', linewidth=2, markersize=6)
    axes[1, 0].fill_between(seasonal_stats.index, 
                           seasonal_stats['mean'] - seasonal_stats['std'],
                           seasonal_stats['mean'] + seasonal_stats['std'], 
                           alpha=0.3, color='green')
    axes[1, 0].set_title('Seasonal Groundwater Patterns', fontweight='bold')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('Groundwater Anomaly (cm)')
    axes[1, 0].set_xticks(range(1, 13))
    
    # Distribution
    axes[1, 1].hist(grace_df['groundwater_cm'], bins=25, color='lightcoral', alpha=0.7, edgecolor='black')
    axes[1, 1].axvline(stats_summary['mean_groundwater_cm'], color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {stats_summary["mean_groundwater_cm"]:.2f} cm')
    axes[1, 1].set_title('Distribution of Groundwater Anomalies', fontweight='bold')
    axes[1, 1].set_xlabel('Groundwater Anomaly (cm)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig('data/outputs/grace_historical_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save results
    results = {
        'period': '2002-2017',
        'data_source': 'GRACE',
        'statistics': stats_summary,
        'trend_analysis': trend_stats,
        'seasonal_patterns': seasonal_stats.to_dict(),
        'key_findings': [
            f"Average groundwater depletion: {stats_summary['mean_groundwater_cm']:.2f} cm below normal",
            f"Long-term trend: {trend_stats['slope_cm_per_year']:.3f} cm/year change",
            f"Total change over 15 years: {stats_summary['total_change']:.2f} cm",
            f"Trend statistical significance: {trend_stats['trend_significance']}"
        ]
    }
    
    with open('data/processed/grace_historical_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return grace_df, results

# Execute historical analysis
grace_data, grace_results = analyze_grace_historical()
print("✅ Historical analysis completed!")