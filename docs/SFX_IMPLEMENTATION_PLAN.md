# SFX (Sound/Visual Effects) 구현 계획

## 현재 상태

### ✅ 완료된 작업

1. **Webtoon Writer** - SFX 효과를 패널에 자동 생성 (`panel.sfx_effects`)
2. **Image Prompt** - SFX 힌트가 프롬프트에 포함 (`[SFX: wind_lines: ...]`)
3. **Frontend UI** - WebtoonSceneEditor에서 SFX 효과 정보 표시

### ❌ 미구현 작업

1. **이미지 생성** - SFX가 실제 이미지에 렌더링되지 않음
2. **비디오 생성** - SFX 효과가 비디오에 적용되지 않음

---

## SFX 효과 유형

현재 시스템에서 지원하는 SFX 유형:

| Type               | Description                             | 렌더링 방식             |
| ------------------ | --------------------------------------- | ----------------------- |
| `screen_effect`    | 화면 전체 효과 (shake, darken, blur)    | Canvas filter/transform |
| `emotional_effect` | 감정 표현 (sweat_drop, blush, sparkles) | Emoji/Icon overlay      |
| `wind_lines`       | 속도선/움직임 선                        | Canvas line drawing     |
| `impact_text`      | 충격 텍스트 (!!, ?!, etc.)              | Bold text overlay       |
| `motion_blur`      | 모션 블러 효과                          | Canvas blur filter      |
| `speed_lines`      | 스피드 라인                             | Radial lines drawing    |

---

## 구현 태스크

### Phase 1: VideoGenerator에 SFX 렌더링 추가

#### Task 1.1: SFX Canvas 효과 함수 작성

**파일**: `viral-story-search/src/components/VideoGenerator.tsx`

```typescript
// SFX 효과 렌더링 함수들
const drawWindLines = (ctx, intensity: 'low' | 'medium' | 'high') => { ... }
const drawSpeedLines = (ctx, intensity) => { ... }
const drawImpactText = (ctx, text: string, position) => { ... }
const drawEmotionalEffect = (ctx, type: 'sweat_drop' | 'blush' | 'sparkles') => { ... }
const applyScreenEffect = (ctx, type: 'shake' | 'darken' | 'blur') => { ... }
```

**예상 시간**: 2-3시간

#### Task 1.2: SFX를 비디오 생성 루프에 통합

- 각 패널 렌더링 시 `panel.sfx_effects` 확인
- 해당 SFX 효과 함수 호출
- 이미지 위에 SFX 오버레이 적용

**예상 시간**: 1-2시간

#### Task 1.3: SFX 타이밍 조정

- screen_effect (shake): 짧은 애니메이션 (200-500ms)
- wind_lines: 패널 지속 시간 동안 유지
- impact_text: fade-in 효과

**예상 시간**: 1시간

---

### Phase 2: 이미지 생성 개선 (Optional)

#### Task 2.1: SFX를 이미지 프롬프트에 더 명확하게 포함

현재 `[SFX: ...]` 형식이 이미지 생성에 효과가 없음
→ 직접적인 시각적 설명으로 변환 필요

예시:

```
[SFX: wind_lines: moving center]
→ "with dynamic motion lines radiating from center, manga-style speed effect"
```

**파일**: `backend/app/prompt/scene_image.py`

---

### Phase 3: HQ Video (FFmpeg) SFX 지원

#### Task 3.1: Backend video generation에 SFX 오버레이 추가

**파일**: `backend/app/routers/webtoon.py` - `/webtoon/video/generate`

- FFmpeg filter로 SFX 효과 적용
- 또는 Pillow로 프레임별 SFX 렌더링

---

## SFX 렌더링 예시 코드

### Wind Lines (속도선)

```typescript
const drawWindLines = (
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  intensity: "low" | "medium" | "high",
  direction: "left" | "right" | "center",
) => {
  const lineCount =
    intensity === "high" ? 30 : intensity === "medium" ? 20 : 10;
  ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
  ctx.lineWidth = 2;

  for (let i = 0; i < lineCount; i++) {
    const y = Math.random() * canvas.height;
    const length = 100 + Math.random() * 200;
    const startX =
      direction === "left"
        ? 0
        : direction === "right"
          ? canvas.width
          : canvas.width / 2;

    ctx.beginPath();
    ctx.moveTo(startX, y);
    ctx.lineTo(
      startX + (direction === "left" ? length : -length),
      y + (Math.random() - 0.5) * 20,
    );
    ctx.stroke();
  }
};
```

### Impact Text (충격 텍스트)

```typescript
const drawImpactText = (
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  scaleRef: number,
) => {
  const fontSize = 80 * scaleRef;
  ctx.font = `900 ${fontSize}px Impact, sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  // White fill with black stroke
  ctx.strokeStyle = "#000000";
  ctx.lineWidth = 8 * scaleRef;
  ctx.fillStyle = "#FFFFFF";

  ctx.strokeText(text, x, y);
  ctx.fillText(text, x, y);
};
```

### Screen Shake Effect

```typescript
const applyShakeEffect = async (
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  drawFrame: () => Promise<void>,
  duration: number = 300,
) => {
  const frames = Math.floor(duration / 33); // ~30fps

  for (let i = 0; i < frames; i++) {
    ctx.save();
    const offsetX = (Math.random() - 0.5) * 20;
    const offsetY = (Math.random() - 0.5) * 20;
    ctx.translate(offsetX, offsetY);
    await drawFrame();
    ctx.restore();
    await new Promise((r) => setTimeout(r, 33));
  }
};
```

---

## 우선순위

1. **High**: `wind_lines`, `speed_lines` - 가장 일반적인 웹툰 효과
2. **Medium**: `impact_text` - 감정 강조
3. **Medium**: `emotional_effect` (sweat_drop, sparkles)
4. **Low**: `screen_effect` (shake, darken) - 더 복잡한 구현 필요

---

## 테스트 시나리오

1. SFX가 있는 패널 생성 후 비디오로 확인
2. 다양한 intensity (low/medium/high) 테스트
3. 여러 SFX가 동시에 있는 패널 테스트
4. Frontend 미리보기와 비디오 출력 일치 확인

---

## 참고 자료

- 현재 SFX 데이터 구조: `backend/app/models/story.py` (WebtoonPanel.sfx_effects)
- SFX 생성 로직: `backend/app/agents/sfx_planner.py`
- 프론트엔드 SFX 표시: `viral-story-search/src/components/WebtoonSceneEditor.tsx`
