from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    name: str
    type: str
    age: int
    special_needs: Optional[str] = None

    def update_info(self, name: str = None, type: str = None, age: int = None, special_needs: str = None) -> None:
        pass

    def get_summary(self) -> str:
        pass


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    time_constraint: Optional[str] = None

    def update_task(self, name: str = None, duration: int = None, priority: str = None, time_constraint: str = None) -> None:
        pass

    def is_high_priority(self) -> bool:
        pass


class Owner:
    def __init__(self, name: str, available_time: int, preferences: Optional[str] = None):
        self.name = name
        self.available_time = available_time
        self.preferences = preferences
        self.pets: list[Pet] = []
        self.schedule: Optional["Schedule"] = None

    def update_availability(self, available_time: int) -> None:
        pass

    def set_preferences(self, preferences: str) -> None:
        pass


class Schedule:
    def __init__(self, available_time: int):
        self.tasks: list[Task] = []
        self.available_time = available_time
        self.generated_plan: Optional[str] = None

    def generate_plan(self) -> None:
        pass

    def sort_tasks_by_priority(self) -> list[Task]:
        pass

    def fit_tasks_into_time(self) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass
