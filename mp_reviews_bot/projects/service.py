from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Project:
    id: str
    name: str
    owner_id: str


_projects: Dict[str, Project] = {}


def create_project(name: str, owner_id: str) -> Project:
    project_id = f"proj-{len(_projects) + 1}"
    project = Project(id=project_id, name=name, owner_id=owner_id)
    _projects[project_id] = project
    return project


def get_project(project_id: str) -> Optional[Project]:
    return _projects.get(project_id)


def update_project(project_id: str, name: str) -> Optional[Project]:
    project = _projects.get(project_id)
    if not project:
        return None
    project.name = name
    _projects[project_id] = project
    return project


def delete_project(project_id: str) -> bool:
    return _projects.pop(project_id, None) is not None
