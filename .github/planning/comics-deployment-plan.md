# Computational Narrative Comic Deployment Plan
## 2026 Map Encryption Library

Version: Draft 1  
Purpose: Define pedagogically grounded comic-strip deployments across the notebook sequence.

---

# 1. Design Philosophy

These comics are not decorative assets.

They serve four instructional functions:

1. Concept Compression
2. Ethical Humanization
3. Threat Intuition
4. Cognitive Decompression

The comics should:
- reduce abstraction burden,
- reinforce mental models,
- provide narrative continuity,
- and improve retention.

The comics should NOT:
- trivialize public-health harms,
- become comedic distractions,
- or replace technical explanations.

---

# 2. Visual Style Guide

## Artistic Style

Target:
- restrained educational line art
- computational narrative aesthetic
- lightly stylized but realistic
- minimal shading
- clear silhouettes
- low visual clutter

Influences:
- scientific illustration
- graphic essays
- educational infographics
- light Victorian sketch style for historical notebooks

Avoid:
- meme aesthetics
- exaggerated cartoon comedy
- anime styling
- hyperreal AI art
- excessive detail

---

# 3. Tonal Guide

| Desired Tone | Avoid |
|---|---|
| thoughtful | goofy |
| reflective | slapstick |
| intellectually playful | sarcastic |
| lightly human | absurdist |
| ethical seriousness | dark humor |

Important:
Humor must NEVER target:
- victims,
- illness,
- overdose,
- death,
- vulnerable populations.

Humor may target:
- technical misconceptions,
- attacker frustration,
- system limitations,
- abstract concepts.

---

# 4. Recurring Character Framework

## 4.1 Privacy Engineer

Purpose:
- explain mechanisms
- introduce safeguards
- frame architectural thinking

Traits:
- calm
- analytical
- understated

Visual:
- notebook/tablet
- diagrams
- neutral clothing

---

## 4.2 Epidemiologist

Purpose:
- emphasize public-health utility
- represent analytic goals

Traits:
- practical
- data-focused
- socially aware

Visual:
- maps
- field notes
- dashboards

---

## 4.3 Adversary

Purpose:
- externalize attack thinking
- make inference risk concrete

Traits:
- observant
- methodical
- not villainous caricature

Important:
Adversary should look realistic and professional,
not evil/hacker stereotype.

Avoid:
- hoodies
- glowing screens
- “cyberpunk hacker” imagery

---

## 4.4 Resident

Purpose:
- humanize disclosure risk
- represent affected communities

Traits:
- grounded
- ordinary
- emotionally realistic

Visual:
- homes
- neighborhoods
- contextual environments

---

## 4.5 Data Steward

Purpose:
- governance
- access control
- trust boundaries

Traits:
- cautious
- procedural
- policy-oriented

---

## 4.6 Victorian Physician

Purpose:
- historical bridge in NB14
- connect Snow-era epidemiology to modern geoprivacy

Style:
- Victorian attire
- sketch aesthetic
- maps and notebooks

---

# 5. Comic Categories

---

## Type A — Concept Compression

Goal:
Explain difficult abstractions visually.

Examples:
- PRP shuffling
- DGGS abstraction
- AEAD verification
- privilege separation

Typical placement:
Immediately after concept introduction.

Typical size:
3–4 panels.

---

## Type B — Ethical Reflection

Goal:
Humanize consequences of disclosure.

Examples:
- stigma
- hotspot labeling
- trust erosion
- community harm

Typical placement:
Before ethics sections or reflection prompts.

Tone:
Quiet and reflective.

---

## Type C — Threat Intuition

Goal:
Show how attacks work.

Examples:
- linkage attacks
- nearest-neighbor inference
- side-channel leakage

Typical placement:
Before adversarial experiments.

---

## Type D — Transition Comics

Goal:
Bridge conceptual jumps between notebooks.

Examples:
- point privacy → DGGS
- local privacy → statistical privacy
- utility → adversarial reasoning

---

# 6. Global Mental Model Reinforcement

A repeated visual abstraction should appear throughout the series:

```text
Exact Coordinate
    ↓
Tile / DGGS Cell
    ↓
Permuted Spatial Identity
    ↓
Encrypted Residual
    ↓
Approximate Display Point
````

This should appear repeatedly across:

* comics,
* diagrams,
* recap cells.

---

# 7. Deployment Strategy by Notebook

---

# NB00 — Geoprivacy Introduction

## Comic Count

2

## Pedagogical Goal

Introduce:

* why geoprivacy matters,
* spatial disclosure intuition.

---

## Comic NB00-C1

### Type

Ethical Reflection

### Placement

Opening section

### Goal

Show tension between:

* public-health mapping
* personal privacy

### Panels

1. Epidemiologist examines outbreak map
2. Resident notices exact household visible
3. Silence / concern
4. Caption:
   “Maps can save lives. They can also expose them.”

---

## Comic NB00-C2

### Type

Concept Compression

### Goal

Introduce geomasking intuition.

### Panels

1. Exact point
2. Jittered point
3. Hex bin
4. Caption:
   “Different protections preserve different truths.”

---

# NB03 — Grid Snapping and PRP

## Comic Count

3

## Comic NB03-C1

### Type

Concept Compression

### Goal

Explain tile abstraction.

### Panels

1. Exact addresses visible
2. Grid overlay appears
3. “We only keep the tile.”
4. Points lose exact identity

---

## Comic NB03-C2

### Type

Threat Intuition

### Goal

Explain why raw tile IDs leak information.

### Panels

1. Adversary comparing tiles
2. Recognizing hotspot region
3. Engineer introduces permutation
4. Caption:
   “Tile identity can still leak geography.”

---

## Comic NB03-C3

### Type

Transition

### Goal

Prepare learner for cryptographic abstraction.

### Panels

1. Original city blocks
2. Shuffled tile coordinates
3. Adversary confused
4. “Spatial meaning has been permuted.”

---

# NB04 — Residual Encryption and AEAD

## Comic Count

3

## Comic NB04-C1

### Type

Concept Compression

### Goal

Explain residual encryption.

### Panels

1. Tile protects coarse location
2. Residual still reveals precision
3. Lock icon around residual
4. “Precision requires additional protection.”

---

## Comic NB04-C2

### Type

Threat Intuition

### Goal

Explain tampering.

### Panels

1. Attacker modifies ciphertext
2. AEAD verification fails
3. System rejects record
4. “Integrity matters too.”

---

## Comic NB04-C3

### Type

Concept Compression

### Goal

Explain associated data binding.

### Panels

1. Ciphertext copied to another tile
2. Verification failure
3. Engineer explains context binding
4. “Coordinates and ciphertext travel together.”

---

# NB05 — Key Derivation and Display Jitter

## Comic Count

3

## Comic NB05-C1

### Type

Concept Compression

### Goal

Explain least privilege.

### Panels

1. Display server requests exact coordinates
2. Data steward refuses
3. Display receives jitter-only key
4. “Rendering does not require precision.”

---

## Comic NB05-C2

### Type

Threat Intuition

### Goal

Explain privilege separation.

### Panels

1. Stolen display key
2. Attacker sees only approximate points
3. Precise coordinates remain inaccessible
4. “Compartmentalization limits damage.”

---

## Comic NB05-C3

### Type

Transition

### Goal

Prepare for full pipeline notebook.

### Panels

1. Tile
2. PRP
3. AEAD
4. Jittered display
5. Caption:
   “Multiple layers create defense-in-depth.”

---

# NB07 — Security and Limitations

## Comic Count

2

## Comic NB07-C1

### Type

Ethical Reflection

### Goal

Normalize limitations.

### Panels

1. Engineer reviewing attack scenarios
2. Whiteboard of unresolved risks
3. Caption:
   “No privacy mechanism is perfect.”

---

## Comic NB07-C2

### Type

Threat Intuition

### Goal

Show metadata leakage.

### Panels

1. Adversary ignores coordinates
2. Uses timing/access patterns
3. Learner realizes hidden leakage
4. “Privacy failures are not always spatial.”

---

# NB10 — Geoprivacy Ethics

## Comic Count

4

## Comic NB10-C1

### Type

Ethical Reflection

### Goal

Public good vs privacy.

### Panels

1. Outbreak dashboard
2. Concerned resident
3. Public-health urgency
4. “Who decides acceptable disclosure?”

---

## Comic NB10-C2

### Type

Ethical Reflection

### Goal

Territorial stigma.

### Panels

1. Neighborhood labeled “high risk”
2. Residents react uneasily
3. Media amplification
4. “Maps can stigmatize places.”

---

## Comic NB10-C3

### Type

Transition

### Goal

Historical continuity.

### Panels

1. Victorian cholera map
2. Modern GIS dashboard
3. Similar hotspot patterns
4. “The tension has not disappeared.”

---

## Comic NB10-C4

### Type

Reflection

### Goal

Encourage learner metacognition.

### Panels

1. Learner looking at map
2. Empty final panel
3. Caption:
   “What level of disclosure would you accept?”

---

# NB11 — DGGS Tile Identifiers

## Comic Count

3

## Comic NB11-C1

### Type

Concept Compression

### Goal

Explain hierarchical cells.

### Panels

1. Globe
2. Hexagonal cells appear
3. Zoom into finer cells
4. “Privacy can operate across scales.”

---

## Comic NB11-C2

### Type

Transition

### Goal

Move from point privacy to pattern privacy.

### Panels

1. Individual points disappear
2. Population structures remain
3. Caption:
   “Sometimes patterns matter more than points.”

---

## Comic NB11-C3

### Type

Concept Compression

### Goal

Explain multi-resolution tradeoffs.

### Panels

1. Large cells → safer but coarse
2. Small cells → useful but risky
3. Slider metaphor
4. “Resolution changes privacy.”

---

# NB14 — Cholera Dataset Augmentation

## Comic Count

4

## Comic NB14-C1

### Type

Historical Reflection

### Goal

Victorian atmosphere.

### Panels

1. Soho street scene
2. Water pump
3. Physician documenting cases
4. “Spatial epidemiology begins.”

---

## Comic NB14-C2

### Type

Ethical Reflection

### Goal

Historical stigma.

### Panels

1. Street marked dangerous
2. Residents avoid area
3. Child looking at warning
4. “Disease maps shape social perception.”

---

## Comic NB14-C3

### Type

Concept Compression

### Goal

Explain building snapping.

### Panels

1. Street-centered point
2. Building footprint snapping
3. Reduced ambiguity
4. “Spatial realism changes inference risk.”

---

## Comic NB14-C4

### Type

Transition

### Goal

Bridge to modern scenarios.

### Panels

1. Victorian map
2. Modern city dashboard
3. Shared hotspot visualization
4. “The technologies changed. The dilemmas remained.”

---

# NB15 — Substance Use Scenario

## Comic Count

3

## Comic NB15-C1

### Type

Ethical Reflection

### Goal

Stigma amplification.

### Panels

1. Public overdose hotspot map
2. Community discomfort
3. Local business concern
4. “Maps affect communities, not just data.”

---

## Comic NB15-C2

### Type

Threat Intuition

### Goal

Linkage attacks.

### Panels

1. Adversary combines ZIP + age
2. Narrowing candidate identities
3. Learner realization
4. “Approximate location may still be enough.”

---

## Comic NB15-C3

### Type

Reflection

### Goal

Trust.

### Panels

1. Resident asked to share data
2. Resident hesitates
3. “Would you trust this system?”

---

# NB17 — Adversarial Experiments

## Comic Count

4

## Comic NB17-C1

### Type

Threat Intuition

### Goal

Nearest-neighbor attacks.

### Panels

1. Attacker comparing candidate points
2. Matching spatial patterns
3. Confidence increases
4. “Patterns leak information.”

---

## Comic NB17-C2

### Type

Threat Intuition

### Goal

Compound attacks.

### Panels

1. Demographics
2. Geography
3. Combined inference
4. “Small clues accumulate.”

---

## Comic NB17-C3

### Type

Concept Compression

### Goal

Defense-in-depth.

### Panels

1. Jitter-only protection breaks
2. Full pipeline resists
3. Multiple safeguards visible
4. “Single layers rarely suffice.”

---

## Comic NB17-C4

### Type

Reflection

### Goal

Critical thinking.

### Panels

1. Attacker whiteboard
2. Learner reviewing defenses
3. “What assumptions are realistic?”

---

# NB18 — Formal Threat Model

## Comic Count

3

## Comic NB18-C1

### Type

Concept Compression

### Goal

Adversary tiers.

### Panels

1. Curious observer
2. Insider analyst
3. Infrastructure attacker
4. “Threats differ in capability.”

---

## Comic NB18-C2

### Type

Concept Compression

### Goal

Trust boundaries.

### Panels

1. Data steward
2. Display server
3. Secure enclave
4. Boundary lines highlighted

---

## Comic NB18-C3

### Type

Reflection

### Goal

Formal reasoning.

### Panels

1. Learner looking at architecture
2. Multiple leakage paths
3. “Security depends on assumptions.”

---

# 8. Implementation Guidance

## Recommended Workflow

1. Define learning goal
2. Define misconception addressed
3. Create storyboard
4. Generate low-detail draft
5. Human review
6. Technical accuracy review
7. Tone review
8. Embed in notebook

---

# 9. AI Generation Guidance

## Recommended Prompt Constraints

* educational line art
* restrained palette
* simple backgrounds
* minimal text
* recurring character consistency
* realistic maps
* no exaggerated expressions
* no meme aesthetics

---

# 10. Evaluation Criteria

A comic should remain only if it:

* reduces abstraction burden,
* improves narrative continuity,
* reinforces mental models,
* or deepens ethical understanding.

If a comic merely decorates:
remove it.

---

# 11. Long-Term Possibility

Future expansion:

* export comics into a printable computational narrative edition,
* Jupyter Book sidebars,
* conference posters,
* microlearning modules,
* animated notebook transitions,
* classroom discussion prompts.

The current deployment plan should remain:
minimal,
purposeful,
and pedagogically disciplined.
