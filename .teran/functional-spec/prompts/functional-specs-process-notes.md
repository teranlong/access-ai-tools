My deliverables:
1. understand and document the current process for writing functional specifications based on the samples provided. Develop a strong sense of the destination we are trying to reach with clear success criteria.
2. create a light process for agent assisted workflow arriving at the same destination as observed here.
3. create a full process vision to track the long term vision for functional specs process



---



---
--- PROCESS ---

context: 
- It is a good idea to include a question section that can ask to the customer to gain information with clarification when details are unclear
- Within The instructions section there should be a process for the agent to query the user or otherwise resolve questions before proceeding
- IMPORTANT: This process and therefore the agents that follow this process must priorit Correctness and Clarity above all else. the agent should always prioritize asking questions to get to explicit facts over making assumptions. All assumptions must be explicitly stated in an assumptions section and decisions based on assumptions should be noted in a well defined process that makes it clear where dicision stem from.
- key decisions should always be justified with clear reasoning and documented in a decision log. This log should include the decision made, the rationale behind it with expicit references to the source material, and any alternatives that were considered. This will help ensure transparency and accountability in the decision-making process.
- There should be an intermediate step where the agent 





Example process flow:
Step 1: Gather source material from customer meetings and document it thoroughly
Deliverables: 
- understanding.md with sections: _________
- linked sub documents for deep dives into specific sections.

source material -> ask questions to the customer/designer -> understanding document
understanding document -> ask questions to the designer -> solution brainstorm, 1, 2, 3 etc. 
selected solution brainstorm -> formalized functional spec 

compare this idea with the latest research and propose a couple of different solution flows




Spec types Brainstorm:

User‑flow–centric spec:
- Top-level sections organized by end‑to‑end user journeys / flows (Sign up, Purchase, Manage subscription, etc.).
- Within each flow: requirements, ACs, data, and edge cases for that journey.
Capability / feature‑centric spec:
- Top-level sections are functional areas or capabilities (Authentication, Billing, Notifications, Admin, Reporting, etc.).
- User flows are referenced inside each capability as examples or subsections.
Data / contract‑centric spec:
- Top-level sections emphasize core entities, invariants, and external contracts (Entities, APIs, Events, Integrations), with flows and capabilities mapping onto those structures.
​- Useful when stability of data and interfaces matters most (e.g., API‑first, integration‑heavy systems).
