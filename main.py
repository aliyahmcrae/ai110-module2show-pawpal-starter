from pawpal_system import Pet, Task, Owner, Schedule, Priority

# --- Pets ---
buddy = Pet(name="Buddy", type="Dog", age=3)
luna = Pet(name="Luna", type="Cat", age=5, special_needs="Hyperthyroidism medication")

# --- Tasks for Buddy ---
buddy.add_task(Task("Morning walk",      duration=30, priority=Priority.HIGH,   frequency="daily"))
buddy.add_task(Task("Feed breakfast",    duration=10, priority=Priority.HIGH,   frequency="daily"))
buddy.add_task(Task("Grooming session",  duration=45, priority=Priority.MEDIUM, frequency="weekly"))

# --- Tasks for Luna ---
luna.add_task(Task("Administer medication", duration=5,  priority=Priority.HIGH,   frequency="daily",  time_constraint="8am"))
luna.add_task(Task("Clean litter box",      duration=10, priority=Priority.MEDIUM, frequency="daily"))
luna.add_task(Task("Playtime",              duration=20, priority=Priority.LOW,    frequency="daily"))

# --- Owner ---
owner = Owner(name="Alex", available_time=60)
owner.add_pet(buddy)
owner.add_pet(luna)

# --- Schedule ---
schedule = Schedule(owner=owner)
owner.schedule = schedule

# --- Run ---
print("=== Pet Summaries ===")
for pet in owner.pets:
    print(pet.get_summary())

print("\n=== All Tasks (unsorted) ===")
for task in owner.get_all_tasks():
    print(f"  {task.name} | {task.priority.name} | {task.duration} min")

print("\n=== Sorted by Priority ===")
for task in schedule.sort_tasks_by_priority():
    print(f"  {task.name} | {task.priority.name} | {task.duration} min")

print("\n=== Generated Plan ===")
schedule.generate_plan()
print(schedule.generated_plan)
