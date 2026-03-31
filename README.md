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

## Demo

### Running the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

### Walkthrough

**Step 1 — Enter owner & pet info**
Fill in the owner name, available time (minutes), pet name, and species, then click **Save owner & pet**. A confirmation banner confirms the session is ready.

**Step 2 — Add tasks**
For each care task, set a title, duration, priority, and category, then click **Add task**. The task table updates immediately. Add as many tasks as needed — try mixing priorities and setting different `preferred_time` values to see sorting and conflict detection in action.

**Step 3 — Generate the schedule**
Click **Generate schedule**. The app will:
- Display a summary (`X tasks scheduled, Y min total`)
- Show a conflict warning if any two tasks share the same preferred time
- Render the scheduled tasks sorted chronologically by preferred time
- List any skipped tasks with the extra minutes needed to fit them in
- Print the plain-language reasoning for every scheduling decision

### Example scenario

| Task | Duration | Priority | Preferred time |
|---|---|---|---|
| Morning meds | 5 min | high | 08:00 |
| Breakfast | 10 min | high | 08:00 |
| Afternoon walk | 20 min | medium | 13:30 |
| Evening grooming | 15 min | low | 18:00 |

With **45 minutes** available, the scheduler fits all four tasks, flags the `08:00` conflict between Meds and Breakfast, and displays them in chronological order.

With **30 minutes** available, Evening grooming is skipped (lowest priority, not enough time remaining) and the app tells you exactly how many extra minutes are needed.

### Screenshot

![PawPal App](Screenshot%202026-03-31%20001415.png)
## Features

### Greedy Priority Scheduling
Tasks are selected using a greedy algorithm that processes them in priority order — `high` before `medium` before `low`. Each task is added to the plan only if its duration fits within the owner's remaining time budget. Once the budget runs out, all remaining tasks are moved to a skipped list. This ensures the most important care never gets dropped because a lower-priority task consumed the available time first.

### Duration Tiebreaking
When two tasks share the same priority, the shorter one is scheduled first. This is implemented as a secondary sort key (`duration_minutes` ascending) inside `get_tasks_by_priority()`, maximizing the number of tasks that fit into the day without any manual configuration.

### Chronological Sorting by Preferred Time
After tasks are selected, the daily plan is reordered by `preferred_time` using `datetime.strptime` to parse `"HH:MM"` strings into comparable `time` objects. Tasks with no preferred time fall back to `"23:59"` so they always appear at the end. This gives the owner a schedule that flows naturally from morning to evening.

### Conflict Detection
Before finalizing the plan, `detect_conflicts()` scans all scheduled tasks for duplicate `preferred_time` values. Any collision produces a `WARNING:` message stored in `scheduler.conflicts` and surfaced in the UI. The scheduler does not crash or drop either task — it flags the issue and lets the owner decide what to adjust.

### Daily and Weekly Recurrence
Tasks can carry a `frequency` of `"daily"` or `"weekly"`. When `complete_task()` is called, `mark_complete()` sets the original task's `completed` flag to `True` and returns a brand-new `CareTask` clone with `completed=False` and the same title, duration, priority, and frequency. The clone is immediately appended to the pet's task list, so the next occurrence is always ready without any manual re-entry.

### Cross-Pet Task Filtering
`owner.filter_tasks()` traverses all pets and returns a flat list of tasks that match any combination of completion status and pet name. The pet name match is case-insensitive. This allows the owner to query things like "all incomplete tasks for Mochi" in a single call without looping through pets manually.

### Scheduling Explanations
After `generate_plan()` runs, `explain()` produces a plain-language summary of every decision: why each task was scheduled (priority level, duration) and why each was skipped (insufficient time). This reasoning is stored in `DailyPlan.reasoning` and displayed in the UI so the owner always knows why the plan looks the way it does.

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
