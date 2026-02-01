# 🗺️ Project Navigator: Ssuljaengi V2

## 🎬 Core Workflow: Shorts Video Creation
This is the roadmap for how the "Text-to-Shorts" feature works:

1.  **Topic & Script**: User enters topic -> `ShortsGenerator.tsx` requests script from `backend/routers/story.py`.
2.  **Character & Scenes**: `ShortsGenerator.tsx` generates images sequentially (`image_generator.py`).
3.  **Video Assembly**: `SceneImageGeneratorV2.tsx` sends panel data -> `video_service.py` -> FFmpeg.

---

## 🗝️ Key Files to Focus On

### 1. Character Consistency 🎨
**Goal**: Ensuring the character looks the same in Scene 1 and Scene 6.

*   **`backend/app/prompt/character_image.py`**:
    *   **The "Bible"**: Defines master templates like `MALE_20_30` or `FEMALE_TEEN`.
    *   **How it works**: Every generated prompt *starts* with these descriptions.
    *   **Action**: Edit this file to change the global "art style" or anatomy of all characters.

*   **`backend/app/services/image_generator.py`**:
    *   **The Engine**: Handles the AI image generation.
    *   **Reference Logic**: When you pass a "Reference Image", this file processes it to guide the new generation (keeping faces consistent).

### 2. Video Rendering 🎥
**Goal**: Merging images, bubbles, and transitions into an MP4.

*   **`backend/app/services/video_service.py`**:
    *   **The Director**: Controls timing, text wrapping, bubble positioning, and scrolling transitions.
    *   **Configuration**: Look for `VideoConfig` class here to change:
        *   `fps` (Frames Per Second)
        *   `transition_duration_ms` (Scroll speed)
        *   `bubble_padding`, `font_size`
    *   **Logic**: Uses **FFmpeg** to stitch frames together.

### 3. Frontend Interface 🖥️
**Goal**: a smooth user experience.

*   **`src/components/ShortsGenerator.tsx`**:
    *   **The Dashboard**: Handles the "Create All" button logic and script editing.
*   **`src/components/SceneImageGeneratorV2.tsx`**:
    *   **The Editor**: Handles dragging/dropping bubbles and "Proceed to Video".

---

## 🚀 Launchers

*   **`START_APP.bat`**: The main launcher (open this to debug!).
*   **`START_APP_NO_WINDOWS.vbs`**: The "Magic" launcher (invisible background mode).
*   **`STOP_APP.bat`**: Panic button to kill all servers.
*   **`INSTALL_FFMPEG.bat`**: Utility to install the video engine.
