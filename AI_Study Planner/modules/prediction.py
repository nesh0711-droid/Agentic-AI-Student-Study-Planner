import joblib      # Import joblib to load machine learning model

# Load pre-trained XGBoost model for priority prediction
model = joblib.load("models/xgboost_model.pkl")  

def predict_priorities(df):
    # Select features needed for the model
    features = df[[
        'days_until_due',
        'points_per_hour',
        'estimated_hours',
        'points',
        'difficulty_encoded',
        'course_encoded'
    ]]

    # Predict assignment priority using XG Boost model
    df['priority'] = model.predict(features)

    return df   # Return DataFrame with 'priority' column