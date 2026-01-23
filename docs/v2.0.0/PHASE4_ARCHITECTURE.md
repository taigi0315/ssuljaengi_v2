# Phase 4 Architecture – Agent-Based Webtoon Generation

## 개요

Phase 4에서는 기존 모놀리식(monolithic) 웹툰 생성 시스템을 **모듈화된 에이전트 기반 아키텍처**로 전환했습니다. 각 에이전트는 특정 작업을 담당하며, LangGraph를 사용하여 orchestration됩니다.

## 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT (User Story)                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Story Analyst Agent   │
                    │  - Extracts key info    │
                    │  - Estimates scene count│
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Scene Planner Agent    │
                    │  - Generates script     │
                    │  - Creates panels       │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Cinematographer Agent   │
                    │  - Analyzes shot types  │
                    │  - Calculates variety   │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Mood Designer Agent    │
                    │  - Assigns moods        │
                    │  - Detects context      │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Visual Prompter Agent   │
                    │  - Enhances prompts     │
                    │  - Adds style & mood    │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   SFX Planner Agent     │
                    │  - Plans visual effects │
                    │  - Analyzes coverage    │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Panel Composer Agent    │
                    │  - Groups into pages    │
                    │  - Calculates layout    │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Evaluator Node       │
                    │  - Scores quality       │
                    │  - Identifies issues    │
                    └─────────────────────────┘
                                 │
                         ┌───────┴───────┐
                         │               │
                Score ≥ Threshold?     Score < Threshold?
                         │               │
                         │               ▼
                         │      ┌─────────────────┐
                         │      │ Rewriter Node   │
                         │      │ - Targeted fix  │
                         │      └─────────────────┘
                         │               │
                         │               │ (max rewrites)
                         │               └────────┐
                         │                        │
                         ▼                        ▼
                    ┌─────────────────────────────────┐
                    │  FINAL OUTPUT (Webtoon Script)  │
                    └─────────────────────────────────┘
```

## 에이전트 목록

### 1. Story Analyst (`story_analyst.py`)

- **책임**: 입력 스토리 분석, 씬 개수 추정
- **입력**: 원본 스토리 텍스트
- **출력**: `story_analysis` (씬 개수, 장르 등)

### 2. Scene Planner (`scene_planner.py`)

- **책임**: 씬 구조화, 스크립트 생성
- **입력**: 스토리 + 장르 + 스타일
- **출력**: `WebtoonScript` (characters, panels)

### 3. Cinematographer (`cinematographer.py`)

- **책임**: 샷 타입 분석, 다양성 메트릭 계산
- **입력**: 패널 리스트
- **출력**: `shot_plan` (shot distribution, variety ratio)

### 4. Mood Designer (`mood_designer.py`)

- **책임**: 씬별 무드 할당
- **입력**: 패널 리스트 (emotional_intensity 포함)
- **출력**: `mood_assignments` (각 패널의 무드 정보)

### 5. Visual Prompter (`visual_prompter.py`)

- **책임**: 이미지 생성 프롬프트 강화
- **입력**: 패널 + 무드 정보
- **출력**: `enhanced_prompts` (스타일·무드가 적용된 프롬프트)

### 6. SFX Planner (`sfx_planner.py`)

- **책임**: 시각 효과 계획 및 분석
- **입력**: 패널 리스트 (sfx_effects 포함)
- **출력**: `sfx_plan` (coverage, distribution)

### 7. Panel Composer (`panel_composer.py`)

- **책임**: 패널을 페이지로 그룹핑
- **입력**: 패널 리스트
- **출력**: `page_groupings` + `page_statistics`

## LangGraph 워크플로우

### State Model: `EnhancedWebtoonState`

```python
class EnhancedWebtoonState(TypedDict):
    # Input
    story: str
    story_genre: str
    image_style: str

    # Agent outputs
    story_analysis: Optional[Dict[str, Any]]
    scene_plan: Optional[Dict[str, Any]]
    webtoon_script: Optional[dict]
    shot_plan: Optional[Dict[str, Any]]
    mood_assignments: Optional[List[dict]]
    enhanced_prompts: Optional[List[str]]
    sfx_plan: Optional[Dict[str, Any]]
    page_groupings: Optional[List[dict]]

    # Evaluation
    evaluation_score: float
    evaluation_feedback: str
    evaluation_issues: List[str]

    # Rewrite tracking
    rewrite_count: int
    rewrite_history: List[Dict[str, Any]]
    target_agent: Optional[str]

    # Workflow state
    current_step: str
    error: Optional[str]
```

### Graph Flow

1. **Entry Point**: `story_analyst`
2. **Sequential Edges**:
   - `story_analyst` → `scene_planner`
   - `scene_planner` → `cinematographer`
   - `cinematographer` → `mood_designer`
   - `mood_designer` → `visual_prompter`
   - `visual_prompter` → `sfx_planner`
   - `sfx_planner` → `panel_composer`
   - `panel_composer` → `evaluator`

3. **Conditional Routing** (after `evaluator`):
   - If `score >= threshold` or `rewrite_count >= max_rewrites` → `END`
   - If `score < threshold` → `rewriter` → loop back to `cinematographer`

### Rewrite Loop

- **Targeted Rewriting**: `identify_rewrite_target()` 함수가 평가 피드백을 분석하여 어떤 에이전트를 재실행할지 결정합니다.
- **Issue → Agent Mapping**:
  - `scene_count`, `story_structure` → `Scene Planner`
  - `shot_variety`, `visual_dynamism` → `Cinematographer`
  - `visual_prompt` → `Visual Prompter`
  - `page`, `grouping` → `Panel Composer`

## 테스트 결과

### Agent Unit Tests (`test_agents.py`)

- ✅ 6 tests passing
- Coverage: Story Analyst, Cinematographer, Mood Designer, Visual Prompter, SFX Planner, Panel Composer

### Workflow Node Tests (`test_workflow_nodes.py`)

- ✅ 6 tests passing
- Coverage: Graph structure + 5 standalone node tests

### Total: 12/12 tests passing

## 사용 예시

```python
from app.workflows.enhanced_webtoon_workflow import enhanced_webtoon_workflow

# Prepare initial state
initial_state = {
    "story": "Your webtoon story here...",
    "story_genre": "MODERN_ROMANCE_DRAMA",
    "image_style": "SOFT_ROMANTIC_WEBTOON",
    "evaluation_score": 0.0,
    "rewrite_count": 0,
    # ... (other fields initialized)
}

# Execute workflow
result = await enhanced_webtoon_workflow.ainvoke(initial_state)

# Access results
script = result["webtoon_script"]
panels = result["panels"]
page_groupings = result["page_groupings"]
evaluation_score = result["evaluation_score"]
```

## 향후 개선 사항

1. **Agent 모듈 완전 분리**: 현재 일부 에이전트는 기존 서비스에 의존합니다. 향후 각 에이전트가 독립적인 LLM 호출을 하도록 개선 필요.
2. **Streaming Support**: LangGraph의 스트리밍 기능을 활용하여 실시간 진행 상황 표시.
3. **Canvas Integration**: 각 에이전트가 생성한 중간 결과를 Canvas에 시각화.
4. **Performance Optimization**: 병렬 실행 가능한 에이전트 식별 및 최적화.
5. **Advanced Routing**: 조건부 라우팅을 더 정교하게 만들어 특정 이슈에 대해 정확한 에이전트만 재실행.

---

**Version**: v2.0.0  
**Date**: 2026-01-22  
**Status**: ✅ Phase 4.1–4.2 Complete
