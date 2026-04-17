import pandas as pd          # Import pandas for data manipulation
import random                # Import random to generate random instructions (will be used later)

# Convert raw API assignment data into a clean DataFrame
def assignments_to_df(api_data):
    rows = []                               # Initialize list to hold each assignment row
    now = pd.Timestamp.now(tz="UTC")        # Current timestamp in UTC
    seen = set()                            # Keep track of assignment we already added (to avoid duplicates)

    for item in api_data:                   
        name = item.get("name", "").lower()             # Get assignment name,convert to lowercase
        course = item.get("course_name", "Unknown")     # Get courses name, deafult "Unknown"

        # Remove clutter or non-important entries
        if any(x in name for x in ["turnitin", "check", "submission link"]): 
            continue


        # Detect type of assignment
        if "group" in name:
            base = "Group Assignment"
        elif "individual" in name:
            base = "Individual Assignment"
        elif "lab" in name:
            base = "Lab Test"
        elif "test" in name or "quiz" in name:
            base = "Test"
        else:
            base = "Assignment"

        clean_name = f"{base} ({course})"   # Get standardized assignment name

        if clean_name in seen:              # Skip if assignment already added
            continue

        seen.add(clean_name)

        due = item.get("due_at")            # Get due date
        if due is None:                     # Skip if no due date
            continue

        due_date = pd.to_datetime(due, utc=True)     # Convert to pandas datetime

        if due_date < now:       # Skip past assignments
            continue

        # Add assignment info to rows list
        rows.append({
            "assignment_name": clean_name,
            "due_date": due_date,
            "points": item.get("points_possible") or 10,    # Default 10 points
            "estimated_hours": 3,                           # Default 3 hours per assignment
            "difficulty_encoded": 1,                        # Default difficulty
            "course_encoded": 1,                            # Default encoding
            "course_name": course
        })

    return pd.DataFrame(rows)   # Convert list of dictionaries to pandas DataFrame

# Preprocess DataFrame to calculate additional metrics for prioritization
def preprocess_new_assignments(df):

    reference = pd.Timestamp.now(tz="UTC")

    #Days until due date
    df['days_until_due'] = (df['due_date'] - reference).dt.total_seconds() / (3600 * 24)
    df['days_until_due'] = df['days_until_due'].astype(int)

    # Urgency score = higher if due soon or more points/effort
    df['urgency_score'] = (
        (1 / df['days_until_due']) * 
        df['estimated_hours'] * 
        (df['points'] / 10)
    )

    # Points per hour = efficiency metric
    df['points_per_hour'] = (
        df['points'] / df['estimated_hours']
    )

     # Adjust priority based on difficulty
    df['adjusted_priority'] = (
        df['urgency_score'] * (1 + df['difficulty_encoded'])
    )

    return df  # Return preprocessed DataFrame


