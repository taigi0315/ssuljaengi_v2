# TASK-020: Feature Updates - Dialogue, Camera, SFX, and UI Improvements

## Overview

이 태스크는 `feature_request.md`에 정의된 기능 개선 사항들을 구현합니다.

---

## Task Breakdown

### Phase 1: Backend Prompt Updates (High Priority)

#### TASK-020-A: Dialogue Enhancement

**목표**: 스토리 전달력 향상을 위한 대화 시스템 개선

- [ ] `backend/app/prompt/webtoon_writer.py` 수정

  - [ ] 대화량 증가 지시 추가 (캐릭터 감정 표현, 스토리 리딩)
  - [ ] 한 씬에 다중 대화 허용 및 순서(`order`) 필드 강화
  - [ ] 대화 최소 갯수 가이드라인 추가 (예: 2-5 lines per scene)

- [ ] `backend/app/models/story.py` 확인
  - [ ] `DialogueLine` 모델에 `order` 필드 확인/추가

**Files**: `webtoon_writer.py`, `story.py`

---

#### TASK-020-B: Image Aspect Ratio Fix (9:16 Vertical)

**목표**: 1:1 이미지 대신 세로형 9:16 비율 이미지 생성

- [ ] `backend/app/prompt/character_image.py` 수정

  - [ ] "vertical 9:16" 강조 추가
  - [ ] "portrait orientation, tall vertical format" 키워드 삽입

- [ ] `backend/app/prompt/scene_image.py` 수정

  - [ ] 9:16 vertical aspect ratio 명시적 지시 추가
  - [ ] **CRITICAL** 태그로 비율 강조

- [ ] `backend/app/services/image_generator.py` 확인
  - [ ] Gemini API 호출 시 aspect ratio 파라미터 확인

**Files**: `character_image.py`, `scene_image.py`, `image_generator.py`

---

#### TASK-020-C: Camera Settings Strengthening

**목표**: 카메라 설정이 이미지 생성에 더 강하게 반영되도록

- [ ] `backend/app/prompt/scene_image.py` 수정

  - [ ] Camera/Shot type 섹션을 프롬프트 앞부분으로 이동
  - [ ] **MANDATORY CAMERA** 태그 추가
  - [ ] Weight 키워드 추가: "MUST follow camera angle exactly"

- [ ] `backend/app/prompt/webtoon_writer.py` 수정
  - [ ] 다중 카메라 설정 허용 (over-the-shoulder, wide-angle 등)
  - [ ] `shot_type` 필드를 배열로 변경 또는 복합 설정 허용

**Files**: `scene_image.py`, `webtoon_writer.py`

---

#### TASK-020-D: SFX (Special Effects) System

**목표**: 각 씬에 시각적 SFX 효과 정의 및 적용

- [ ] `backend/app/models/story.py` 수정

  - [ ] `WebtoonPanel`에 `sfx_effects` 필드 추가
    ```python
    sfx_effects: Optional[List[dict]] = Field(
        default=None,
        description="SFX effects: [{'type': 'speed_lines', 'intensity': 'high', 'description': '...'}]"
    )
    ```

- [ ] `backend/app/prompt/webtoon_writer.py` 수정

  - [ ] SFX 생성 지시 추가 (speed lines, impact effects, emotion bubbles 등)
  - [ ] 각 씬별 SFX 정의 요구

- [ ] `backend/app/prompt/scene_image.py` 수정

  - [ ] SFX 정보를 이미지 프롬프트에 반영하는 섹션 추가

- [ ] `backend/app/routers/webtoon.py` 수정
  - [ ] `generate_scene_image`에서 SFX 정보 추출 및 프롬프트에 주입

**Files**: `story.py`, `webtoon_writer.py`, `scene_image.py`, `webtoon.py`

---

### Phase 2: Frontend UI Updates (Medium Priority)

#### TASK-020-E: Chat Bubble Styling

**목표**: 대화 버블 UI 개선

- [ ] `viral-story-search/src/components/` 관련 컴포넌트 수정
  - [ ] Chat bubble 배경 opacity 30% 적용 (텍스트는 100%)
  - [ ] Dark gray border 추가
  - [ ] 이름 제거 (대화 내용만 표시)

**CSS 예시**:

```css
.chat-bubble {
  background-color: rgba(50, 50, 50, 0.3);
  border: 2px solid #4a4a4a;
}
.chat-bubble-text {
  opacity: 1; /* Text remains fully visible */
}
```

**Files**: Frontend components (TBD after inspection)

---

#### TASK-020-F: Draggable Chat Bubbles

**목표**: 이미지 위 대화 버블 위치 조정 가능

- [ ] React DnD 또는 커스텀 드래그 구현

  - [ ] 버블 위치를 씬 데이터에 저장 (`x`, `y` 좌표)
  - [ ] 저장된 위치 복원

- [ ] Backend API 확장 (필요시)
  - [ ] 버블 위치 저장 엔드포인트

**Files**: Frontend components, potentially `webtoon.py`

---

### Phase 3: Expensive Feature (Low Priority - Deferred)

#### TASK-020-G: Sequential Dialogue Animation in Video

**목표**: 비디오에서 대화 버블 순차 표시

- [ ] 다이얼로그별 타이밍 정의 (기본 1초 간격)
- [ ] 사용자 조정 가능한 타이밍 UI
- [ ] 비디오 생성 시 순차 대화 오버레이 적용

> ⚠️ **Deferred**: 이 기능은 다른 기능 완료 후 마지막에 진행

---

## Execution Order

1. **TASK-020-B**: 9:16 비율 수정 (가장 시급)
2. **TASK-020-A**: 대화 강화
3. **TASK-020-C**: 카메라 설정 강화
4. **TASK-020-D**: SFX 시스템
5. **TASK-020-E**: Chat Bubble 스타일링
6. **TASK-020-F**: 드래그 가능 버블
7. **TASK-020-G**: 순차 대화 애니메이션 (Deferred)

---

## Success Criteria

- [ ] 생성된 이미지가 9:16 세로 비율
- [ ] 각 씬에 2-5개의 대화 라인 포함
- [ ] 카메라 설정이 이미지에 명확히 반영
- [ ] SFX 효과가 이미지에 시각적으로 표현
- [ ] Chat bubble UI가 사양대로 동작
- [ ] 버블 드래그 및 위치 저장 가능
