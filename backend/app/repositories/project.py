from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.project import Project
from ..schemas.project import ProjectCreate, ProjectUpdate

class ProjectRepository:
    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Optional[Project]:
        return db.scalar(select(Project).where(Project.id == project_id))

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Project]:
        return db.scalar(select(Project).where(Project.name == name))

    @staticmethod
    def get_all(db: Session) -> List[Project]:
        return list(db.scalars(select(Project)).all())

    @staticmethod
    def create(db: Session, schema: ProjectCreate) -> Project:
        db_project = Project(
            name=schema.name,
            description=schema.description,
            manager_name=schema.manager_name,
            status=schema.status
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def update(db: Session, db_project: Project, schema: ProjectUpdate) -> Project:
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        db.commit()
        db.refresh(db_project)
        return db_project
