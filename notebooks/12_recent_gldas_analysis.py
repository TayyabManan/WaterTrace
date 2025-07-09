# notebooks/24_recent_gldas_analysis_CLEAN.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

def analyze_gldas_recent():
    """Comprehensive analysis of GLDAS recent data with clean visualizations"""
    
    # Load GLDAS data
    file_path = 'data/csv/pakistan_gldas_2018_2024_monthly.csv'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None, None
    
    gldas_df = pd.read_csv(file_path)
    gldas_df['date'] = pd.to_datetime(gldas_df['date'])
    gldas_df = gldas_df.sort_values('date')
    
    print(f"📅 Recent Period: {gldas_df['date'].min()} to {gldas_df['date'].max()}")
    print(f"📊 Data Points: {len(gldas_df)}")
    print(f"📋 All Columns: {list(gldas_df.columns)}")
    
    # Identify water-related columns
    water_columns = [col for col in gldas_df.columns if any(keyword in col.lower() 
                    for keyword in ['soil', 'moisture', 'water', 'rain', 'evap', 'snow', 'groundwater'])]
    
    print(f"💧 Water Variables: {water_columns}")
    
    # Find the actual groundwater column
    possible_gw_columns = [
        'groundwater_cm',
        'groundwater_ccm', 
        'deep_soil_moisture',
        'SoilMoi100_200cm_inst',
        'lwe_thickness',
        'value'
    ]
    
    primary_var = None
    for col in possible_gw_columns:
        if col in gldas_df.columns:
            primary_var = col
            break
    
    if primary_var is None and water_columns:
        primary_var = water_columns[0]
    
    if primary_var is None:
        numeric_cols = gldas_df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col not in ['year', 'month', 'system:index']]
        if numeric_cols:
            primary_var = numeric_cols[0]
    
    if primary_var is None:
        print("❌ No suitable groundwater column found!")
        return None, None
    
    print(f"✅ Using primary variable: {primary_var}")
    
    # Check for missing values
    if gldas_df[primary_var].isnull().any():
        print(f"⚠️ Found {gldas_df[primary_var].isnull().sum()} missing values in {primary_var}")
        gldas_df = gldas_df.dropna(subset=[primary_var])
        print(f"📊 Data points after removing missing values: {len(gldas_df)}")
    
    # Analyze primary groundwater proxy
    gw_proxy = gldas_df[primary_var]
    
    recent_stats = {
        'mean_value': gw_proxy.mean(),
        'std_value': gw_proxy.std(),
        'min_value': gw_proxy.min(),
        'max_value': gw_proxy.max(),
        'recent_change': gw_proxy.iloc[-1] - gw_proxy.iloc[0] if len(gw_proxy) > 1 else 0,
        'column_used': primary_var
    }
    
    print(f"\n📊 Recent Statistics (2018-2024):")
    print(f"   Mean Value: {recent_stats['mean_value']:.4f}")
    print(f"   Standard Deviation: {recent_stats['std_value']:.4f}")
    print(f"   Range: {recent_stats['min_value']:.4f} to {recent_stats['max_value']:.4f}")
    print(f"   Total Change: {recent_stats['recent_change']:.4f} over period")
    
    # Determine layout based on available data
    has_multiple_vars = len(water_columns) > 1
    has_year_data = 'year' in gldas_df.columns
    has_month_data = 'month' in gldas_df.columns
    
    # Create appropriate subplot layout
    if has_year_data and has_month_data:
        # We have enough data for 3 meaningful plots
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        plot_count = 3
    elif has_year_data or has_month_data:
        # We have data for 2 meaningful plots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        plot_count = 2
    else:
        # Only time series plot
        fig, axes = plt.subplots(1, 1, figsize=(12, 6))
        axes = [axes]  # Make it a list for consistent indexing
        plot_count = 1
    
    print(f"📊 Creating {plot_count} meaningful visualizations...")
    
    # Plot 1: Primary variable time series (always shown)
    axes[0].plot(gldas_df['date'], gw_proxy, 'g-', linewidth=2, marker='o', markersize=4)
    axes[0].set_title(f'Pakistan {primary_var} Time Series (2018-2024)', fontweight='bold', fontsize=14)
    axes[0].set_ylabel(f'{primary_var}', fontsize=12)
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)
    
    # Add trend line
    if len(gw_proxy) > 1:
        z = np.polyfit(range(len(gw_proxy)), gw_proxy, 1)
        p = np.poly1d(z)
        axes[0].plot(gldas_df['date'], p(range(len(gw_proxy))), 'r--', 
                    alpha=0.8, linewidth=2, label=f'Trend: {z[0]:.6f}/month')
        axes[0].legend()
    
    # Plot 2: Annual trends (if year data available)
    if plot_count >= 2 and has_year_data:
        annual_means = gldas_df.groupby('year')[primary_var].mean()
        bars = axes[1].bar(annual_means.index, annual_means.values, color='lightgreen', alpha=0.8, edgecolor='darkgreen')
        axes[1].set_title(f'Annual Average {primary_var}', fontweight='bold', fontsize=14)
        axes[1].set_ylabel(f'Average {primary_var}', fontsize=12)
        axes[1].set_xlabel('Year', fontsize=12)
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=10)
    
    elif plot_count >= 2 and has_month_data:
        # If no year data, show monthly patterns
        monthly_means = gldas_df.groupby('month')[primary_var].mean()
        axes[1].plot(monthly_means.index, monthly_means.values, 'go-', linewidth=3, markersize=8)
        axes[1].set_title(f'Monthly Average {primary_var}', fontweight='bold', fontsize=14)
        axes[1].set_xlabel('Month', fontsize=12)
        axes[1].set_ylabel(f'Average {primary_var}', fontsize=12)
        axes[1].set_xticks(range(1, 13))
        axes[1].grid(True, alpha=0.3)
        
        # Add month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        axes[1].set_xticklabels(month_labels, rotation=45)
    
    # Plot 3: Distribution histogram (if we have 3 plots)
    if plot_count >= 3:
        n, bins, patches = axes[2].hist(gw_proxy, bins=15, color='lightcoral', alpha=0.7, edgecolor='black')
        axes[2].axvline(recent_stats['mean_value'], color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {recent_stats["mean_value"]:.4f}')
        axes[2].axvline(recent_stats['mean_value'] + recent_stats['std_value'], color='orange', linestyle=':', 
                       linewidth=2, label=f'+1 SD: {recent_stats["mean_value"] + recent_stats["std_value"]:.4f}')
        axes[2].axvline(recent_stats['mean_value'] - recent_stats['std_value'], color='orange', linestyle=':', 
                       linewidth=2, label=f'-1 SD: {recent_stats["mean_value"] - recent_stats["std_value"]:.4f}')
        axes[2].set_title(f'Distribution of {primary_var}', fontweight='bold', fontsize=14)
        axes[2].set_xlabel(f'{primary_var}', fontsize=12)
        axes[2].set_ylabel('Frequency', fontsize=12)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Create output directory and save
    os.makedirs('data/outputs', exist_ok=True)
    plt.savefig('data/outputs/gldas_recent_analysis_clean.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create additional detailed statistics plot
    fig2, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Create a comprehensive statistics summary plot
    stats_text = f"""
Pakistan GLDAS Water Analysis Summary (2018-2024)

Dataset Information:
- Variable: {primary_var}
- Time Period: {gldas_df['date'].min().strftime('%Y-%m-%d')} to {gldas_df['date'].max().strftime('%Y-%m-%d')}
- Total Data Points: {len(gldas_df)}

Statistical Summary:
- Mean: {recent_stats['mean_value']:.6f}
- Standard Deviation: {recent_stats['std_value']:.6f}
- Minimum: {recent_stats['min_value']:.6f}
- Maximum: {recent_stats['max_value']:.6f}
- Range: {recent_stats['max_value'] - recent_stats['min_value']:.6f}
- Total Change: {recent_stats['recent_change']:.6f}

Trend Analysis:
- Overall Direction: {'Increasing' if recent_stats['recent_change'] > 0 else 'Decreasing' if recent_stats['recent_change'] < 0 else 'Stable'}
- Rate of Change: {recent_stats['recent_change'] / len(gldas_df):.8f} per month
- Variability: {'High' if recent_stats['std_value'] > abs(recent_stats['mean_value']) * 0.1 else 'Low'}
    """
    
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Pakistan Groundwater Analysis - Statistical Summary', fontweight='bold', fontsize=16)
    
    plt.tight_layout()
    plt.savefig('data/outputs/gldas_statistical_summary.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save results
    results = {
        'period': '2018-2024',
        'data_source': 'GLDAS',
        'primary_variable': primary_var,
        'statistics': recent_stats,
        'water_variables_found': water_columns,
        'total_data_points': len(gldas_df),
        'visualizations_created': plot_count,
        'key_findings': [
            f"Primary variable used: {primary_var}",
            f"Mean value: {recent_stats['mean_value']:.6f}",
            f"Total change over period: {recent_stats['recent_change']:.6f}",
            f"Trend direction: {'Increasing' if recent_stats['recent_change'] > 0 else 'Decreasing' if recent_stats['recent_change'] < 0 else 'Stable'}",
            f"Data coverage: {gldas_df['date'].min()} to {gldas_df['date'].max()}"
        ]
    }
    
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/gldas_recent_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return gldas_df, results

# Execute recent analysis
try:
    print("📊 Recent GLDAS Analysis (2018-2024) - Clean Version")
    gldas_data, gldas_results = analyze_gldas_recent()
    if gldas_data is not None:
        print("✅ Recent analysis completed successfully!")
        print(f"📋 Results saved to: data/processed/gldas_recent_analysis.json")
        print(f"📊 Main visualization: data/outputs/gldas_recent_analysis_clean.png")
        print(f"📈 Statistical summary: data/outputs/gldas_statistical_summary.png")
    else:
        print("❌ Analysis failed - check your data file")
except Exception as e:
    print(f"❌ Error during analysis: {e}")
    import traceback
    traceback.print_exc()