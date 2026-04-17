import datetime
import pandas as pd
import random

# Generate a task instruction string for study plan
def generate_instruction(row, is_final=False, is_review=False):

    name = row["assignment_name"]
    subject = row.get("course_name", "")

    # Final submission
    if is_final:
        return f"Submit {name} ({subject})"

    # Final review before submission
    if is_review:
        return f"Final review for {name} ({subject})"

    # Test preparation
    if "test" in name.lower():
        return random.choice([
            f"Revise key concepts for {name} ({subject})",
            f"Practice questions for {name} ({subject})",
            f"Do mock test for {name} ({subject})"
        ])

    # Normal assignment work
    return random.choice([
        f"Work on {name} ({subject})",
    ])


# Smart scheduler that assigns tasks over days
def smart_schedule(df, events, risk_df):

    df = df.sort_values(
        by=["priority", "days_until_due"],  # Sort: priority first, then due soon
        ascending=[False, True]
    ).copy()

    today = datetime.date.today()

    weekday_slots = [18, 20]        # Weekday time slots (6pm, 8pm)
    weekend_slots = [10, 14, 18]    # Weekend slots (10am, 2pm, 6pm)

    daily_load = {}
    schedule = []

    for _, row in df.iterrows():

        days_left = int(row["days_until_due"])
        due_date = row["due_date"].date()

        is_risky = row["assignment_name"] in risk_df["assignment_name"].values

        # Decide when to start working (start date)
        if days_left <= 3:
            start_offset = 0
        elif days_left <= 7:
            start_offset = 1
        else:
            start_offset = max(days_left - 5, 0)

        start_day = today + datetime.timedelta(days=start_offset)

        name_lower = row["assignment_name"].lower()

        # Determine number of sessions needed
        if is_risky:
            sessions = 4
        elif "group" in name_lower:
            sessions = 3
        elif "test" in name_lower:
            sessions = 2
        else:
            sessions = 2

        count = 0    # Track how many sessions assigned

        for i in range(days_left + 1):

            day = start_day + datetime.timedelta(days=i)

            if day >= due_date:
                break

            if day.weekday() < 5:
                slots = weekday_slots
                max_tasks = 2
            else:
                slots = weekend_slots
                max_tasks = 3

            if day not in daily_load:
                daily_load[day] = []

            for hour in slots:

                if len(daily_load[day]) >= max_tasks:
                    break

                schedule.append({
                    "Task_Instruction": generate_instruction(row),
                    "Scheduled_Date": str(day),
                    "Scheduled_Time": f"{hour}:00",
                    "due_date": due_date
                })

                daily_load[day].append(hour)
                count += 1

                if count >= sessions:
                    break

            if count >= sessions:
                break

        # Add final review 1 day before due
        review_day = due_date - datetime.timedelta(days=1)

        schedule.append({
            "Task_Instruction": generate_instruction(row, is_review=True),
            "Scheduled_Date": str(review_day),
            "Scheduled_Time": "20:00",
            "due_date": due_date
        })

        # Add final submission
        schedule.append({
            "Task_Instruction": generate_instruction(row, is_final=True),
            "Scheduled_Date": str(due_date),
            "Scheduled_Time": "21:00",
            "due_date": due_date
        })

    return pd.DataFrame(schedule)