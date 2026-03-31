# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler goes beyond a simple task list with the following features:

**Priority-first selection with duration tiebreaking**
Tasks are selected greedily in priority order (high → medium → low). When two tasks share the same priority, the shorter one is scheduled first to fit more tasks into the available time budget.

**Time-slot ordering (`preferred_time`)**
Each task can be assigned a preferred time in `HH:MM` format. After selection, the final plan is sorted chronologically using `datetime.strptime` so the daily schedule flows naturally from morning to evening. Tasks with no preferred time are placed at the end.

**Shared time budget across pets**
The owner's `available_minutes` is a single daily pool shared across all pets. Time used scheduling one pet is deducted before the next pet is scheduled.

**Conflict detection**
If two tasks for the same pet are scheduled at the same `preferred_time`, the scheduler prints a warning message without crashing. Conflicts are stored in `scheduler.conflicts` and displayed in the output.

**Recurring tasks**
Tasks can be marked `frequency="daily"` or `frequency="weekly"`. When `pet.complete_task()` is called on a recurring task, a fresh next occurrence is automatically added to the pet's task list.

**Task filtering**
`owner.filter_tasks()` lets you query tasks across all pets by completion status, pet name, or both — for example, all incomplete tasks for a specific pet.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Run the tests

```bash
python -m pytest
```

### What the tests cover

| Area | What is verified |
|---|---|
| **Sorting correctness** | Tasks with `preferred_time` are returned in chronological order (e.g., `08:00` → `13:30` → `18:00`). Tasks with no preferred time sort to the end. |
| **Recurrence logic** | Marking a `frequency="daily"` task complete automatically appends a fresh, incomplete next occurrence to the pet's task list. The original task is marked `completed=True` and the new one starts as `completed=False` with the same title and frequency. |
| **Conflict detection** | The scheduler flags duplicate `preferred_time` slots with a `WARNING:` message stored in `scheduler.conflicts`. Tasks with no preferred time do not produce false positives. |
| **Priority scheduling** | High-priority tasks are selected before lower-priority ones. When priorities tie, the shorter task is preferred to maximize the number of tasks that fit within the time budget. |
| **Time budget enforcement** | Tasks that exceed the remaining available minutes are moved to `skipped_tasks`. Re-running `generate_plan()` after changing available time resets all state correctly. |
| **Owner task filtering** | `filter_tasks()` correctly filters by completion status, pet name (case-insensitive), or both combined. |

### Confidence Level

**4 / 5 stars**

The core scheduling behaviors — priority selection, time-slot sorting, conflict detection, and recurring task generation — are each covered by multiple focused tests, including edge cases like ties, zero available time, and tasks with no preferred time. One star is withheld because conflict detection only catches exact-time matches (`"08:00" == "08:00"`) and does not detect overlapping time windows (e.g., a 30-min task at `08:00` overlapping a task at `08:15"`), leaving a real-world scheduling gap untested.
