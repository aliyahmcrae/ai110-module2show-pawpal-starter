import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Pet, Task, Priority, Owner, Schedule


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=30, priority=Priority.HIGH)
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", type="Dog", age=3)
    pet.add_task(Task(name="Morning walk", duration=30, priority=Priority.HIGH))
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_tasks_by_priority_returns_high_before_medium_before_low():
    """Tasks are returned highest-priority first regardless of insertion order."""
    low_task    = Task(name="Grooming",      duration=20, priority=Priority.LOW)
    high_task   = Task(name="Morning walk",  duration=30, priority=Priority.HIGH)
    medium_task = Task(name="Evening walk",  duration=30, priority=Priority.MEDIUM)

    pet = Pet(name="Buddy", type="Dog", age=3)
    # Insert in LOW → HIGH → MEDIUM order to confirm sort isn't relying on insertion
    pet.add_task(low_task)
    pet.add_task(high_task)
    pet.add_task(medium_task)

    owner = Owner(name="Alex", available_time=120)
    owner.add_pet(pet)
    schedule = Schedule(owner)

    sorted_tasks = schedule.sort_tasks_by_priority()

    assert sorted_tasks[0].priority == Priority.HIGH
    assert sorted_tasks[1].priority == Priority.MEDIUM
    assert sorted_tasks[2].priority == Priority.LOW


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_completing_daily_task_creates_next_occurrence():
    """Marking a daily task complete appends a fresh copy due tomorrow."""
    daily_task = Task(name="Feed breakfast", duration=10, priority=Priority.HIGH, frequency="daily")

    pet = Pet(name="Luna", type="Cat", age=2)
    pet.add_task(daily_task)

    next_task = pet.complete_task("Feed breakfast")

    # Original task should be marked done
    assert pet.tasks[0].completed is True

    # A new, uncompleted task should have been appended
    assert next_task is not None
    assert len(pet.tasks) == 2
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_start_time():
    """Two pending tasks that start at exactly the same time produce a conflict."""
    task_a = Task(name="Morning walk",        duration=30, priority=Priority.HIGH,   time_constraint="08:00")
    task_b = Task(name="Administer medicine", duration=10, priority=Priority.MEDIUM, time_constraint="08:00")

    pet_a = Pet(name="Buddy", type="Dog", age=3)
    pet_a.add_task(task_a)

    pet_b = Pet(name="Luna", type="Cat", age=2)
    pet_b.add_task(task_b)

    owner = Owner(name="Alex", available_time=120)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)
    schedule = Schedule(owner)

    conflicts = schedule.detect_conflicts()

    assert len(conflicts) >= 1
    assert any("Conflict" in c for c in conflicts)


def test_detect_conflicts_flags_overlapping_windows():
    """A task starting mid-way through another task is still a conflict."""
    # Walk: 08:00–08:30. Meds: 08:20–08:25 — clearly overlaps.
    task_a = Task(name="Morning walk",        duration=30, priority=Priority.HIGH,   time_constraint="08:00")
    task_b = Task(name="Administer medicine", duration=5,  priority=Priority.MEDIUM, time_constraint="08:20")

    pet = Pet(name="Buddy", type="Dog", age=3)
    pet.add_task(task_a)
    pet.add_task(task_b)

    owner = Owner(name="Alex", available_time=120)
    owner.add_pet(pet)
    schedule = Schedule(owner)

    conflicts = schedule.detect_conflicts()

    assert any("Conflict" in c for c in conflicts)


def test_detect_conflicts_no_conflict_for_sequential_tasks():
    """Tasks that end before the next one starts should not be flagged."""
    # Walk: 08:00–08:30. Meds: 08:30–08:35 — back-to-back, no overlap.
    task_a = Task(name="Morning walk",        duration=30, priority=Priority.HIGH,   time_constraint="08:00")
    task_b = Task(name="Administer medicine", duration=5,  priority=Priority.MEDIUM, time_constraint="08:30")

    pet = Pet(name="Buddy", type="Dog", age=3)
    pet.add_task(task_a)
    pet.add_task(task_b)

    owner = Owner(name="Alex", available_time=120)
    owner.add_pet(pet)
    schedule = Schedule(owner)

    conflicts = schedule.detect_conflicts()

    assert not any("Conflict" in c for c in conflicts)


def test_detect_conflicts_invalid_time_format_produces_warning():
    """A task with a bad time string gets a Warning, not a crash."""
    task = Task(name="Play", duration=15, priority=Priority.LOW, time_constraint="not-a-time")

    pet = Pet(name="Whiskers", type="Cat", age=1)
    pet.add_task(task)

    owner = Owner(name="Alex", available_time=120)
    owner.add_pet(pet)
    schedule = Schedule(owner)

    warnings = schedule.detect_conflicts()

    assert any("Warning" in w for w in warnings)


# ---------------------------------------------------------------------------
# Recurrence — weekly and once
# ---------------------------------------------------------------------------

def test_completing_weekly_task_creates_next_occurrence_in_seven_days():
    """Marking a weekly task complete queues a copy due 7 days from today."""
    weekly_task = Task(name="Grooming", duration=20, priority=Priority.MEDIUM, frequency="weekly")

    pet = Pet(name="Buddy", type="Dog", age=3)
    pet.add_task(weekly_task)

    next_task = pet.complete_task("Grooming")

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)
    assert next_task.completed is False


def test_completing_once_task_does_not_create_next_occurrence():
    """A one-off task should never be re-queued after completion."""
    once_task = Task(name="Vet visit", duration=60, priority=Priority.HIGH, frequency="once")

    pet = Pet(name="Luna", type="Cat", age=2)
    pet.add_task(once_task)

    next_task = pet.complete_task("Vet visit")

    assert next_task is None
    assert len(pet.tasks) == 1  # no new task added


# ---------------------------------------------------------------------------
# Greedy scheduler (fit_tasks_into_time)
# ---------------------------------------------------------------------------

def _make_schedule(tasks, available_time):
    """Helper: one pet, one owner, one schedule."""
    pet = Pet(name="Buddy", type="Dog", age=3)
    for t in tasks:
        pet.add_task(t)
    owner = Owner(name="Alex", available_time=available_time)
    owner.add_pet(pet)
    return Schedule(owner)


def test_fit_tasks_zero_available_time_schedules_nothing():
    """Owner with 0 minutes available should get an empty schedule."""
    task = Task(name="Walk", duration=30, priority=Priority.HIGH)
    schedule = _make_schedule([task], available_time=0)

    assert schedule.fit_tasks_into_time() == []


def test_fit_tasks_exact_time_fit_includes_task():
    """A task whose duration exactly equals available_time should be scheduled."""
    task = Task(name="Walk", duration=30, priority=Priority.HIGH)
    schedule = _make_schedule([task], available_time=30)

    scheduled = schedule.fit_tasks_into_time()

    assert len(scheduled) == 1
    assert scheduled[0].name == "Walk"


def test_fit_tasks_skips_tasks_that_dont_fit():
    """Tasks exceeding remaining time are skipped; smaller ones still get in."""
    big_task   = Task(name="Long grooming", duration=90, priority=Priority.HIGH)
    small_task = Task(name="Quick feed",    duration=10, priority=Priority.MEDIUM)

    schedule = _make_schedule([big_task, small_task], available_time=30)

    scheduled = schedule.fit_tasks_into_time()
    names = [t.name for t in scheduled]

    assert "Long grooming" not in names
    assert "Quick feed" in names


def test_fit_tasks_excludes_completed_tasks():
    """Already-completed tasks should never appear in the scheduled output."""
    done_task    = Task(name="Morning walk", duration=30, priority=Priority.HIGH, completed=True)
    pending_task = Task(name="Evening feed", duration=10, priority=Priority.MEDIUM)

    schedule = _make_schedule([done_task, pending_task], available_time=60)

    scheduled = schedule.fit_tasks_into_time()
    names = [t.name for t in scheduled]

    assert "Morning walk" not in names
    assert "Evening feed" in names


# ---------------------------------------------------------------------------
# filter_tasks
# ---------------------------------------------------------------------------

def _make_two_pet_schedule():
    """Helper: Buddy (dog) + Luna (cat), each with one done and one pending task."""
    buddy_done    = Task(name="Morning walk", duration=30, priority=Priority.HIGH,   completed=True)
    buddy_pending = Task(name="Evening walk", duration=30, priority=Priority.MEDIUM)
    luna_pending  = Task(name="Feed Luna",    duration=10, priority=Priority.HIGH)

    buddy = Pet(name="Buddy", type="Dog", age=3)
    buddy.add_task(buddy_done)
    buddy.add_task(buddy_pending)

    luna = Pet(name="Luna", type="Cat", age=2)
    luna.add_task(luna_pending)

    owner = Owner(name="Alex", available_time=120)
    owner.add_pet(buddy)
    owner.add_pet(luna)
    return Schedule(owner)


def test_filter_tasks_completed_false_returns_only_pending():
    schedule = _make_two_pet_schedule()
    results = schedule.filter_tasks(completed=False)
    assert all(not t.completed for t in results)
    assert len(results) == 2  # Evening walk + Feed Luna


def test_filter_tasks_completed_true_returns_only_done():
    schedule = _make_two_pet_schedule()
    results = schedule.filter_tasks(completed=True)
    assert all(t.completed for t in results)
    assert len(results) == 1  # Morning walk


def test_filter_tasks_by_pet_name_returns_only_that_pets_tasks():
    schedule = _make_two_pet_schedule()
    results = schedule.filter_tasks(pet_name="Buddy")
    assert len(results) == 2
    assert all(t.name in ("Morning walk", "Evening walk") for t in results)


def test_filter_tasks_unknown_pet_name_returns_empty():
    schedule = _make_two_pet_schedule()
    assert schedule.filter_tasks(pet_name="NoSuchPet") == []


def test_filter_tasks_no_args_returns_all():
    schedule = _make_two_pet_schedule()
    assert len(schedule.filter_tasks()) == 3
