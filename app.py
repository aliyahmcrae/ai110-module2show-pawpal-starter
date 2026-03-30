import re
from pawpal_system import Owner, Pet, Task, Schedule, Priority
import streamlit as st

PRIORITY_BADGE = {
    "HIGH":   "🔴 HIGH",
    "MEDIUM": "🟡 MEDIUM",
    "LOW":    "🟢 LOW",
}

def _render_conflicts(conflicts: list[str]) -> None:
    """Display conflict warnings in a structured, pet-owner-friendly format."""
    # Pattern: "Conflict: [PetA] 'TaskA' (HH:MM, D min)  overlaps  [PetB] 'TaskB' (HH:MM, D min)"
    conflict_pattern = re.compile(
        r"Conflict: \[(.+?)\] '(.+?)' \((.+?), (\d+) min\)\s+overlaps\s+\[(.+?)\] '(.+?)' \((.+?), (\d+) min\)"
    )

    true_conflicts = [c for c in conflicts if c.startswith("Conflict")]
    format_warnings = [c for c in conflicts if c.startswith("Warning")]

    if true_conflicts:
        st.markdown("#### ⚠️ Scheduling Conflicts")
        st.caption("These tasks overlap — one pet may be left unattended. Adjust a start time to resolve.")

        for msg in true_conflicts:
            m = conflict_pattern.match(msg)
            if m:
                pet_a, task_a, time_a, dur_a, pet_b, task_b, time_b, dur_b = m.groups()
                with st.container(border=True):
                    col_a, mid, col_b = st.columns([5, 1, 5])
                    with col_a:
                        st.markdown(f"**{pet_a}** — {task_a}")
                        st.caption(f"🕐 {time_a} · {dur_a} min")
                    with mid:
                        st.markdown("<div style='text-align:center;padding-top:8px'>vs</div>",
                                    unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"**{pet_b}** — {task_b}")
                        st.caption(f"🕐 {time_b} · {dur_b} min")
                    st.warning(f"💡 Tip: reschedule one of these tasks so they don't overlap.", icon="💡")
            else:
                # Fallback if the string doesn't match the expected pattern
                st.warning(msg)

    if format_warnings:
        with st.expander("⚠️ Time format issues"):
            for w in format_warnings:
                st.info(w)

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

    task_constraint = st.text_input("Time constraint (optional, HH:MM e.g. 08:30)", value="")
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
        st.markdown("**Current tasks (sorted by priority):**")

        # Summary metrics
        all_tasks = owner.get_all_tasks()
        pending_count = sum(1 for t in all_tasks if not t.completed)
        conflict_count = sum(1 for c in schedule.detect_conflicts() if c.startswith("Conflict"))
        m1, m2, m3 = st.columns(3)
        m1.metric("Total tasks", len(all_tasks))
        m2.metric("Pending", pending_count)
        m3.metric("Conflicts", conflict_count, delta=None if conflict_count == 0 else "⚠️", delta_color="inverse")

        # Filter control — drives schedule.filter_tasks()
        filter_choice = st.radio(
            "Show", ["All", "Pending only", "Completed only"], horizontal=True
        )
        completed_filter = None if filter_choice == "All" else filter_choice == "Completed only"
        filtered = schedule.filter_tasks(completed=completed_filter)

        if not filtered:
            st.info("No tasks match that filter.")
        else:
            task_to_pet = {id(t): pet.name for pet in owner.pets for t in pet.tasks}
            sorted_filtered = sorted(filtered, key=lambda t: t.priority.value, reverse=True)
            rows = [
                {
                    "Pet": task_to_pet.get(id(t), "—"),
                    "Task": t.name,
                    "Priority": PRIORITY_BADGE[t.priority.name],
                    "Duration (min)": t.duration,
                    "Frequency": t.frequency,
                    "Time": t.time_constraint or "—",
                    "Done": "✓" if t.completed else "",
                }
                for t in sorted_filtered
            ]
            st.table(rows)

        # Conflict warnings — structured display via helper
        _render_conflicts(schedule.detect_conflicts())

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
