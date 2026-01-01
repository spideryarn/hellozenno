# Chief Engineer Workflow

A structured multi-phase workflow for tackling complex development tasks with research, planning, review, and implementation.

## When to Use

Use this workflow for:
- Complex features spanning multiple files/systems
- Architecture changes or significant refactors
- High-risk changes requiring careful review
- Tasks where understanding the problem space is crucial

## Workflow Phases

### Phase 1: Research

**Delegate to:** `@researcher` subagent

Gather information before engaging in discussion:
- Explore relevant codebase areas
- Search web for best practices, documentation, known issues
- Understand the problem space thoroughly
- Return synthesized findings

**Output:** Research summary with key findings, relevant code locations, and external references.

---

### Phase 2: Sounding Board Conversation

**Execute directly** (not delegated)

Engage in collaborative discussion with the user:
- Investigate the codebase and search the web as needed
- Ask questions to clarify requirements (max 2 at a time to avoid overload)
- Raise concerns and consider success criteria
- Suggest alternatives and weigh trade-offs
- Point out if you see a better way

**Goal:** Help the user think through the problem and make the best decision.

**Important:** Use extended thinking. Don't make changes yet.

---

### Phase 3: Planning

**Delegate to:** `@planner` subagent

Create a staged implementation plan:
- Break work into discrete, testable stages
- Document approach, risks, and dependencies
- Save plan to `docs/plans/YYMMDD_<task>.md`

**Output:** Planning document with staged implementation steps.

---

### Phase 4: Plan Review

**Review type:** Single (default) or Triple (for complex/high-risk)

**Single Review:**
- Delegate to `@reviewer-gpt5.2-high`

**Triple Review** (when specified or for high-risk changes):
- Delegate to ALL THREE reviewers in parallel:
  - `@reviewer-gpt5.2-high`
  - `@reviewer-gemini`
  - `@reviewer-opus`

Each reviewer returns:
- Confidence score (0-100%)
- Issues found (categorized as "must fix" vs "suggestions")
- Specific recommendations

**Proceed if:** All reviewers >= 80% confidence
**Refine if:** Any reviewer < 80% confidence (max 2 iterations, then ask user)

---

### Phase 5: User Review

Present to the user:
- Summary of planned approach
- Key decisions and trade-offs
- Risk assessment
- Estimated scope

**Requirement:** Get explicit user approval before implementation.

---

### Phase 6: Implementation

**Delegate to:** `@implementer` subagent (per stage)

For each stage in the plan:
1. Invoke implementer with stage instructions
2. Implementer updates planning doc with learnings
3. Run tests and verify stage completion

Continue until all stages complete.

---

### Phase 7: Implementation Review

**Review type:** Match Phase 4 configuration (single or triple)

**Single Review:**
- Delegate to `@reviewer-gpt5.2-high`

**Triple Review:**
- Delegate to all three reviewers in parallel

Each reviewer examines:
- Code quality and correctness
- Security implications
- Performance considerations
- Test coverage
- Adherence to plan

**Auto-proceed if:** ALL reviewers >= 80% confidence
**Refine if:** Any reviewer < 80% confidence (max 2 iterations, then ask user)

---

### Phase 8: Conclusion

Summarize and close:
- Summary of work completed
- Flag anything noteworthy:
  - Unusual decisions made
  - Technical debt introduced
  - Recommended follow-ups
  - Outstanding concerns
- Offer to commit changes

---

## Subagent Reference

| Subagent | Purpose | Model |
|----------|---------|-------|
| `@researcher` | Information gathering from codebase and web | inherit |
| `@planner` | Creates staged implementation plans | inherit |
| `@implementer` | Executes implementation stages | inherit |
| `@reviewer-gpt5.2-high` | Primary review (thorough, high reasoning) | gpt-5.2 |
| `@reviewer-gemini` | Secondary review (alternative perspective) | gemini-3-pro-preview |
| `@reviewer-opus` | Deep review (nuanced analysis) | claude-opus-4-5-20251101 |

## Confidence Threshold Rules

- **>= 80% from ALL reviewers:** Auto-proceed to next phase
- **< 80% from ANY reviewer:** Requires refinement, then re-review
- **Max 2 refinement iterations:** After 2 failed attempts, ask user for guidance

## Quick Reference

```
Phase 1: Research        → @researcher
Phase 2: Sounding Board  → Direct (no delegation)
Phase 3: Planning        → @planner
Phase 4: Plan Review     → @reviewer-gpt5.2-high (or all 3)
Phase 5: User Review     → Direct (get approval)
Phase 6: Implementation  → @implementer (per stage)
Phase 7: Impl Review     → @reviewer-gpt5.2-high (or all 3)
Phase 8: Conclusion      → Direct (summarize, offer commit)
```
