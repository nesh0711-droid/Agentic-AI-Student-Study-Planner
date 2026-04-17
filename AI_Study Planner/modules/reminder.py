import pandas as pd
from datetime import date, timedelta

def generate_reminders(schedule):

    today = date.today()

    reminders = []

    for _, row in schedule.iterrows():

        due = row["due_date"]

        if "Submit" in row["Task_Instruction"]:

            # Reminder 4 days before
            if (due - today).days == 4:
                reminders.append({
                    "Reminder": f"Assignment due is coming: {row['Task_Instruction']}",
                    "Due_Date": due
                })

            # Reminder on due date
            if due == today:
                reminders.append({
                    "Reminder": f"Due Today: {row['Task_Instruction']}",
                    "Due_Date": due
                })

    return pd.DataFrame(reminders)