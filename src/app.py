"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from pathlib import Path
from typing import List

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


class AccessReconciliationRequest(BaseModel):
    system_access_list: List[str]
    database_access_list: List[str]


class AccessReconciliationResult(BaseModel):
    grant_system_access: List[str]
    revoke_system_access: List[str]
    matched_access: List[str]


class AccessReconciliationAgent:
    @staticmethod
    def reconcile(system_access_list: List[str], database_access_list: List[str]) -> AccessReconciliationResult:
        system_access = set(system_access_list)
        database_access = set(database_access_list)

        return AccessReconciliationResult(
            grant_system_access=sorted(database_access - system_access),
            revoke_system_access=sorted(system_access - database_access),
            matched_access=sorted(system_access & database_access),
        )


access_reconciliation_agent = AccessReconciliationAgent()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/access/reconcile", response_model=AccessReconciliationResult)
def reconcile_access(request: AccessReconciliationRequest):
    return access_reconciliation_agent.reconcile(
        request.system_access_list, request.database_access_list
    )


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
