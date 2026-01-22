"""
Unit tests for the Cinematographer service.

Tests shot planning, variety rules enforcement, and scoring.
"""

import pytest
from app.models.story import (
    Shot,
    ShotPlan,
    ShotType,
    CameraAngle,
    WebtoonScript,
    WebtoonPanel,
    Character
)
from app.services.cinematographer import CinematographerService, cinematographer_service


@pytest.fixture
def sample_character():
    """Sample character for testing."""
    return Character(
        name="Ji-hoon",
        reference_tag="Ji-hoon(20s, athletic build, black hair)",
        gender="male",
        age="25",
        face="sharp jawline, dark eyes",
        hair="short black hair",
        body="athletic build",
        outfit="casual clothes",
        mood="confident",
        visual_description="A young man with sharp jawline, dark eyes, short black hair, athletic build, wearing casual clothes, confident demeanor"
    )


@pytest.fixture
def sample_panel():
    """Sample panel for testing."""
    return WebtoonPanel(
        panel_number=1,
        shot_type="Medium Shot",
        active_character_names=["Ji-hoon"],
        visual_prompt="A young man standing in a coffee shop",
        story_beat="Ji-hoon enters the coffee shop",
        environment_focus="coffee shop",
        emotional_intensity=5
    )


@pytest.fixture
def sample_script(sample_character, sample_panel):
    """Sample script with one panel."""
    return WebtoonScript(
        characters=[sample_character],
        panels=[sample_panel]
    )


@pytest.fixture
def sample_shots():
    """Sample shots for variety testing."""
    return [
        Shot(
            shot_id="scene_1_shot_1",
            shot_type=ShotType.WIDE,
            subject="coffee_shop",
            subject_characters=[],
            frame_percentage=20,
            angle=CameraAngle.EYE_LEVEL,
            emotional_purpose="establish_setting",
            emotional_intensity=3,
            belongs_to_scene=1,
            story_beat="Establishing shot"
        ),
        Shot(
            shot_id="scene_1_shot_2",
            shot_type=ShotType.MEDIUM,
            subject="ji-hoon",
            subject_characters=["Ji-hoon"],
            frame_percentage=45,
            angle=CameraAngle.EYE_LEVEL,
            emotional_purpose="introduce_character",
            emotional_intensity=4,
            belongs_to_scene=1,
            story_beat="Ji-hoon enters"
        ),
        Shot(
            shot_id="scene_1_shot_3",
            shot_type=ShotType.CLOSE_UP,
            subject="ji-hoon_face",
            subject_characters=["Ji-hoon"],
            frame_percentage=75,
            angle=CameraAngle.EYE_LEVEL,
            emotional_purpose="show_emotion",
            emotional_intensity=6,
            belongs_to_scene=1,
            story_beat="Ji-hoon's reaction"
        ),
    ]


class TestShotType:
    """Tests for ShotType enum."""

    def test_shot_type_values(self):
        """Test all shot types are defined."""
        assert ShotType.EXTREME_CLOSE_UP.value == "extreme_close_up"
        assert ShotType.CLOSE_UP.value == "close_up"
        assert ShotType.MEDIUM.value == "medium"
        assert ShotType.WIDE.value == "wide"
        assert ShotType.DETAIL.value == "detail"

    def test_frame_percentage_range(self):
        """Test frame percentage ranges are correct."""
        assert ShotType.get_frame_percentage_range(ShotType.EXTREME_CLOSE_UP) == (85, 100)
        assert ShotType.get_frame_percentage_range(ShotType.CLOSE_UP) == (70, 85)
        assert ShotType.get_frame_percentage_range(ShotType.MEDIUM) == (30, 50)
        assert ShotType.get_frame_percentage_range(ShotType.WIDE) == (15, 30)


class TestShot:
    """Tests for Shot model."""

    def test_shot_creation(self):
        """Test basic shot creation."""
        shot = Shot(
            shot_id="test_shot_1",
            shot_type=ShotType.MEDIUM,
            subject="character",
            frame_percentage=45,
            emotional_purpose="test",
            belongs_to_scene=1
        )
        assert shot.shot_id == "test_shot_1"
        assert shot.shot_type == ShotType.MEDIUM
        assert shot.frame_percentage == 45
        assert shot.emotional_intensity == 5  # default

    def test_shot_with_all_fields(self):
        """Test shot with all fields populated."""
        shot = Shot(
            shot_id="full_shot",
            shot_type=ShotType.CLOSE_UP,
            subject="hero_face",
            subject_characters=["Hero"],
            frame_percentage=75,
            angle=CameraAngle.LOW_ANGLE,
            emotional_purpose="show_determination",
            emotional_intensity=8,
            belongs_to_scene=2,
            story_beat="Hero makes a decision"
        )
        assert shot.subject_characters == ["Hero"]
        assert shot.angle == CameraAngle.LOW_ANGLE
        assert shot.emotional_intensity == 8


class TestShotPlan:
    """Tests for ShotPlan model."""

    def test_empty_shot_plan_variety_calculation(self):
        """Test variety score calculation handles edge case."""
        # ShotPlan requires at least 1 shot, so we test the calculate method directly
        # by creating a minimal plan
        shot = Shot(
            shot_id="single_shot",
            shot_type=ShotType.MEDIUM,
            subject="scene",
            frame_percentage=45,
            emotional_purpose="test",
            belongs_to_scene=1
        )
        plan = ShotPlan(shots=[shot], total_scenes=1)
        score = plan.calculate_variety_score()
        # Single shot should have low variety but not zero
        assert 0.0 <= score <= 1.0

    def test_shot_plan_creation(self, sample_shots):
        """Test shot plan creation with shots."""
        plan = ShotPlan(shots=sample_shots, total_scenes=1)
        assert len(plan.shots) == 3
        assert plan.total_scenes == 1

    def test_calculate_variety_score(self, sample_shots):
        """Test variety score calculation."""
        plan = ShotPlan(shots=sample_shots, total_scenes=1)
        score = plan.calculate_variety_score()

        assert 0.0 <= score <= 1.0
        assert plan.variety_score == score
        assert "wide" in plan.shot_type_distribution
        assert "medium" in plan.shot_type_distribution
        assert "close_up" in plan.shot_type_distribution

    def test_low_variety_score(self):
        """Test that low variety gives low score."""
        # All same shot type
        shots = [
            Shot(
                shot_id=f"shot_{i}",
                shot_type=ShotType.MEDIUM,
                subject="scene",
                frame_percentage=45,
                emotional_purpose="test",
                belongs_to_scene=1
            )
            for i in range(10)
        ]
        plan = ShotPlan(shots=shots, total_scenes=1)
        score = plan.calculate_variety_score()

        # Should be penalized for no variety
        assert score < 0.5


class TestCinematographerService:
    """Tests for CinematographerService."""

    def test_service_initialization(self):
        """Test service can be initialized."""
        service = CinematographerService()
        assert service.llm is not None

    def test_format_scenes(self, sample_script):
        """Test scene formatting for prompt."""
        service = CinematographerService()
        scenes_text = service._format_scenes(sample_script.panels)

        assert "Scene 1" in scenes_text
        assert "Ji-hoon" in scenes_text
        assert "coffee shop" in scenes_text.lower()

    def test_format_characters(self, sample_script):
        """Test character formatting for prompt."""
        service = CinematographerService()
        chars_text = service._format_characters(sample_script.characters)

        assert "Ji-hoon" in chars_text
        assert "male" in chars_text

    def test_enforce_variety_rules_consecutive(self):
        """Test that consecutive same-type shots are fixed."""
        service = CinematographerService()

        # Create 3 consecutive medium shots (violation)
        shots = [
            Shot(
                shot_id=f"shot_{i}",
                shot_type=ShotType.MEDIUM,
                subject="scene",
                frame_percentage=45,
                emotional_purpose="test",
                emotional_intensity=5,
                belongs_to_scene=1
            )
            for i in range(5)
        ]
        plan = ShotPlan(shots=shots, total_scenes=1)

        fixed_plan = service._enforce_variety_rules(plan)

        # Check that no 3 consecutive shots have same type
        for i in range(2, len(fixed_plan.shots)):
            types = [
                fixed_plan.shots[i].shot_type,
                fixed_plan.shots[i-1].shot_type,
                fixed_plan.shots[i-2].shot_type
            ]
            assert len(set(types)) > 1, f"Found 3 consecutive same types at index {i}"

    def test_enforce_variety_rules_emotional_peak(self):
        """Test that high intensity shots become close-ups."""
        service = CinematographerService()

        shots = [
            Shot(
                shot_id="shot_1",
                shot_type=ShotType.WIDE,  # Should become close-up
                subject="scene",
                frame_percentage=20,
                emotional_purpose="emotional_peak",
                emotional_intensity=9,  # High intensity
                belongs_to_scene=1
            )
        ]
        plan = ShotPlan(shots=shots, total_scenes=1)

        fixed_plan = service._enforce_variety_rules(plan)

        # High intensity shot should be close-up
        assert fixed_plan.shots[0].shot_type in [
            ShotType.CLOSE_UP,
            ShotType.EXTREME_CLOSE_UP,
            ShotType.DETAIL
        ]

    def test_get_alternative_shot_type(self):
        """Test alternative shot type selection."""
        service = CinematographerService()

        # High intensity should get close-up
        alt = service._get_alternative_shot_type(ShotType.WIDE, intensity=8)
        assert alt == ShotType.CLOSE_UP

        # Low intensity should get wider shots
        alt = service._get_alternative_shot_type(ShotType.CLOSE_UP, intensity=3)
        assert alt in [ShotType.WIDE, ShotType.MEDIUM_WIDE, ShotType.MEDIUM]

    def test_generate_fallback_shot_plan(self, sample_script):
        """Test fallback plan generation."""
        service = CinematographerService()

        plan = service._generate_fallback_shot_plan(sample_script, target_count=10)

        assert len(plan.shots) > 0
        assert plan.total_scenes == len(sample_script.panels)
        assert plan.variety_score > 0  # Should have some variety

    def test_score_variety(self, sample_shots):
        """Test detailed variety scoring."""
        service = CinematographerService()
        plan = ShotPlan(shots=sample_shots, total_scenes=1)

        result = service.score_variety(plan)

        assert "overall_score" in result
        assert "type_distribution" in result
        assert "consecutive_violations" in result
        assert "close_up_ratio" in result
        assert "issues" in result
        assert 0.0 <= result["overall_score"] <= 1.0

    def test_score_variety_low_variety(self):
        """Test scoring catches low variety."""
        service = CinematographerService()

        # All same type
        shots = [
            Shot(
                shot_id=f"shot_{i}",
                shot_type=ShotType.MEDIUM,
                subject="scene",
                frame_percentage=45,
                emotional_purpose="test",
                belongs_to_scene=1
            )
            for i in range(10)
        ]
        plan = ShotPlan(shots=shots, total_scenes=1)

        result = service.score_variety(plan)

        assert result["overall_score"] < 0.5
        assert len(result["issues"]) > 0
        assert "medium" in str(result["issues"]).lower()

    def test_score_variety_consecutive_violations(self):
        """Test scoring catches consecutive violations."""
        service = CinematographerService()

        # 3 consecutive same types
        shots = [
            Shot(shot_id="s1", shot_type=ShotType.MEDIUM, subject="a", frame_percentage=45, emotional_purpose="t", belongs_to_scene=1),
            Shot(shot_id="s2", shot_type=ShotType.MEDIUM, subject="b", frame_percentage=45, emotional_purpose="t", belongs_to_scene=1),
            Shot(shot_id="s3", shot_type=ShotType.MEDIUM, subject="c", frame_percentage=45, emotional_purpose="t", belongs_to_scene=1),
            Shot(shot_id="s4", shot_type=ShotType.WIDE, subject="d", frame_percentage=20, emotional_purpose="t", belongs_to_scene=1),
        ]
        plan = ShotPlan(shots=shots, total_scenes=1)

        result = service.score_variety(plan)

        assert result["consecutive_violations"] >= 1


class TestGlobalInstance:
    """Test the global cinematographer instance."""

    def test_global_instance_exists(self):
        """Test global instance is available."""
        assert cinematographer_service is not None
        assert isinstance(cinematographer_service, CinematographerService)
