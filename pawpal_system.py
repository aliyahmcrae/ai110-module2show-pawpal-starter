from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    name: str
    duration: int        # in minutes
    priority: Priority
    description: str = ""
    frequency: str = "once"   # e.g. "daily", "weekly", "once"
    completed: bool = False
    time_constraint: Optional[str] = None

    def update_task(
        self,
        name: str = None,
        duration: int = None,
        priority: Priority = None,
        description: str = None,
        frequency: str = None,
        time_constraint: str = None,
    ) -> None:
        """Update any task fields; omitted arguments are left unchanged."""
        if name is not None:
            self.name = name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if description is not None:
            self.description = description
        if frequency is not None:
            self.frequency = frequency
        if time_constraint is not None:
            self.time_constraint = time_constraint

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is HIGH."""
        return self.priority == Priority.HIGH


@dataclass
class Pet:
    name: str
    type: str
    age: int
    special_needs: Optional[str] = None
    tasks: list[Task] = field(default_factory=list)

    def update_info(
        self,
        name: str = None,
        type: str = None,
        age: int = None,
        special_needs: str = None,
    ) -> None:
        """Update any pet fields; omitted arguments are left unchanged."""
        if name is not None:
            self.name = name
        if type is not None:
            self.type = type
        if age is not None:
            self.age = age
        if special_needs is not None:
            self.special_needs = special_needs

    def get_summary(self) -> str:
        """Return a one-line string with the pet's key details and pending task count."""
        summary = f"{self.name} ({self.type}, {self.age} yrs)"
        if self.special_needs:
            summary += f" — Special needs: {self.special_needs}"
        pending = [t for t in self.tasks if not t.completed]
        summary += f" | Tasks: {len(self.tasks)} total, {len(pending)} pending"
        return summary

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove all tasks with the given name from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.name != task_name]


class Owner:
    def __init__(self, name: str, available_time: int, preferences: Optional[str] = None):
        self.name = name
        self.available_time = available_time   # in minutes
        self.preferences = preferences
        self.pets: list[Pet] = []
        self.schedule: Optional["Schedule"] = None

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of all tasks across every pet this owner has."""
        return [task for pet in self.pets for task in pet.tasks]

    def update_availability(self, available_time: int) -> None:
        """Update the number of minutes the owner has available."""
        self.available_time = available_time

    def set_preferences(self, preferences: str) -> None:
        """Set the owner's scheduling preferences."""
        self.preferences = preferences


class Schedule:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.generated_plan: Optional[str] = None

    @property
    def available_time(self) -> int:
        """Mirror the owner's available time so the schedule stays in sync."""
        return self.owner.available_time

    def sort_tasks_by_priority(self) -> list[Task]:
        """Return all tasks across the owner's pets sorted highest priority first."""
        tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.priority.value, reverse=True)

    def fit_tasks_into_time(self) -> list[Task]:
        """Greedily select tasks by priority until the owner's available time is filled."""
        sorted_tasks = self.sort_tasks_by_priority()
        scheduled, time_used = [], 0
        for task in sorted_tasks:
            if not task.completed and time_used + task.duration <= self.available_time:
                scheduled.append(task)
                time_used += task.duration
        return scheduled

    def generate_plan(self) -> None:
        """Build and store the formatted plan string in generated_plan."""
        self.generated_plan = self.explain_plan()

    def explain_plan(self) -> str:
        """Return a formatted terminal string of the scheduled plan grouped by pet."""
        scheduled = self.fit_tasks_into_time()
        if not scheduled:
            return "No tasks fit within the available time."

        scheduled_ids = {id(t) for t in scheduled}
        pet_emoji = {"dog": "🐶", "cat": "🐱"}
        priority_badge = {Priority.HIGH: "[!!!]", Priority.MEDIUM: "[!! ]", Priority.LOW: "[!  ]"}
        width = 46

        lines = [
            f"╔{'═' * width}╗",
            f"║{'PawPal+ Plan for ' + self.owner.name:^{width}}║",
            f"╚{'═' * width}╝",
            "",
        ]

        skipped, time_used = [], 0

        for pet in self.owner.pets:
            pet_scheduled = [t for t in pet.tasks if id(t) in scheduled_ids]
            skipped.extend(t for t in pet.tasks if id(t) not in scheduled_ids and not t.completed)

            if not pet_scheduled:
                continue

            emoji = pet_emoji.get(pet.type.lower(), "🐾")
            lines.append(f"  {emoji} {pet.name}")
            lines.append(f"  {'─' * (width - 2)}")

            for task in pet_scheduled:
                badge = priority_badge[task.priority]
                constraint = f"  ← {task.time_constraint}" if task.time_constraint else ""
                lines.append(f"  {badge} {task.name:<26} {task.duration:>3} min  {task.frequency}{constraint}")
                time_used += task.duration

            lines.append("")

        bar_width = 22
        filled = round((time_used / self.available_time) * bar_width) if self.available_time else 0
        bar = "█" * filled + "░" * (bar_width - filled)

        lines.append(f"  {'─' * (width - 2)}")
        lines.append(f"  Time used  {bar}  {time_used}/{self.available_time} min")

        if skipped:
            lines.append(f"  Skipped    {', '.join(t.name for t in skipped)}")

        return "\n".join(lines)
