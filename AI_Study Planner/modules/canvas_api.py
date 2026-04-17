import requests                                          # For making HTTP requests to Canvas API
from config import CANVAS_API_URL, CANVAS_API_TOKEN      # API URL and token for authentication
from datetime import datetime                            # For date/time handling

# Authorization headers for Canvas API
headers = {
    "Authorization": f"Bearer {CANVAS_API_TOKEN}"   # Include token for secure API access
}

# ---------------- GET COURSES ----------------
def get_courses():

    url = f"{CANVAS_API_URL}courses?enrollment_state=active&per_page=100"   # API endpoint to get courses

    response = requests.get(url, headers=headers)   # Send GET request with auth headers

    if response.status_code != 200: # Check if request failed
        print("Error:", response.text)
        return []    # Return empty list if error

    return response.json()  # Return courses as JSON list

# ---------------- FETCH ASSIGNMENTS FOR A COURSE ----------------
def fetch_assignments(course_id):

    url = f"{CANVAS_API_URL}courses/{course_id}/assignments"    # Endpoint for course assignments

    response = requests.get(url, headers=headers)    # GET request

    if response.status_code == 200:
        return response.json()  # Return assignments as JSON

    else:
        print("Error fetching assignments")
        return []   # Return empty list on error