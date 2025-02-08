# Project Management Practices

This is a guide for writing planning/project management `.md` files.


## Document structure

1. **Goal Statement**
   - Clear problem/goal at top, with enough context/description to pick up where we left off
   - Example: "Migrate phrases from JSON to relational DB to enable better searching and management"
   - If the goal is complex, break things down in detail about the desired behaviour.

2. **Progress/next steps**
   - Most immediate or important tasks first
   - Label the beginning of each action section with TODO, DONE, SKIP, etc
   - Include subtasks with clear acceptance criteria
   - Refer to specific files/functions to so it's clear exactly what needs to be done
   - Update the tasks & status when we make changes
   - When updating, make minimal changes

## Key Tactics Used

- Prioritisation
   - Start with core functionality, the simplest version
   - Implement features end-to-end (DB → API → UI), and complete one slice before starting next

- Testing
   - Write tests before implementation
   - Think about whether to test at multiple levels (smoke, unit, integration, frontend) - see `planning_docs/FRONTEND_TESTING.md`
   - Discuss edge case tests
   - Every so often run all the tests, but focus on running & fixing a small number of tests at a time for speed of iteration with `-x --lf`

- Next Steps
   - Order the tasks in the order you want to do them, so the next task is always the topmost task that hasn't been done
   - Break large tasks into smaller pieces
