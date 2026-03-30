from pawpal_system import Pet, Task, Owner, Schedule, Priority

# --- Pets ---
buddy = Pet(name="Buddy", type="Dog", age=3)
luna = Pet(name="Luna", type="Cat", age=5, special_needs="Hyperthyroidism medication")

# --- Tasks for Buddy (added out of order by time) ---
buddy.add_task(Task("Evening walk",      duration=30, priority=Priority.MEDIUM, frequency="daily",  time_constraint="18:00"))
buddy.add_task(Task("Feed breakfast",    duration=10, priority=Priority.HIGH,   frequency="daily",  time_constraint="07:30"))
buddy.add_task(Task("Grooming session",  duration=45, priority=Priority.MEDIUM, frequency="weekly"))
buddy.add_task(Task("Morning walk",      duration=30, priority=Priority.HIGH,   frequency="daily",  time_constraint="08:00"))
buddy.add_task(Task("Feed dinner",       duration=10, priority=Priority.HIGH,   frequency="daily",  time_constraint="17:00"))

# --- Tasks for Luna (added out of order by time) ---
luna.add_task(Task("Playtime",              duration=20, priority=Priority.LOW,    frequency="daily",  time_constraint="15:00"))
luna.add_task(Task("Administer medication", duration=5,  priority=Priority.HIGH,   frequency="daily",  time_constraint="08:00"))
luna.add_task(Task("Clean litter box",      duration=10, priority=Priority.MEDIUM, frequency="daily",  time_constraint="09:30"))

# Mark one task complete to demo the completed filter (no recurrence — uses mark_complete directly)
buddy.tasks[0].mark_complete()   # Evening walk -> completed, no recurrence check

# --- Owner ---
owner = Owner(name="Alex", available_time=90)
owner.add_pet(buddy)
owner.add_pet(luna)

# --- Schedule ---
schedule = Schedule(owner=owner)
owner.schedule = schedule

# --- Pet summaries ---
print("=== Pet Summaries ===")
for pet in owner.pets:
    print(pet.get_summary())

# --- All tasks as added (unsorted) ---
print("\n=== All Tasks (unsorted, as added) ===")
for task in owner.get_all_tasks():
    status = "done" if task.completed else "pending"
    print(f"  {task.name:<26} | {task.priority.name:<6} | {task.time_constraint or 'no time'} | {status}")

# --- Sorted by priority ---
print("\n=== Sorted by Priority (high → low) ===")
for task in schedule.sort_tasks_by_priority():
    print(f"  {task.name:<26} | {task.priority.name}")

# --- filter_tasks: pending only ---
print("\n=== filter_tasks(completed=False) — pending tasks only ===")
for task in schedule.filter_tasks(completed=False):
    print(f"  {task.name:<26} | {task.priority.name}")

# --- filter_tasks: completed only ---
print("\n=== filter_tasks(completed=True) — completed tasks only ===")
for task in schedule.filter_tasks(completed=True):
    print(f"  {task.name:<26} | {task.priority.name}")

# --- filter_tasks: by pet name ---
print("\n=== filter_tasks(pet_name='Luna') — Luna's tasks only ===")
for task in schedule.filter_tasks(pet_name="Luna"):
    print(f"  {task.name:<26} | {task.priority.name}")

# --- filter_tasks: pending tasks for a specific pet ---
print("\n=== filter_tasks(completed=False, pet_name='Buddy') — Buddy's pending tasks ===")
for task in schedule.filter_tasks(completed=False, pet_name="Buddy"):
    print(f"  {task.name:<26} | {task.priority.name}")

# --- Recurrence demo ---
print("\n=== Recurrence Demo ===")
print(f"Buddy tasks before completing 'Feed breakfast': {len(buddy.tasks)}")

next_task = buddy.complete_task("Feed breakfast")
print(f"Buddy tasks after  completing 'Feed breakfast': {len(buddy.tasks)}")
if next_task:
    print(f"  New occurrence: '{next_task.name}' | {next_task.frequency} | due={next_task.due_date} | completed={next_task.completed}")

# 'once' tasks should not recur
buddy.add_task(Task("Vet checkup", duration=60, priority=Priority.HIGH, frequency="once"))
print(f"\nBuddy tasks before completing 'Vet checkup': {len(buddy.tasks)}")
result = buddy.complete_task("Vet checkup")
print(f"Buddy tasks after  completing 'Vet checkup': {len(buddy.tasks)}")
print(f"  New occurrence: {result}  (None expected — 'once' tasks do not recur)")

# Weekly task recurrence
luna.add_task(Task("Flea treatment", duration=10, priority=Priority.HIGH, frequency="weekly", time_constraint="10:00"))
print(f"\nLuna tasks before completing 'Flea treatment': {len(luna.tasks)}")
luna.complete_task("Flea treatment")
new_flea = luna.tasks[-1]
print(f"Luna tasks after  completing 'Flea treatment': {len(luna.tasks)}")
print(f"  New occurrence: '{new_flea.name}' | {new_flea.frequency} | due={new_flea.due_date}")

# --- Conflict detection demo ---
print("\n=== Conflict Detection Demo ===")

# Same-pet conflict: Buddy's Morning walk starts 08:00 for 30 min (ends 08:30)
# Brush teeth starts 08:15 — squarely inside that window
buddy.add_task(Task("Brush teeth",   duration=10, priority=Priority.LOW,  frequency="daily", time_constraint="08:15"))

# Cross-pet conflict: Luna's Administer medication is also at 08:00
# It runs 5 min — overlaps the start of Buddy's Morning walk exactly

# Verify no conflicts exist before adding the clashing tasks
print("Before adding same-time tasks:")
warnings = schedule.detect_conflicts()
print(f"  Conflicts found: {len([w for w in warnings if w.startswith('Conflict')])}")

print("\nAfter adding 'Brush teeth' (08:15) and noting Luna's medication (08:00):")
warnings = schedule.detect_conflicts()
if warnings:
    for msg in warnings:
        print(f"  {msg}")
else:
    print("  No conflicts found.")

# --- Generated plan ---
print("\n=== Generated Plan ===")
schedule.generate_plan()
print(schedule.generated_plan)
