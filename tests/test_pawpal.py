import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task, Priority


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=30, priority=Priority.HIGH)
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", type="Dog", age=3)
    pet.add_task(Task(name="Morning walk", duration=30, priority=Priority.HIGH))
    assert len(pet.tasks) == 1
