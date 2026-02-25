---
name: excalidraw-feedback
version: 1.0.0
description: Interactive design feedback playground for Excalidraw documents. Load, render, and analyze .excalidraw diagrams with structured AI feedback, then iterate with suggested improvements rendered inline.
---

# Excalidraw Feedback Playground

An interactive loop for analyzing and improving Excalidraw designs. Render the diagram, evaluate it across eight design dimensions, then optionally suggest and render improvements—all without leaving the chat.

## Required MCP Tools

| Tool | Purpose |
|------|---------|
| `read_me` (Excalidraw) | Load element format reference before first render |
| `create_view` (Excalidraw) | Render and display elements with draw-on animation |
| `export_to_excalidraw` (Excalidraw) | Publish to excalidraw.com for a shareable link |
| `save_checkpoint` (Excalidraw) | Snapshot current design state |
| `read_checkpoint` (Excalidraw) | Restore a previous snapshot |

---

## Workflow

### Step 1 — Accept the Document

Accept input in any of these forms:

**A. File path** — Read the `.excalidraw` file directly (it is plain JSON).

```
User: /path/to/diagram.excalidraw
```

**B. Pasted JSON** — User pastes Excalidraw JSON inline.

**C. Checkpoint ID** — User provides a checkpoint ID from a previous session; call `read_checkpoint` to restore it.

Parse the JSON and extract `elements[]` and `appState`. If the file is empty or malformed, tell the user immediately rather than proceeding.

---

### Step 2 — Load the Format Reference

Call `read_me` **once per session** before the first `create_view` call. This loads the element format reference needed to author or modify elements correctly.

---

### Step 3 — Render the Original

Call `create_view` with the full `elements` array from the document.

```json
// Pass the elements array exactly as found in the .excalidraw file
create_view({ elements: "<JSON array string>" })
```

Confirm to the user that the diagram is rendered and you are ready to analyze it.

---

### Step 4 — Save Initial Checkpoint

Immediately after rendering, call `save_checkpoint` with:
- `id`: `"original"`
- `data`: the full document JSON (elements + appState)

This lets you restore the unmodified design at any time.

---

### Step 5 — Analyze the Design

Score and narrate feedback across **eight dimensions**. Use this format for each:

```
## [Dimension Name]
Rating: ★★★☆☆  (1–5 stars)
Observation: [What you see]
Suggestion: [What to improve, or "looks good"]
```

#### The Eight Dimensions

**1. Visual Hierarchy**
- Is the most important element (title, outcome, key node) visually dominant?
- Are font sizes, stroke widths, and element sizes used to signal importance?
- Red flag: everything the same size, nothing draws the eye first.

**2. Layout & Composition**
- Is there a clear reading direction (top→bottom, left→right)?
- Are elements aligned to an implicit grid? Are whitespace gaps consistent?
- Are clusters of related elements physically close?
- Red flag: random placement, elements overlapping or touching edges.

**3. Color Usage**
- Is color used semantically (e.g., green = success, red = error)?
- Is the palette limited (≤5 colors)? Are similar things the same color?
- Red flag: many random colors with no pattern, or everything is the default stroke color with no differentiation.

**4. Typography**
- Is all text legible at normal viewing scale?
- Is there a clear hierarchy between headings, labels, and body text?
- Is text inside shapes centered and not clipped?
- Red flag: tiny labels on connectors, text overflowing shapes, inconsistent font sizes.

**5. Connectors & Flow**
- Do arrows have clear direction (arrowheads visible)?
- Do connector labels explain the relationship they represent?
- Are connectors crossing unnecessarily? Do they route logically?
- Red flag: unlabeled arrows, bidirectional arrows without explanation, spaghetti routing.

**6. Grouping & Boundaries**
- Are logically related elements grouped (using Excalidraw frames or surrounding rectangles)?
- Do groups have clear labels?
- Are unrelated elements visually separated?
- Red flag: no grouping in a complex diagram, unclear where one subsystem ends and another begins.

**7. Labeling & Annotation**
- Does every significant element have a label?
- Are labels self-explanatory or do they require external context?
- Is there a legend if symbols or color coding is used?
- Red flag: unnamed shapes, cryptic abbreviations, no legend for color/icon conventions.

**8. Diagram Clarity (Overall)**
- Can a newcomer understand the diagram's purpose within 30 seconds?
- Is the diagram's scope well-bounded (not trying to show everything at once)?
- Is there a title or caption?
- Red flag: no title, mixed concerns, too much information density for a single view.

---

### Step 6 — Produce the Feedback Report

After all dimensions, write a concise **Summary** block:

```markdown
## Summary

**Strengths:** [2–3 things done well]

**Top 3 improvements:**
1. [Highest-impact change]
2. [Second change]
3. [Third change]

**Overall rating:** ★★★☆☆
```

Then ask the user:
> Would you like me to render a revised version with the suggested improvements applied?

---

### Step 7 — Render Improvements (if requested)

If the user says yes (or asks for specific changes):

1. Modify the `elements` array to apply the improvements.
   - Use the element format from `read_me` as your reference.
   - Preserve element IDs where possible; only change what needs changing.
   - Add new elements (frames, labels, arrows) as needed.

2. Call `create_view` with the revised elements.

3. Save the revised state as a checkpoint:
   - `id`: `"revision-1"` (increment for subsequent revisions)
   - `data`: the updated document JSON

4. Narrate what changed:
   > Applied: added frame labels, standardized connector arrowheads, introduced a 3-color semantic palette.

---

### Step 8 — Export (if requested)

If the user wants a shareable link, call `export_to_excalidraw` with the current document JSON and return the URL.

If the user wants to save a revised `.excalidraw` file, write the updated JSON back to the original file path (or a new path if they specify one).

---

## Iterative Loop

After each revision, return to **Step 5** for the revised diagram. Continue until the user is satisfied or exits.

Commands the user can give during the loop:

| User says | Action |
|-----------|--------|
| "restore original" | `read_checkpoint("original")` + `create_view` |
| "undo" / "go back" | `read_checkpoint("revision-N-1")` + `create_view` |
| "export" / "share" | `export_to_excalidraw` + return URL |
| "save" | Write revised JSON back to file |
| "what changed?" | Diff current elements vs checkpoint, summarize |
| "focus on [dimension]" | Re-analyze and re-render targeting only that dimension |
| "done" | Summarize all changes made, offer export, close the loop |

---

## Feedback Tone Guidelines

- Be specific and actionable — "add arrowheads to the three unlabeled connectors" not "improve arrows."
- Be positive first — note what works before listing issues.
- Rank suggestions by impact, not by effort — a high-impact easy fix beats a low-impact hard one.
- If the diagram is already excellent, say so clearly and briefly.
- Adapt depth to diagram complexity — a simple 5-node flowchart needs less analysis than a 50-element system architecture.

---

## Element Authoring Quick Reference

When modifying or adding elements, use these common patterns:

```json
// Rectangle / Frame
{ "type": "rectangle", "x": 100, "y": 100, "width": 200, "height": 80,
  "strokeColor": "#1e1e1e", "backgroundColor": "#e8f4fd",
  "fillStyle": "solid", "strokeWidth": 2, "roughness": 1 }

// Text label
{ "type": "text", "x": 110, "y": 130, "text": "Label",
  "fontSize": 16, "fontFamily": 1, "textAlign": "center" }

// Arrow connector
{ "type": "arrow", "x": 300, "y": 140, "points": [[0,0],[100,0]],
  "strokeColor": "#1e1e1e", "strokeWidth": 2,
  "startArrowhead": null, "endArrowhead": "arrow" }
```

Always call `read_me` first for the full format reference.

---

## Semantic Color Palette (Suggested Defaults)

Use this palette when suggesting color improvements, unless the document already has a deliberate color system:

| Role | Fill | Stroke |
|------|------|--------|
| Primary action / focus | `#e8f4fd` | `#1971c2` |
| Success / complete | `#ebfbee` | `#2f9e44` |
| Warning / caution | `#fff9db` | `#f08c00` |
| Error / blocked | `#fff5f5` | `#e03131` |
| Neutral / background | `#f8f9fa` | `#868e96` |
| Highlight / annotation | `#f3f0ff` | `#7048e8` |
