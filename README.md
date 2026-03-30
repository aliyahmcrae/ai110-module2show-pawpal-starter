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
