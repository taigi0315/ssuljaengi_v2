# Webtoon Fidelity Validator - Implementation Plan

## Overview

This document outlines the implementation tasks and test cases for the Webtoon Fidelity Validator, a self-correcting agentic workflow that ensures stories are successfully translated into webtoon format using a "Blind Reader" validation approach.

---

## Architecture Summary

```
graph TD
    Start([Seed Input]) --> Node1[Story Architect]
    Node1 --> Node2[Webtoon Scripter]

    subgraph Validation_Loop
    Node2 --> Node3[Blind Reader]
    Node3 --> Node4[Evaluator Agent]
    end

    Node4 -- "REJECT" --> Node2
    Node4 -- "PASS" --> End([Final Output])
```

---

## Task Breakdown

### Phase 1: Data Models & State Schema

#### Task 1.1: Define WebtoonFidelityState TypedDict
**File:** `backend/app/models/fidelity_state.py`

**Description:** Create the central state schema for passing data between nodes.

```python
from typing import List, Optional, TypedDict

class PanelData(TypedDict):
    panel_number: int
    visual_description: str
    dialogue: List[dict]  # {character: str, text: str}
    shot_type: str
    environment: str

class FidelityGap(TypedDict):
    category: str  # 'plot', 'motivation', 'emotion', 'relationship', 'conflict'
    original_element: str
    reader_interpretation: str
    severity: str  # 'critical', 'major', 'minor'
    suggested_fix: str

class WebtoonFidelityState(TypedDict):
    # Input
    seed: str

    # Node 1 Output (Ground Truth - generated once)
    original_story: str
    story_summary: str  # Key plot points for evaluation
    character_motivations: dict  # {character_name: motivation}
    key_conflicts: List[str]

    # Node 2 Output (Modified on each iteration)
    script_panels: List[PanelData]
    characters: List[dict]

    # Node 3 Output (Blind Reader's reconstruction)
    reconstructed_story: str
    inferred_motivations: dict
    inferred_conflicts: List[str]
    reader_confidence: float  # 0.0 - 1.0

    # Node 4 Output (Evaluation)
    fidelity_score: float  # 0.0 - 100.0
    information_gaps: List[FidelityGap]
    critique: Optional[str]

    # Control
    iteration: int
    max_iterations: int
    is_validated: bool
    current_step: str
    error: Optional[str]
```

**Acceptance Criteria:**
- [ ] All fields have proper type annotations
- [ ] Compatible with existing LangGraph patterns in codebase
- [ ] Supports serialization to/from JSON

---

#### Task 1.2: Create FidelityEvaluation Response Model
**File:** `backend/app/models/fidelity_state.py`

```python
from pydantic import BaseModel, Field

class FidelityEvaluation(BaseModel):
    fidelity_score: float = Field(ge=0.0, le=100.0)
    is_valid: bool
    gaps: List[FidelityGap]
    critique: str
    iteration: int
    converged: bool  # True if score improved from previous iteration
```

---

### Phase 2: Node Implementations

#### Task 2.1: Create StoryArchitect Node (Node 1)
**File:** `backend/app/services/fidelity/story_architect.py`

**Description:** Generates the "Ground Truth" story from a seed input. Runs only once at the start.

**Prompt Template:**
```python
STORY_ARCHITECT_PROMPT = """
Based on the seed: "{seed}"

Write a detailed 1-page story (400-600 words) that includes:

1. **Clear Character Motivations**: For each character, explicitly state:
   - What they want (goal)
   - Why they want it (motivation)
   - What's stopping them (obstacle)

2. **Key Plot Points**: Number each major story beat (aim for 5-7)

3. **Hidden Conflicts**: Include at least one:
   - Internal conflict (character vs self)
   - External conflict (character vs character/environment)

4. **Emotional Beats**: Mark moments where emotions shift

Output Format (JSON):
{{
    "story": "<full narrative text>",
    "summary": "<3-5 sentence summary>",
    "character_motivations": {{
        "<name>": {{
            "goal": "<what they want>",
            "motivation": "<why>",
            "obstacle": "<what blocks them>"
        }}
    }},
    "key_conflicts": ["<conflict 1>", "<conflict 2>"],
    "plot_points": ["<beat 1>", "<beat 2>", ...]
}}
"""
```

**Implementation:**
```python
class StoryArchitect:
    def __init__(self, llm_config: LLMConfig):
        self.llm = llm_config.get_model()

    async def generate_story(self, seed: str) -> dict:
        """Generate ground truth story from seed."""
        chain = prompt | self.llm | JsonOutputParser()
        result = await chain.ainvoke({"seed": seed})
        return result
```

**Acceptance Criteria:**
- [ ] Generates complete story from seed
- [ ] Extracts character motivations as structured data
- [ ] Identifies key conflicts explicitly
- [ ] Returns JSON-parseable output

---

#### Task 2.2: Create WebtoonScripter Node (Node 2)
**File:** `backend/app/services/fidelity/webtoon_scripter.py`

**Description:** Converts story to panels. On subsequent iterations, uses critique to improve clarity.

**Prompt Template (Initial):**
```python
SCRIPTER_INITIAL_PROMPT = """
Convert this story into webtoon panels.

Story:
{story}

Character Motivations:
{character_motivations}

Requirements:
1. Each panel must have:
   - Visual Description: What the reader SEES (150+ chars)
   - Dialogue: What characters SAY (if applicable)
   - Shot Type: (close-up, medium, wide, etc.)

2. SHOW emotions through:
   - Facial expressions
   - Body language
   - Environmental cues

3. SHOW motivations through:
   - Character actions
   - Dialogue choices
   - Visual metaphors

Output 8-12 panels in JSON format.
"""
```

**Prompt Template (Revision):**
```python
SCRIPTER_REVISION_PROMPT = """
The reader couldn't understand parts of the story from your panels.

Original Panels:
{current_panels}

Critique (Information Gaps):
{critique}

Instructions:
1. Do NOT change the story - only improve HOW it's visualized
2. For each gap listed:
   - Add visual cues that SHOW the missing information
   - Add/modify dialogue to TELL the missing context
   - Use environmental details to reinforce meaning

Focus especially on:
{specific_gaps}

Return the COMPLETE revised panel list.
"""
```

**Acceptance Criteria:**
- [ ] Generates panels with visual descriptions and dialogue
- [ ] On revision, incorporates critique without changing story
- [ ] Visual descriptions are detailed enough for image generation
- [ ] Maintains character consistency across panels

---

#### Task 2.3: Create BlindReader Node (Node 3) - CRITICAL
**File:** `backend/app/services/fidelity/blind_reader.py`

**Description:** Reconstructs story from panels only. **MUST NOT** access original_story.

**State Isolation Strategy:**
```python
class BlindReaderNode:
    """
    CRITICAL: This node receives a FILTERED state that excludes:
    - original_story
    - story_summary
    - character_motivations
    - key_conflicts

    This isolation is enforced at the graph level.
    """

    @staticmethod
    def filter_state_for_blind_reader(state: WebtoonFidelityState) -> dict:
        """Extract ONLY what BlindReader should see."""
        return {
            "script_panels": state["script_panels"],
            "characters": state["characters"],
            # Explicitly NOT including original_story or related fields
        }
```

**Prompt Template:**
```python
BLIND_READER_PROMPT = """
You are a reader who has NEVER seen the original story.
Analyze these webtoon panels and reconstruct what you can understand.

Panels:
{panels_json}

Characters Defined:
{characters_json}

Based ONLY on what you can see and read in these panels:

1. **Reconstruct the Story**: What happened? Write a narrative summary.

2. **Character Analysis**: For each character:
   - What do they seem to want?
   - Why might they want it?
   - What emotions did you observe?

3. **Conflict Identification**: What conflicts or tensions exist?

4. **Unclear Elements**: What was confusing or unclear?

5. **Confidence Score**: How confident are you in your interpretation? (0-100%)

Output JSON:
{{
    "reconstructed_story": "<your interpretation>",
    "inferred_motivations": {{
        "<character>": {{
            "apparent_goal": "<what you think they want>",
            "confidence": <0-100>
        }}
    }},
    "inferred_conflicts": ["<conflict 1>", ...],
    "unclear_elements": ["<element 1>", ...],
    "overall_confidence": <0-100>
}}
"""
```

**Acceptance Criteria:**
- [ ] **NEVER** accesses original_story (enforced by state filtering)
- [ ] Produces honest reconstruction based only on panels
- [ ] Identifies unclear/ambiguous elements
- [ ] Provides confidence scores

---

#### Task 2.4: Create Evaluator Node (Node 4)
**File:** `backend/app/services/fidelity/evaluator.py`

**Description:** Compares original story to reconstruction, identifies gaps.

**Implementation Strategy:**
```python
class FidelityEvaluator:
    """
    Compares ground truth to blind reader's reconstruction.
    Identifies specific information gaps and generates actionable critique.
    """

    async def evaluate(
        self,
        original_story: str,
        story_summary: str,
        character_motivations: dict,
        key_conflicts: List[str],
        reconstructed_story: str,
        inferred_motivations: dict,
        inferred_conflicts: List[str],
        reader_confidence: float
    ) -> FidelityEvaluation:
        """
        Returns structured evaluation with:
        - Fidelity score (0-100)
        - List of information gaps
        - Actionable critique for scripter
        """
```

**Evaluation Criteria:**

| Category | Weight | Measurement |
|----------|--------|-------------|
| Plot Accuracy | 30% | Key plot points captured |
| Motivation Clarity | 25% | Character goals understood |
| Conflict Recognition | 20% | Conflicts identified correctly |
| Emotional Beats | 15% | Emotional shifts captured |
| Coherence | 10% | Story makes logical sense |

**Gap Detection Prompt:**
```python
EVALUATOR_PROMPT = """
Compare the ORIGINAL story to the READER'S reconstruction.

ORIGINAL STORY:
{original_story}

ORIGINAL CHARACTER MOTIVATIONS:
{character_motivations}

ORIGINAL CONFLICTS:
{key_conflicts}

---

READER'S RECONSTRUCTION:
{reconstructed_story}

READER'S INFERRED MOTIVATIONS:
{inferred_motivations}

READER'S INFERRED CONFLICTS:
{inferred_conflicts}

---

Identify INFORMATION GAPS - things in the original that the reader missed or misunderstood.

For each gap:
1. Category: plot/motivation/emotion/relationship/conflict
2. Original Element: What was in the original
3. Reader's Interpretation: What the reader understood (or missed)
4. Severity: critical (breaks understanding) / major (significant confusion) / minor (small detail)
5. Suggested Fix: How the scripter can clarify this visually

Calculate Fidelity Score:
- 100%: Reader perfectly understood everything
- 80-99%: Minor gaps only
- 60-79%: Some major gaps
- Below 60%: Critical information missing

Output JSON:
{{
    "fidelity_score": <0-100>,
    "is_valid": <true if score >= 80>,
    "gaps": [
        {{
            "category": "<category>",
            "original_element": "<what was intended>",
            "reader_interpretation": "<what was understood>",
            "severity": "<severity>",
            "suggested_fix": "<actionable improvement>"
        }}
    ],
    "critique": "<structured feedback for scripter>"
}}
"""
```

**Acceptance Criteria:**
- [ ] Accurately compares original to reconstruction
- [ ] Identifies specific, actionable gaps
- [ ] Generates structured critique for scripter
- [ ] Calculates meaningful fidelity score

---

### Phase 3: Workflow Assembly

#### Task 3.1: Implement Routing Logic
**File:** `backend/app/workflows/fidelity_workflow.py`

```python
def should_continue(state: WebtoonFidelityState) -> str:
    """
    Determines next step after evaluation.

    Returns:
        "webtoon_scripter" - Continue loop (needs improvement)
        "END" - Exit loop (validated or max iterations)
    """
    # Exit if validated
    if state["is_validated"]:
        return "END"

    # Exit if max iterations reached
    if state["iteration"] >= state["max_iterations"]:
        return "END"

    # Continue loop
    return "webtoon_scripter"
```

---

#### Task 3.2: Build LangGraph Workflow
**File:** `backend/app/workflows/fidelity_workflow.py`

```python
from langgraph.graph import StateGraph, END

def create_fidelity_workflow() -> StateGraph:
    """
    Creates the fidelity validation workflow graph.

    Graph Structure:
        story_architect → webtoon_scripter → blind_reader → evaluator
                              ↑                               |
                              └───────── (if REJECT) ─────────┘
    """
    workflow = StateGraph(WebtoonFidelityState)

    # Add nodes
    workflow.add_node("story_architect", story_architect_node)
    workflow.add_node("webtoon_scripter", webtoon_scripter_node)
    workflow.add_node("blind_reader", blind_reader_node)  # Receives filtered state
    workflow.add_node("evaluator", evaluator_node)

    # Add edges
    workflow.add_edge("story_architect", "webtoon_scripter")
    workflow.add_edge("webtoon_scripter", "blind_reader")
    workflow.add_edge("blind_reader", "evaluator")

    # Conditional edge from evaluator
    workflow.add_conditional_edges(
        "evaluator",
        should_continue,
        {
            "webtoon_scripter": "webtoon_scripter",
            "END": END
        }
    )

    # Set entry point
    workflow.set_entry_point("story_architect")

    return workflow.compile()
```

**Acceptance Criteria:**
- [ ] Workflow compiles successfully
- [ ] Nodes execute in correct order
- [ ] Conditional routing works correctly
- [ ] State passes correctly between nodes

---

#### Task 3.3: Implement Node Functions with State Filtering
**File:** `backend/app/workflows/fidelity_workflow.py`

```python
async def blind_reader_node(state: WebtoonFidelityState) -> dict:
    """
    Blind Reader node with STATE ISOLATION.

    CRITICAL: Only passes script_panels and characters to the reader.
    """
    # Filter state - SECURITY CRITICAL
    filtered_input = {
        "script_panels": state["script_panels"],
        "characters": state["characters"]
    }

    # The BlindReader service only receives filtered data
    reader = BlindReader(llm_config)
    result = await reader.reconstruct_story(
        panels=filtered_input["script_panels"],
        characters=filtered_input["characters"]
    )

    return {
        "reconstructed_story": result["reconstructed_story"],
        "inferred_motivations": result["inferred_motivations"],
        "inferred_conflicts": result["inferred_conflicts"],
        "reader_confidence": result["overall_confidence"] / 100.0,
        "current_step": "blind_reader"
    }
```

---

### Phase 4: API Integration

#### Task 4.1: Create API Endpoint
**File:** `backend/app/routers/fidelity.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/fidelity", tags=["fidelity"])

class FidelityValidationRequest(BaseModel):
    seed: str
    max_iterations: int = 3

class FidelityValidationResponse(BaseModel):
    workflow_id: str
    status: str
    final_score: Optional[float]
    iterations_used: int
    script_panels: Optional[List[dict]]
    validation_history: List[dict]

@router.post("/validate")
async def validate_webtoon_fidelity(
    request: FidelityValidationRequest
) -> FidelityValidationResponse:
    """
    Run the fidelity validation workflow.

    This endpoint:
    1. Generates a story from the seed
    2. Converts it to panels
    3. Validates via blind reader
    4. Iterates until validated or max iterations
    """
    result = await run_fidelity_workflow(
        seed=request.seed,
        max_iterations=request.max_iterations
    )
    return FidelityValidationResponse(**result)
```

---

### Phase 5: Configuration

#### Task 5.1: Add Configuration Settings
**File:** `backend/app/config.py`

```python
# Add to Settings class:
fidelity_validation_threshold: float = 80.0  # Score needed to pass
fidelity_max_iterations: int = 3
fidelity_min_panel_description_length: int = 150
```

---

## Test Cases

### Unit Tests

#### Test Suite 1: State Isolation Tests
**File:** `backend/tests/test_fidelity_state_isolation.py`

```python
import pytest
from app.workflows.fidelity_workflow import blind_reader_node
from app.models.fidelity_state import WebtoonFidelityState

class TestStateIsolation:
    """
    CRITICAL: Verify that BlindReader cannot access original story.
    """

    @pytest.fixture
    def full_state(self) -> WebtoonFidelityState:
        """Create a complete state with sensitive data."""
        return {
            "seed": "test seed",
            "original_story": "SECRET: The hero is actually the villain's brother.",
            "story_summary": "SECRET SUMMARY",
            "character_motivations": {"Hero": {"goal": "SECRET GOAL"}},
            "key_conflicts": ["SECRET CONFLICT"],
            "script_panels": [
                {
                    "panel_number": 1,
                    "visual_description": "A man stands alone",
                    "dialogue": [],
                    "shot_type": "wide",
                    "environment": "city"
                }
            ],
            "characters": [{"name": "Hero"}],
            "reconstructed_story": "",
            "inferred_motivations": {},
            "inferred_conflicts": [],
            "reader_confidence": 0.0,
            "fidelity_score": 0.0,
            "information_gaps": [],
            "critique": None,
            "iteration": 1,
            "max_iterations": 3,
            "is_validated": False,
            "current_step": "webtoon_scripter",
            "error": None
        }

    def test_blind_reader_does_not_receive_original_story(self, full_state, mocker):
        """
        Verify BlindReader service is NOT called with original_story.
        """
        mock_reader = mocker.patch('app.services.fidelity.blind_reader.BlindReader')

        # Run the node
        blind_reader_node(full_state)

        # Get the call arguments
        call_args = mock_reader.return_value.reconstruct_story.call_args

        # Assert original_story was NOT passed
        assert "original_story" not in str(call_args)
        assert "SECRET" not in str(call_args)

    def test_filtered_state_only_contains_panels_and_characters(self, full_state):
        """
        Verify the filtered state structure.
        """
        from app.services.fidelity.blind_reader import BlindReaderNode

        filtered = BlindReaderNode.filter_state_for_blind_reader(full_state)

        # Should ONLY contain these keys
        assert set(filtered.keys()) == {"script_panels", "characters"}

        # Should NOT contain sensitive keys
        assert "original_story" not in filtered
        assert "story_summary" not in filtered
        assert "character_motivations" not in filtered
        assert "key_conflicts" not in filtered

    def test_blind_reader_cannot_infer_secret_from_context(self, full_state, mocker):
        """
        Integration test: Run actual BlindReader and verify
        it doesn't "know" secrets not in panels.
        """
        # Panels don't mention "brother" relationship
        result = await blind_reader_node(full_state)

        # The reconstruction should NOT contain the secret
        assert "brother" not in result["reconstructed_story"].lower()
        assert "villain's brother" not in result["reconstructed_story"].lower()
```

---

#### Test Suite 2: Convergence Tests
**File:** `backend/tests/test_fidelity_convergence.py`

```python
import pytest
from app.workflows.fidelity_workflow import run_fidelity_workflow

class TestConvergence:
    """
    Verify that the system improves over iterations.
    """

    @pytest.mark.asyncio
    async def test_fidelity_score_improves_after_revision(self):
        """
        After one iteration, fidelity score should improve.
        """
        result = await run_fidelity_workflow(
            seed="A man discovers his wife has been hiding a secret identity",
            max_iterations=2
        )

        history = result["validation_history"]

        if len(history) > 1:
            # Second score should be >= first score
            assert history[1]["fidelity_score"] >= history[0]["fidelity_score"]

    @pytest.mark.asyncio
    async def test_gap_count_decreases_after_revision(self):
        """
        Number of information gaps should decrease.
        """
        result = await run_fidelity_workflow(
            seed="Two rivals compete for a promotion",
            max_iterations=2
        )

        history = result["validation_history"]

        if len(history) > 1:
            initial_gaps = len(history[0]["information_gaps"])
            revised_gaps = len(history[1]["information_gaps"])

            # Should have fewer or equal gaps
            assert revised_gaps <= initial_gaps

    @pytest.mark.asyncio
    async def test_passes_within_max_iterations(self):
        """
        System should typically pass within 3 iterations for simple seeds.
        """
        result = await run_fidelity_workflow(
            seed="A simple love story",
            max_iterations=3
        )

        # Should either pass or use all iterations
        assert result["status"] in ["validated", "max_iterations_reached"]

    @pytest.mark.asyncio
    async def test_complex_story_may_need_multiple_iterations(self):
        """
        Complex stories with hidden subplots need more iterations.
        """
        result = await run_fidelity_workflow(
            seed="A detective realizes the victim staged their own death to frame their business partner",
            max_iterations=3
        )

        # Complex plots typically need revision
        assert result["iterations_used"] >= 1
```

---

#### Test Suite 3: Routing Logic Tests
**File:** `backend/tests/test_fidelity_routing.py`

```python
import pytest
from app.workflows.fidelity_workflow import should_continue

class TestRoutingLogic:
    """
    Verify conditional routing behavior.
    """

    def test_returns_end_when_validated(self):
        """Pass immediately when is_validated is True."""
        state = {
            "is_validated": True,
            "iteration": 1,
            "max_iterations": 3
        }
        assert should_continue(state) == "END"

    def test_returns_end_when_max_iterations_reached(self):
        """Stop when iteration >= max_iterations."""
        state = {
            "is_validated": False,
            "iteration": 3,
            "max_iterations": 3
        }
        assert should_continue(state) == "END"

    def test_returns_scripter_when_not_validated(self):
        """Continue loop when validation failed."""
        state = {
            "is_validated": False,
            "iteration": 1,
            "max_iterations": 3
        }
        assert should_continue(state) == "webtoon_scripter"

    def test_iteration_counter_increments(self):
        """Verify iteration tracking."""
        state = {
            "is_validated": False,
            "iteration": 2,
            "max_iterations": 5
        }
        # Should continue (2 < 5)
        assert should_continue(state) == "webtoon_scripter"

        state["iteration"] = 5
        # Should stop (5 >= 5)
        assert should_continue(state) == "END"
```

---

#### Test Suite 4: Component Tests
**File:** `backend/tests/test_fidelity_components.py`

```python
import pytest
from app.services.fidelity.story_architect import StoryArchitect
from app.services.fidelity.webtoon_scripter import WebtoonScripter
from app.services.fidelity.blind_reader import BlindReader
from app.services.fidelity.evaluator import FidelityEvaluator

class TestStoryArchitect:
    """Test Node 1: Story generation."""

    @pytest.mark.asyncio
    async def test_generates_story_with_required_fields(self):
        """Output must contain all required fields."""
        architect = StoryArchitect(llm_config)
        result = await architect.generate_story("A chef opens a restaurant")

        assert "story" in result
        assert "character_motivations" in result
        assert "key_conflicts" in result
        assert len(result["story"]) > 100  # Meaningful length

    @pytest.mark.asyncio
    async def test_character_motivations_are_structured(self):
        """Motivations must have goal/motivation/obstacle."""
        architect = StoryArchitect(llm_config)
        result = await architect.generate_story("A teacher helps a struggling student")

        for name, motivation in result["character_motivations"].items():
            assert "goal" in motivation
            assert "motivation" in motivation or "why" in motivation


class TestWebtoonScripter:
    """Test Node 2: Panel generation."""

    @pytest.mark.asyncio
    async def test_generates_panels_from_story(self):
        """Should produce 8-12 panels."""
        scripter = WebtoonScripter(llm_config)
        result = await scripter.convert_to_panels(
            story="A short story about friendship...",
            character_motivations={}
        )

        assert 8 <= len(result["panels"]) <= 12

    @pytest.mark.asyncio
    async def test_panels_have_visual_descriptions(self):
        """Each panel must have visual description."""
        scripter = WebtoonScripter(llm_config)
        result = await scripter.convert_to_panels(
            story="A story...",
            character_motivations={}
        )

        for panel in result["panels"]:
            assert "visual_description" in panel
            assert len(panel["visual_description"]) >= 50

    @pytest.mark.asyncio
    async def test_revision_incorporates_critique(self):
        """Revised panels should address critique."""
        scripter = WebtoonScripter(llm_config)

        initial_panels = [...]  # Mock initial panels
        critique = "The reader didn't understand why the hero was angry. ADD visual cues showing his frustration."

        result = await scripter.revise_panels(
            current_panels=initial_panels,
            critique=critique
        )

        # Check that some panel mentions anger/frustration
        all_descriptions = " ".join(p["visual_description"] for p in result["panels"])
        anger_words = ["angry", "frustration", "furious", "clenched", "scowl"]
        assert any(word in all_descriptions.lower() for word in anger_words)


class TestBlindReader:
    """Test Node 3: Story reconstruction."""

    @pytest.mark.asyncio
    async def test_produces_coherent_reconstruction(self):
        """Output must be a readable story."""
        reader = BlindReader(llm_config)
        result = await reader.reconstruct_story(
            panels=[
                {"visual_description": "A man in a suit enters an office", "dialogue": []},
                {"visual_description": "He looks worried", "dialogue": [{"character": "Man", "text": "I need to tell you something"}]}
            ],
            characters=[{"name": "Man"}]
        )

        assert len(result["reconstructed_story"]) > 50

    @pytest.mark.asyncio
    async def test_identifies_unclear_elements(self):
        """Should flag ambiguous panels."""
        reader = BlindReader(llm_config)
        result = await reader.reconstruct_story(
            panels=[
                {"visual_description": "Someone stands", "dialogue": []},  # Vague
            ],
            characters=[]
        )

        assert len(result.get("unclear_elements", [])) > 0

    @pytest.mark.asyncio
    async def test_confidence_correlates_with_clarity(self):
        """Clear panels = higher confidence."""
        reader = BlindReader(llm_config)

        # Vague panels
        vague_result = await reader.reconstruct_story(
            panels=[{"visual_description": "Things happen", "dialogue": []}],
            characters=[]
        )

        # Clear panels
        clear_result = await reader.reconstruct_story(
            panels=[
                {
                    "visual_description": "A young woman with red hair sits at a cafe, nervously checking her phone",
                    "dialogue": [{"character": "Emma", "text": "He's late again..."}]
                }
            ],
            characters=[{"name": "Emma"}]
        )

        assert clear_result["overall_confidence"] > vague_result["overall_confidence"]


class TestFidelityEvaluator:
    """Test Node 4: Comparison and scoring."""

    @pytest.mark.asyncio
    async def test_perfect_match_scores_100(self):
        """Identical stories should score 100%."""
        evaluator = FidelityEvaluator(llm_config)

        story = "A simple story about X."
        result = await evaluator.evaluate(
            original_story=story,
            story_summary="Summary",
            character_motivations={},
            key_conflicts=[],
            reconstructed_story=story,  # Identical
            inferred_motivations={},
            inferred_conflicts=[],
            reader_confidence=1.0
        )

        assert result.fidelity_score >= 90.0

    @pytest.mark.asyncio
    async def test_identifies_missing_motivation(self):
        """Detect when reader misses character motivation."""
        evaluator = FidelityEvaluator(llm_config)

        result = await evaluator.evaluate(
            original_story="John wants revenge because his brother was killed.",
            character_motivations={"John": {"goal": "revenge", "motivation": "brother killed"}},
            key_conflicts=["revenge"],
            reconstructed_story="John seems upset about something.",  # Missing motivation
            inferred_motivations={"John": {"apparent_goal": "unknown"}},
            inferred_conflicts=[],
            reader_confidence=0.3
        )

        # Should identify the gap
        gap_categories = [g["category"] for g in result.gaps]
        assert "motivation" in gap_categories

    @pytest.mark.asyncio
    async def test_critique_is_actionable(self):
        """Critique should contain specific instructions."""
        evaluator = FidelityEvaluator(llm_config)

        result = await evaluator.evaluate(
            original_story="The villain smirks because he knows the hero's weakness.",
            character_motivations={"Villain": {"goal": "defeat hero"}},
            key_conflicts=["hero vs villain"],
            reconstructed_story="There's a bad guy.",
            inferred_motivations={},
            inferred_conflicts=[],
            reader_confidence=0.2
        )

        # Critique should mention what to add
        assert len(result.critique) > 50
        assert any(word in result.critique.lower() for word in ["add", "show", "include", "clarify"])
```

---

### Integration Tests

#### Test Suite 5: Full Workflow Tests
**File:** `backend/tests/test_fidelity_workflow_integration.py`

```python
import pytest
from app.workflows.fidelity_workflow import run_fidelity_workflow

class TestFullWorkflow:
    """End-to-end workflow tests."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_completes_without_error(self):
        """Basic smoke test."""
        result = await run_fidelity_workflow(
            seed="A detective solves a mystery",
            max_iterations=2
        )

        assert result["status"] in ["validated", "max_iterations_reached"]
        assert result["script_panels"] is not None
        assert len(result["script_panels"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_preserves_story_integrity(self):
        """Original story should remain unchanged through iterations."""
        result = await run_fidelity_workflow(
            seed="A unique story about a purple elephant",
            max_iterations=3
        )

        # All iterations should reference same original story
        original = result["validation_history"][0].get("original_story_hash")
        for iteration in result["validation_history"]:
            assert iteration.get("original_story_hash") == original

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_json_output_valid(self):
        """Final output must be valid JSON for image generation."""
        result = await run_fidelity_workflow(
            seed="A romantic comedy",
            max_iterations=2
        )

        panels = result["script_panels"]

        # Each panel must have required fields
        for panel in panels:
            assert "panel_number" in panel
            assert "visual_description" in panel
            assert isinstance(panel.get("dialogue", []), list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_handles_llm_failure_gracefully(self, mocker):
        """System should handle LLM errors without crashing."""
        # Mock LLM to fail on second call
        mock_llm = mocker.patch('app.services.llm_config.LLMConfig.get_model')
        mock_llm.return_value.ainvoke.side_effect = [
            {"story": "...", "character_motivations": {}, "key_conflicts": []},  # First call succeeds
            Exception("LLM API Error")  # Second call fails
        ]

        result = await run_fidelity_workflow(seed="Test", max_iterations=2)

        assert result["error"] is not None
        assert result["status"] == "error"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_validation_history_tracks_all_iterations(self):
        """Each iteration should be recorded."""
        result = await run_fidelity_workflow(
            seed="A complex story requiring revision",
            max_iterations=3
        )

        history = result["validation_history"]

        # Should have at least 1 iteration
        assert len(history) >= 1

        # Each entry should have score and gaps
        for entry in history:
            assert "fidelity_score" in entry
            assert "information_gaps" in entry
            assert "iteration" in entry
```

---

### Performance Tests

#### Test Suite 6: Performance & Limits
**File:** `backend/tests/test_fidelity_performance.py`

```python
import pytest
import time

class TestPerformance:
    """Performance and limit testing."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_single_iteration_completes_in_reasonable_time(self):
        """One iteration should complete in < 60 seconds."""
        start = time.time()

        result = await run_fidelity_workflow(
            seed="Quick test",
            max_iterations=1
        )

        elapsed = time.time() - start
        assert elapsed < 60

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_max_iterations_enforced(self):
        """System must stop at max_iterations."""
        result = await run_fidelity_workflow(
            seed="Impossible to understand story xyz123",
            max_iterations=2
        )

        assert result["iterations_used"] <= 2

    @pytest.mark.asyncio
    async def test_handles_long_seed_input(self):
        """Should handle very long seed text."""
        long_seed = "A story about " + "adventures and " * 100 + "endings."

        result = await run_fidelity_workflow(
            seed=long_seed,
            max_iterations=1
        )

        assert result["status"] != "error"
```

---

## File Structure Summary

```
backend/
├── app/
│   ├── models/
│   │   └── fidelity_state.py          # Task 1.1, 1.2
│   ├── services/
│   │   └── fidelity/
│   │       ├── __init__.py
│   │       ├── story_architect.py     # Task 2.1
│   │       ├── webtoon_scripter.py    # Task 2.2
│   │       ├── blind_reader.py        # Task 2.3
│   │       └── evaluator.py           # Task 2.4
│   ├── workflows/
│   │   └── fidelity_workflow.py       # Task 3.1, 3.2, 3.3
│   ├── routers/
│   │   └── fidelity.py                # Task 4.1
│   └── config.py                      # Task 5.1 (modifications)
└── tests/
    ├── test_fidelity_state_isolation.py
    ├── test_fidelity_convergence.py
    ├── test_fidelity_routing.py
    ├── test_fidelity_components.py
    ├── test_fidelity_workflow_integration.py
    └── test_fidelity_performance.py
```

---

## Implementation Order

### Recommended Sequence:

1. **Phase 1** (Foundation)
   - Task 1.1: State schema
   - Task 1.2: Response models

2. **Phase 2** (Core Logic)
   - Task 2.1: StoryArchitect
   - Task 2.2: WebtoonScripter
   - Task 2.3: BlindReader (with isolation)
   - Task 2.4: Evaluator

3. **Phase 3** (Integration)
   - Task 3.1: Routing logic
   - Task 3.2: LangGraph workflow
   - Task 3.3: Node functions

4. **Phase 4** (API)
   - Task 4.1: REST endpoint

5. **Phase 5** (Polish)
   - Task 5.1: Configuration
   - All test suites

---

## Success Criteria Checklist

- [ ] **State Isolation**: BlindReader cannot access original_story (verified by tests)
- [ ] **Convergence**: Fidelity score improves across iterations (verified by tests)
- [ ] **JSON Output**: Final panels are valid JSON ready for image generation
- [ ] **Loop Termination**: System exits after validation OR max iterations
- [ ] **Error Handling**: Graceful failure on LLM errors
- [ ] **Performance**: Single iteration < 60 seconds

---

## Notes for Implementation

1. **State Isolation is CRITICAL**: The blind reader node must use a filtered state. This is the core of the validation concept.

2. **Reuse Existing Patterns**: The codebase already has LangGraph workflows with TypedDict state - follow the same patterns in `webtoon_workflow.py`.

3. **Existing Services**: Consider reusing or extending `WebtoonWriter` for the scripter node instead of creating from scratch.

4. **Testing First**: Write state isolation tests before implementing blind_reader_node to ensure the architecture enforces isolation.
