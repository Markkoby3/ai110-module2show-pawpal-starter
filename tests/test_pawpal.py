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
        assert set(d.keys()) == {"title", "duration_minutes", "priority", "category", "preferred_time", "is_scheduled"}

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
