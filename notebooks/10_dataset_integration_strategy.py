# notebooks/22_dataset_integration_strategy.py
import json
import pandas as pd
import matplotlib.pyplot as plt

print("🔗 Dataset Integration & Harmonization Strategy")

def analyze_temporal_coverage():
    """Analyze temporal coverage and overlaps"""
    
    # Expected coverage based on our exports
    datasets_coverage = {
        'GRACE Historical': {
            'start': '2002-03-31',
            'end': '2017-05-22', 
            'source': 'GRACE satellites',
            'variable': 'Groundwater anomaly (cm)',
            'status': 'deprecated_but_usable'
        },
        'GLDAS Recent': {
            'start': '2018-01-01',
            'end': '2024-12-31',
            'source': 'GLDAS V021',
            'variable': 'Deep soil moisture (m³/m³)',
            'status': 'current_preferred'
        }
    }
    
    # Create timeline visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    
    y_pos = 0
    colors = ['#ff6b6b', '#4ecdc4']
    
    for i, (name, info) in enumerate(datasets_coverage.items()):
        start = pd.to_datetime(info['start'])
        end = pd.to_datetime(info['end'])
        
        # Plot timeline bar
        ax.barh(y_pos, (end - start).days, left=start, height=0.3, 
                color=colors[i], alpha=0.7, label=name)
        
        # Add dataset info
        ax.text(start + (end - start)/2, y_pos + 0.4, 
                f"{name}\n{info['variable']}", 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        y_pos += 1
    
    # Mark transition period
    transition_start = pd.to_datetime('2017-06-01')
    transition_end = pd.to_datetime('2017-12-31')
    ax.axvspan(transition_start, transition_end, alpha=0.3, color='orange', 
               label='Data Gap Period')
    
    ax.set_ylim(-0.5, len(datasets_coverage))
    ax.set_xlabel('Year')
    ax.set_title('WaterTrace Dataset Timeline Coverage', fontsize=16, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/outputs/dataset_timeline_coverage.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return datasets_coverage

def create_integration_plan():
    """Create detailed integration plan"""
    
    integration_plan = {
        'strategy': 'Sequential Analysis with Overlap Validation',
        'phases': {
            'phase_1_historical': {
                'period': '2002-2017',
                'primary_dataset': 'GRACE',
                'analysis_type': 'Historical trend analysis',
                'key_insights': [
                    'Long-term groundwater depletion trends',
                    'Seasonal patterns and cycles', 
                    'Impact of major droughts/floods',
                    'Baseline groundwater status'
                ]
            },
            'phase_2_recent': {
                'period': '2018-2024',
                'primary_dataset': 'GLDAS',
                'analysis_type': 'Current status assessment',
                'key_insights': [
                    'Recent groundwater trends',
                    'Climate change impacts',
                    'Current water stress levels',
                    'Post-2018 policy impacts'
                ]
            },
            'phase_3_integrated': {
                'period': '2002-2024',
                'methodology': 'Combined trend analysis',
                'challenges': [
                    'Different measurement units (cm vs m³/m³)',
                    'Different spatial resolutions',
                    'Data gap in 2017-2018'
                ],
                'solutions': [
                    'Normalize both datasets to z-scores',
                    'Focus on relative trends rather than absolute values',
                    'Statistical correlation during overlap period'
                ]
            }
        }
    }
    
    return integration_plan

# Execute analysis
coverage = analyze_temporal_coverage()
plan = create_integration_plan()

print("📋 Integration Strategy Summary:")
print("1. Historical Analysis (2002-2017): GRACE data")
print("2. Recent Analysis (2018-2024): GLDAS data") 
print("3. Combined Trend Analysis: Normalized comparison")

# Save integration plan
with open('data/processed/integration_plan.json', 'w') as f:
    json.dump(plan, f, indent=2)

print("✅ Integration strategy completed!")