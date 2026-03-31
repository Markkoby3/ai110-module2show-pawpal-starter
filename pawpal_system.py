class Owner:
    def __init__(self, name, available_minutes, preferences=None):
        """Initialize an Owner with a name, daily time budget, and optional preferences."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets = []

    def add_pet(self, pet):
        """Add a Pet to this owner's list of pets."""
        self.pets.append(pet)

    def set_available_time(self, minutes):
        """Update the owner's total available time for pet care today."""
        self.available_minutes = minutes


class Pet:
    def __init__(self, name, species, age):
        """Initialize a Pet with a name, species, and age."""
        self.name = name
        self.species = species
        self.age = age
        self.tasks = []

    def add_task(self, task):
        """Add a CareTask to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name):
        """Remove a task from this pet's list by title."""
        self.tasks = [t for t in self.tasks if t.title != task_name]

    def get_tasks_by_priority(self):
        """Return tasks sorted by priority (high first), then by duration ascending to break ties."""
        # Primary sort: priority (high → medium → low)
        # Secondary sort: duration ascending so shorter tasks are preferred when priority ties,
        # maximizing the number of tasks that fit in the available time budget.
        order = {"high": 0, "medium": 1, "low": 2}
        return sorted(self.tasks, key=lambda t: (order.get(t.priority, 3), t.duration_minutes))


class CareTask:
    def __init__(self, title, duration_minutes, priority, category, preferred_time=None):
        """Initialize a CareTask with its title, duration, priority, category, and optional preferred time."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.preferred_time = preferred_time  # Reserved for future time-slot scheduling
        self.is_scheduled = False
        self.completed = False

    def to_dict(self):
        """Return a dictionary representation of this task."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "preferred_time": self.preferred_time,
            "is_scheduled": self.is_scheduled,
        }

    def is_high_priority(self):
        """Return True if this task's priority is high."""
        return self.priority == "high"

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True


class Scheduler:
    def __init__(self, owner, pet):
        """Initialize the Scheduler, validating that the pet belongs to the owner."""
        if pet not in owner.pets:
            raise ValueError(f"Pet '{pet.name}' does not belong to owner '{owner.name}'. Use owner.add_pet() first.")
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks = []
        self.skipped_tasks = []
        self._plan_generated = False

    def generate_plan(self):
        """Build the daily schedule by fitting tasks into the owner's time budget in priority order."""
        self.scheduled_tasks = []
        self.skipped_tasks = []
        self._plan_generated = True
        time_remaining = self.owner.available_minutes

        # Reset all task flags up front to avoid stale state from previous runs
        for task in self.pet.tasks:
            task.is_scheduled = False

        for task in self.pet.get_tasks_by_priority():
            if task.duration_minutes <= time_remaining:
                task.is_scheduled = True
                self.scheduled_tasks.append(task)
                time_remaining -= task.duration_minutes
            else:
                self.skipped_tasks.append(task)

    def get_plan(self):
        """Return a DailyPlan for today based on the last call to generate_plan()."""
        if not self._plan_generated:
            raise RuntimeError("Call generate_plan() before get_plan().")
        from datetime import date
        return DailyPlan(
            date=str(date.today()),
            scheduled_tasks=self.scheduled_tasks,
            skipped_tasks=self.skipped_tasks,
            reasoning=self.explain(),
        )

    def explain(self):
        """Return a plain-language explanation of why each task was scheduled or skipped."""
        if not self._plan_generated:
            raise RuntimeError("Call generate_plan() before explain().")
        lines = []
        for task in self.scheduled_tasks:
            lines.append(f"'{task.title}' was scheduled ({task.priority} priority, {task.duration_minutes} min).")
        for task in self.skipped_tasks:
            lines.append(f"'{task.title}' was skipped (not enough time remaining).")
        return " ".join(lines)


class DailyPlan:
    def __init__(self, date, scheduled_tasks, skipped_tasks, reasoning):
        """Initialize a DailyPlan with its date, task lists, and scheduling reasoning."""
        self.date = date
        self.entries = scheduled_tasks
        self.skipped = skipped_tasks
        self.total_duration = sum(t.duration_minutes for t in scheduled_tasks)
        self.reasoning = reasoning

    def display(self):
        """Print the daily plan and reasoning to the terminal."""
        print(f"Daily Plan for {self.date}")
        print(f"Total time: {self.total_duration} min")
        for task in self.entries:
            print(f"  - {task.title} ({task.duration_minutes} min, {task.priority})")
        if self.skipped:
            print("Skipped:")
            for task in self.skipped:
                print(f"  - {task.title}")
        print(f"Reasoning: {self.reasoning}")

    def to_dict(self):
        """Return the scheduled tasks as a list of dictionaries."""
        return [t.to_dict() for t in self.entries]

    def summary(self):
        """Return a one-line summary of the plan."""
        return f"{len(self.entries)} tasks scheduled, {self.total_duration} min total."
