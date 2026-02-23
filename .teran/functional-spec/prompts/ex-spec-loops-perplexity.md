# AI-Assisted Functional Spec Generation – Four-Loop Process

This document describes a four-loop, human-in-the-loop workflow for generating high-quality functional specifications with LLM-based assistants. Domain- and org-specific details can be filled in later.

---

## Loop 1 – Problem & Context Understanding

**Intuition / Objective**  
- Build a shared, unambiguous understanding of the problem, users, constraints, and goals before considering solutions.
- Normalize messy source material (PRDs, emails, notes, recordings) into a concise, structured understanding document.

**Inputs / Source Material**  
- Raw product inputs: briefs, PRDs, UX docs, emails, user research, meeting notes, tickets.  
- Known constraints: technical stack, integration boundaries, SLAs, compliance, org policies.  
- Stakeholder list and roles (who decides what).

**Outputs / Deliverables**  
- "Problem & Context Document" containing:  
  - Problem statement and goals.  
  - User roles/personas and primary use cases.  
  - Business and technical constraints / assumptions.  
  - Explicit open questions and unknowns, grouped by stakeholder.

**Success / Acceptance Criteria**  
- All key source documents have been ingested and reflected in the understanding doc.  
- Stakeholders agree the problem, goals, and constraints are correctly captured.  
- All major ambiguities are captured as explicit open questions.  
- No solution decisions are baked in yet (solution-agnostic).

**Loop / Process / Steps**  
1. Feed source material and constraints to the LLM/agent.  
2. Ask it to draft an initial Problem & Context Document and a list of clarifying questions.  
3. Review, answer questions, correct misunderstandings.  
4. Have the agent update the document; repeat 2–3 until questions converge and stakeholders sign off.

---

## Loop 2 – Solution Options & Design Direction

**Intuition / Objective**  
- Explore multiple coherent solution options before committing to one.  
- Make trade-offs explicit so the chosen direction is deliberate and documented.

**Inputs**  
- Approved Problem & Context Document from Loop 1.  
- Any existing architectural/UX constraints or preferences.  
- Non-functional priorities (performance, reliability, security, cost, etc.).

**Outputs / Deliverables**  
- 2–3 alternative solution briefs, each describing:  
  - High-level architecture / system boundaries.  
  - Main user flows and interactions.  
  - Data model highlights and key entities.  
  - Pros, cons, and key risks.  
- A **selected solution brief** (possibly a hybrid) that will drive the spec.

**Success / Acceptance Criteria**  
- At least two materially different solution options are described.  
- Each option clearly links back to Loop 1 goals and constraints.  
- Pros/cons and risks are explicit for each option.  
- Stakeholders agree on a single selected solution brief to move forward with.

**Loop / Process / Steps**  
1. Provide the approved Problem & Context Document to the LLM/agent.  
2. Instruct it to generate 2–3 distinct solution options with pros/cons and risks.  
3. Review as a human: comment, prune, or hybridize options.  
4. Ask the agent to synthesize the final, selected solution brief reflecting your decisions.  
5. Lock the solution brief as the design input to the spec.

---

## Loop 3 – Functional Spec Drafting

**Intuition / Objective**  
- Transform the selected solution brief into a clear, implementation-agnostic functional spec that can guide design, implementation, and testing.

**Inputs**  
- Approved Problem & Context Document (Loop 1).  
- Selected solution brief (Loop 2).  
- Spec template / house style (section list, formatting rules, terminology).  
- Spec acceptance-criteria checklist for "what a good spec looks like".

**Outputs / Deliverables**  
- Draft functional specification with at least these sections:  
  - Overview and goals.  
  - Scope and out-of-scope.  
  - Stakeholders and user roles.  
  - Assumptions and constraints.  
  - User stories / use cases.  
  - Functional requirements (numbered, atomic, testable).  
  - Non-functional requirements.  
  - Data and interfaces.  
  - UX notes / references.  
  - Acceptance criteria per flow or feature.  
  - Risks, open questions, dependencies.

**Success / Acceptance Criteria (Spec Quality)**  
- All required sections from the template are present and populated.  
- Every functional requirement is atomic, observable, and testable.  
- Each major user flow has at least one corresponding requirement and acceptance criteria set.  
- The spec stays solution-aligned (matches the selected solution brief) and implementation-agnostic (no low-level code decisions).  
- All open questions are called out rather than silently filled in.

**Loop / Process / Steps**  
1. Provide the context doc, solution brief, and spec template to the LLM/agent.  
2. Have it propose a section-by-section outline for the spec; adjust as needed.  
3. Generate the spec section-by-section, reviewing and correcting after each major section.  
4. Ensure the agent references the spec-quality acceptance-criteria checklist while drafting.  
5. Iterate until the draft passes a self-check against the checklist.

---

## Loop 4 – Evaluation, Refinement & Downstream Alignment

**Intuition / Objective**  
- Treat the spec as a living contract that must be evaluated, refined, and aligned with downstream artifacts (tickets, tests, monitoring, future model prompts).  
- Use checklists and rubrics to catch gaps and keep the spec in sync with reality over time.

**Inputs**  
- Draft functional spec from Loop 3.  
- Spec-quality acceptance-criteria checklist (sections, atomicity, testability, traceability).  
- Optional scoring rubric for LLM-as-judge style evaluation (e.g., completeness, clarity, instruction adherence).  
- Links to downstream artifacts: tickets, test plans, monitoring requirements.

**Outputs / Deliverables**  
- Reviewed and refined spec with comments resolved.  
- A short issues list (ambiguities, contradictions, missing edge cases, misalignments).  
- Updated spec-quality checklist status and, optionally, rubric scores.  
- Traceability links from spec requirements and ACs to tickets/tests/monitors.

**Success / Acceptance Criteria**  
- Spec passes the acceptance-criteria checklist: all required sections present, requirements and ACs testable, traceability established.  
- Any LLM-as-judge rubric scores meet agreed thresholds (e.g., completeness >= 4/5, clarity >= 4/5).  
- No known high-severity ambiguities or contradictions remain.  
- Core spec sections stay aligned with actual implementation and tickets (no major drift).

**Loop / Process / Steps**  
1. Ask the LLM/agent (or a separate "reviewer" agent) to critique the spec using:  
   - The spec-quality checklist (pass/fail per item).  
   - An optional multi-dimensional rubric (e.g., completeness, clarity, alignment).  
2. Review the issues list; decide which changes to apply.  
3. Have the drafting agent apply accepted changes and regenerate the spec cleanly.  
4. Establish or update traceability: link requirements and ACs to tickets, tests, and monitoring items.  
5. Repeat this evaluation loop when requirements change or major implementation decisions are updated, to keep the spec current.

---

## Overall Usage Notes

- Each loop produces a concrete artifact that becomes the input to the next loop.  
- Human review and decision points are explicit at the end of each loop; the agent proposes, humans decide.  
- The same high-level structure can be reused across domains by plugging in domain-specific templates, constraints, and checklists later.  
- Loops can be run in a single interactive session (single-agent) or split across multiple specialized agents in a pipeline.