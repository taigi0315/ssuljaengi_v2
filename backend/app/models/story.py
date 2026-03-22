"""
Data models for story generation.

This module defines Pydantic models for story generation requests, responses,
workflow status tracking, and evaluation results.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal, List, Any
from datetime import datetime
from enum import Enum
from app.prompt.story_genre import STORY_GENRE_PROMPTS
from app.prompt.image_style import VISUAL_STYLE_PROMPTS


# Story mood types - now dynamic based on keys
StoryMood = str


class ShotType(str, Enum):
    """
    Enumeration of shot types for cinematography planning.

    Used by the Cinematographer agent to plan visual variety
    and by the evaluator to score shot distribution.
    
    v2.1.0 E1-T03: Added romance-specific shot types (macro_*, silhouette, etc.)
    """
    EXTREME_CLOSE_UP = "extreme_close_up"  # Eyes, lips, small details - 85-100% frame
    CLOSE_UP = "close_up"                   # Face/head - 70-85% frame
    MEDIUM_CLOSE_UP = "medium_close_up"     # Head and shoulders - 50-70% frame
    MEDIUM = "medium"                       # Waist up - 30-50% frame
    MEDIUM_WIDE = "medium_wide"             # Knees up - 20-40% frame
    WIDE = "wide"                           # Full body with environment - 15-30% frame
    EXTREME_WIDE = "extreme_wide"           # Establishing shot - 5-15% frame
    DETAIL = "detail"                       # Objects, hands, symbolic elements
    OVER_SHOULDER = "over_shoulder"         # Conversation shot - 40-60% frame
    POV = "pov"                             # Point of view shot
    # v2.1.0 E1-T03: Romance-specific shot types
    MACRO_EYES = "macro_eyes"               # Glistening eyes, tears - 90-100% frame
    MACRO_HANDS = "macro_hands"             # Hand touches, rings - 80-95% frame
    MACRO_LIPS = "macro_lips"               # Kiss scenes, whispered words - 85-100% frame
    FULL_BODY = "full_body"                 # Complete figure, posture - 15-35% frame
    SILHOUETTE = "silhouette"               # Dramatic backlit moments - 10-40% frame
    TWO_SHOT = "two_shot"                   # Both characters in frame - 30-60% frame
    SPLIT_SCREEN = "split_screen"           # Parallel moments - 50/50

    @classmethod
    def get_frame_percentage_range(cls, shot_type: "ShotType") -> tuple[int, int]:
        """Return typical frame percentage range for character in this shot type."""
        ranges = {
            cls.EXTREME_CLOSE_UP: (85, 100),
            cls.CLOSE_UP: (70, 85),
            cls.MEDIUM_CLOSE_UP: (50, 70),
            cls.MEDIUM: (30, 50),
            cls.MEDIUM_WIDE: (20, 40),
            cls.WIDE: (15, 30),
            cls.EXTREME_WIDE: (5, 15),
            cls.DETAIL: (10, 90),  # Varies based on subject
            cls.OVER_SHOULDER: (40, 60),
            cls.POV: (0, 100),  # Varies
            # v2.1.0 additions
            cls.MACRO_EYES: (90, 100),
            cls.MACRO_HANDS: (80, 95),
            cls.MACRO_LIPS: (85, 100),
            cls.FULL_BODY: (15, 35),
            cls.SILHOUETTE: (10, 40),
            cls.TWO_SHOT: (30, 60),
            cls.SPLIT_SCREEN: (50, 50),
        }
        return ranges.get(shot_type, (30, 50))
    
    @classmethod
    def get_style_mode_for_shot(cls, shot_type: "ShotType") -> str | None:
        """
        v2.1.0 E1-T03: Get recommended style_mode for a shot type.
        
        Returns the default style mode that works best with this shot type.
        """
        romantic_detail_shots = {
            cls.EXTREME_CLOSE_UP, cls.MACRO_EYES, cls.MACRO_HANDS,
            cls.MACRO_LIPS, cls.CLOSE_UP, cls.SILHOUETTE, cls.DETAIL
        }
        action_shots = {cls.SPLIT_SCREEN}
        
        if shot_type in romantic_detail_shots:
            return "romantic_detail"
        elif shot_type in action_shots:
            return "action_dynamic"
        return None


class StoryRequest(BaseModel):
    """
    Request model for story generation.
    
    Attributes:
        post_id: Unique identifier for the Reddit post
        post_title: Title of the Reddit post
        post_content: Content/body of the Reddit post
        mood: Story mood/style selection
        options: Optional configuration for story generation
    """
    post_id: Optional[str] = Field(default=None, description="Reddit post ID (optional for custom stories)")
    post_title: str = Field(..., description="Reddit post title", min_length=1)
    post_content: str = Field(..., description="Reddit post content")
    mood: StoryMood = Field(..., description="Story mood/style")
    options: Optional[dict] = Field(default=None, description="Optional generation options")

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, v: str) -> str:
        if v not in STORY_GENRE_PROMPTS:
            raise ValueError(f"Invalid mood '{v}'. Must be one of: {list(STORY_GENRE_PROMPTS.keys())}")
        return v


class Story(BaseModel):
    """
    Story model representing a generated story.
    
    Attributes:
        id: Unique identifier for the story
        content: The generated story text
        evaluation_score: Quality score from evaluator (1-10)
        rewrite_count: Number of times the story was rewritten
        created_at: Timestamp when the story was created
        metadata: Optional additional metadata
    """
    id: str = Field(..., description="Unique story ID")
    content: str = Field(..., description="Generated story content")
    evaluation_score: float = Field(..., description="Quality score (1-10)", ge=0, le=10)
    rewrite_count: int = Field(default=0, description="Number of rewrites", ge=0)
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class StoryResponse(BaseModel):
    """
    Response model for story retrieval.
    
    Attributes:
        story: The generated story
        generation_time: Time taken to generate the story (seconds)
        workflow_info: Information about the workflow execution
    """
    story: Story = Field(..., description="Generated story")
    generation_time: float = Field(..., description="Generation time in seconds", ge=0)
    workflow_info: dict = Field(..., description="Workflow execution details")


class WorkflowStatus(BaseModel):
    """
    Model for tracking workflow execution status.
    
    Attributes:
        workflow_id: Unique identifier for the workflow
        status: Current status of the workflow
        current_step: Current step being executed
        progress: Progress percentage (0.0 to 1.0)
        story_id: ID of the generated story (when completed)
        error: Error message (if failed)
    """
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: Literal["started", "in_progress", "completed", "failed"] = Field(
        ..., description="Workflow status"
    )
    current_step: str = Field(..., description="Current workflow step")
    progress: float = Field(..., description="Progress (0.0 to 1.0)", ge=0.0, le=1.0)
    story_id: Optional[str] = Field(default=None, description="Story ID when completed")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class EvaluationResult(BaseModel):
    """
    Model for story evaluation results.
    
    Attributes:
        score: Overall quality score (1-10)
        feedback: Detailed feedback for improvement
        coherence: Coherence score (1-10)
        engagement: Engagement score (1-10)
        length_appropriate: Whether the length is appropriate
    """
    score: float = Field(..., description="Overall score (1-10)", ge=0, le=10)
    feedback: str = Field(..., description="Detailed feedback")
    coherence: float = Field(..., description="Coherence score (1-10)", ge=0, le=10)
    engagement: float = Field(..., description="Engagement score (1-10)", ge=0, le=10)
    length_appropriate: bool = Field(..., description="Is length appropriate")



class TextType(str, Enum):
    """
    v2.1.0 E2-T01: Text type classification for webtoon dialogue.
    
    Determines how text should be rendered:
    - DIALOGUE: Standard speech bubble (round)
    - MONOLOGUE: Internal thought (square box)  
    - SFX: Atmospheric/sound effect (free-floating artistic text)
    - NARRATION: Story narration (box at top/bottom)
    """
    DIALOGUE = "dialogue"           # "Hello!" → Round speech bubble
    MONOLOGUE = "monologue"         # *I can't believe this...* → Square thought box
    SFX = "sfx"                     # *THUMP* *Silence* → Artistic floating text
    NARRATION = "narration"         # "The next day..." → Narrator box


# Keywords for automatic text type classification
SFX_KEYWORDS = [
    "silence", "thump", "thud", "bang", "crash", "whoosh", "sigh",
    "gasp", "nervousness", "tension", "heartbeat", "thunder", "rain",
    "wind", "footsteps", "door", "click", "ring", "buzz", "beep"
]

MONOLOGUE_PATTERNS = [
    r"^\*[^*]+\*$",           # *text enclosed in asterisks*
    r"^[（(].+[)）]$",         # (text in parentheses) or （Japanese parentheses）
    r"^『.+』$",               # Japanese thought quotes
    r"^\[.+\]$",              # [bracketed text]
]


class DialogueLine(BaseModel):
    """
    Single line of dialogue/text in a webtoon panel.
    
    v2.1.0 E2-T02: Extended with text_type for rendering classification.
    """
    character: str = Field(..., description="Name of the character speaking.")
    text: str = Field(..., description="The dialogue text.")
    # v2.1.0 E2-T02: Text type classification
    text_type: TextType = Field(
        default=TextType.DIALOGUE,
        description="Type of text: dialogue (speech bubble), monologue (thought box), sfx (artistic), narration (narrator box)"
    )
    order: int = Field(
        default=1,
        description="Order of this dialogue within the panel (for multiple speakers)",
        ge=1
    )
    
    @classmethod
    def auto_classify(cls, character: str, text: str, order: int = 1) -> "DialogueLine":
        """
        v2.1.0 E2-T01: Automatically classify text type based on content.
        
        Classification rules:
        1. Text wrapped in * or () → MONOLOGUE
        2. Text matching SFX keywords → SFX
        3. Narrator/System as character → NARRATION
        4. Everything else → DIALOGUE
        
        Args:
            character: Character name
            text: The text content
            order: Order within panel
            
        Returns:
            DialogueLine with auto-detected text_type
        """
        import re
        
        text_lower = text.lower().strip()
        text_stripped = text.strip()
        
        # Check for monologue patterns
        for pattern in MONOLOGUE_PATTERNS:
            if re.match(pattern, text_stripped):
                return cls(
                    character=character,
                    text=text,
                    text_type=TextType.MONOLOGUE,
                    order=order
                )
        
        # Check for SFX keywords (often marked with * or standalone)
        if text_stripped.startswith("*") and text_stripped.endswith("*"):
            inner_text = text_stripped[1:-1].lower()
            if any(kw in inner_text for kw in SFX_KEYWORDS):
                return cls(
                    character=character,
                    text=text,
                    text_type=TextType.SFX,
                    order=order
                )
        
        # Check for narration (usually by Narrator or system)
        if character.lower() in ["narrator", "나레이터", "system", "narration"]:
            return cls(
                character=character,
                text=text,
                text_type=TextType.NARRATION,
                order=order
            )
        
        # Default to dialogue
        return cls(
            character=character,
            text=text,
            text_type=TextType.DIALOGUE,
            order=order
        )


class Character(BaseModel):
    """
    Character model with detailed physical and personality attributes.
    
    The LLM generates these fields from the story. They should all be populated.
    """
    name: str = Field(
        ..., 
        description="The name of the character.",
        min_length=1,
        max_length=100
    )
    reference_tag: str = Field(
        ...,
        description="Minimal prompt tag (e.g., 'Ji-hoon(20s, athletic build, black hair)').",
        min_length=1,
        max_length=200
    )
    gender: str = Field(
        ..., 
        description="Gender of the character (e.g., male, female, non-binary).",
        min_length=1,
        max_length=50
    )
    age: str = Field(
        ..., 
        description="Age of the character (e.g., '20', '30', '40').",
        min_length=1,
        max_length=50
    )
    face: str = Field(
        default="",
        description="Facial features.",
        max_length=500
    )
    hair: str = Field(
        default="",
        description="Hair description.",
        max_length=500
    )
    body: str = Field(
        default="",
        description="Body type.",
        max_length=500
    )
    outfit: str = Field(
        default="",
        description="Clothing description.",
        max_length=500
    )
    mood: str = Field(
        default="",
        description="Personality vibe.",
        max_length=200
    )
    appearance_notes: str = Field(
        default="", 
        description="Detailed visual notes (optional legacy field).",
        max_length=1000
    )
    typical_outfit: str = Field(
        default="",
        description="Legacy outfit field.",
        max_length=500
    )
    personality_brief: str = Field(
        default="",
        description="Legacy personality field.",
        max_length=200
    )
    visual_description: str = Field(
        ..., 
        description="Complete visual description combining all attributes. Used for image generation.",
        min_length=20,
        max_length=2000
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ji-hoon",
                "reference_tag": "Ji-hoon(20s, athletic build, black hair)",
                "gender": "male",
                "age": "20s",
                "appearance_notes": "Sharp jawline, dark brown eyes, olive skin tone, high cheekbones. Short black hair, neatly styled with slight wave. Tall athletic build, broad shoulders, lean muscular frame.",
                "typical_outfit": "Tailored navy suit with white dress shirt",
                "personality_brief": "Confident",
                "visual_description": "A tall man with sharp jawline, dark brown eyes, olive skin, high cheekbones, short black hair neatly styled with slight wave, athletic build with broad shoulders and lean muscular frame, wearing a tailored navy suit with white dress shirt, confident demeanor"
            }
        }


class CameraAngle(str, Enum):
    """Camera angle for shot composition."""
    EYE_LEVEL = "eye_level"         # Standard, neutral
    LOW_ANGLE = "low_angle"         # Looking up, adds power/dominance
    HIGH_ANGLE = "high_angle"       # Looking down, vulnerability/smallness
    DUTCH_ANGLE = "dutch_angle"     # Tilted, tension/unease
    BIRDS_EYE = "birds_eye"         # Directly above
    WORMS_EYE = "worms_eye"         # Directly below


class Shot(BaseModel):
    """
    A single shot planned by the Cinematographer agent.

    Represents one visual moment that will be generated as an image
    or as part of a multi-panel page.
    """
    shot_id: str = Field(
        ...,
        description="Unique identifier for this shot (e.g., 'scene_1_shot_3')"
    )
    shot_type: ShotType = Field(
        ...,
        description="Type of shot (close_up, wide, detail, etc.)"
    )
    subject: str = Field(
        ...,
        description="What/who is the focus (e.g., 'character_a_face', 'both_characters', 'hands_on_table')"
    )
    subject_characters: List[str] = Field(
        default_factory=list,
        description="Character names involved in this shot"
    )
    frame_percentage: int = Field(
        ...,
        description="Percentage of frame the subject occupies (0-100)",
        ge=0,
        le=100
    )
    angle: CameraAngle = Field(
        default=CameraAngle.EYE_LEVEL,
        description="Camera angle for this shot"
    )
    emotional_purpose: str = Field(
        ...,
        description="Why this shot exists narratively (e.g., 'show_tension', 'reveal_reaction', 'establish_mood')"
    )
    emotional_intensity: int = Field(
        default=5,
        description="Emotional intensity of this moment (1-10, drives style modifiers)",
        ge=1,
        le=10
    )
    belongs_to_scene: int = Field(
        ...,
        description="Scene number this shot belongs to",
        ge=1
    )
    story_beat: str = Field(
        default="",
        description="Brief description of what happens in this shot"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "shot_id": "scene_1_shot_2",
                "shot_type": "close_up",
                "subject": "character_a_face",
                "subject_characters": ["Ji-hoon"],
                "frame_percentage": 75,
                "angle": "eye_level",
                "emotional_purpose": "show_determination",
                "emotional_intensity": 7,
                "belongs_to_scene": 1,
                "story_beat": "Ji-hoon realizes the truth"
            }
        }


class ShotPlan(BaseModel):
    """
    Complete shot plan output from the Cinematographer agent.

    Contains all planned shots for a webtoon with variety scoring.
    """
    shots: List[Shot] = Field(
        ...,
        description="Ordered list of all shots",
        min_items=1
    )
    total_scenes: int = Field(
        ...,
        description="Total number of scenes covered",
        ge=1
    )
    variety_score: float = Field(
        default=0.0,
        description="Shot variety score (0.0-1.0). Higher = better distribution",
        ge=0.0,
        le=1.0
    )
    shot_type_distribution: dict = Field(
        default_factory=dict,
        description="Count of each shot type used"
    )

    def calculate_variety_score(self) -> float:
        """Calculate and update the variety score based on shot distribution."""
        if not self.shots:
            return 0.0

        from collections import Counter
        shot_types = [s.shot_type for s in self.shots]
        counts = Counter(shot_types)
        total = len(shot_types)

        # Penalize if >50% are same type
        most_common_ratio = max(counts.values()) / total
        base_score = 1.0 - max(0, (most_common_ratio - 0.3) * 1.5)

        # Bonus for having close-ups and detail shots
        has_closeup = any(st in counts for st in [ShotType.CLOSE_UP, ShotType.EXTREME_CLOSE_UP])
        has_detail = ShotType.DETAIL in counts

        bonus = (0.1 if has_closeup else 0) + (0.1 if has_detail else 0)

        self.variety_score = min(1.0, max(0.0, base_score + bonus))
        self.shot_type_distribution = {st.value: count for st, count in counts.items()}

        return self.variety_score

    class Config:
        json_schema_extra = {
            "example": {
                "shots": [
                    {
                        "shot_id": "scene_1_shot_1",
                        "shot_type": "wide",
                        "subject": "coffee_shop_interior",
                        "subject_characters": [],
                        "frame_percentage": 20,
                        "angle": "eye_level",
                        "emotional_purpose": "establish_location",
                        "emotional_intensity": 3,
                        "belongs_to_scene": 1,
                        "story_beat": "Establishing the coffee shop setting"
                    }
                ],
                "total_scenes": 5,
                "variety_score": 0.85,
                "shot_type_distribution": {"wide": 3, "medium": 5, "close_up": 4, "detail": 2}
            }
        }


class WebtoonPanel(BaseModel):
    """
    Webtoon panel with scene description and dialogue.
    
    Each panel represents a single frame in the webtoon with
    camera angle, characters, visual description, and optional dialogue.
    """
    panel_number: int = Field(
        ..., 
        description="Sequential panel number starting from 1.",
        ge=1,
        le=100
    )
    shot_type: str = Field(
        default="Medium Shot", 
        description="Camera angle (e.g., Low Angle, Dutch Angle, Close-up, Wide Shot, Bird's Eye).",
        max_length=100
    )
    active_character_names: List[str] = Field(
        default_factory=list, 
        description="List of character names appearing in this panel.",
        max_items=10
    )
    visual_prompt: str = Field(
        default="", 
        description="Self-contained image generation prompt with full character descriptions, not just names.",
        max_length=2000
    )
    negative_prompt: str = Field(
        default="", 
        description="Negative prompt tokens to avoid.",
        max_length=1000
    )
    composition_notes: str = Field(
        default="", 
        description="Notes on framing and composition.",
        max_length=500
    )
    environment_focus: str = Field(
        default="", 
        description="Primary location setting.",
        max_length=500
    )
    environment_details: str = Field(
        default="", 
        description="Specific environmental elements.",
        max_length=1000
    )
    atmospheric_conditions: str = Field(
        default="", 
        description="Lighting, weather, time of day.",
        max_length=500
    )
    story_beat: str = Field(
        default="",
        description="Narrative action in this panel.",
        max_length=500
    )
    emotional_intensity: int = Field(
        default=5,
        description="Emotional intensity of this panel (1-10). Drives shot selection and style modifiers. 1=calm/neutral, 5=moderate, 10=peak emotion.",
        ge=1,
        le=10
    )
    character_frame_percentage: int = Field(
        default=40, 
        description="Percentage of frame occupied by characters.",
        ge=0,
        le=100
    )
    environment_frame_percentage: int = Field(
        default=60, 
        description="Percentage of frame occupied by environment.",
        ge=0,
        le=100
    )
    character_placement_and_action: str = Field(
        default="", 
        description="Description of where characters are and what they are doing.",
        max_length=1000
    )
    sfx_effects: Optional[List[dict]] = Field(
        default=None,
        description="List of SFX effects: [{'type': 'speed_lines', 'intensity': 'high', 'description': '...', 'position': 'background'}]"
    )
    dialogue: Optional[List[dict]] = Field(
        default=None, 
        description="List of dialogue objects: [{'character': 'Name', 'text': 'Speech'}]",
    )
    # v2.1.0 E5-T01: Panel-level style mode for dynamic style switching
    style_mode: Optional[str] = Field(
        default=None,
        description="Panel-level style override: 'romantic_detail' (high detail for serious/romantic), 'comedy_chibi' (SD/chibi for humor), 'action_dynamic' (dynamic lines for action), or null for default"
    )
    scene_number: int = Field(
        default=1,
        description="Scene number this panel belongs to",
        ge=1
    )
    
    @classmethod
    def get_style_mode_keywords(cls, style_mode: Optional[str]) -> str:
        """
        v2.1.0 E5-T01: Get style keywords based on style_mode.
        
        Returns style modifier keywords to append to visual prompts
        based on the panel's style mode setting.
        """
        if not style_mode:
            return ""
        
        style_keywords = {
            "romantic_detail": (
                "highly detailed illustration, soft lighting, delicate linework, "
                "subtle color gradients, romantic atmosphere, professional webtoon quality, "
                "expressive eyes, soft focus on background"
            ),
            "comedy_chibi": (
                "chibi style, super-deformed proportions, exaggerated expressions, "
                "simplified features, cute aesthetic, comedic effect, big head small body, "
                "expressive oversized reactions"
            ),
            "action_dynamic": (
                "dynamic action pose, speed lines, motion blur effects, "
                "high contrast, dramatic angles, powerful composition, "
                "intense energy, bold linework"
            ),
        }
        return style_keywords.get(style_mode, "")
    
    class Config:
        json_schema_extra = {
            "example": {
                "panel_number": 1,
                "shot_type": "Medium Shot",
                "active_character_names": ["Ji-hoon", "Hana"],
                "visual_prompt": "Medium shot of a tall man with sharp jawline... (Ji-hoon) ...",
                "dialogue": [{"character": "Ji-hoon", "text": "We need to talk about what happened."}],
                "style_mode": "romantic_detail"
            }
        }


class WebtoonScene(BaseModel):
    """
    Webtoon scene containing multiple panels.
    
    Each scene represents a narrative unit that can contain 1-3 panels
    for detailed storytelling within that scene context.
    """
    scene_number: int = Field(
        ..., 
        description="Sequential scene number starting from 1.",
        ge=1,
        le=50
    )
    scene_type: str = Field(
        default="story", 
        description="Scene type: bridge (transition), story (plot), impact (emotional peak).",
        max_length=20
    )
    scene_title: str = Field(
        default="", 
        description="Brief title or description of the scene.",
        max_length=100
    )
    panels: List[WebtoonPanel] = Field(
        ..., 
        description="List of panels within this scene (1-3 panels recommended).",
        min_items=1,
        max_items=3
    )
    is_hero_shot: bool = Field(
        default=False,
        description="Whether this scene is the hero shot (thumbnail/key visual)."
    )
    hero_video_prompt: Optional[str] = Field(
        default=None,
        description="Video generation prompt for hero shot scenes.",
        max_length=500
    )


class WebtoonScript(BaseModel):
    """
    Complete webtoon script with characters and panels.
    
    Contains all character definitions and sequential panels
    for the webtoon story.
    """
    characters: List[Character] = Field(
        ..., 
        description="List of all characters in the webtoon.",
        min_items=1,
        max_items=20
    )
    scenes: List[WebtoonScene] = Field(
        default_factory=list,
        description="List of sequential scenes (8-20 recommended).",
        max_items=50
    )

    @model_validator(mode="before")
    @classmethod
    def ensure_scenes_from_legacy_panels(cls, data: Any) -> Any:
        """
        Accept legacy payloads that still pass flat `panels` lists.

        The release 2.x integration moved the canonical schema to `scenes`,
        but a large part of the existing code and tests still instantiate
        `WebtoonScript(characters=[...], panels=[...])`. To preserve backward
        compatibility we automatically wrap those panels into one-panel scenes.
        """
        if not isinstance(data, dict):
            return data

        if data.get("scenes"):
            return data

        legacy_panels = data.get("panels")
        if not legacy_panels:
            return data

        scenes: list[dict[str, Any]] = []
        for idx, panel in enumerate(legacy_panels, start=1):
            if isinstance(panel, WebtoonPanel):
                panel_payload = panel.model_dump()
            else:
                panel_payload = dict(panel)
            panel_payload.setdefault("scene_number", idx)
            scenes.append(
                {
                    "scene_number": idx,
                    "scene_type": "story",
                    "scene_title": panel_payload.get("story_beat", "") or f"Scene {idx}",
                    "panels": [panel_payload],
                    "is_hero_shot": False,
                    "hero_video_prompt": None,
                }
            )

        patched = dict(data)
        patched["scenes"] = scenes
        return patched
    
    @property
    def panels(self) -> List[WebtoonPanel]:
        """Get all panels from all scenes as a flat list for backward compatibility."""
        all_panels = []
        panel_number = 1
        for scene in self.scenes:
            for panel in scene.panels:
                # Update panel number to be sequential across all scenes
                panel.panel_number = panel_number
                all_panels.append(panel)
                panel_number += 1
        return all_panels
    
    class Config:
        json_schema_extra = {
            "example": {
                "characters": [
                    {
                        "name": "Ji-hoon",
                        "gender": "male",
                        "face": "sharp jawline, dark brown eyes, olive skin",
                        "hair": "short black hair, neatly styled",
                        "body": "tall athletic build, broad shoulders",
                        "outfit": "tailored navy suit with white shirt",
                        "mood": "confident and charismatic",
                        "visual_description": "A tall man with sharp jawline, dark brown eyes, olive skin, short black hair neatly styled, athletic build with broad shoulders, wearing a tailored navy suit with white shirt, confident demeanor"
                    }
                ],
                "panels": [
                    {
                        "panel_number": 1,
                        "shot_type": "Wide Shot",
                        "active_character_names": ["Ji-hoon"],
                        "visual_prompt": "Wide shot of a tall man with sharp jawline, dark brown eyes, olive skin (Ji-hoon) standing in a modern office",
                        "dialogue": "Ji-hoon: 'This is just the beginning.'"
                    }
                ]
            }
        }



class CharacterImage(BaseModel):
    """
    Model for generated character images.
    
    Attributes:
        id: Unique identifier for the image
        character_name: Name of the character
        description: Visual description used to generate the image
        image_url: URL or base64 encoded image data
        created_at: Timestamp when the image was created
        is_selected: Whether this image is selected as the final version
    """
    id: str = Field(..., description="Unique image ID")
    character_name: str = Field(..., description="Character name")
    description: str = Field(..., description="Visual description used for generation")
    image_url: str = Field(..., description="Image URL or base64 data")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    is_selected: bool = Field(default=False, description="Is this the selected final image")
    prompt_used: str = Field(default="", description="The exact prompt used for generation")


class PageImage(BaseModel):
    """
    Model for generated multi-panel page images.
    
    Attributes:
        id: Unique identifier for the image
        page_number: Page number this image belongs to
        panel_indices: List of panel indices included in this page
        image_url: URL or base64 encoded image data
        created_at: Timestamp when the image was created
        is_selected: Whether this is the selected final image
    """
    id: str = Field(..., description="Unique image ID")
    page_number: int = Field(..., description="Page number")
    panel_indices: List[int] = Field(..., description="Indices of panels in this page")
    image_url: str = Field(..., description="Image URL or base64 data")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    is_selected: bool = Field(default=False, description="Is this the selected image")


class WebtoonScriptResponse(BaseModel):
    """
    Response model for webtoon script with generated images.
    
    Attributes:
        script_id: Unique identifier for the script
        story_id: ID of the source story
        characters: List of characters with descriptions
        panels: List of scene panels
        character_images: Dictionary mapping character names to their generated images
        scene_images: Dictionary mapping panel numbers to generated scene images
        page_images: Dictionary mapping page numbers to generated page images
        created_at: Timestamp when the script was created
    """
    script_id: str = Field(..., description="Unique script ID")
    story_id: str = Field(..., description="Source story ID")
    characters: List[Character] = Field(..., description="List of characters")
    panels: List[WebtoonPanel] = Field(..., description="List of scene panels")
    character_images: dict = Field(default_factory=dict, description="Character name to images mapping")
    scene_images: dict = Field(default_factory=dict, description="Panel number to scene images mapping")
    page_images: dict = Field(default_factory=dict, description="Page number to page images mapping")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class GenerateWebtoonRequest(BaseModel):
    """
    Request model for webtoon script generation.

    Attributes:
        story_id: ID of the story to convert to webtoon script
        story_content: Optional direct story content (bypasses story lookup if provided)
    """
    story_id: str = Field(..., description="Story ID to convert")
    story_content: Optional[str] = Field(default=None, description="Optional direct story content (bypasses story lookup)")
    genre: Optional[str] = Field(default="MODERN_ROMANCE_DRAMA", description="Story genre for narrative style")
    image_style: Optional[str] = Field(default="SOFT_ROMANTIC_WEBTOON", description="Visual style/mood for image generation")


class GenerateCharacterImageRequest(BaseModel):
    """
    Request model for character image generation.
    
    Attributes:
        script_id: ID of the webtoon script
        character_name: Name of the character
        description: Visual description for image generation
        gender: Character gender for base style selection
        image_style: Image style/mood selection
        reference_image_url: Optional reference image URL for consistent character generation
    """
    script_id: str = Field(..., description="Webtoon script ID")
    character_name: str = Field(..., description="Character name")
    description: str = Field(..., description="Visual description for generation")
    gender: str = Field(..., description="Character gender (male/female)")
    image_style: str = Field(..., description="Image style/genre selection")
    reference_image_url: Optional[str] = Field(default=None, description="Optional reference image URL for multimodal generation")

    @field_validator('image_style')
    @classmethod
    def validate_image_style(cls, v: str) -> str:
        if v not in VISUAL_STYLE_PROMPTS:
            raise ValueError(f"Invalid image_style '{v}'. Must be one of: {list(VISUAL_STYLE_PROMPTS.keys())}")
        return v


class ImportCharacterImageRequest(BaseModel):
    """
    Request model for importing an existing character image into a script context.
    
    Attributes:
        script_id: ID of the target webtoon script
        character_name: Name of the character
        image_url: URL of the existing image to import
        description: Visual description for the image record
    """
    script_id: str = Field(..., description="Target webtoon script ID")
    character_name: str = Field(..., description="Character name")
    image_url: str = Field(..., description="Image URL to import")
    description: str = Field(..., description="Visual description for record")


class GenerateSceneImageRequest(BaseModel):
    """
    Request model for scene image generation.
    
    Attributes:
        script_id: ID of the webtoon script
        panel_number: Panel number to generate image for
        visual_prompt: Visual prompt (possibly edited by user)
        genre: Genre/style for image generation
        active_character_names: Optional override for active characters in scene.
    """
    script_id: str = Field(..., description="Webtoon script ID")
    panel_number: int = Field(..., description="Panel number", ge=1)
    visual_prompt: str = Field(..., description="Visual prompt for generation")
    genre: str = Field(..., description="Genre/style selection")
    active_character_names: Optional[List[str]] = Field(
        default=None, 
        description="Override active characters for this generation"
    )


class SceneImage(BaseModel):
    """
    Model for generated scene images.
    
    Attributes:
        id: Unique identifier for the image
        panel_number: Panel number this image belongs to
        image_url: URL or base64 encoded image data
        prompt_used: The prompt used to generate this image
        is_selected: Whether this is the selected final image
        created_at: Timestamp when the image was created
    """
    id: str = Field(..., description="Unique image ID")
    panel_number: int = Field(..., description="Panel number")
    image_url: str = Field(..., description="Image URL or base64 data")
    prompt_used: str = Field(..., description="Prompt used for generation")
    is_selected: bool = Field(default=False, description="Is this the selected image")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")


class GenerateShortsRequest(BaseModel):
    """
    Request model for shorts generation.
    """
    topic: Optional[str] = Field(default=None, description="Topic for the shorts script")
