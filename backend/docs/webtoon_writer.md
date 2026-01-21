# V10

# 웹툰 라이터 프롬프트 업데이트 가이드

## 핵심 변경사항

### ✨ 새로운 개념: Creative Authority (창작 권한)

웹툰 라이터가 이제 **고정된 규칙을 따르는 게 아니라, 스토리텔링을 위해 장르/스타일을 능동적으로 해석하고 변형**할 수 있습니다.

---

## 주요 추가사항

### 1. **Genre-Style Fluidity (장르-스타일 유연성)**

**기존 방식 (경직됨):**

```
IMAGE_STYLE = "Soft Romantic"
→ 모든 12개 scene이 무조건 soft romantic rendering
```

**새로운 방식 (유연함):**

```
IMAGE_STYLE = "Soft Romantic" (기본 방향)
→ Scene 1-2: Soft romantic (기본)
→ Scene 5: Chibi cute style (코미디 릴리프)
→ Scene 8: Dramatic high-contrast (절정 장면)
→ Scene 10-12: Soft romantic으로 복귀
```

**프롬프트에 추가된 내용:**

```
You have the creative authority to interpret how GENRE and IMAGE_STYLE
interact for each scene. The IMAGE_STYLE provides a default aesthetic
direction, NOT a rigid rule. You can adapt or override the style for
specific scenes when the story demands it.
```

**예시:**

- 로맨스 + Soft Romantic 스타일인데, 웃긴 장면 나옴
  → 그 scene만 chibi/cute style로 전환 가능
- 일반적으로 밝은 스타일인데, 회상 장면
  → Desaturated/nostalgic style로 전환 가능

---

### 2. **Style Influencing Scene Construction**

**핵심:** 스타일이 단순히 렌더링 태그가 아니라, **scene을 어떻게 묘사할지**에 영향을 줘야 함

**예시 1: Sensual Romantic 스타일 선택됨**

웹툰 라이터가 scene 묘사할 때:

```json
{
  "visual_prompt": "Medium shot, ...,
  Ji-hoon leaning very close to Soojin with barely any space between them,
  his hand resting on the table near hers with fingers almost touching,
  soft silk blouse catching warm amber light,
  intimate atmosphere with palpable tension,
  warm glow highlighting skin tones and facial features,
  shadows accentuating the curves of her neck and shoulder..."
}
```

→ Physical proximity, 촉각적 디테일 (silk, touching), 피부 톤 강조, 긴장감

**예시 2: Cute Chibi 스타일 선택됨**

```json
{
  "visual_prompt": "Medium shot rendered in cute simplified chibi style,
  Ji-hoon depicted with comically oversized head and tiny body,
  huge sparkling eyes taking up half his face,
  exaggerated shocked expression with jaw dropped and floating sweat drops,
  simplified proportions, bright saturated pastel colors..."
}
```

→ 과장된 비율, 단순화된 형태, 밝은 색상

**프롬프트에 추가된 내용:**

```
The IMAGE_STYLE should inform how you describe scenes, not just be a tag.
If "Sensual Romantic" style:
  - Describe intimate physical proximity
  - Emphasize soft fabrics, silk, flowing clothing
  - Use sensual lighting keywords
  - Include atmosphere of tension/attraction

If "Cute Chibi" style:
  - Describe exaggerated expressions
  - Simplified proportions
  - Playful compositions
```

---

### 3. **Genre Influencing Visual Choices**

장르가 어떤 **shot/composition**을 선택할지 가이드

**프롬프트에 추가된 내용:**

```
GENRE_STYLE INTERPRETATION GUIDE:

Romance/Drama:
  - Shot: Medium close-ups (40-45% character)
  - Emphasis: Facial expressions, emotional intimacy
  - Environment: Cozy intimate spaces, warm lighting

Thriller/Suspense:
  - Shot: Wide shots (25-35% character)
  - Emphasis: Environment tension, ominous details
  - Environment: Dark spaces, harsh lighting, isolation

Comedy:
  - Shot: Medium full shots (35-40% character)
  - Emphasis: Body language, visual gags
  - Environment: Colorful chaotic spaces
```

---

## 실제 사용 예시

### 시나리오: Romance 장르 + Soft Romantic 스타일

**Scene 1-3 (Setup):** Soft romantic (기본 스타일 유지)

```json
{
  "panel_number": 1,
  "visual_prompt": "...soft golden-hour sunlight, dreamy atmosphere,
  delicate sparkles, warm peachy tones, ultra-soft cel-shading..."
}
```

**Scene 5 (Comedy relief - 웃긴 오해):** Chibi style로 전환

```json
{
  "panel_number": 5,
  "visual_prompt": "...cute simplified chibi style, Ji-hoon with
  comically oversized shocked eyes, exaggerated proportions, bright
  saturated colors, playful rendering...",
  "style_adaptation_note": "Chibi style for comedy beat"
}
```

**Scene 8 (Emotional climax - 고백 장면):** Dramatic style로 전환

```json
{
  "panel_number": 8,
  "visual_prompt": "...dramatic high-contrast lighting, sharp shadows,
  desaturated background with single warm spotlight on characters,
  cinematic tension, emotional intensity...",
  "style_adaptation_note": "Dramatic contrast for emotional peak"
}
```

**Scene 10-12 (Resolution):** Soft romantic으로 복귀

```json
{
  "panel_number": 12,
  "visual_prompt": "...warm golden glow, dreamy soft focus,
  delicate sparkles returning, hopeful atmosphere..."
}
```

---

## 새로운 JSON 필드

### `style_adaptation_note` (선택적)

스타일을 변형한 경우 이유 설명:

```json
{
  "panel_number": 5,
  "style_adaptation_note": "Switched to chibi for comedy relief"
}

{
  "panel_number": 8,
  "style_adaptation_note": "Dramatic high-contrast for emotional climax"
}

{
  "panel_number": 3,
  "style_adaptation_note": "Desaturated nostalgic tone for flashback"
}
```

---

## Input 데이터 변경

### 기존:

```python
WEBTOON_WRITER_PROMPT.format(
    web_novel_story=story,
    genre_style=genre
)
```

### 새로운 방식:

```python
WEBTOON_WRITER_PROMPT.format(
    web_novel_story=story,
    genre_style=genre,        # "MODERN_ROMANCE_DRAMA"
    image_style=image_style   # "SOFT_ROMANTIC_WEBTOON"
)
```

---

## 체크리스트에 추가된 항목

```
✅ IMAGE_STYLE keywords are woven into visual_prompts (not just tagged at end)
✅ GENRE_STYLE influences shot choices and composition
✅ Atmospheric_conditions reflect IMAGE_STYLE (soft/harsh/magical lighting)
✅ Style adaptations noted if you switched styles for specific scenes
```

---

## 왜 이게 중요한가?

### Before (경직):

```
Romance + Soft → 모든 scene이 똑같이 부드러움
Comedy moment도 억지로 soft romantic으로 렌더링
→ 어색함
```

### After (유연):

```
Romance + Soft → 대부분 부드럽지만
Comedy moment → Chibi로 전환 (자연스러움)
Climax moment → Dramatic으로 전환 (긴장감)
→ 스토리텔링이 살아남
```

---

## 통합 예시

**Input:**

```python
story = "Ji-hoon meets Soojin at cafe. They talk. Funny moment. Confession. Happy ending."
genre = "MODERN_ROMANCE_DRAMA"
style = "SOFT_ROMANTIC_WEBTOON"
```

**Output (웹툰 라이터가 생성):**

```json
{
  "scenes": [
    {
      "panel_number": 1,
      "shot_type": "Wide Shot",
      "visual_prompt": "...soft golden sunlight, dreamy cafe, delicate sparkles...",
      "atmospheric_conditions": "Warm golden-hour, soft diffused light, dreamy"
      // Soft romantic 스타일 유지
    },
    {
      "panel_number": 5,
      "shot_type": "Medium Shot",
      "visual_prompt": "...cute chibi style, oversized heads, exaggerated shock...",
      "atmospheric_conditions": "Bright playful, simplified rendering",
      "style_adaptation_note": "Chibi for comedic misunderstanding"
      // 웃긴 장면 - 스타일 변경
    },
    {
      "panel_number": 8,
      "shot_type": "Medium Close-Up",
      "visual_prompt": "...dramatic lighting, emotional tension, Ji-hoon leaning close to Soojin with barely any space, warm intimate glow on skin, palpable attraction...",
      "atmospheric_conditions": "Intimate sensual lighting, warm tension",
      "style_adaptation_note": "Sensual intimate framing for confession"
      // 고백 - Sensual 요소 추가
    },
    {
      "panel_number": 12,
      "shot_type": "Wide Shot",
      "visual_prompt": "...soft romantic glow returns, dreamy atmosphere, delicate sparkles...",
      "atmospheric_conditions": "Warm hopeful, soft diffused light"
      // Soft romantic으로 복귀
    }
  ]
}
```

---

## 요약

### 핵심 철학 변화:

**기존:**

> "장르/스타일은 규칙이다. 따라야 한다."

**새로운:**

> "장르/스타일은 도구다. 스토리를 위해 능동적으로 활용하라."

### 웹툰 라이터의 새로운 권한:

1. ✅ 스타일을 scene별로 변형 가능 (chibi, dramatic, nostalgic 등)
2. ✅ 스타일이 scene 묘사 방식에 영향 (sensual → intimate details)
3. ✅ 장르가 shot 선택/composition에 영향
4. ✅ 둘을 유기적으로 결합해서 최고의 스토리텔링 달성

### 기존 프롬프트 유지:

- ✅ 8-12 scene 필수
- ✅ Dialogue-driven
- ✅ 완전한 visual_prompt (150-250 words)
- ✅ 모든 기존 규칙 그대로

### 추가된 것:

- ✅ Genre-Style fluidity
- ✅ Style influencing scene construction
- ✅ Creative authority
- ✅ Style adaptation notes

이제 웹툰 라이터가 진짜 감독처럼 작동합니다! 🎬
