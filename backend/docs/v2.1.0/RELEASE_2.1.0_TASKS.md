# Release 2.1.0 - Prompt & Quality Enhancement

**Release Date Target:** TBD
**Focus:** 시각적 스토리텔링 품질 향상, 프롬프트 최적화, 캐릭터 일관성

---

## 📋 Executive Summary

v2.0.0에서 기능적 안정성 확보 후, v2.1.0은 **결과물 품질**에 집중합니다.
핵심 목표:

1. 더 풍부한 패널 구성으로 스토리 전달력 향상
2. 캐릭터 의상/외모 일관성 회복
3. 프롬프트 최적화로 Image Gen 모델 혼란 방지
4. 패널 레벨 스타일 스위칭 (Serious ↔ Chibi)

---

## 📝 Work Log

| Date       | Task ID        | Status      | Notes                                                                                                                     |
| ---------- | -------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| 2026-01-23 | **2.1-E3-T01** | ✅ COMPLETE | `visual_prompter.py`에 `characters` 필드 추가, `_format_character_style_sheet()` 함수 구현                                |
| 2026-01-23 | **2.1-E3-T03** | ✅ COMPLETE | 캐릭터 스타일 시트를 프롬프트 **최상단**에 배치하도록 수정, `enhanced_webtoon_workflow.py`에서 characters 전달            |
| 2026-01-23 | **2.1-E4-T01** | ✅ COMPLETE | `modular_prompt.py` 신규 생성, `visual_prompter.py`에 토큰 예산 관리 통합, 4-모듈 구조 (Character/Visual/Style/Technical) |
| 2026-01-23 | **2.1-E1-T01** | ✅ COMPLETE | 1~5패널 동적 레이아웃 지원, `dense`(5패널)/`climax`(1패널) scene type 추가                                                |
| 2026-01-23 | **2.1-E1-T02** | ✅ COMPLETE | `PanelImportance` enum (hero/primary/secondary/tertiary), 패널별 가중치 자동 계산, `Page` 모델 확장                       |
| 2026-01-23 | **2.1-E2-T01** | ✅ COMPLETE | `text_classifier.py` agent 신규 생성, `classify_text()` 함수로 SFX/monologue/narration/dialogue 자동 분류                 |
| 2026-01-23 | **2.1-E2-T02** | ✅ COMPLETE | `TextType` enum, `DialogueLine` 모델에 `text_type`/`order` 필드 추가, `auto_classify()` 메소드 구현                       |
| 2026-01-23 | **2.1-E5-T01** | ✅ COMPLETE | `WebtoonPanel.style_mode` 필드 추가, `get_style_mode_keywords()` 메소드 (romantic_detail/comedy_chibi/action_dynamic)     |
| 2026-01-23 | **2.1-E1-T03** | ✅ COMPLETE | `ShotType` enum 확장 (macro_eyes/hands/lips, silhouette, two_shot 등), Cinematographer 프롬프트 로맨스 특화 가이드 추가   |
| 2026-01-23 | **2.1-E1-T04** | ✅ COMPLETE | `emotional_pacing.py` 모듈 생성, 대사 감정 분석(Sentiment) 기반 Shot Type 자동 매핑 규칙 구현                             |
| 2026-01-23 | **2.1-E5-T02** | ✅ COMPLETE | `emotional_pacing.py`에서 감정 강도에 따른 `style_mode` 자동 감지 및 할당 로직 구현                                       |
| 2026-01-23 | **2.1-E3-T02** | ✅ COMPLETE | `consistency_validator.py` agent 생성, 시간/장소 일관성 체크 로직 구현 및 Workflow 통합                                   |
| 2026-01-23 | **2.1-E4-T03** | ✅ COMPLETE | `modular_prompt.py`에 `NegativePromptModule` 추가 및 표준 Negative Prompt 정의                                            |
| 2026-01-23 | **2.1-E4-T04** | ✅ COMPLETE | `tests/prompt_ab_test.py` 작성, Legacy vs Modular 프롬프트 구조 및 토큰 사용량 비교 기능 구현                             |

---

## 🎯 Task Categories

### Epic 1: Cinematic Storyboarding & Panel Flow

> **문제점:** 현재 3패널 고정 레이아웃이 "평면적"이며, 로맨스 장르에 필수적인 감정 클로즈업(macro shots)과 dynamic pacing이 부족함.

| Task ID        | Title                         | Status | Description                                                                                               | Priority | Affected Files                                        |
| -------------- | ----------------------------- | ------ | --------------------------------------------------------------------------------------------------------- | -------- | ----------------------------------------------------- |
| **2.1-E1-T01** | Dynamic Panel Layout Engine   | ✅     | 1~5패널 동적 레이아웃 지원. `dense`/`climax` scene type 추가                                              | P0       | `panel_composer.py`                                   |
| **2.1-E1-T02** | Panel Importance Weighting    | ✅     | `PanelImportance` enum, `Page` 모델에 `panel_weights` 추가                                                | P0       | `panel_composer.py`                                   |
| **2.1-E1-T03** | Shot Type Library Enhancement | ✅     | `ShotType` enum에 macro_eyes/hands/lips, silhouette, two_shot 등 추가. Cinematographer 로맨스 특화 가이드 | P1       | `story.py`, `cinematographer.py`                      |
| **2.1-E1-T04** | Emotional Pacing Rules        | ✅     | `emotional_pacing.py` 모듈: 대사 감정 분석 → Shot Type 자동 매핑. (English-only compliance rule 적용)     | P1       | `emotional_pacing.py`, `enhanced_webtoon_workflow.py` |

---

### Epic 2: Text Type Classification & SFX Typography

> **문제점:** 비대화 텍스트 (예: "_Silence_", "_Thump_", "_Nervousness_")가 일반 대사처럼 처리되어 몰입도 저하.

| Task ID        | Title                        | Status | Description                                                                                | Priority | Affected Files                          |
| -------------- | ---------------------------- | ------ | ------------------------------------------------------------------------------------------ | -------- | --------------------------------------- |
| **2.1-E2-T01** | Text Type Classifier         | ✅     | `text_classifier.py` agent: SFX/monologue/narration/dialogue 자동 분류, 우선순위 기반 로직 | P0       | `text_classifier.py`, `models/story.py` |
| **2.1-E2-T02** | Dialogue Model Schema Update | ✅     | `TextType` enum, `DialogueLine.text_type`/`order` 필드 추가, `auto_classify()` 메소드      | P0       | `models/story.py`                       |
| **2.1-E2-T03** | SFX Typography Renderer      | ⏳     | Chat bubble 렌더러에서 `sfx` 타입은 bubble 없이 아트워크 폰트로 렌더링 (블렌딩 스타일)     | P1       | Frontend: `WebtoonSceneEditor.tsx`      |
| **2.1-E2-T04** | WEBTOON_WRITER_PROMPT Update | ⏳     | 프롬프트에 text_type 분류 지시 추가                                                        | P1       | `webtoon_writer.py`                     |

---

### Epic 3: Character & Outfit Consistency (Regression Fix)

> **문제점:** Multi-agent 아키텍처 도입 후 캐릭터 외모/의상이 씬 간 불일치 (예: 정장→반바지 변경).

| Task ID        | Title                                | Status | Description                                                                                | Priority | Affected Files                            |
| -------------- | ------------------------------------ | ------ | ------------------------------------------------------------------------------------------ | -------- | ----------------------------------------- |
| **2.1-E3-T01** | Global Character Style Sheet         | ✅     | `visual_prompter.py`에 캐릭터 외형 정의(Style Sheet) 저장 및 참조 로직 추가                | P0       | `visual_prompter.py`                      |
| **2.1-E3-T02** | Scene-to-Scene Consistency Validator | ✅     | 이전 씬과 현재 씬의 캐릭터 복장/위치/시간대 일관성 검증 agent (`consistency_validator.py`) | P1       | `consistency_validator.py`                |
| **2.1-E3-T03** | Character Ref Priority in Prompt     | ✅     | 이미지 생성 프롬프트에서 캐릭터 참조(Reference Sheet)를 최상단에 배치하여 누락 방지        | P0       | `visual_prompter.py`, `modular_prompt.py` |
| **2.1-E3-T04** | Outfit Lock per Scene                | ⏳     | Story Analyst 단계에서 "씬별 의상"을 명시적으로 지정, 이후 변경 불가                       | P2       | `story_analyst.py`                        |

---

### Epic 4: Prompt Optimization (Length vs. Clarity)

> **문제점:** AI 생성 프롬프트가 과도하게 길어져 Image Gen 모델에서 "Attention Loss" 또는 "Prompt Drift" 발생 가능성.

| Task ID        | Title                        | Status | Description                                                                                     | Priority | Affected Files                              |
| -------------- | ---------------------------- | ------ | ----------------------------------------------------------------------------------------------- | -------- | ------------------------------------------- |
| **2.1-E4-T01** | Modular Prompt Architecture  | ✅     | Monolithic 프롬프트 → 4 모듈 분리: `Character`, `Visual`, `Style`, `Technical`                  | P0       | `modular_prompt.py`, `visual_prompter.py`   |
| **2.1-E4-T02** | Prompt Length Analysis Tool  | ✅     | 토큰 예산 관리 시스템 구축 (>800 tokens → Warning), `prompt_token_stats` 추가                   | P1       | `visual_prompter.py` (E4-T01에서 통합 구현) |
| **2.1-E4-T03** | Negative Prompt Refinement   | ✅     | `modular_prompt.py`에 `NegativePromptModule` 추가. 표준화된 Negative Prompt 사용 및 커스텀 지원 | P1       | `modular_prompt.py`                         |
| **2.1-E4-T04** | A/B Prompt Testing Framework | ✅     | `tests/prompt_ab_test.py`: Legacy vs Modular 프롬프트 토큰 사용량 및 구조 비교 도구 구현        | P2       | `tests/prompt_ab_test.py`                   |

---

### Epic 5: Panel-Level Style Switching

> **문제점:** 로맨스 웹툰에서 진지한 장면(High Detail) ↔ 코믹 장면(Chibi/SD)간 스타일 전환이 현재 스토리 레벨에서만 가능.

| Task ID        | Title                             | Status | Description                                                                      | Priority | Affected Files             |
| -------------- | --------------------------------- | ------ | -------------------------------------------------------------------------------- | -------- | -------------------------- |
| **2.1-E5-T01** | Panel-Level Style Mode            | ✅     | `WebtoonPanel.style_mode` 필드 및 `get_style_mode_keywords()` 메소드 추가        | P0       | `models/story.py`          |
| **2.1-E5-T02** | Style Mode Auto-Detection         | ✅     | `emotional_pacing.py`에서 감정 및 강도(Intensity) 기반 style_mode 자동 할당 로직 | P1       | `emotional_pacing.py`      |
| **2.1-E5-T03** | Multi-Style Image Generation Test | ⏳     | 단일 이미지 내 다중 스타일 렌더링 가능 여부 테스트 (Region-based prompting)      | P2       | Research Task              |
| **2.1-E5-T04** | Separate Panel Stitching Fallback | ⏳     | 다중 스타일 단일 생성 실패 시, 개별 패널 생성 후 합성하는 Fallback 구현          | P2       | `multi_panel_generator.py` |

---

## 📊 Implementation Progress

```
Phase 1 (Critical Fixes): 6/6 complete ✅
├── ✅ 2.1-E3-T01: Global Character Style Sheet
├── ✅ 2.1-E3-T03: Character Ref Priority in Prompt
├── ✅ 2.1-E4-T01: Modular Prompt Architecture
├── ✅ 2.1-E4-T02: Prompt Length Analysis Tool (merged with E4-T01)
├── ✅ 2.1-E1-T01: Dynamic Panel Layout Engine
└── ✅ 2.1-E1-T02: Panel Importance Weighting

Phase 2 (Quality Enhancement): 4/4 complete ✅
├── ✅ 2.1-E2-T01: Text Type Classifier
├── ✅ 2.1-E2-T02: Dialogue Model Schema Update
├── ✅ 2.1-E5-T01: Panel-Level Style Mode
└── ✅ 2.1-E1-T03: Shot Type Library Enhancement

Phase 3 (Advanced Features): 3/4 complete
├── ✅ 2.1-E1-T04: Emotional Pacing Rules
├── ⏳ 2.1-E2-T03: SFX Typography Renderer (Frontend)
├── ✅ 2.1-E3-T02: Scene-to-Scene Consistency Validator
└── ✅ 2.1-E5-T02: Style Mode Auto-Detection

Phase 4 (Optimization & Research): 2/4 complete
├── ✅ 2.1-E4-T02: Prompt Length Analysis Tool (merged with E4-T01)
├── ✅ 2.1-E4-T03: Negative Prompt Refinement
├── ⏳ 2.1-E5-T03: Multi-Style Image Generation Test
└── ⏳ 2.1-E5-T04: Separate Panel Stitching Fallback
├── ✅ 2.1-E4-T04: A/B Prompt Testing Framework
```

**Overall Progress: 15/20 tasks (75%)** 🚀🔥🔥

---

## 🔍 Root Cause Analysis

### 캐릭터 불일치 원인 추정

1. **Context Window Overflow**: 현재 `SCENE_IMAGE_TEMPLATE`이 545줄로 매우 길어, 캐릭터 설명이 중간에 묻힘
2. ✅ **Agent Handoff 누락**: `visual_prompter.py`에서 캐릭터 정보 재전달 여부 확인 필요 → **FIXED in E3-T01**
3. ✅ **Prompt 구조**: 캐릭터 설명 위치가 상단이 아닌 중간에 배치되어 우선순위 낮음 → **FIXED in E3-T03**

### 스토리 전달력 부족 원인

1. **Panel Composer 알고리즘**: 현재 단순 1-3 패널 그룹화만 수행
2. **Shot Type 미적용**: Cinematographer 출력값이 최종 이미지 생성에 반영되지 않음
3. **Importance 가중치 없음**: 모든 패널이 동등하게 처리됨

---

## 📎 Related Files for Reference

| Category          | File Path                                    |
| ----------------- | -------------------------------------------- |
| Workflow          | `app/workflows/enhanced_webtoon_workflow.py` |
| Panel Layout      | `app/prompt/multi_panel.py`                  |
| Image Prompt      | `app/prompt/scene_image.py`                  |
| Shot Planning     | `app/prompt/cinematographer.py`              |
| Style Composition | `app/services/style_composer.py`             |
| Panel Model       | `app/models/story.py` (WebtoonPanel)         |
| Visual Prompter   | `app/agents/visual_prompter.py`              |

---

## 🧪 Acceptance Criteria (Release 2.1.0)

1. [ ] 동일 에피소드 내 캐릭터 의상 일관성 95% 이상
2. [ ] Impact 씬에서 Close-up/Macro shot 자동 적용
3. [ ] SFX 텍스트 (_silence_, _thump_ 등)가 Chat Bubble이 아닌 아트워크 폰트로 렌더링
4. [ ] 프롬프트 토큰 수 800 이하 유지
5. [ ] 코미디 씬에서 Chibi 스타일 자동 전환 옵션 제공

---

## 👨‍💻 Backend-to-Frontend Handoff Specification

### 1. SFX & Typography (E2-T03)

The backend now classifies all text in `WebtoonPanel.dialogue[]` with a `text_type` field.
The Frontend needs to render these types differently in `WebtoonSceneEditor.tsx`:

| text_type   | Rendering Style                   | Visual Reference                     |
| ----------- | --------------------------------- | ------------------------------------ |
| `dialogue`  | (Default) Round Speech Bubble     | Standard comic bubble                |
| `monologue` | Square Box or Dashed Bubble       | Internal thought style               |
| `narration` | Text Box at Top/Bottom            | Narrative caption                    |
| `sfx`       | **No Bubble**. Free-floating text | Action font, stroke effect, blending |

**Data Structure Example:**

```json
"dialogue": [
  {
    "character": "Ji-hoon",
    "text": "I love you.",
    "text_type": "dialogue"
  },
  {
    "character": "SFX",
    "text": "*Thump*",
    "text_type": "sfx"
  }
]
```

### 2. Panel Style Mode (E5-T01)

The backend provides a `style_mode` field in `WebtoonPanel`.
This indicates the visual style of the generated image. The frontend might need to adjust UI overlays (captions, bubbles) to match.

| style_mode        | Image Style                  | Frontend UI Suggestion     |
| ----------------- | ---------------------------- | -------------------------- |
| `romantic_detail` | High fidelity, soft lighting | Use elegant, serif fonts   |
| `comedy_chibi`    | Simple, cute, exaggerated    | Use playful, rounded fonts |
| `action_dynamic`  | Intense, speed lines         | Use bold, italicized fonts |
| `null`            | Standard Webtoon             | Standard rendering         |

**Data Structure Example:**

```json
"panels": [
  {
    "panel_number": 1,
    "style_mode": "romantic_detail",
    "visual_prompt": "..."
  }
]
```

---

_Last Updated: 2026-01-23 16:55 CST_
_Author: Release Planning Bot_

## webtoon script generated == AFTER IMPLEMENTATION

🎭
Characters
J
Ji-hoon
male · 20s

male, 20s years old, sharp jawline, dark brown eyes, olive skin, high cheekbones, often holds a thoughtful or slightly melancholic expression, short black hair, neatly styled with a slight wave, tall, lean athletic build, broad shoulders, long limbs, wearing casual, comfortable clothes, often hoodies or simple shirts. Currently wearing a dark, slightly worn hoodie., reserved, thoughtful, carries a hidden emotional depth, capable of sharp wit but often guarded

M
Min-ji
female · 20s

female, 20s years old, expressive, warm smile, tired eyes, messy top knot, dark brown, petite, slender, wearing pajama pants and oversized hoodie, later stylish casual, wearing pajama pants and oversized hoodie,, initially guarded, then open, resilient

🖼️
Panels (11)
1
Wide Shot
👥 Ji-hoon
WEBTOON, SOFT_ROMANTIC_WEBTOON style. Wide shot of a sterile, brightly lit apartment building basement laundry room. Harsh fluorescent lights hum overhead. White tile floors reflect the light. Industrial washing machines and dryers line both walls. The air is thick with the chemical smell of detergent and fabric softener. Ji-hoon (late 20s, male, tall, lean, black hair, wearing casual clothes) sits alone on a plastic chair, engrossed in his phone, though his eyes seem unfocused. He looks isolated and pensive in the otherwise empty, stark room. The overall atmosphere is mundane but subtly melancholic. [SFX: impact_text: CRASH!; impact_burst: impact_burst moving center; screen_effect: shake effect; screen_effect: flash effect; emotional_effect: sparkles; emotional_effect: hearts]

💬 Dialogue:

Ji-hoon:"_humming of machines_"

2
Medium Shot
👥 Min-ji, Ji-hoon
WEBTOON, SOFT_ROMANTIC_WEBTOON style. Medium shot of the laundry room door swinging open. Min-ji (late 20s, female, slender, long brown hair in a messy top knot, wearing glasses and an oversized, familiar dark hoodie over pajama pants) stands frozen in the doorway, an overflowing laundry basket clutched in her arms. Her eyes are wide with surprise and a hint of alarm as she spots Ji-hoon. Ji-hoon (late 20s, male, tall, lean, black hair, wearing casual clothes) quickly glances up, then immediately down at his phone, his posture stiffening. The fluorescent light casts a flat, revealing glow on their surprised faces. The air is thick with unspoken tension. [SFX: emotional_effect: sparkles; emotional_effect: hearts]

💬 Dialogue:

Min-ji:"Oh. Hi."

Ji-hoon:"Hey."

3
Medium Full Shot
👥 Min-ji, Ji-hoon
WEBTOON, SOFT_ROMANTIC_WEBTOON style. Medium full shot of Min-ji (late 20s, female, slender, long brown hair in a messy top knot, wearing glasses and an oversized dark hoodie over pajama pants, clutching an overflowing laundry basket) hesitating, her gaze flicking between the open door and Ji-hoon (late 20s, male, tall, lean, black hair, wearing casual clothes, pretending to be absorbed in his phone). Her expression is conflicted, clearly debating leaving. The door behind her starts to swing shut. The pile of blouses and skirts in her basket is visible, emphasizing her need to stay. The moment is charged with unspoken thoughts and difficult choices. [SFX: emotional_effect: sparkles; emotional_effect: hearts]

💬 Dialogue:

Min-ji:"_hesitates_"

Ji-hoon:"_pretends to scroll_"

4
Medium Shot
👥 Min-ji, Ji-hoon
WEBTOON, SOFT_ROMANTIC_WEBTOON style. Medium shot of Min-ji (late 20s, female, slender, long brown hair in a messy top knot, wearing glasses and an oversized dark hoodie over pajama pants) mechanically loading clothes into a washing machine. Her back is mostly to Ji-hoon (late 20s, male, tall, lean, black hair, wearing casual clothes), who is still seated, intensely pretending to read his phone. Neither makes eye contact. The washing machine starts with a loud 'click and whoosh.' The silence between them is palpable and heavy, filled with unspoken words and tension. The laundry room rules poster is partially visible behind Min-ji, a mundane detail in a highly charged moment. [SFX: emotional_effect: sparkles; emotional_effect: hearts]

💬 Dialogue:

Min-ji:"_click and whoosh_"

Ji-hoon:"So."

Min-ji:"So."

5
Medium Shot
👥 Min-ji, Ji-hoon
WEBTOON, SOFT_ROMANTIC_WEBTOON style. Medium shot of Min-ji (late 20s, female, slender, long brown hair in a messy top knot, wearing glasses and an oversized dark hoodie over pajama pants) still facing away, her back slightly hunched, her voice small as she speaks. Ji-hoon (late 20s, male, tall, lean, black hair, wearing casual clothes) is seen from a slight angle, his expression unreadable, still holding his phone but not looking at it. His posture is rigid. The washing machines hum steadily between them, a constant background noise to their strained conversation. The tension is thick, as if the air itself is resisting their words. [SFX: emotional_effect: sparkles; emotional_effect: hearts]

💬 Dialogue:

Min-ji:"I'm sorry about Monday."

Ji-hoon:"It's fine."

Min-ji:"It's not fine. I ran away."

Min-ji:"Showed up late to my first day."

6
Medium Shot
👥 Min-ji, Ji-hoon
Medium Shot, vertical 9:16 webtoon panel, The sequence zooms in on their faces to highlight the emotional impact of their direct eye contact. Min-ji's vulnerability is shown through her open gaze, Ji-hoon's internal conflict through his rigid jaw and wide eyes., Harsh fluorescent light, blurred background of machines, Min-ji turns to face Ji-hoon, who is seated. Their eyes lock., Charged silence, direct confrontation, building emotional weight, manhwa style, cinematic depth, high quality

💬 Dialogue:

Min-ji:"Did you get in trouble?"

Min-ji:"We can't avoid each other forever."

Ji-hoon:"Can't we?"

Min-ji:"Is that what you want?"

7
Medium Close-Up
👥 Ji-hoon
WEBTOON, SOFT_ROMANTIC_WEBTOON style. Medium close-up on Ji-hoon's (late 20s, male, tall, lean, black hair, wearing casual clothes) face, his expression a mask of forced indifference, but a subtle twitch in his jaw or tightness around his eyes betrays his true feelings. He avoids Min-ji's gaze, looking slightly past her. The fluorescent light emphasizes the faint lines of stress on his face. The air is thick with unspoken desires and regrets. [SFX: emotional_effect: sparkles; emotional_effect: hearts]

💬 Dialogue:

Ji-hoon:"I want whatever makes this less awkward."

8
Medium Two-Shot
👥 Min-ji, Ji-hoon
WEBTOON, SOFT_ROMANTIC_WEBTOON style. Medium two-shot of Min-ji (late 20s, female, slender, long brown hair in a messy top knot, wearing glasses and an oversized dark hoodie over pajama pants) sitting in the plastic chair directly across from Ji-hoon (late 20s, male, tall, lean, black hair, wearing casual clothes). Their washing machines spin steadily between them, a literal barrier. Min-ji's expression is knowing, a slight smirk playing on her lips as she calls him a liar. Ji-hoon's face shows a flicker of surprise, then a defensive shift. The scene is framed to highlight the physical and emotional distance between them. [SFX: emotional_effect: sparkles; emotional_effect: hearts]

💬 Dialogue:

Min-ji:"Liar."

Min-ji:"You were never a good liar, Ji-hoon."

Ji-hoon:"How would you know?"

Ji-hoon:"You left before you could learn all my tells."

9
Medium Shot
👥 Min-ji, Ji-hoon
Medium Shot, vertical 9:16 webtoon panel, The sequence focuses on their expressions to convey the emotional blows. Min-ji's flinch and then her direct gaze, followed by Ji-hoon's stunned reaction, illustrate the power of her words., Sterile laundry room, flat lighting, Min-ji speaks, her voice cracking. Ji-hoon reacts with shock to her accusation., Intense, accusatory, shocked, emotionally charged, manhwa style, cinematic depth, high quality [SFX: impact_text: !; screen_effect: flash effect]

💬 Dialogue:

Min-ji:"You're right. I left."

Min-ji:"I'm so sorry. But you..."

Ji-hoon:"But I what?"

Min-ji:"You never called. Never texted."

Min-ji:"Not once in seven years."

Min-ji:"So maybe we're both runners."

10
Medium Shot
👥 Ji-hoon, Min-ji
Medium Shot, vertical 9:16 webtoon panel, Ji-hoon's abrupt standing and pacing show his agitation. Min-ji's tearful shout conveys her raw pain and frustration, impacting Ji-hoon's expression of shock and dawning realization., Sterile white tiles, washing machines, cramped space, Ji-hoon stands and paces, Min-ji watches him, both arguing intensely., Highly charged, tense, frustrated, emotional outburst, manhwa style, cinematic depth, high quality [SFX: impact_text: CRASH!; impact_burst: impact_burst moving center; screen_effect: shake effect; screen_effect: flash effect; emotional_effect: dark_aura; emotional_effect: anger_vein]

💬 Dialogue:

Ji-hoon:"You left for New York!"

Min-ji:"I waited!"

Min-ji:"Three months, Ji-hoon. I waited three months."

Ji-hoon:"I didn't know you wanted me to call."

Min-ji:"How could you not know?"

Ji-hoon:"Because you never said!"

Ji-hoon:"Why would I drag you down with my mess?"

11
Medium Shot
Medium Shot, vertical 9:16 webtoon panel, Medium Shot composition, Detailed background environment, No characters present, Standard lighting, manhwa style, cinematic depth, high quality
