import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, and_
from ..models.employee import Employee
from ..models.seat import Seat
from ..models.allocation import SeatAllocation
from ..models.project import Project

class AIService:
    @staticmethod
    def process_query(db: Session, query: str, employee_id: int | None = None) -> str:
        """
        Process the user natural language query using a deterministic intent parser.
        Converts natural language to SQL queries and returns a conversational response.
        """
        query_clean = query.strip().lower()

        # Resolve 'my' / 'me' queries using the passed employee_id
        if employee_id:
            current_emp = db.get(Employee, employee_id)
            if current_emp:
                if "my seat" in query_clean or "where is my seat" in query_clean or "where am i seated" in query_clean or "where am i seeted" in query_clean:
                    return AIService._handle_employee_seat(db, current_emp.name)
                if "my project" in query_clean or "which project am i assigned to" in query_clean or "project am i" in query_clean or "which project is assigned to me" in query_clean:
                    return AIService._handle_employee_project(db, current_emp.name)
                if "near me" in query_clean or "sitting near me" in query_clean or "who sits near me" in query_clean:
                    return AIService._handle_neighbors(db, current_emp.name)
                if "reserved seats" in query_clean:
                    if current_emp.project_id:
                        proj = db.get(Project, current_emp.project_id)
                        if proj:
                            return AIService._handle_project_reserved_seats(db, proj)
                    return "You do not have an active project assigned."

        # Pattern: where are the reserved seats in Project X
        m_reserved = re.search(r"reserved\s+seats\s+(?:in|for)\s+(?:project\s+)?([\w\s\d]+)", query_clean)
        if m_reserved:
            proj_param = m_reserved.group(1).strip()
            proj = db.scalar(select(Project).where(func.lower(Project.name) == proj_param.lower()))
            if proj:
                return AIService._handle_project_reserved_seats(db, proj)

        # Pattern 1: Where is employee X seated? / Where sits X? / Where is X?
        m_seat = re.search(r"where\s+is\s+(?:employee\s+)?([\w\s\d]+?)\s+seated", query_clean) or \
                 re.search(r"where\s+is\s+(?:employee\s+)?([\w\s\d]+)", query_clean) or \
                 re.search(r"where\s+sits\s+([\w\s\d]+)", query_clean)
        if m_seat:
            name_param = m_seat.group(1).strip()
            return AIService._handle_employee_seat(db, name_param)

        # Pattern 2: Which project is X assigned to? / Project of X?
        m_proj = re.search(r"which\s+project\s+is\s+([\w\s\d]+?)\s+assigned\s+to", query_clean) or \
                 re.search(r"project\s+of\s+([\w\s\d]+)", query_clean)
        if m_proj:
            name_param = m_proj.group(1).strip()
            return AIService._handle_employee_project(db, name_param)

        # Pattern 3: Show all available seats on Floor X
        m_floor_seats = re.search(r"(?:available\s+seats|seats\s+available)\s+on\s+floor\s+(\d+)", query_clean) or \
                         re.search(r"floor\s+(\d+)\s+available\s+seats", query_clean)
        if m_floor_seats:
            floor_param = int(m_floor_seats.group(1))
            return AIService._handle_floor_availability(db, floor_param)

        # Pattern 4: Who sits near X? / Who is sitting near X?
        m_near = re.search(r"who\s+(?:sits|is\s+sitting)\s+near\s+([\w\s\d]+)", query_clean)
        if m_near:
            name_param = m_near.group(1).strip()
            return AIService._handle_neighbors(db, name_param)

        # Pattern 5: Who is in Project X?
        m_proj_members = re.search(r"who\s+is\s+in\s+(?:project\s+)?([\w\s\d]+)", query_clean)
        if m_proj_members:
            proj_param = m_proj_members.group(1).strip()
            return AIService._handle_project_members(db, proj_param)

        # Pattern 6: Seat utilization (Project / Zone)
        m_util_zone = re.search(r"zone\s+([\w\s\d]+?)\s+(?:seat\s+)?utilization", query_clean)
        if m_util_zone:
            zone_param = m_util_zone.group(1).strip()
            return AIService._handle_zone_utilization(db, zone_param)

        m_util_proj = re.search(r"(?:project\s+)?([\w\s\d]+?)\s+utilization", query_clean)
        if m_util_proj:
            proj_param = m_util_proj.group(1).strip()
            # Verify if this is indeed a project to avoid misfiring
            proj = db.scalar(select(Project).where(func.lower(Project.name) == proj_param.lower()))
            if proj:
                return AIService._handle_project_utilization(db, proj)

        # Pattern 7: List all available seats / available seats count
        if "available seats" in query_clean or "seats available" in query_clean:
            return AIService._handle_total_availability(db)

        # Fallback Help Response
        return (
            "I couldn't match your query. Try asking me:\n"
            "- 'Where is employee Amit seated?'\n"
            "- 'Which project is Amit assigned to?'\n"
            "- 'Show all available seats on Floor 3'\n"
            "- 'Who is sitting near Amit?'\n"
            "- 'Who is in Project Talos?'\n"
            "- 'Zone A utilization'\n"
            "- 'Project Talos utilization'\n"
            "- 'List available seats'"
        )

    @staticmethod
    def _find_employee(db: Session, name: str) -> Optional[Employee]:
        # 1. Try exact match by name
        emp = db.scalar(
            select(Employee)
            .options(joinedload(Employee.project))
            .where(func.lower(Employee.name) == name.lower())
        )
        if emp:
            return emp
            
        # 2. Try match after removing spaces
        clean_name = name.lower().replace(" ", "")
        emp = db.scalar(
            select(Employee)
            .options(joinedload(Employee.project))
            .where(func.replace(func.lower(Employee.name), ' ', '') == clean_name)
        )
        if emp:
            return emp
            
        # 3. Try exact match by code
        emp = db.scalar(
            select(Employee)
            .options(joinedload(Employee.project))
            .where(func.lower(Employee.employee_code) == name.lower())
        )
        if emp:
            return emp
            
        # 4. Try match by code after removing spaces
        emp = db.scalar(
            select(Employee)
            .options(joinedload(Employee.project))
            .where(func.replace(func.lower(Employee.employee_code), ' ', '') == clean_name)
        )
        if emp:
            return emp

        # 5. If the input name is just a number (e.g. "62"), try prefixing with "Employee" or formatting as EMP code
        if name.strip().isdigit():
            num = int(name.strip())
            # Try "Employee 62"
            emp = db.scalar(
                select(Employee)
                .options(joinedload(Employee.project))
                .where(func.lower(Employee.name) == f"employee {num}")
            )
            if emp:
                return emp

            # Try "EMP0062"
            padded_code = f"EMP{num:04d}"
            emp = db.scalar(
                select(Employee)
                .options(joinedload(Employee.project))
                .where(func.lower(Employee.employee_code) == padded_code.lower())
            )
            if emp:
                return emp

        return None

    @staticmethod
    def _project_label(name: str | None) -> str:
        if not name:
            return "No Project"
        return name if name.strip().lower().startswith("project") else f"Project {name}"

    @staticmethod
    def _handle_employee_seat(db: Session, name: str) -> str:
        employee = AIService._find_employee(db, name)
        if not employee:
            return f"Employee matching '{name}' was not found."

        # Fetch active allocation
        alloc = db.scalar(
            select(SeatAllocation)
            .options(joinedload(SeatAllocation.seat))
            .where(
                and_(
                    SeatAllocation.employee_id == employee.id,
                    SeatAllocation.allocation_status == "Active"
                )
            )
        )

        project_label = AIService._project_label(employee.project.name if employee.project else None)

        if not alloc:
            return f"{employee.name} is currently unseated (status: {employee.status}). They are assigned to {project_label}."

        seat = alloc.seat
        # Return exact format matched in PDF
        return f"{employee.name} is seated on Floor {seat.floor}, Zone {seat.zone}, Bay {seat.bay}, Seat {seat.seat_number}. He is assigned to {project_label}."

    @staticmethod
    def _handle_employee_project(db: Session, name: str) -> str:
        employee = AIService._find_employee(db, name)
        if not employee:
            return f"Employee matching '{name}' was not found."

        if employee.project:
            return f"Employee {employee.name} is assigned to {AIService._project_label(employee.project.name)}."
        return f"Employee {employee.name} is currently not assigned to any project."

    @staticmethod
    def _handle_floor_availability(db: Session, floor: int) -> str:
        seats = db.scalars(
            select(Seat)
            .where(and_(Seat.floor == floor, Seat.status == "Available"))
            .order_by(Seat.zone, Seat.bay, Seat.seat_number)
        ).all()

        if not seats:
            return f"There are no available seats on Floor {floor}."

        sample_str = ", ".join([s.seat_number for s in seats[:5]])
        if len(seats) > 5:
            sample_str += ", ..."
        return f"There are {len(seats)} available seats on Floor {floor}. Sample seats: {sample_str}"

    @staticmethod
    def _handle_total_availability(db: Session) -> str:
        total = db.scalar(select(func.count(Seat.id)).where(Seat.status == "Available")) or 0
        
        # Floor breakdown
        floor_counts = db.execute(
            select(Seat.floor, func.count(Seat.id))
            .where(Seat.status == "Available")
            .group_by(Seat.floor)
            .order_by(Seat.floor)
        ).all()

        breakdown = "\n".join([f"- Floor {row[0]}: {row[1]} available" for row in floor_counts])
        return f"There are currently {total} available seats in the workspace.\nBreakdown by floor:\n{breakdown}"

    @staticmethod
    def _handle_neighbors(db: Session, name: str) -> str:
        employee = AIService._find_employee(db, name)
        if not employee:
            return f"Employee matching '{name}' was not found."

        alloc = db.scalar(
            select(SeatAllocation)
            .options(joinedload(SeatAllocation.seat))
            .where(
                and_(
                    SeatAllocation.employee_id == employee.id,
                    SeatAllocation.allocation_status == "Active"
                )
            )
        )
        if not alloc:
            return f"{employee.name} is currently unseated, so we cannot determine neighbors."

        seat = alloc.seat
        # Find neighbors: Seated in the same floor, zone, and bay (excluding the employee themselves)
        neighbors = db.scalars(
            select(Employee)
            .select_from(SeatAllocation)
            .join(Employee, SeatAllocation.employee_id == Employee.id)
            .join(Seat, SeatAllocation.seat_id == Seat.id)
            .where(
                and_(
                    Seat.floor == seat.floor,
                    Seat.zone == seat.zone,
                    Seat.bay == seat.bay,
                    SeatAllocation.allocation_status == "Active",
                    Employee.id != employee.id
                )
            )
        ).all()

        if not neighbors:
            return f"No other employees are currently seated in Bay {seat.bay} (Zone {seat.zone}) near {employee.name}."

        neighbor_names = ", ".join([f"{emp.name} ({db.scalar(select(Seat.seat_number).select_from(SeatAllocation).join(Seat).where(and_(SeatAllocation.employee_id == emp.id, SeatAllocation.allocation_status == 'Active')))})" for emp in neighbors])
        return f"Employees seated near {employee.name} in Bay {seat.bay} (Zone {seat.zone}): {neighbor_names}."

    @staticmethod
    def _handle_project_members(db: Session, project_name: str) -> str:
        project = db.scalar(
            select(Project)
            .where(func.lower(Project.name) == project_name.lower())
        )
        if not project:
            return f"Project '{project_name}' was not found."

        # Fetch employees seated under this project
        members = db.scalars(
            select(Employee)
            .select_from(SeatAllocation)
            .join(Employee, SeatAllocation.employee_id == Employee.id)
            .where(
                and_(
                    SeatAllocation.project_id == project.id,
                    SeatAllocation.allocation_status == "Active"
                )
            )
        ).all()

        if not members:
            return f"No active seated employees found for {AIService._project_label(project.name)}."

        member_list = ", ".join([m.name for m in members])
        return f"Active seated employees for {AIService._project_label(project.name)}: {member_list}."

    @staticmethod
    def _handle_zone_utilization(db: Session, zone: str) -> str:
        zone_norm = zone.strip()
        if len(zone_norm) == 1:
            zone_norm = f"Zone {zone_norm.upper()}"
        elif not zone_norm.lower().startswith("zone"):
            zone_norm = f"Zone {zone_norm}"

        total = db.scalar(select(func.count(Seat.id)).where(func.lower(Seat.zone) == zone_norm.lower())) or 0
        if total == 0:
            return f"Zone '{zone}' was not found or has no seats."

        occupied = db.scalar(
            select(func.count(Seat.id))
            .where(
                and_(
                    func.lower(Seat.zone) == zone_norm.lower(),
                    Seat.status == "Occupied"
                )
            )
        ) or 0

        rate = round((occupied / total) * 100, 1)
        return f"Zone {zone_norm.upper()} has {total} total seats, with {occupied} currently occupied (Utilization Rate: {rate}%)."

    @staticmethod
    def _handle_project_utilization(db: Session, project: Project) -> str:
        count = db.scalar(
            select(func.count(SeatAllocation.id))
            .where(
                and_(
                    SeatAllocation.project_id == project.id,
                    SeatAllocation.allocation_status == "Active"
                )
            )
        ) or 0
        return f"{AIService._project_label(project.name)} currently has {count} active seat allocations."

    @staticmethod
    def _handle_project_reserved_seats(db: Session, project: Project) -> str:
        allocs = db.scalars(
            select(SeatAllocation)
            .options(joinedload(SeatAllocation.seat))
            .where(
                and_(
                    SeatAllocation.project_id == project.id,
                    SeatAllocation.allocation_status == "Reserved"
                )
            )
        ).all()
        
        if not allocs:
            return f"There are no seats reserved for {AIService._project_label(project.name)}."
            
        seats_str = ", ".join(f"{alloc.seat.seat_number} (Floor {alloc.seat.floor}, {alloc.seat.zone}, Bay {alloc.seat.bay})" for alloc in allocs)
        return f"The following seats are reserved for {AIService._project_label(project.name)}: {seats_str}."
