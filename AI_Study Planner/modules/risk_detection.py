def detect_risk(df):

    df = df.copy()

    # Calculate risk score (urgent and important tasks are riskier)
    df['risk_score'] = (
        (1 / df['days_until_due'].clip(lower=0.5)) *
        df['estimated_hours'] *
        (df['points'] / 10)
    )

    # Sort descending by risk
    df = df.sort_values(by="risk_score", ascending=False)

    # Define high risk: priority 2 (from model) & due soon
    high_risk = df[
        (df['priority'] == 2) &
        (df['days_until_due'] <= 7)
    ]

    # If no high risk, pick top 2 most risky tasks
    if high_risk.empty:
        return df.head(2)

    return high_risk