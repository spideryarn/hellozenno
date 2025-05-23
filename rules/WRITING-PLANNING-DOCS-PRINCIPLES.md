# Project Management Practices

This is a guide for writing planning/project management `.md` files, e.g. `planning/yyMMdd_complex_project.md`.

Aim to keep these concise, and only include stuff explicitly agreed with the user.

If you're starting the doc from scratch, store it in `planning/`, and first ask the user questions about their project requirements to clarify key decisions. (Use MCP or run `date +"%y%m%d"` command first to get the current date for naming the file)

Update this doc regularly to keep the actions up-to-date. When you change it, make minimal, focused changes, based on new user input.


## Document structure

### Goal, context

- Clear problem/goal statement(s) at top, plus enough context/background to pick up where we left off
- If the goal is complex, break things down in detail about the desired behaviour.

### Principles, key decisions

- Include any specific principles/approaches or decisions that have been explicitly agreed with the user (over and above existing Cursor rules, project examples, best practices, etc).
- As you get new information from the user, update this doc so it's always up-to-date.


### Useful references

- Include a list of highly relevant documentation, files, functions, webpages, etc.
- Provide a 1-sentence summary for each, emphasising what's useful/relevant about it, directing attention to the most important part, and perhaps a HIGH/MEDIUM/LOW priority for how essential it is to read for this project.


### Actions

- Break into lots of stages. Start with a really simple working v1, and gradually layer in complexity, ending each stage with passing tests and working code.
- Order the actions in the order that they should be tackled
- Don't number the stages, so that it's easier to move them around without having to renumber everything
- Update task status as we go along
- Include subtasks with clear acceptance criteria
- Refer concretely to specific files/functions, so it's clear exactly what needs to be done
- Explicitly add tasks for writing automated tests, usually before writing code. (Perhaps one or two end-to-end tests first, then gradually adding more detailed tests as complexity grows). Explicitly add tasks for running the automated tests before ending each stage. see `docs/FRONTEND_TESTING.md`
- If there are actions that the user needs to do, add those in too, so we can track progress and remind the user.
- Ask the user whether we should have an early action to create a `yyMMdd_complex_project` Git branch (and move over any changes), and a final action to merge that back into `main`.


Example action:

- [ ] This is a top-level action description line
  - [ ] It can have sub-points that get ticked off
  - [x] This one has already been finished


# Appendix

Add any other important context here, e.g.
- example data
- other information that should be capture but doesn't fit neatly in the above sections
