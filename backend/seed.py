import os
import sys
from datetime import datetime, date, timedelta
import random
from sqlalchemy import select, and_

# Add parent directory to path to enable local app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.database import Base, engine, SessionLocal
    from app.models.project import Project
    from app.models.employee import Employee
    from app.models.seat import Seat
    from app.models.allocation import SeatAllocation
except ModuleNotFoundError:
    from backend.app.database import Base, engine, SessionLocal
    from backend.app.models.project import Project
    from backend.app.models.employee import Employee
    from backend.app.models.seat import Seat
    from backend.app.models.allocation import SeatAllocation

def seed_database():
    print("Initializing local SQLite database and tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Create Projects (10 projects)
        print("Seeding projects...")
        project_names = [
            "Project Indigo", "Project Indreed", "Project Mydreed", "Project Preed",
            "Project Serfy", "Project Oreed", "Project bedegreed", "Project Opreed",
            "Project Serry", "Project Kaary", "Project Mered", "Project Talos"
        ]
        projects = []
        for name in project_names:
            proj = Project(
                name=name,
                description=f"Workspace operation mapping for {name}",
                manager_name=f"Manager {name.split()[-1]}",
                status="Active"
            )
            db.add(proj)
            projects.append(proj)
        db.commit()

        # 2. Create Seats (5,500 seats across 5 floors, 10 zones, multiple bays)
        print("Seeding 5,500 seats across 5 floors and 10 zones...")
        floors = [1, 2, 3, 4, 5]
        zones = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E", "Zone F", "Zone G", "Zone H", "Zone I", "Zone J"]
        bays = [1, 2, 3, 4, 5] # 5 bays per floor-zone

        seats = []
        seat_counter = 1
        
        # We need 5,500 seats. Let's distribute them:
        # 5 floors * 10 zones * 5 bays = 250 combinations.
        # 5,500 seats / 250 = 22 seats per bay.
        for floor in floors:
            for zone in zones:
                for bay in bays:
                    for seat_idx in range(1, 23): # 22 seats per bay = 5500 total
                        seat_number = f"S-F{floor}{zone[5]}-B{bay:02d}-{seat_idx:02d}"
                        seat = Seat(
                            floor=floor,
                            zone=zone,
                            bay=bay,
                            seat_number=seat_number,
                            status="Available"
                        )
                        db.add(seat)
                        seats.append(seat)
        db.commit()

        # 3. Create 5,000 Employees
        print("Seeding 5,000 employees...")
        departments = ["Engineering", "Product", "Design", "Marketing", "HR", "Sales", "Finance", "Legal"]
        roles = ["Developer", "Senior Developer", "PM", "Designer", "Analyst", "Lead", "Associate"]
        
        first_names = [
            "John", "Jane", "Alex", "Emily", "Michael", "Sarah", "David", "Jessica", "Daniel", "Ashley",
            "James", "Mary", "Robert", "Patricia", "Charles", "Jennifer", "Matthew", "Elizabeth", "Joseph", "Linda",
            "William", "Barbara", "Thomas", "Susan", "Christopher", "Margaret", "Nicholas", "Dorothy", "Tyler", "Lisa",
            "Raj", "Amit", "Priya", "Rahul", "Siddharth", "Anjali", "Vikram", "Neha", "Arjun", "Kiran",
            "Carlos", "Maria", "Juan", "Ana", "Luis", "Elena", "Pedro", "Sofia", "Diego", "Carmen",
            "Yuki", "Haruto", "Yuto", "Sakura", "Mei", "Ren", "Sota", "Aoi", "Hinata", "Yua",
            "Hans", "Klaus", "Dieter", "Helga", "Ursula", "Gunter", "Brigitte", "Wolfgang", "Monika", "Jorgen",
            "Jean", "Marie", "Pierre", "Michel", "Philippe", "Alain", "Françoise", "Jacqueline", "Nathalie", "Isabelle"
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
            "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
            "Sharma", "Patel", "Mehta", "Kumar", "Singh", "Joshi", "Verma", "Rao", "Gupta", "Nair",
            "Muller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann",
            "Bernard", "Dubois", "Richard", "Petit", "Durand", "Leroy", "Moreau",
            "Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"
        ]

        employees = []
        start_date = date(2025, 1, 1)

        for i in range(1, 5001):
            emp_code = f"EMP{i:04d}"
            f_name = random.choice(first_names)
            l_name = random.choice(last_names)
            name = f"{f_name} {l_name}"
            
            # Clean special characters from names for emails
            clean_f = "".join(c for c in f_name.lower() if c.isalnum())
            clean_l = "".join(c for c in l_name.lower() if c.isalnum())
            email = f"{clean_f}.{clean_l}{i}@ethara.ai"
            
            dept = random.choice(departments)
            role = random.choice(roles)
            joining_date = start_date + timedelta(days=random.randint(0, 500))
            
            # Map randomly to projects
            proj = random.choice(projects)
            
            # Set Amit details specifically to match PDF example
            if i == 42:
                name = "Amit"
                email = "amit@ethara.ai"
                # Locate Project Talos
                talos_proj = next((p for p in projects if p.name == "Project Talos"), None)
                if talos_proj:
                    proj = talos_proj

            emp = Employee(
                employee_code=emp_code,
                name=name,
                email=email,
                department=dept,
                role=role,
                joining_date=joiningDate if 'joiningDate' in locals() else joining_date, # fallback
                status="Active",
                project_id=proj.id
            )
            db.add(emp)
            employees.append(emp)
        db.commit()

        # 4. Seat Allocation mapping
        # Requirements: At least 500 available, at least 100 reserved, at least 50 pending allocation
        # Total seats: 5,500. Total employees: 5,000.
        # Let's allocate 4,850 employees to seats.
        # This leaves 150 employees unallocated (pending allocation count: 150 >= 50)
        # Occupied seats: 4,850.
        # Let's reserve 120 seats (reserved seats count: 120 >= 100).
        # Let's set 30 seats to Maintenance.
        # Available seats remaining: 5,500 - 4,850 - 120 - 30 = 500 available seats (available seats: 500 >= 500).
        
        print("Mapping seat allocations and states...")
        
        # Shuffle seats to allocate randomly
        random.shuffle(seats)
        
        occupied_seats = seats[:4850]
        reserved_seats = seats[4850:4970]
        maintenance_seats = seats[4970:5000]
        available_seats = seats[5000:]

        # Mark seat statuses
        for s in occupied_seats:
            s.status = "Occupied"
        for s in reserved_seats:
            s.status = "Reserved"
        for s in maintenance_seats:
            s.status = "Maintenance"
        for s in available_seats:
            s.status = "Available"
        db.commit()

        # Create active allocations
        # Shuffle employees
        random.shuffle(employees)
        seated_employees = employees[:4850]
        
        # Specifically force Amit to be seated on Seat B4-23 on Floor 2, Zone B, Bay 4 in Project Talos to match PDF
        amit_emp = next((e for e in employees if e.name == "Amit"), None)
        if amit_emp:
            # Find Floor 2, Zone B, Bay 4, Seat B4-23
            target_seat = db.scalar(
                select(Seat).where(
                    and_(
                        Seat.floor == 2,
                        Seat.zone == "Zone B",
                        Seat.bay == 4,
                        Seat.seat_number.like("%23")
                    )
                )
            )
            if target_seat:
                target_seat.status = "Occupied"
                # If target_seat was in another status group, swap it
                if target_seat in available_seats:
                    available_seats.remove(target_seat)
                
                # Make sure amit_emp is in seated_employees
                if amit_emp not in seated_employees:
                    # replace a random employee
                    replaced_emp = seated_employees.pop()
                    seated_employees.append(amit_emp)

                # Allocate target seat to Amit
                alloc = SeatAllocation(
                    employee_id=amit_emp.id,
                    seat_id=target_seat.id,
                    project_id=amit_emp.project_id,
                    allocation_status="Active",
                    allocation_date=datetime.utcnow() - timedelta(days=10)
                )
                db.add(alloc)
                # Remove this seat from occupied list so we don't double allocate it below
                if target_seat in occupied_seats:
                    occupied_seats.remove(target_seat)
                if amit_emp in seated_employees:
                    seated_employees.remove(amit_emp)

        # Allocate rest of seated employees
        for emp, seat in zip(seated_employees, occupied_seats):
            alloc = SeatAllocation(
                employee_id=emp.id,
                seat_id=seat.id,
                project_id=emp.project_id,
                allocation_status="Active",
                allocation_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(alloc)
        
        db.commit()
        print("Database seeding completed successfully!")
        print(f"Stats:\n- Total Projects: {len(projects)}\n- Total Seats: 5,500 (Available: {len(available_seats)}, Occupied: {len(occupied_seats) + 1}, Reserved: {len(reserved_seats)}, Maintenance: {len(maintenance_seats)})\n- Total Employees: 5,000 (Seated: 4,850, Pending Allocation: 150)")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
