Prompt #1 - functional spec builder (generalized into skill)
Understand and document the current process for writing functional specifications based on the samples provided. Develop a strong sense of the destination we are trying to reach with clear success criteria.


Reivew the Functional specs under the following directories. 

- \SampleProjects\Heartland Bank\Functional Specifications
- \SampleProjects\KnightG\Functional Specifications
- \SampleProjects\Statewide\Functional Specifications
- \SampleProjects\Youngdahl\Functional Specifications

seek to understand the structure and content of the functional specs. In the future we will 

Deliverables (under .teran\functional-specs):
- functional spec template .md file
    - this file should include a clear structure for writing functional specifications based on the samples provided. this file contains specifies structure only. High fidelity to the samples is not required, but the structure should be informed by the samples. if multiple formats are detected you may provide minimal reasonable variations with clear labels. 
- functional spec guidelines .md file
    - this file provides the guidelines, including best practices, what should and should not be included, and tips for ensuring clarity and completeness. This file should be based on the observed samples. Distill the samples in to guidelines that can be used to reprocude specs like these
- acceptance criteria .md file
    - this file should include a template for writing acceptance criteria based on the samples provided.
- functional spec scoring rubric .md file
    - this file should include a scoring rubric that can be used to evaluate the quality of functional specifications. The rubric can include general reasonable criteria such as clarity, completeness, accuracy, and adherence to the template, however it should maintian high fidelity to the samples. Each criterion should have a clear description and a scoring scale (e.g., 1-5).
- insights_on_current_process.md
    - this files should be used to note down any observations, insights, or patterns identified during the review of the functional specs that do not fit into the other files. if it is important it should be noted here. This file can be used to inform the others.  
- future_thoughts_and_recommendations.md
    - this file should be used to note down any thoughts or recommendations for improving the functional specification process based on the review of the current specs. it can include ideas for enhancing the overall process. let this document be informed by roadblocks encountered, friction points, or strokes of inisight you have. you may refelect on the process afterwards, but do not force anything. keep this document to the point with specific thoughts and actions only.
- [non deliverable] functional spec process-instructions .md file - [I mention this now to inform the big picture, but this is not a deliverable for this phase. we will create this together once we have defined the destination.]
    - this file should provide detailed instructions on how to write functional specifications. This file specifies the process only.    



Here are some general guidelines for the writing style:
- Optimize for clarity over cleverness
Use simple, unambiguous language and avoid “etc.” or “handle all edge cases” without examples.
Keep requirements atomic: one behavior per bullet/ID so they can be individually designed, built, and tested.
- Make requirements measurable and testable
Phrase behaviors so a QA engineer can say “pass/fail” based on observable outcomes.
Back each requirement with acceptance criteria (rule lists or Given/When/Then scenarios) rather than vague statements.
- Anchor everything in user and business value and explicit facts, not assumptions or opinions.
Start from user stories or use cases and trace each requirement back to a user need or business objective.
De‑prioritize or explicitly mark “nice‑to‑have” requirements to avoid bloat.

Please ask clarifying questions if you need more information. The objective is to first learn from and understand the current processes that my team uses to build functional specs. 

context:
- The requirements for these functional specs are gathered through a series of meetings with the customers. ofthen this will come in the form of transcripts, documents, emails from the customer. I will refer to this as the source material. 
