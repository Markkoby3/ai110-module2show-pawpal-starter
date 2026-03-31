# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

To start the project, I read through the README carefully to understand the full scope of PawPal+. The app needs to help a busy pet owner stay consistent with pet care by tracking tasks (walks, feeding, meds, enrichment, grooming, etc.), accounting for constraints like available time and priority, and producing a daily schedule with an explanation of why that plan was chosen.

From those requirements, I identified the following key responsibilities the system needs to handle:

- Collecting basic owner and pet information from the user
- Allowing the user to add and edit care tasks, each with at least a duration and priority
- Running a scheduling algorithm that generates a daily plan based on constraints and priorities
- Displaying the plan clearly and explaining the reasoning behind it
- Covering edge cases and validating the scheduling logic through tests

The suggested workflow from the README guided the design process: start with a UML diagram to map out classes and relationships, then convert that into Python stubs, implement the scheduling logic incrementally, write tests, and finally wire everything into the Streamlit UI in `app.py`.

After reviewing the README and the starter `app.py`, I brainstormed the main objects the system needs. For each object I identified what information it must hold (attributes) and what actions it can perform (methods):

**Owner** holds the owner's name, their total available time for pet care that day, and any preferences (such as preferring morning walks). It can associate a pet, update available time, and store preference settings.

**Pet** holds the pet's name, species, age, and a list of assigned care tasks. It can add or remove tasks and return tasks sorted by priority.

**CareTask** holds a title, duration in minutes, priority level (low/medium/high), category (walk, feeding, meds, grooming, enrichment, etc.), an optional preferred time of day, and a flag for whether it was scheduled. It can serialize itself to a dictionary and check whether it is high priority.

**Scheduler** holds a reference to the Pet and Owner being planned for, as well as two lists — the tasks that fit within the constraints and the tasks that were skipped. It can run the core scheduling algorithm (sort by priority, fill the time budget, assign time slots), return the finished plan, and produce a plain-language explanation of why each task was included or left out.

**DailyPlan** holds the date, an ordered list of (time slot, task) entries, the total scheduled duration, and a reasoning string. It can format itself for display in Streamlit, serialize to a dictionary for table rendering, and produce a one-line summary.

The relationships between these objects are: an Owner has one or more Pets; a Pet has many CareTasks; the Scheduler takes an Owner and a Pet as input and produces a DailyPlan as output.

**b. Design changes**

Yes, several changes were made after reviewing the initial design for missing relationships and logic bottlenecks.

The most significant structural change was enforcing the `Owner` → `Pet` relationship inside the `Scheduler`. In the original design, the `Scheduler` accepted an `Owner` and a `Pet` as separate arguments with no validation between them. This meant a pet could be scheduled under the wrong owner's time budget without any error. The fix was to require the pet to already exist in `owner.pets` before the `Scheduler` is created, raising a `ValueError` otherwise. This makes the intended relationship between objects explicit and enforced at runtime.

The secondary sort in `get_tasks_by_priority()` was also added during this phase. The original version sorted only by priority level, leaving tasks within the same priority in arbitrary insertion order. This could cause a single long task to consume all remaining time and block several shorter tasks of equal priority. Adding duration as a tiebreaker — shortest first — makes the scheduler fit more tasks into the available time without changing the priority logic.

Two defensive guards were added to `Scheduler`: `get_plan()` and `explain()` now raise a `RuntimeError` if called before `generate_plan()`. The original design silently returned empty results in that case, which would have been difficult to debug in the UI.

Finally, the `is_scheduled` flag reset was moved to before the priority-sorted loop rather than inside it. The original reset happened as each task was processed, which meant if the loop structure ever changed, previously scheduled tasks could retain a stale `True` flag. Resetting all flags up front in a separate pass makes the behavior consistent regardless of loop order.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two main constraints: the owner's total available time for the day (`available_minutes`) and each task's priority level (high, medium, or low). Tasks are sorted by priority first so that the most important care tasks — medications, feeding — are always attempted before lower-priority ones. Within the same priority level, tasks are sorted by duration ascending, so shorter tasks are scheduled first. This secondary sort maximizes the number of tasks that fit within the time budget when tasks are tied on priority.

Time was chosen as the primary hard constraint because it is a fixed real-world limit. Priority was chosen as the primary ordering criterion because some tasks (like medication) are non-negotiable regardless of how long they take.

**b. Tradeoffs**

The most significant tradeoff is that the scheduler separates *which tasks get scheduled* from *when they appear in the day*. Priority and duration determine whether a task makes the plan at all; `preferred_time` only controls the display order after selection is already done. This means a low-priority task set to `"07:00"` could end up at the top of the printed schedule even though it was nearly cut — while a high-priority task with no preferred time is shown at the bottom.

This tradeoff was a deliberate design choice. Combining selection and time-slot ordering into one pass would require comparing tasks across two dimensions simultaneously, making the algorithm harder to explain and test. Keeping them as two separate steps — greedy selection by priority, then `sort_by_time()` on the result — means each step has a single clear responsibility. The reasoning output stays readable because it only explains why a task was included or skipped, not why it appears at a particular time.

The cost is that `preferred_time` does not influence scheduling decisions at all. A task marked `"07:00"` has no advantage over one marked `"18:00"` when it comes to fitting inside the time budget. For a pet care app this is acceptable — the owner sets priority to reflect importance, and preferred time is just a convenience hint for planning the day. If time-of-day constraints ever became strict requirements (e.g. medication must be given before 9am), the selection step would need to be reworked to factor in time slots, which is a known future limitation.

Two additional design decisions made during review:

- `get_plan()` and `explain()` now raise a `RuntimeError` if called before `generate_plan()`. Previously they silently returned empty results, which would have been a hard-to-debug failure.
- The `Scheduler` now validates that the pet passed in actually belongs to the owner via a check against `owner.pets`. This enforces the intended object relationship and prevents scheduling a pet under the wrong owner's time budget.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used across every phase of the project, but in different ways depending on the task.

During the design phase, AI was used for brainstorming — specifically to pressure-test the initial UML. I described the five classes and their relationships and asked what was missing. This surfaced the need for `is_scheduled` and `completed` as separate flags on `CareTask`, and the importance of validating that a pet belongs to the owner before the `Scheduler` is constructed.

During implementation, the most useful prompts were narrow and specific: "What should `mark_complete()` return when frequency is None?" and "How should `sort_by_time()` handle a task with no preferred_time without crashing?" These produced focused answers that slotted directly into the existing class structure rather than suggesting rewrites.

During testing, AI helped identify edge cases that were easy to overlook — particularly the `is_scheduled` reset bug (stale flags surviving a second call to `generate_plan()`) and the case where `get_plan()` is called before `generate_plan()`. Both became explicit tests.

During the UI phase, AI helped translate scheduler outputs into Streamlit components — specifically deciding which component (`st.warning`, `st.caption`, `st.table`) fit each type of information.

**b. Judgment and verification — AI strategy with VS Code Copilot**

*Which Copilot features were most effective?*

Inline completions were most useful for boilerplate — filling in `to_dict()` key lists, writing `__init__` parameter assignments, and generating the `pytest` fixture helpers (`make_owner`, `make_pet`, `make_task`). These are mechanical and low-risk, so accepting completions directly saved time without introducing design risk.

The chat panel was more valuable for reasoning through design questions, especially when a suggestion needed to be evaluated against the existing class structure before accepting it.

*One AI suggestion that was rejected or modified:*

When implementing `detect_conflicts()`, Copilot suggested detecting conflicts inside `generate_plan()` by comparing every pair of tasks using a nested loop — O(n²) — and flagging any pair whose preferred times were within 30 minutes of each other as a potential conflict. This was rejected for two reasons. First, the 30-minute overlap window was an assumption the system had no basis to make — preferred time is a hint, not a strict slot, so two tasks at `08:00` and `08:20` might be perfectly fine. Second, adding overlap logic would have required `detect_conflicts()` to know about task durations, giving it two responsibilities instead of one. The final implementation uses exact-match detection only (`task.preferred_time in seen`), which is simpler, testable in isolation, and honest about what the system actually enforces.

*How did using separate chat sessions for different phases help?*

Keeping design, implementation, testing, and UI work in separate sessions prevented context bleed. When writing tests, the session only contained the finalized class contracts — there was no earlier brainstorming suggesting alternative method signatures that might have confused the suggestions. Each session started with a clear scope, which made AI suggestions more predictable and easier to evaluate. It also made it easier to reject a suggestion: if a suggestion didn't fit the scope of the current session's phase, that was a clear signal to move on.

*What it means to be the "lead architect" when using powerful AI tools:*

The most important lesson was that AI is very good at filling in the inside of a box but cannot define the box itself. Every useful AI contribution in this project happened after a design decision was already made: what the class is called, what it is responsible for, what its method signatures are. When AI was asked open-ended questions ("how should I design the scheduler?"), the suggestions were generic and required significant filtering. When it was asked narrow questions ("given this method signature, what should the body do?"), the suggestions were directly usable. Being the lead architect meant making all the structural decisions first and using AI only to execute them — not to make them.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers six behavioral areas:

1. **Sorting correctness** — tasks with `preferred_time` are returned in chronological order; tasks with no preferred time sort to the end. This matters because the daily plan is only useful if it reflects the actual order of the day.

2. **Recurrence logic** — completing a `frequency="daily"` task appends a fresh incomplete copy to `pet.tasks`. This was tested at both the `CareTask` level (`mark_complete()` returns the right object) and the `Pet` level (`complete_task()` correctly appends it), because both layers can fail independently.

3. **Conflict detection** — tasks sharing a `preferred_time` produce a `WARNING:` message in `scheduler.conflicts`; tasks with no preferred time produce no false positives. Testing the negative case (no false positives) was just as important as the positive case.

4. **Priority scheduling with tiebreaking** — high-priority tasks are always selected before low-priority ones; when priorities tie, the shorter task is scheduled first to maximize coverage.

5. **Time budget enforcement** — tasks that exceed remaining time are moved to `skipped_tasks`; re-running `generate_plan()` resets all state cleanly. The reset test caught a real bug during development where `is_scheduled` flags were not being cleared before a second run.

6. **Owner task filtering** — `filter_tasks()` correctly filters by completion status, pet name (case-insensitive), or both combined.

**b. Confidence**

Confidence level: **4 out of 5**.

The scheduler's core behaviors are each covered by multiple focused tests, including edge cases like zero available time, all-identical priorities, and tasks with no preferred time. The main gap is conflict detection: the current implementation only flags exact-time matches (`"08:00" == "08:00"`). It does not detect overlapping windows — a 30-minute task starting at `08:00` and a task starting at `08:15` would both be scheduled without any warning. If the project continued, that would be the first test to add, followed by tests for recurring tasks across a DST boundary and month-end recurrence edge cases.

---

## 5. Reflection

**a. What went well**

The separation of scheduling logic from display logic was the strongest design decision in the project. Because `Scheduler` stores its results in `scheduled_tasks`, `skipped_tasks`, and `conflicts` rather than printing them directly, the Streamlit UI could read each list independently and render it with the right component (`st.warning` for conflicts, `st.table` for tasks, `st.caption` for actionable hints). If the logic had been coupled to print statements or string output from the start, adding the UI would have required rewriting core methods rather than just reading their outputs. The same separation made testing straightforward — tests assert on list contents and object state, not on printed strings.

**b. What I would improve**

The conflict detection logic is the clearest candidate for improvement. The current exact-match approach is simple and testable but does not reflect real scheduling conflicts — two tasks at `"08:00"` and `"08:25"` can genuinely overlap if the first task takes 30 minutes. A reworked `detect_conflicts()` would compare task start times plus durations to find actual overlaps, not just identical time strings. This would require `preferred_time` to be parsed and stored as a `datetime.time` object rather than a raw string, which is a small change that would also make `sort_by_time()` simpler.

I would also add a `preferred_time` input field to the Streamlit task form. Currently the UI has no way to set preferred times — they can only be set in code — which means the conflict detection and chronological sorting features are invisible to a user running the app normally.

**c. Key takeaway**

The most important thing I learned is that AI tools amplify whatever decisions you have already made — good or bad. When the class responsibilities were clearly defined and the method signatures were settled, AI suggestions fit cleanly into the existing design and were easy to evaluate. When design questions were still open, AI suggestions added noise rather than clarity. The skill that mattered most in this project was not knowing how to prompt AI effectively — it was knowing when the design was solid enough to hand a piece of it to AI, and when it wasn't. That judgment belongs to the architect, not the tool.
