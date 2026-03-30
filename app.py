from pawpal_system import Owner, Pet, Task, Schedule, Priority
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ─── Session state init ───────────────────────────────────────────────────────
# Owner and Schedule are created once and persist across re-runs.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_time=60)

if "schedule" not in st.session_state:
    st.session_state.schedule = Schedule(owner=st.session_state.owner)

owner: Owner = st.session_state.owner
schedule: Schedule = st.session_state.schedule

# ─── Owner setup ─────────────────────────────────────────────────────────────
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value=owner.name or "Jordan")
with col2:
    available_time = st.number_input("Available time (minutes)", min_value=1, max_value=480, value=owner.available_time)

if st.button("Save owner"):
    owner.name = owner_name
    owner.update_availability(available_time)
    st.success(f"Saved: {owner.name}, {owner.available_time} min available")

st.divider()

# ─── Add a pet ────────────────────────────────────────────────────────────────
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    pet_type = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=2)

special_needs = st.text_input("Special needs (optional)", value="")

if st.button("Add pet"):
    new_pet = Pet(
        name=pet_name,
        type=pet_type,
        age=pet_age,
        special_needs=special_needs if special_needs else None,
    )
    owner.add_pet(new_pet)         # <-- Pet.add_pet() stores it on the Owner
    st.success(f"Added {pet_name} to {owner.name}'s pets.")

if owner.pets:
    st.markdown("**Current pets:**")
    for pet in owner.pets:
        st.caption(pet.get_summary())  # <-- Pet.get_summary() drives the display

st.divider()

# ─── Add a task ──────────────────────────────────────────────────────────────
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_name = st.text_input("Task name", value="Morning walk")
    with col2:
        task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        task_priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"], index=0)

    task_constraint = st.text_input("Time constraint (optional, e.g. 8am)", value="")
    task_frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add task"):
        new_task = Task(
            name=task_name,
            duration=task_duration,
            priority=Priority[task_priority],   # "HIGH" -> Priority.HIGH
            frequency=task_frequency,
            time_constraint=task_constraint if task_constraint else None,
        )
        selected_pet.add_task(new_task)         # <-- Pet.add_task() appends to pet.tasks
        st.success(f"Added '{task_name}' to {selected_pet.name}.")

    if any(p.tasks for p in owner.pets):
        st.markdown("**Current tasks by pet:**")
        for pet in owner.pets:
            if pet.tasks:
                st.markdown(f"*{pet.name}*")
                rows = [
                    {"Task": t.name, "Duration": t.duration, "Priority": t.priority.name, "Frequency": t.frequency}
                    for t in pet.tasks
                ]
                st.table(rows)

st.divider()

# ─── Generate schedule ────────────────────────────────────────────────────────
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not owner.pets or not owner.get_all_tasks():
        st.warning("Add at least one pet and one task first.")
    elif not owner.name:
        st.warning("Save an owner name before generating a plan.")
    else:
        schedule.generate_plan()               # <-- Schedule.generate_plan() builds the plan
        st.code(schedule.generated_plan, language=None)
