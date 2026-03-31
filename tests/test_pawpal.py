import pytest
from pawpal_system import Owner, Pet, CareTask, Scheduler, DailyPlan


# --- Helpers ---

def make_owner(minutes=60):
    owner = Owner(name="Jordan", available_minutes=minutes)
    return owner

def make_pet(owner, name="Mochi", species="dog", age=3):
    pet = Pet(name=name, species=species, age=age)
    owner.add_pet(pet)
    return pet

def make_task(title="Walk", duration=20, priority="medium", category="walk"):
    return CareTask(title=title, duration_minutes=duration, priority=priority, category=category)


# --- Owner ---

class TestOwner:
    def test_add_pet(self):
        owner = make_owner()
        pet = make_pet(owner)
        assert pet in owner.pets

    def test_set_available_time(self):
        owner = make_owner(60)
        owner.set_available_time(90)
        assert owner.available_minutes == 90

    def test_multiple_pets(self):
        owner = make_owner()
        make_pet(owner, name="Mochi")
        make_pet(owner, name="Luna")
        assert len(owner.pets) == 2

    def test_filter_tasks_by_completion(self):
        owner = make_owner()
        pet = make_pet(owner)
        done = make_task(title="Done task")
        pending = make_task(title="Pending task")
        done.mark_complete()
        pet.add_task(done)
        pet.add_task(pending)
        assert owner.filter_tasks(completed=True)  == [done]
        assert owner.filter_tasks(completed=False) == [pending]
        assert len(owner.filter_tasks()) == 2

    def test_filter_tasks_by_pet_name(self):
        owner = make_owner()
        mochi = make_pet(owner, name="Mochi")
        luna  = make_pet(owner, name="Luna")
        mochi.add_task(make_task(title="Walk"))
        luna.add_task(make_task(title="Brush"))
        assert [t.title for t in owner.filter_tasks(pet_name="Mochi")] == ["Walk"]
        assert [t.title for t in owner.filter_tasks(pet_name="Luna")]  == ["Brush"]

    def test_filter_tasks_by_pet_name_case_insensitive(self):
        owner = make_owner()
        pet = make_pet(owner, name="Mochi")
        pet.add_task(make_task(title="Walk"))
        assert len(owner.filter_tasks(pet_name="mochi")) == 1
        assert len(owner.filter_tasks(pet_name="MOCHI")) == 1

    def test_filter_tasks_combined(self):
        owner = make_owner()
        mochi = make_pet(owner, name="Mochi")
        luna  = make_pet(owner, name="Luna")
        done = make_task(title="Done walk")
        done.mark_complete()
        mochi.add_task(done)
        mochi.add_task(make_task(title="Pending walk"))
        luna.add_task(make_task(title="Luna task"))
        result = owner.filter_tasks(completed=True, pet_name="Mochi")
        assert len(result) == 1
        assert result[0].title == "Done walk"


# --- Pet ---

class TestPet:
    def test_add_task(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = make_task()
        pet.add_task(task)
        assert task in pet.tasks

    def test_add_task_increases_count(self):
        owner = make_owner()
        pet = make_pet(owner)
        assert len(pet.tasks) == 0
        pet.add_task(make_task(title="Walk"))
        assert len(pet.tasks) == 1
        pet.add_task(make_task(title="Feed"))
        assert len(pet.tasks) == 2

    def test_remove_task(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = make_task(title="Walk")
        pet.add_task(task)
        pet.remove_task("Walk")
        assert task not in pet.tasks

    def test_complete_task_adds_next_occurrence(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(CareTask(title="Feed", duration_minutes=10, priority="high", category="feeding", frequency="daily"))
        assert len(pet.tasks) == 1
        pet.complete_task("Feed")
        assert len(pet.tasks) == 2
        assert pet.tasks[0].completed is True
        assert pet.tasks[1].completed is False

    def test_complete_task_no_recurrence_does_not_add(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(title="One-off"))
        pet.complete_task("One-off")
        assert len(pet.tasks) == 1

    def test_remove_nonexistent_task_does_not_raise(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.remove_task("Nonexistent")  # should not raise

    def test_get_tasks_by_priority_order(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(title="Low",    priority="low",    duration=10))
        pet.add_task(make_task(title="High",   priority="high",   duration=10))
        pet.add_task(make_task(title="Medium", priority="medium", duration=10))
        sorted_tasks = pet.get_tasks_by_priority()
        priorities = [t.priority for t in sorted_tasks]
        assert priorities == ["high", "medium", "low"]

    def test_get_tasks_by_priority_tiebreak_by_duration(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(title="Long high",  priority="high", duration=30))
        pet.add_task(make_task(title="Short high", priority="high", duration=5))
        sorted_tasks = pet.get_tasks_by_priority()
        assert sorted_tasks[0].title == "Short high"


# --- CareTask ---

class TestCareTask:
    def test_is_high_priority_true(self):
        task = make_task(priority="high")
        assert task.is_high_priority() is True

    def test_is_high_priority_false(self):
        task = make_task(priority="medium")
        assert task.is_high_priority() is False

    def test_to_dict_keys(self):
        task = make_task()
        d = task.to_dict()
        assert set(d.keys()) == {"title", "duration_minutes", "priority", "category", "preferred_time", "frequency", "is_scheduled", "completed"}

    def test_default_is_scheduled_false(self):
        task = make_task()
        assert task.is_scheduled is False

    def test_default_completed_false(self):
        task = make_task()
        assert task.completed is False

    def test_mark_complete_changes_status(self):
        task = make_task()
        task.mark_complete()
        assert task.completed is True

    def test_mark_complete_no_recurrence_returns_none(self):
        task = make_task()
        assert task.mark_complete() is None

    def test_mark_complete_daily_returns_new_task(self):
        task = CareTask(title="Feed", duration_minutes=10, priority="high", category="feeding", frequency="daily")
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task is not task
        assert next_task.completed is False
        assert next_task.frequency == "daily"
        assert next_task.title == "Feed"

    def test_mark_complete_weekly_returns_new_task(self):
        task = CareTask(title="Grooming", duration_minutes=20, priority="low", category="grooming", frequency="weekly")
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task.frequency == "weekly"
        assert next_task.completed is False

    def test_invalid_frequency_raises(self):
        with pytest.raises(ValueError):
            CareTask(title="Walk", duration_minutes=10, priority="high", category="walk", frequency="monthly")


# --- Scheduler ---

class TestScheduler:
    def test_scheduler_rejects_pet_not_owned(self):
        owner = make_owner()
        stray_pet = Pet(name="Stray", species="cat", age=1)
        with pytest.raises(ValueError):
            Scheduler(owner=owner, pet=stray_pet)

    def test_all_tasks_fit(self):
        owner = make_owner(minutes=60)
        pet = make_pet(owner)
        pet.add_task(make_task(title="Walk",   duration=20, priority="high"))
        pet.add_task(make_task(title="Feed",   duration=10, priority="high"))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        assert len(scheduler.scheduled_tasks) == 2
        assert len(scheduler.skipped_tasks) == 0

    def test_task_skipped_when_over_time(self):
        owner = make_owner(minutes=15)
        pet = make_pet(owner)
        pet.add_task(make_task(title="Long walk", duration=30, priority="high"))
        pet.add_task(make_task(title="Feed",      duration=10, priority="high"))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        titles = [t.title for t in scheduler.scheduled_tasks]
        assert "Feed" in titles
        assert "Long walk" not in titles

    def test_high_priority_scheduled_before_low(self):
        owner = make_owner(minutes=20)
        pet = make_pet(owner)
        pet.add_task(make_task(title="Low task",  duration=15, priority="low"))
        pet.add_task(make_task(title="High task", duration=15, priority="high"))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        assert scheduler.scheduled_tasks[0].title == "High task"
        assert scheduler.skipped_tasks[0].title == "Low task"

    def test_is_scheduled_flag_set(self):
        owner = make_owner(minutes=60)
        pet = make_pet(owner)
        task = make_task(duration=10)
        pet.add_task(task)
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        assert task.is_scheduled is True

    def test_is_scheduled_resets_on_rerun(self):
        owner = make_owner(minutes=60)
        pet = make_pet(owner)
        task = make_task(duration=10)
        pet.add_task(task)
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        owner.set_available_time(0)
        scheduler.generate_plan()
        assert task.is_scheduled is False

    def test_get_plan_before_generate_raises(self):
        owner = make_owner()
        pet = make_pet(owner)
        scheduler = Scheduler(owner=owner, pet=pet)
        with pytest.raises(RuntimeError):
            scheduler.get_plan()

    def test_explain_before_generate_raises(self):
        owner = make_owner()
        pet = make_pet(owner)
        scheduler = Scheduler(owner=owner, pet=pet)
        with pytest.raises(RuntimeError):
            scheduler.explain()

    def test_get_plan_returns_daily_plan(self):
        owner = make_owner(minutes=60)
        pet = make_pet(owner)
        pet.add_task(make_task())
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        plan = scheduler.get_plan()
        assert isinstance(plan, DailyPlan)

    def test_no_conflicts_when_times_are_unique(self):
        owner = make_owner(minutes=120)
        pet = make_pet(owner)
        pet.add_task(CareTask(title="Walk",      duration_minutes=20, priority="high",   category="walk",    preferred_time="07:00"))
        pet.add_task(CareTask(title="Breakfast",  duration_minutes=10, priority="high",   category="feeding", preferred_time="08:00"))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        assert scheduler.conflicts == []

    def test_conflict_detected_for_same_time(self):
        owner = make_owner(minutes=120)
        pet = make_pet(owner)
        pet.add_task(CareTask(title="Meds",      duration_minutes=5,  priority="high",   category="meds",    preferred_time="08:00"))
        pet.add_task(CareTask(title="Breakfast",  duration_minutes=10, priority="high",   category="feeding", preferred_time="08:00"))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        assert len(scheduler.conflicts) == 1
        assert "08:00" in scheduler.conflicts[0]
        assert "WARNING" in scheduler.conflicts[0]

    def test_no_conflict_for_tasks_with_no_time(self):
        owner = make_owner(minutes=120)
        pet = make_pet(owner)
        pet.add_task(make_task(title="Task A", duration=10))
        pet.add_task(make_task(title="Task B", duration=10))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        assert scheduler.conflicts == []

    def test_sort_by_time_orders_slots(self):
        owner = make_owner(minutes=120)
        pet = make_pet(owner)
        pet.add_task(CareTask(title="Evening walk",  duration_minutes=20, priority="medium", category="walk",        preferred_time="18:00"))
        pet.add_task(CareTask(title="Morning meds",  duration_minutes=5,  priority="high",   category="meds",        preferred_time="08:00"))
        pet.add_task(CareTask(title="Afternoon play", duration_minutes=15, priority="medium", category="enrichment",  preferred_time="13:30"))
        pet.add_task(CareTask(title="Unset task",    duration_minutes=10, priority="low",    category="other"))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        times = [t.preferred_time for t in scheduler.scheduled_tasks]
        assert times == ["08:00", "13:30", "18:00", None]

    def test_zero_available_time_skips_all(self):
        owner = make_owner(minutes=0)
        pet = make_pet(owner)
        pet.add_task(make_task(duration=10))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        assert len(scheduler.scheduled_tasks) == 0
        assert len(scheduler.skipped_tasks) == 1


# --- DailyPlan ---

class TestDailyPlan:
    def _make_plan(self, minutes=60):
        owner = make_owner(minutes=minutes)
        pet = make_pet(owner)
        pet.add_task(make_task(title="Walk", duration=20, priority="high"))
        pet.add_task(make_task(title="Feed", duration=10, priority="high"))
        scheduler = Scheduler(owner=owner, pet=pet)
        scheduler.generate_plan()
        return scheduler.get_plan()

    def test_total_duration(self):
        plan = self._make_plan()
        assert plan.total_duration == 30

    def test_summary_format(self):
        plan = self._make_plan()
        assert "tasks scheduled" in plan.summary()
        assert "min total" in plan.summary()

    def test_to_dict_returns_list(self):
        plan = self._make_plan()
        result = plan.to_dict()
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
