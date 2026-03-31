from pawpal_system import Owner, Pet, CareTask, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog", age=3)
luna = Pet(name="Luna", species="cat", age=5)

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Tasks for Mochi ---
mochi.add_task(CareTask(title="Morning walk",   duration_minutes=30, priority="high",   category="walk"))
mochi.add_task(CareTask(title="Breakfast",      duration_minutes=10, priority="high",   category="feeding"))
mochi.add_task(CareTask(title="Flea medication",duration_minutes=5,  priority="high",   category="meds"))
mochi.add_task(CareTask(title="Fetch in yard",  duration_minutes=20, priority="medium", category="enrichment"))

# --- Tasks for Luna ---
luna.add_task(CareTask(title="Breakfast",       duration_minutes=10, priority="high",   category="feeding"))
luna.add_task(CareTask(title="Brush coat",      duration_minutes=15, priority="low",    category="grooming"))
luna.add_task(CareTask(title="Laser toy play",  duration_minutes=10, priority="medium", category="enrichment"))

# --- Schedule each pet and print ---
print("=" * 40)
print("        Today's Schedule")
print("=" * 40)

for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    plan = scheduler.get_plan()

    print(f"\n{pet.name} ({pet.species})")
    print(f"  {plan.summary()}")
    print("  Scheduled tasks:")
    for task in plan.entries:
        print(f"    - {task.title:<20} {task.duration_minutes} min  [{task.priority}]")
    if plan.skipped:
        print("  Skipped (not enough time):")
        for task in plan.skipped:
            print(f"    - {task.title:<20} {task.duration_minutes} min  [{task.priority}]")

print("\n" + "=" * 40)
print("Reasoning:")
for pet in owner.pets:
    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    print(f"\n  {pet.name}: {scheduler.explain()}")
print("=" * 40)
