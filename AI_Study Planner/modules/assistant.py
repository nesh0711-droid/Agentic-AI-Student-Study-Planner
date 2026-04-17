import pandas as pd
from datetime import timedelta
from modules.chatbot import chatbot_response

# ---------------- INTENT DETECTION ----------------
def detect_intent(user_input):

    text = user_input.lower()

    if "due this week" in text:
        return "due_this_week"

    elif "study schedule" in text or "plan my study" in text:
        return "study_plan"

    elif "study today" in text:
        return "study_today"

    else:
        return "chat"


# ---------------- ASSIGNMENTS DUE THIS WEEK ----------------
def get_due_this_week(df):

    today = pd.Timestamp.today(tz="UTC")
    end_week = today + timedelta(days=7)

    upcoming = df[
        (df['due_date'] >= today) &
        (df['due_date'] <= end_week)
    ]

    if upcoming.empty:
        return "No assignments due this week."

    result = "Assignments due this week:\n"

    for _, row in upcoming.iterrows():
        result += f"- {row['assignment_name']} (Due: {row['due_date'].date()})\n"

    return result


# ---------------- STUDY SCHEDULE ----------------
def get_study_schedule(schedule):

    upcoming = schedule.head(5)

    result = "Your upcoming study schedule:\n"

    for _, row in upcoming.iterrows():

        result += (
            f"- {row['Task_Instruction']} "
            f"on {row['Scheduled_Date']} at {row['Scheduled_Time']}\n"
        )

    return result


# ---------------- STUDY TODAY ----------------
def study_today(schedule):

    today = pd.Timestamp.today().date()

    today_tasks = schedule[
        schedule["Scheduled_Date"] == str(today)
    ]

    if today_tasks.empty:
        return "No study tasks scheduled for today."

    result = "Today's study tasks:\n"

    for _, row in today_tasks.iterrows():

        result += (
            f"- {row['Task_Instruction']} "
            f"at {row['Scheduled_Time']}\n"
        )

    return result


# ---------------- MAIN ASSISTANT ----------------
def smart_assistant(user_input, df, schedule):

    intent = detect_intent(user_input)

    if intent == "due_this_week":
        return get_due_this_week(df)

    elif intent == "study_plan":
        return get_study_schedule(schedule)

    elif intent == "study_today":
        return study_today(schedule)

    else:
        return chatbot_response(user_input)