# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Several algorithmic improvements were added to `pawpal_system.py` beyond the base scheduler:

**Task filtering — `Schedule.filter_tasks(completed, pet_name)`**
Returns tasks narrowed by completion status, pet name, or both. Each parameter is optional — passing neither returns all tasks. Useful for building focused views without modifying the underlying data.

**Automatic recurrence — `Task.recur()` and `Pet.complete_task(task_name)`**
Marking a `"daily"` or `"weekly"` task complete via `complete_task()` automatically queues a fresh copy for the next occurrence. Due dates are calculated with Python's `timedelta` (`+1 day` for daily, `+7 days` for weekly). One-off tasks (`frequency="once"`) return `None` from `recur()` and are never re-queued.

**Conflict detection — `Schedule.detect_conflicts()`**
Checks every pair of pending timed tasks for overlapping windows using the interval overlap condition `start_a < end_b and start_b < end_a`. Returns a flat list of human-readable warning strings — one per conflict — rather than raising exceptions. Tasks with unrecognised time formats produce a `Warning:` message and are skipped gracefully instead of crashing the program.

## Testing PawPal+

### Running the tests

```bash
python3 -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test | What it verifies |
|------|-----------------|
| `test_mark_complete_changes_status` | Calling `mark_complete()` flips `completed` to `True` |
| `test_add_task_increases_pet_task_count` | `add_task()` appends the task to the pet's list |
| `test_sort_tasks_by_priority_returns_high_before_medium_before_low` | `sort_tasks_by_priority()` always returns HIGH → MEDIUM → LOW regardless of insertion order |
| `test_completing_daily_task_creates_next_occurrence` | Completing a `"daily"` task appends a fresh copy with `due_date = today + 1 day` and `completed = False` |
| `test_detect_conflicts_flags_same_start_time` | `detect_conflicts()` returns at least one `"Conflict"` warning when two tasks share the same start time |
| `test_detect_conflicts_flags_overlapping_windows` | A task starting mid-way through another is still caught as a conflict |
| `test_detect_conflicts_no_conflict_for_sequential_tasks` | Back-to-back tasks (one ends exactly when the next begins) are not flagged |
| `test_detect_conflicts_invalid_time_format_produces_warning` | A bad time string produces a `"Warning"` message instead of crashing |
| `test_completing_weekly_task_creates_next_occurrence_in_seven_days` | Completing a `"weekly"` task queues a copy due 7 days from today |
| `test_completing_once_task_does_not_create_next_occurrence` | A `"once"` task is never re-queued after completion |
| `test_fit_tasks_zero_available_time_schedules_nothing` | Owner with 0 minutes available gets an empty schedule |
| `test_fit_tasks_exact_time_fit_includes_task` | A task whose duration exactly equals available time is included |
| `test_fit_tasks_skips_tasks_that_dont_fit` | A large task that won't fit is skipped; smaller lower-priority tasks still get in |
| `test_fit_tasks_excludes_completed_tasks` | Already-completed tasks never appear in the scheduled output |
| `test_filter_tasks_completed_false_returns_only_pending` | `filter_tasks(completed=False)` returns only pending tasks |
| `test_filter_tasks_completed_true_returns_only_done` | `filter_tasks(completed=True)` returns only completed tasks |
| `test_filter_tasks_by_pet_name_returns_only_that_pets_tasks` | `filter_tasks(pet_name=...)` scopes results to one pet |
| `test_filter_tasks_unknown_pet_name_returns_empty` | An unknown pet name returns an empty list |
| `test_filter_tasks_no_args_returns_all` | Calling `filter_tasks()` with no arguments returns every task |

### Confidence Level: ⭐⭐⭐⭐ (4 / 5)

All 19 tests pass. The suite now covers every major subsystem:

- **Priority sorting** — correct order regardless of insertion sequence
- **Recurrence** — `daily`, `weekly`, and `once` frequencies all verified
- **Conflict detection** — same-time, overlapping, sequential (no conflict), and invalid format cases
- **Greedy scheduler** — zero budget, exact fit, tasks too large to fit, completed tasks excluded
- **Filtering** — all four combinations of `completed` and `pet_name` arguments

One star is held back because the Streamlit UI layer (`app.py`) and plan formatting (`explain_plan`) have no automated tests — those paths can only be verified manually through the browser.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
