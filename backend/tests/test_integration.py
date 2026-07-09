import pytest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.project import Project
from backend.app.models.employee import Employee
from backend.app.models.seat import Seat

def test_employee_lifecycle(client: TestClient):
    # 1. Create Project first
    proj_resp = client.post("/api/projects/", json={
        "name": "Project Apollo",
        "description": "Space mission project"
    })
    assert proj_resp.status_code == 201
    proj_id = proj_resp.json()["id"]

    # 2. Create Employee
    emp_resp = client.post("/api/employees/", json={
        "employee_code": "EMP1001",
        "name": "John Doe",
        "email": "johndoe@ethara.ai",
        "department": "Engineering",
        "role": "Software Engineer",
        "joining_date": "2026-07-09",
        "status": "Active",
        "project_id": proj_id
      })
    assert emp_resp.status_code == 201
    emp_id = emp_resp.json()["id"]
    assert emp_resp.json()["employee_code"] == "EMP1001"

    # 3. Retrieve Employee
    get_resp = client.get(f"/api/employees/{emp_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "John Doe"

    # 4. Update Employee
    update_resp = client.put(f"/api/employees/{emp_id}", json={
        "name": "John Smith",
        "email": "johnsmith@ethara.ai"
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "John Smith"
    assert update_resp.json()["email"] == "johnsmith@ethara.ai"

    # 5. Deactivate Employee
    deac_resp = client.delete(f"/api/employees/{emp_id}")
    assert deac_resp.status_code == 200
    assert deac_resp.json()["status"] == "Deactivated"


def test_proximity_seat_allocation_logic(client: TestClient, db_session: Session):
    # 1. Create Project
    proj_resp = client.post("/api/projects/", json={"name": "Project Orion"})
    proj_id = proj_resp.json()["id"]

    # 2. Create seats in different configurations
    # Seat 1: Floor 2, Zone B, Bay 4 (Team seat)
    # Seat 2: Floor 2, Zone B, Bay 4 (Team seat - close)
    # Seat 3: Floor 2, Zone B, Bay 5 (Same zone - medium close)
    # Seat 4: Floor 3, Zone A, Bay 1 (Different floor - far)
    seats_data = [
        {"floor": 2, "zone": "Zone B", "bay": 4, "seat_number": "B4-01", "status": "Available"},
        {"floor": 2, "zone": "Zone B", "bay": 4, "seat_number": "B4-02", "status": "Available"},
        {"floor": 2, "zone": "Zone B", "bay": 5, "seat_number": "B5-01", "status": "Available"},
        {"floor": 3, "zone": "Zone A", "bay": 1, "seat_number": "A1-01", "status": "Available"},
    ]
    for s in seats_data:
        client.post("/api/seats/", json=s)

    # Fetch seat details from DB to map IDs
    db_seats = db_session.query(Seat).all()
    seat_map = {s.seat_number: s.id for s in db_seats}

    # 3. Create Employee 1 and allocate Seat 1 (B4-01)
    emp1_resp = client.post("/api/employees/", json={
        "employee_code": "EMP2001",
        "name": "Alice Cooper",
        "email": "alice@ethara.ai",
        "joining_date": "2026-07-09",
        "project_id": proj_id
    })
    emp1_id = emp1_resp.json()["id"]
    
    # Allocate seat 1 to employee 1
    alloc_resp = client.post("/api/seats/allocate", json={
        "employee_id": emp1_id,
        "seat_id": seat_map["B4-01"]
    })
    assert alloc_resp.status_code == 200

    # 4. Create Employee 2 (same project)
    emp2_resp = client.post("/api/employees/", json={
        "employee_code": "EMP2002",
        "name": "Bob Marley",
        "email": "bob@ethara.ai",
        "joining_date": "2026-07-09",
        "project_id": proj_id
    })
    emp2_id = emp2_resp.json()["id"]

    # 5. Fetch suggested seats for Employee 2
    suggest_resp = client.get(f"/api/seats/suggest/{emp2_id}?limit=2")
    assert suggest_resp.status_code == 200
    suggestions = suggest_resp.json()
    
    # The first suggestion must be B4-02 (same floor, zone, bay as teammate Alice)
    assert len(suggestions) == 2
    assert suggestions[0]["seat_number"] == "B4-02"
    # The second suggestion should be B5-01 (same floor, zone, but adjacent bay)
    assert suggestions[1]["seat_number"] == "B5-01"


def test_concurrent_allocation_safety(client: TestClient, db_session: Session):
    # Setup project
    proj_resp = client.post("/api/projects/", json={"name": "Project Gemini"})
    proj_id = proj_resp.json()["id"]

    # Create one available seat
    seat_resp = client.post("/api/seats/", json={
        "floor": 1,
        "zone": "Zone A",
        "bay": 1,
        "seat_number": "A1-10",
        "status": "Available"
    })
    seat_id = seat_resp.json()["id"]

    # Create two employees
    emp1_resp = client.post("/api/employees/", json={
        "employee_code": "EMP3001",
        "name": "Dave Mustaine",
        "email": "dave@ethara.ai",
        "joining_date": "2026-07-09",
        "project_id": proj_id
    })
    emp1_id = emp1_resp.json()["id"]

    emp2_resp = client.post("/api/employees/", json={
        "employee_code": "EMP3002",
        "name": "James Hetfield",
        "email": "james@ethara.ai",
        "joining_date": "2026-07-09",
        "project_id": proj_id
    })
    emp2_id = emp2_resp.json()["id"]

    # Simulate concurrent allocation of the same seat to two different users
    def send_allocation(employee_id: int):
        return client.post("/api/seats/allocate", json={
            "employee_id": employee_id,
            "seat_id": seat_id
        })

    # Execute concurrent requests using a thread pool
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(send_allocation, emp1_id),
            executor.submit(send_allocation, emp2_id)
        ]
        results = [f.result() for f in futures]

    # One request must succeed, and the other must fail with a 400 Bad Request
    status_codes = [r.status_code for r in results]
    assert 200 in status_codes
    assert 400 in status_codes
    
    # Verify that the seat is now occupied in the database
    seat_db = db_session.query(Seat).filter(Seat.id == seat_id).first()
    assert seat_db.status == "Occupied"
