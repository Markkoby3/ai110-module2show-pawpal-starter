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

The scheduler uses a greedy algorithm: it processes tasks in priority + duration order and accepts each one if it fits in the remaining time, skipping it otherwise. This is fast and simple but it is not globally optimal. For example, two short medium-priority tasks might together use less time and deliver more value than one long high-priority task, but the greedy approach will always schedule the high-priority task first.

This tradeoff is reasonable for a pet care context because priority reflects genuine importance — a dog's medication should not be skipped in favor of fitting in more enrichment activities. The greedy approach also produces predictable, easy-to-explain output, which matters for the reasoning display. A true knapsack optimization would be harder to explain to a non-technical user.

Two additional design decisions made during review:

- `get_plan()` and `explain()` now raise a `RuntimeError` if called before `generate_plan()`. Previously they silently returned empty results, which would have been a hard-to-debug failure.
- The `Scheduler` now validates that the pet passed in actually belongs to the owner via a check against `owner.pets`. This enforces the intended object relationship and prevents scheduling a pet under the wrong owner's time budget.

`preferred_time` on `CareTask` is stored but not yet used by the scheduler. It is reserved for a future enhancement where tasks would be assigned to morning, afternoon, or evening slots rather than just an ordered list.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
