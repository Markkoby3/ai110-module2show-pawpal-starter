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
