# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
My initial UML design focused on breaking the app into a few clear, simple classes that each handle a specific part of the system. I wanted to keep things organized so the logic would be easy to build and extend later.

I included four main classes: Pet, Task, Owner, and Schedule (Planner).

The Pet class is responsible for storing basic information about the pet, like name, type, age, and any special needs. It helps personalize the care plan based on the pet.
The Task class represents individual care activities like walks, feeding, or medication. It stores details like duration, priority, and any time constraints, and helps determine how important or urgent a task is.
The Owner class holds information about the user, mainly their available time and preferences. This allows the system to generate a schedule that actually fits their day.
The Schedule (Planner) class is the core of the system. It takes in tasks and the owner’s available time, then generates a daily plan by prioritizing tasks and fitting them into the schedule. It’s also responsible for explaining why the plan was created in a certain way.

Overall, my design separates data (Pet, Task, Owner) from logic (Schedule), which makes the system easier to manage and scale.

**b. Design changes**
Yes, my design did change during implementation as I refined how the classes should interact and made the system more structured.

One major change was replacing the priority attribute in the Task class from a simple string to a Priority Enum (LOW, MEDIUM, HIGH). This made the code more reliable and consistent, since it avoids errors from random string values and makes comparisons easier in methods like is_high_priority().

I also added a pet attribute to the Task class so that each task can be linked to a specific pet. This makes the system more realistic and scalable, especially if the user has multiple pets.

Another important change was updating the Schedule class to take in an Owner object instead of just an available_time integer. This better represents the relationship between the owner and the schedule and keeps related data grouped together.

Along with that, I changed available_time in the Schedule class into a @property that directly reads from the owner. This prevents duplicated data and ensures everything stays in sync automatically.

Finally, I cleaned up small things like removing unused imports to keep the code more organized.

Overall, these changes made the design more structured, realistic, and easier to maintain.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
