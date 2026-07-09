import os
import sys
from datetime import datetime, date, timedelta
import random
from sqlalchemy import select, and_, insert, update

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

        employees_data = []
        start_date = date(2025, 1, 1)

        for i in range(1, 5001):
            emp_code = f"EMP{i:04d}"
            f_name = random.choice(first_names)
            l_name = random.choice(last_names)
            name = f"{f_name} {l_name}"
            
            clean_f = "".join(c for c in f_name.lower() if c.isalnum())
            clean_l = "".join(c for c in l_name.lower() if c.isalnum())
            email = f"{clean_f}.{clean_l}{i}@ethara.ai"
            
            dept = random.choice(departments)
            role = random.choice(roles)
            joining_date = start_date + timedelta(days=random.randint(0, 500))
            proj = random.choice(projects)

            if i == 42:
                name = "Amit"
                email = "amit@ethara.ai"
                talos_proj = next((p for p in projects if p.name == "Project Talos"), None)
                if talos_proj:
                    proj = talos_proj

            employees_data.append({
                "employee_code": emp_code,
                "name": name,
                "email": email,
                "department": dept,
                "role": role,
                "joining_date": joining_date,
                "status": "Active",
                "project_id": proj.id,
            })

        # Bulk insert all employees at once — much faster than ORM one-by-one
        db.execute(insert(Employee), employees_data)
        db.commit()
        print(f"  -> {len(employees_data)} employees inserted.")

        # Reload only necessary columns (id, name, project_id) as lightweight row objects.
        # This is 100x faster than loading full ORM objects over a remote network.
        employees = list(db.execute(select(Employee.id, Employee.name, Employee.project_id)).all())

        # 4. Seat Allocation mapping
        # Requirements: At least 500 available, at least 100 reserved, at least 50 pending allocation
        # Total seats: 5,500. Total employees: 5,000.
        # Occupied: 4,850 | Reserved: 120 | Maintenance: 30 | Available: 500
        print("Mapping seat allocations and states...")

        seat_ids = [s.id for s in seats]
        random.shuffle(seat_ids)

        occupied_ids   = seat_ids[:4850]
        reserved_ids   = seat_ids[4850:4970]
        maintenance_ids = seat_ids[4970:5000]
        available_ids  = seat_ids[5000:]

        # Bulk update seat statuses using WHERE id IN (...)
        with engine.connect() as conn:
            from sqlalchemy import text
            def id_list(ids): return ",".join(str(i) for i in ids)
            conn.execute(text(f"UPDATE seats SET status='Occupied'    WHERE id IN ({id_list(occupied_ids)})"))
            conn.execute(text(f"UPDATE seats SET status='Reserved'    WHERE id IN ({id_list(reserved_ids)})"))
            conn.execute(text(f"UPDATE seats SET status='Maintenance' WHERE id IN ({id_list(maintenance_ids)})"))
            conn.execute(text(f"UPDATE seats SET status='Available'   WHERE id IN ({id_list(available_ids)})"))
            conn.commit()
        print("  -> Seat statuses updated.")

        # Create bulk allocations
        random.shuffle(employees)
        seated_employees = list(employees[:4850])

        # Find Amit and give him a specific seat
        amit_emp = next((e for e in employees if e.name == "Amit"), None)
        amit_alloc = None
        if amit_emp:
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
                db.execute(update(Seat).where(Seat.id == target_seat.id).values(status="Occupied"))
                db.commit()
                amit_alloc = {
                    "employee_id": amit_emp.id,
                    "seat_id": target_seat.id,
                    "project_id": amit_emp.project_id,
                    "allocation_status": "Active",
                    "allocation_date": datetime.utcnow() - timedelta(days=10),
                }
                if amit_emp in seated_employees:
                    seated_employees.remove(amit_emp)
                if target_seat.id in occupied_ids:
                    occupied_ids.remove(target_seat.id)

        # Build allocations list
        alloc_occupied = occupied_ids[:len(seated_employees)]
        allocations_data = [
            {
                "employee_id": emp.id,
                "seat_id": seat_id,
                "project_id": emp.project_id,
                "allocation_status": "Active",
                "allocation_date": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            }
            for emp, seat_id in zip(seated_employees, alloc_occupied)
        ]
        if amit_alloc:
            allocations_data.append(amit_alloc)

        # Bulk insert allocations
        db.execute(insert(SeatAllocation), allocations_data)
        db.commit()
        print(f"  -> {len(allocations_data)} seat allocations inserted.")
        print("Database seeding completed successfully!")
        print(f"Stats:\n- Total Projects: {len(projects)}\n- Total Seats: 5,500 (Available: {len(available_ids)}, Occupied: {len(occupied_ids)}, Reserved: {len(reserved_ids)}, Maintenance: {len(maintenance_ids)})\n- Total Employees: 5,000 (Seated: ~4,850, Pending Allocation: ~150)")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
