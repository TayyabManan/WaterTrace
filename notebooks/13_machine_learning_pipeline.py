# notebooks/25_machine_learning_pipeline.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

def create_ml_features():
    """Create features for machine learning from both datasets"""
    
    # Load both datasets
    grace_df = pd.read_csv('data/csv/pakistan_grace_2002_2017_complete.csv')
    gldas_df = pd.read_csv('data/csv/pakistan_gldas_2018_2024_monthly.csv')
    
    # Prepare GRACE features (historical training data)
    grace_df['date'] = pd.to_datetime(grace_df['date'])
    grace_df = grace_df.sort_values('date')
    
    # Create time-based features
    grace_df['year'] = grace_df['date'].dt.year
    grace_df['month'] = grace_df['date'].dt.month
    grace_df['season'] = grace_df['month'].map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring', 
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
    })
    
    # Create lag features
    for lag in [1, 2, 3, 6, 12]:
        grace_df[f'gw_lag_{lag}'] = grace_df['groundwater_cm'].shift(lag)
    
    # Create rolling averages
    for window in [3, 6, 12]:
        grace_df[f'gw_ma_{window}'] = grace_df['groundwater_cm'].rolling(window=window).mean()
    
    # Create trend and seasonal decomposition features
    grace_df['linear_trend'] = range(len(grace_df))
    grace_df['seasonal_avg'] = grace_df.groupby('month')['groundwater_cm'].transform('mean')
    grace_df['seasonal_anomaly'] = grace_df['groundwater_cm'] - grace_df['seasonal_avg']
    
    # Drop rows with NaN values (due to lag features)
    grace_ml = grace_df.dropna()
    
    return grace_ml

def train_prediction_models():
    """Train multiple ML models for groundwater prediction"""
    
    # Prepare data
    ml_data = create_ml_features()
    
    # Define features and target
    feature_cols = [col for col in ml_data.columns if col not in 
                   ['date', 'groundwater_cm', 'season', 'data_source', 'system_time', 'variable', '.geo', 'system:index']]
    
    X = ml_data[feature_cols]
    y = ml_data['groundwater_cm']
    
    # Time series split (important for temporal data)
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Models to test
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    # Train and evaluate models
    results = {}
    
    for name, model in models.items():
        print(f"🤖 Training {name}...")
        
        # Cross-validation scores
        cv_scores = []
        feature_importance_sum = np.zeros(len(feature_cols))
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Train model
            if name == 'Linear Regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_val_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                
                # Accumulate feature importance
                if hasattr(model, 'feature_importances_'):
                    feature_importance_sum += model.feature_importances_
            
            # Calculate metrics
            cv_score = r2_score(y_val, y_pred)
            cv_scores.append(cv_score)
        
        # Final model training on full dataset
        scaler = StandardScaler()
        if name == 'Linear Regression':
            X_scaled = scaler.fit_transform(X)
            model.fit(X_scaled, y)
            final_pred = model.predict(X_scaled)
        else:
            model.fit(X, y)
            final_pred = model.predict(X)
        
        # Calculate final metrics
        rmse = np.sqrt(mean_squared_error(y, final_pred))
        mae = mean_absolute_error(y, final_pred)
        r2 = r2_score(y, final_pred)
        
        results[name] = {
            'model': model,
            'scaler': scaler if name == 'Linear Regression' else None,
            'cv_scores': cv_scores,
            'cv_mean': np.mean(cv_scores),
            'cv_std': np.std(cv_scores),
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'feature_importance': feature_importance_sum / 5 if hasattr(model, 'feature_importances_') else None
        }
        
        print(f"   ✅ R² Score: {r2:.3f}")
        print(f"   ✅ RMSE: {rmse:.3f}")
        print(f"   ✅ CV Score: {np.mean(cv_scores):.3f} ± {np.std(cv_scores):.3f}")
    
    # Select best model
    best_model_name = max(results.keys(), key=lambda x: results[x]['r2'])
    best_model = results[best_model_name]
    
    print(f"\n🏆 Best Model: {best_model_name}")
    
    # Save best model
    joblib.dump(best_model['model'], 'data/processed/best_groundwater_model.pkl')
    if best_model['scaler']:
        joblib.dump(best_model['scaler'], 'data/processed/feature_scaler.pkl')
    
    # Save feature importance
    if best_model['feature_importance'] is not None:
        feature_importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': best_model['feature_importance']
        }).sort_values('importance', ascending=False)
        
        feature_importance_df.to_csv('data/processed/feature_importance.csv', index=False)
        
        print(f"\n📊 Top 5 Important Features:")
        for _, row in feature_importance_df.head().iterrows():
            print(f"   {row['feature']}: {row['importance']:.3f}")
    
    return results, feature_cols

# Execute ML pipeline
ml_results, features = train_prediction_models()
print("✅ Machine learning pipeline completed!")