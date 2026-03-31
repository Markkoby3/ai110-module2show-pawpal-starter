import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- Owner + Pet Setup ---
st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=60)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save owner & pet"):
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    pet = Pet(name=pet_name, species=species, age=0)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.tasks = []
    st.success(f"Saved! Owner: {owner.name} | Pet: {pet.name} ({pet.species}) | Time budget: {owner.available_minutes} min")

if st.session_state.owner:
    st.caption(
        f"Current session — Owner: **{st.session_state.owner.name}** | "
        f"Pet: **{st.session_state.pet.name}** | "
        f"Time budget: **{st.session_state.owner.available_minutes} min**"
    )

st.divider()

# --- Task Management ---
st.subheader("Tasks")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"])

if st.button("Add task"):
    if st.session_state.pet is None:
        st.warning("Save your owner & pet info first.")
    else:
        task = CareTask(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
        )
        st.session_state.pet.add_task(task)
        st.session_state.tasks.append(task.to_dict())
        st.success(f"Added: {task_title}")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule Generation ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None or st.session_state.pet is None:
        st.warning("Save your owner & pet info first.")
    elif not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner, pet=st.session_state.pet)
        scheduler.generate_plan()
        plan = scheduler.get_plan()

        st.success(plan.summary())

        st.markdown("### Scheduled Tasks")
        if plan.entries:
            st.table([t.to_dict() for t in plan.entries])
        else:
            st.info("No tasks could fit in the available time.")

        if plan.skipped:
            st.markdown("### Skipped Tasks")
            st.table([t.to_dict() for t in plan.skipped])

        st.markdown("### Reasoning")
        st.write(plan.reasoning)
