from pawpal_system import Owner, Pet, CareTask, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Tasks added OUT OF ORDER (time-wise) to prove sorting works ---
# NOTE: "Flea medication" and "Breakfast" both set to 08:00 → intentional conflict for Mochi
mochi.add_task(CareTask(title="Fetch in yard",   duration_minutes=20, priority="medium", category="enrichment", preferred_time="15:00", frequency="daily"))
mochi.add_task(CareTask(title="Flea medication", duration_minutes=5,  priority="high",   category="meds",       preferred_time="08:00", frequency="weekly"))
mochi.add_task(CareTask(title="Morning walk",    duration_minutes=30, priority="high",   category="walk",       preferred_time="07:00", frequency="daily"))
mochi.add_task(CareTask(title="Breakfast",       duration_minutes=10, priority="high",   category="feeding",    preferred_time="08:00", frequency="daily"))

# NOTE: "Laser toy play" and "Brush coat" both set to 11:00 → intentional conflict for Luna
luna.add_task(CareTask(title="Laser toy play",   duration_minutes=10, priority="medium", category="enrichment", preferred_time="11:00"))
luna.add_task(CareTask(title="Breakfast",        duration_minutes=10, priority="high",   category="feeding",    preferred_time="08:00", frequency="daily"))
luna.add_task(CareTask(title="Brush coat",       duration_minutes=15, priority="low",    category="grooming",   preferred_time="11:00", frequency="weekly"))

# Complete recurring tasks — next occurrences auto-created
mochi.complete_task("Morning walk")   # daily → spawns new task
luna.complete_task("Breakfast")       # daily → spawns new task
mochi.complete_task("Flea medication") # weekly → spawns new task

# --- Recurrence demo ---
print("=" * 45)
print("Recurrence check (after completing tasks):")
for pet in owner.pets:
    print(f"\n  {pet.name}:")
    for task in pet.tasks:
        status = "done" if task.completed else "pending"
        freq   = f"[{task.frequency}]" if task.frequency else ""
        print(f"    - {task.title:<20} {status:<8} {freq}")

# --- Schedule each pet, drawing from a shared time budget ---
print("\n" + "=" * 45)
print("           Today's Schedule")
print(f"      Total budget: {owner.available_minutes} min")
print("=" * 45)

plans = []
for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    plan = scheduler.get_plan()
    plans.append((pet, plan))
    owner.set_available_time(owner.available_minutes - scheduler.time_used)

    print(f"\n{pet.name} ({pet.species})  —  {plan.summary()}")
    if scheduler.conflicts:
        for warning in scheduler.conflicts:
            print(f"  [CONFLICT] {warning}")
    print(f"  {'Title':<20} {'Time':>6}  {'Duration':>10}  Priority")
    print(f"  {'-'*20} {'-'*6}  {'-'*10}  {'-'*8}")
    for task in plan.entries:
        t = task.preferred_time or "—"
        print(f"  {task.title:<20} {t:>6}  {task.duration_minutes:>8} min  {task.priority}")
    if plan.skipped:
        print("  Skipped:")
        for task in plan.skipped:
            print(f"    - {task.title}")

print(f"\n  Remaining budget: {owner.available_minutes} min")

# --- Reasoning ---
print("\n" + "=" * 45)
print("Reasoning:")
for pet, plan in plans:
    print(f"\n  {pet.name}: {plan.reasoning}")

# --- Filter: completed tasks across all pets ---
print("\n" + "=" * 45)
print("Completed tasks (all pets):")
for task in owner.filter_tasks(completed=True):
    print(f"  - {task.title}")

# --- Filter: incomplete tasks across all pets ---
print("\nIncomplete tasks (all pets):")
for task in owner.filter_tasks(completed=False):
    print(f"  - {task.title}")

# --- Filter: all tasks for Mochi only ---
print("\nAll tasks for Mochi:")
for task in owner.filter_tasks(pet_name="Mochi"):
    status = "done" if task.completed else "pending"
    print(f"  - {task.title:<20} [{status}]")

# --- Filter: incomplete tasks for Luna only ---
print("\nIncomplete tasks for Luna:")
for task in owner.filter_tasks(completed=False, pet_name="Luna"):
    print(f"  - {task.title}")

print("=" * 45)
