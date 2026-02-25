
You are a senior agentic workflow architect. You are tasked with creating a workflow for generating functional specifications. Below I have provided a first draft at the prompt that will be used to generate the skill for the functional spec workflow. Your job is to read the prompt below and the reference files and create an improved prompt that will be used to generate the skill for the functional spec workflow. use your knowledge of agentic skills and of the resource files provided to create a more specific prompt.

You should ensure that:
- the prompt remains true to the original intent and details of the prompt I have specified below
- the prompt is clear and concise, specific and actionable
- the prompt is well structured and easy to follow
- the prompt specifies all deliverables, including the format and location of the deliverables
- the promp specifies which md information should be reused and where
- the prompt hase a well defined success criteria
- the prompt has well defined and rational output schema including where there will be muliple verions of files.

You should also ensure that the input files are well organized 
- organize the .teran folder such that the prompt is clear where to look and doesnt need to sift through irrelevant context

you may use the question tool to ask clarifying questions. when an intent or outcome is unclear you should ask a question to clarify. 

Output this prompt as a single md file called functional-spec-workflow-master-prompt.md under .teran/functional-spec/prompts/. Only output the improved prompt. do not follow the prompt instructions until specified.

<start of the agentic workflow prompt>

using the latest research aavailable on agentic workflows generate 3 differt detailed agentic workflows. This should outline the process at a high level. all output files should be put under .teran/claude-functional-specs-workflow-proposals/

# Your deliverables:
- 1 or more folders titled workflow-x/ containing a proposed workflow. each with
    - skill.md - a markdown file with the workflow details at a high level. coordiation only. keep it lean and reference deep dives phase-x-{title}.md
    - phase-x-{title}.md - a markdown file for each phase of the workflow. this will contain the details of the phase.
    - reusable md library components where appropriate. two examples are: human in the loop feedback mechanism and deliverable requirements. these md files should be referenced in the phase files where appropriate rather than the infomation copied
- /deliverable-specs/spec-{deliverable name}/v{version}/ - a folder for each deliverable identified in the workflow following the deliverable requirements. there may be multiple versions of a deliverable. this folder serves as a library of deliverable specs for experimentaion later

# Always requirements (applicable to every phase/step of the process):
- All details must be recorded to markdown files in a well organized directory of markdown files called with details such as the phase (e.g. customer-understanding) tool version number and client name in the path
- There should be no details left unstated in context. Each phase will be handed off to a new agent so it is crucial that all details are recorded. This includes less concrete details such as intention and intuition. The agent may record anything that is important but does not fit into the outlined process in a document called agent-inisights.md. this file should always be read by the agents and should be updated with new insights as soon as they come up. 
- there can be multiple versions of each md file. there should be a configuration file that specifies which version of each file to use for the current run. the agent should clarify if it is ambiguous which versions to use. these instrucitons should be an md file module, and a separate configuration md file.
- this process should be repeatable and as deterministic as possible. all deliverables should be specified via specs and all process steps should be explicitly defined.

# Key decisions and justifications
- there should be a defined process for justifying key decisions. The agent should record key decisions in a markdown file called decisions.md with the options that were considered and the justification for the decision. a user should be able to review the decisions.md file and understand the reasoning behind the decisions. These decisions are per-run so they should live in the same directory as the other md outputs. 

# Relevant files: 
- Reference files and instructions. Entire directory: C:\Users\Teran\LocalProjects\access-ai-tools\.teran
- Sample project results (some files are very large. be extremely careful with the context window if you read from here): C:\Users\Teran\LocalProjects\access-ai-tools\agent-data\ai-compatible\v1.3.0

# human in the loop feedback mechanism
The process should be 
  1. the agent should determnine the questions it needs to ask to ensure it has a complete understanding of the requirements. there should be a mechanism for the user to provide a folder of question documents. the answers to each of the questions should be recorded. there can be muiltiple files in this questions folder such as : question-template/db-requirements, question-template/functional-requirements, question-template/user-persona-requirements, question-template/workflow-requirements. brainstorm these categories and create a well organized directory of these question templates for each human in the loop phase. this 
  2. the other methodology is to have the human in the loop review the consolidated customer requirements and provide feedback using the document critique  playground skill

# Deliverable requirements (applicable to every deliverable)
- all deliverables must have an explicit criteria in the form of folder under templates/ with at least the following files:
  - template.md: structural template to be copied and filled out
  - scoring-rubric.md (see C:\Users\Teran\LocalProjects\access-ai-tools\.teran\functional-spec-builder\v0\functional-spec-scoring-rubric.md) - how to determine if the deliverable is complete and meets the criteria. it should link to information checklist 
  - guidance.md (see C:\Users\Teran\LocalProjects\access-ai-tools\.teran\functional-spec-builder\v0\functional-spec-guidelines.md)- guidelines and rulesl for the deliverable.
  - information-checklist.md - a list of all the information that needs to be included in the deliverable in the form of quesions the need to have an answer.
  - agent-feedback.md - a file that contains all of the insights and intuition that the agent has about this step. this is the core of the self learning/self improving process.


# Step by step process
Generally, I want the workflow to include four parts and explicity include human in the loop at each step
## Phase 1. Catelog, gather, normalize information. 
### normalize information
- there already is a skill to normalize information which converts all documents to plain text documents. this skill works well

### catelog information
- there is a catalog skill but it likely needs updates to be useful
- we are working with large documents so we need to be careful about token limits and context. part of the cateloging process is to get an idea of what kind of information each document contains so that it can intelligently load only the most relevant information into the context window. this process will needs to be done with subagents, or some other way to manage the context window.
- the main agent needs to be aware of all of the relevant information, without wasting context on irrelevant details. 
- One solution is to have subagents categorize all documents so that a main agent can load only the relevant doucments. another solution would be for sub agents to extract only the relevant information from each document and then consolidate it into a master factsheet document. you may explor other context effecient methodologies based on the latest research. 

### consolidate customer requirements
- At this point, the agent needs to pay special attention to documents pertaining to customer meetings and requirements.
- the agent needs to have an extremely clear and detailed understanding of the customer requirements, technology, current state and success criteria. 
- all details of the customers requirements should be recorded to markdown files. there should be no details left "to remember" in the agents understanding. This includes less concrete details such as intention and intuition. everthing should be explicitly recorded in a well organized directory of markdown files called customer-understanding with the tool version number and client name inthe path
- the agent should now be able to generate a functional spec for the customer requirements at the top level only. Take a look at the documents I have in .teran for some distilled examples of functional specs based on the provided samples, but please provide multiple templates in a well organized directory of md files. one version should mirror what I have today, but please provide alternative detailed and streamlined versions so that we can choose the best one.
- again, each section should come directly from a template file. gather these sections from the documents I have generated in .teran synthisizing the requiremnts. remember to propose multiple versions of templates when there are different ways to organize the information.

### Human in the loop
- The agent should stop at this point to ensure that its understanding is accurate and complete via human in the loop question answering and document review. 
- at this point there should be no "solutions" as the agent is in a gathering phase. the agent should iterate on this phase until the human in the loop approves the understanding of the requirements. this is a hard requiremnts that should never be skipped. The agent should always surface its lack of understanding and ask for clarification proactively. It should ask itself where abmiguity exists until it is confident that it has a complete understanding of the requirements.

## Phase 2: brainstorm solutions
- at this points the agent should have a complete understanding of the customer requirements.
- the agent should now brainstorm solutions to the customer requirements.

### module determination
- our access projects are divided into modules. The agent should break the requirements into modules based on the customers requirments. You should now use the files provided in the .teran directory and sample files to determine how modules are generally split up. this is a deliverable so it should follow the deliverable reqirements in these instructions
- the agent should should produce multiple versions of the module breakdown and allow the human in the loop to choose the best one. (target 3-5 options) deliverable: module-proposals
- the agent should ensure that all of the customer requirements are covered in the module breakdown. in this deliverable each and every requirmement should be covered in the module breakdown. the agent should show the mapping of each requirement to one or more modules. 
- the agent should ensure that the module breakdown is complete and accurate and that all requirements are satisfied

### Human in the loop
- hard stop, the agent should not proceed until the human in the loop approves the module breakdown.

## Phase 3: Functional Spec Drafting loop
# Sequential drafting 
- the agent should now draft the functional spec for each module one at a time, based on the customer requirements and the module breakdown and the selected specifications. drafts should be exactly baesd on the spec templates
# Human in the loop
- follow the human in the loop process for each module.
- record applicable learnings in feedback.md so that later modules can benefit from corrections in earlier modules.
# repeat
- repeat these steps for each module until all modules are complete.

# Phase 4: Final Review and Approval
- going back to the customer requirements, the agent should ensure that all requirements are covered in the functional spec. the agent should show the mapping of each requirement to one or more functional specs.
- the agent should ensure that the functional spec is complete and accurate and that all requirements are satisfied.
- the agent should ensure all decisions are documented and justified.

<end of the agentic workflow prompt>
