# PrepAIred Architecture - Detailed Explanation & Corrections

## Overview of Changes

The original diagram had several structural issues that have been corrected in the new architecture. This document explains both the problems and solutions.

---

## Problems Identified & Fixed

### ❌ **Original Issues**

1. **Ambiguous Circular Data Flows**
   - Multiple feedback loops made it unclear which path was primary
   - Bidirectional arrows created potential infinite loops
   - Difficult to trace the execution sequence

2. **Disconnected Agents**
   - "Transcriptor Evaluation Agent" seemed isolated
   - Unclear relationship between input agents and orchestrator
   - Some components appeared redundant

3. **Missing Explicit Orchestration Hub**
   - Unclear which agent coordinates all other agents
   - Message passing pathways not clearly defined
   - Made it hard to understand session flow

4. **Poor Layer Organization**
   - Input, processing, and output layers not clearly separated
   - Made system complexity harder to understand
   - New developers couldn't easily onboard

5. **Feedback Loop Ambiguity**
   - Unclear how validators, feedback agents, and strategy agents coordinate
   - Possible race conditions or order dependencies not visible

---

## ✅ **Corrected Architecture**

### **Key Principles**

1. **Clear Layering**: Input → Processing → Refinement → Output → Strategy
2. **Hub-and-Spoke Model**: Orchestrator is the single coordination point
3. **Unidirectional Primary Flow**: Main data flows in one direction (except explicit loops)
4. **Parallel Processing**: Independent agents work simultaneously under orchestrator
5. **Explicit External Services**: Code executor, storage, and logging are clearly separated

---

## **Detailed Component Breakdown**

### **Layer 1: Candidate Interface 👤**
```
Interview UI ← → WebSocket ← → Backend
    ↑
    ├─ Voice Input (🎤)
    ├─ Code Input (💻)
    └─ Text Input (📝)
```
**Role**: User interaction point. Sends raw candidate responses.
**Correction**: Unified under single UI component (removed ambiguous "Candidate Layer")

---

### **Layer 2: Input Analysis 📊**
```
Audio Pipeline    → Speech-to-Text
  ├─ Confidence scoring
  ├─ Hesitation detection
  └─ Prosody features

Code Analyzer     → Syntax validation, structure analysis

Text Processor    → Language processing, intent extraction
```
**Role**: Pre-process all input types into standardized format
**Correction**: Explicit parallel processing of different input modalities
**Why**: Separates input concerns from evaluation logic

---

### **Layer 3: Core Orchestration 🎯**
```
Interview Orchestrator (Central Hub)
├─ Manages session lifecycle
├─ Coordinates all agents
├─ Maintains state
└─ Routes all messages
```
**Role**: Single source of truth. All communication flows through here.
**Correction**: Made explicit as THE central hub (was ambiguous before)
**Why**: Prevents race conditions and ensures consistent state

---

### **Layer 4: Processing Agents ⚙️**
Three agents work **in parallel**, triggered by Orchestrator:

**a) Question Selector**
- Maintains question difficulty level
- Considers topic coverage
- Selects next question based on session history
- Input: Current difficulty estimate
- Output: Next question ID, difficulty level

**b) Session Timer**
- Tracks time per question
- Generates timeout alerts
- Part of state signal for RL
- Input: Question start time
- Output: Time metrics, timeout signals

**c) Evaluator Agent**
- Computes 3-component score:
  1. **Semantic Score**: Does the answer address the question?
  2. **Concept Score**: Is core concept understood?
  3. **Reasoning Score**: Is reasoning sound?
- Calls Code Executor if code evaluation needed
- Input: Answer transcript/code, question rubric
- Output: Multi-component score, metrics

**Correction**: Explicit parallel structure (was unclear in original)

---

### **Layer 5: Refinement ✅**
```
Score Validator
├─ Post-hoc guardrails
├─ Score bounds checking
├─ Consistency validation
└─ Anomaly detection
```
**Role**: Catch evaluation edge cases before feedback gen
**Correction**: Explicit separate layer (was merged with evaluator)
**Why**: Separation of concerns - evaluation vs. validation

---

### **Layer 6: Output Layer 📋**
```
Feedback Agent (15-field)
├─ Strengths
├─ Areas for improvement
├─ Misconceptions detected
├─ Specific tips
├─ Confidence indicators
└─ [+10 more fields]
```
**Role**: Generate structured, actionable feedback
**Output**: JSON with 15 fields for rich feedback
**Correction**: Made explicit as dedicated output layer

---

### **Layer 7: Adaptive Strategy 🤖**
```
Strategy Agent (PPO-based RL)
├─ State (6D):
│  ├─ Performance
│  ├─ Rolling average
│  ├─ Confidence
│  ├─ Hesitation
│  ├─ Time normalized
│  └─ Current difficulty
│
├─ Actions (3):
│  ├─ Easier
│  ├─ Same
│  └─ Harder
└─ Output: Next action + difficulty adjustment
```
**Role**: Adaptively adjust difficulty using trained PPO policy
**Baseline Phase**: First N questions are deterministic (no RL)
**Correction**: Explicit decision layer (was embedded in original)
**Why**: Makes RL strategy visible and testable

> Note: Hint and follow-up generation are auxiliary support paths handled by Qwen and the orchestrator; they are not part of the RL action space in the frozen design.

### **Layer 8: Execution 💾**
```
Code Executor (Sandbox)
├─ Runs code in isolated process
├─ Timeout protection (e.g., 5s)
├─ Test case execution
└─ Output validation
```
**Role**: Safely execute and evaluate code submissions
**Correction**: Extracted from evaluator (was mixed in original)
**Why**: Better separation, easier to test, clearer security boundary

---

### **Layer 9: Storage 🗄️**
```
Session Logger
├─ Turn-level events
├─ Candidate responses
├─ Scores + feedback
└─ Session analytics

Vector Store (FAISS)
├─ Question embeddings
├─ Answer embeddings
└─ Semantic search index
```
**Role**: Persist session data and enable semantic search
**Correction**: Made explicit (was implicit in original)

---

## **Data Flow: Single Interview Turn**

```
Turn Start
    ↓
Interview UI → Input Analysis (parallel: audio, code, text)
    ↓
→ Orchestrator (receive processed input)
    ↓
→ [Parallel] Question Selector, Timer, Evaluator
    ↓
Evaluator [if code] → Code Executor → back to Evaluator
    ↓
→ Orchestrator (collect all results)
    ↓
Score Validator (refine & guardrail)
    ↓
Feedback Agent (generate 15-field feedback)
    ↓
Strategy Agent (compute next action)
    ↓
Update Vector Store
    ↓
Log Turn (Session Logger)
    ↓
→ Interview UI (send question + feedback)
    ↓
→ Next Turn
```

---

## **Key Improvements in Corrected Diagram**

| Aspect | Original | Corrected |
|--------|----------|-----------|
| **Central Hub** | Ambiguous | Explicit Orchestrator |
| **Data Flow** | Circular, bidirectional | Linear with clear loops |
| **Processing** | Sequential, unclear | Parallel, coordinated |
| **Agent Roles** | Overlapping | Clearly separated |
| **Validation** | Mixed with evaluation | Explicit separate layer |
| **Execution** | Embedded in evaluator | Isolated sandbox layer |
| **Storage** | Not visible | Explicit logging layer |
| **Feedback Loop** | Tangled arrows | Clear Strategy → Orchestrator → UI |

---

## **Why This Matters**

1. **Onboarding**: New developers can quickly understand the architecture
2. **Debugging**: Clear pathways make it easier to trace issues
3. **Testing**: Each layer can be tested independently
4. **Scaling**: Clear boundaries make it easier to add features
5. **Security**: Explicit sandbox layer shows isolation
6. **Performance**: Parallel processing opportunities are visible

---

## **Next Steps**

To align code with this corrected architecture:

1. ✅ Ensure `Orchestrator` is the sole message hub
2. ✅ Verify input agents feed directly to Orchestrator
3. ✅ Confirm parallel processing of Selector, Timer, Evaluator
4. ✅ Extract Code Executor to own service
5. ✅ Make Validator a separate step (not merged with Evaluator)
6. ✅ Ensure feedback gen → strategy → loop back is explicit
7. ✅ Add comprehensive logging at each layer

---

## **Files to Update**

- `agents/orchestrator/interview_orchestrator.py` - verify hub role
- `agents/evaluator/` - extract code execution logic
- `agents/validation/score_validator.py` - confirm independence
- `agents/feedback/feedback_agent.py` - confirm output structure
- `agents/strategy/hybrid_orchestrator.py` - confirm RL decision point
- `services/` - ensure clear service boundaries
