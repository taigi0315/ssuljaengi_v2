# SFX (Sound/Visual Effects) 구현 계획

## 최종 결정사항

### ❌ Video SFX 렌더링 - 사용하지 않음

- 비디오에서 Canvas로 직접 그리는 SFX는 품질이 좋지 않음
- 너무 harsh하고 프로페셔널하지 않게 보임
- **결론: 비디오에는 SFX를 적용하지 않음**

### ✅ Image Generation SFX - 권장 접근 방식

- 이미지 생성 프롬프트에 SFX를 자연어로 설명하여 포함
- AI가 이미지 자체에 SFX를 렌더링하도록 함
- 더 자연스럽고 일관된 스타일

---

## 현재 상태 (2026-01-23 업데이트)

### ✅ 완료된 작업

1. **Webtoon Writer** - SFX 효과를 패널에 자동 생성 (`panel.sfx_effects`)
2. **Frontend UI** - WebtoonSceneEditor에서 SFX 효과 정보 표시
3. **SFX → Prompt Enhancement 함수** ✅ `sfx_to_prompt_enhancement()` 구현 완료
4. **Image Generation 통합** ✅ `webtoon.py`에서 함수 사용하도록 업데이트

### ❌ 사용하지 않음

1. **Video SFX** - Canvas 기반 SFX 렌더링 (품질 이슈로 취소)

---

## 구현 세부사항

### `sfx_to_prompt_enhancement()` 함수

**파일**: `backend/app/prompt/scene_image.py`

이 함수는 구조화된 SFX 데이터를 AI가 이해할 수 있는 자연어로 변환합니다:

```python
def sfx_to_prompt_enhancement(sfx_effects: list) -> str:
    """
    Convert SFX effects to natural language prompt enhancement.

    Returns:
        str: 예) "Visual Effects to include: dramatic motion blur lines..."
    """
```

### 변환 예시

| SFX Type           | SFX Data                                           | 프롬프트 변환                                                                              |
| ------------------ | -------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `wind_lines`       | `{type: "wind_lines", description: "from left"}`   | "dramatic motion blur lines streaking from left side, manga-style speed effect"            |
| `speed_lines`      | `{type: "speed_lines", intensity: "high"}`         | "dramatic radial speed lines emanating outward from focal point, high-energy manga effect" |
| `impact_text`      | `{type: "impact_text", details: "Text: CRASH!"}`   | "bold stylized impact text 'CRASH!' rendered in manga style, dramatic typography"          |
| `emotional_effect` | `{type: "emotional_effect", description: "sweat"}` | "small anime-style sweat drops near character's head indicating nervousness"               |
| `screen_effect`    | `{type: "screen_effect", description: "vignette"}` | "vignette effect with darkened corners drawing focus to center, cinematic drama"           |

### 지원되는 SFX 타입

1. **wind_lines** - 방향성 speed lines (left, right, center)
2. **speed_lines** - 중심점에서 방사형 speed lines
3. **impact_text** - 망가 스타일 충격 텍스트 (!, CRASH, 쾅 등)
4. **emotional_effect** - 감정 표현 심볼
   - sweat (땀방울)
   - sparkle/shine (반짝임)
   - blush (홍조)
   - anger/vein (분노 표시)
   - heart (하트)
   - shock/surprise (놀람)
   - tear (눈물)
5. **screen_effect** - 화면 효과
   - darken (어두워짐)
   - vignette (비네트)
   - flash/white (플래시)
   - blur (블러)
   - glow (글로우)
6. **motion_blur** - 모션 블러 효과

---

## 통합 위치

### Backend Router (webtoon.py)

```python
@router.post("/scene/image")
async def generate_scene_image(request):
    from app.prompt.scene_image import SCENE_IMAGE_TEMPLATE, sfx_to_prompt_enhancement

    # Extract SFX effects and convert to AI-readable descriptions
    sfx_effects = panel.get("sfx_effects", [])
    if sfx_effects:
        panel_metadata["sfx_description"] = sfx_to_prompt_enhancement(sfx_effects)
    else:
        panel_metadata["sfx_description"] = "None"
```

### Scene Image Template (scene_image.py)

```text
<visual_effects_instructions>
{sfx_description}
</visual_effects_instructions>
```

---

## 테스트 결과

```bash
$ python -c "from app.prompt.scene_image import sfx_to_prompt_enhancement;
print(sfx_to_prompt_enhancement([
  {'type': 'wind_lines', 'description': 'rushing from left', 'intensity': 'high'},
  {'type': 'emotional_effect', 'description': 'sweat drops', 'intensity': 'medium'}
]))"

# Output:
# Visual Effects to include: dramatic motion blur lines streaking from left side,
# manga-style speed effect showing movement, small anime-style sweat drops near
# character's head indicating nervousness or anxiety
```

---

## 참고 자료

- 현재 SFX 데이터 구조: `backend/app/models/story.py` (WebtoonPanel.sfx_effects)
- SFX 생성 로직: `backend/app/services/webtoon_writer.py`
- 이미지 생성 프롬프트: `backend/app/prompt/scene_image.py`
- 이미지 생성 라우터: `backend/app/routers/webtoon.py`
