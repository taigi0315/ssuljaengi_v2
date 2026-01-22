"""
Unit tests for SFX Planner service.

Tests the SFX planning functionality including keyword detection,
emotion/action mapping, and bundle generation.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.models.sfx import (
    ImpactText,
    MotionEffect,
    ScreenEffect,
    EmotionalEffect,
    SFXBundle,
    EffectIntensity,
    MotionEffectType,
    ScreenEffectType,
    EmotionalEffectType,
)
from app.models.story import WebtoonPanel
from app.services.sfx_planner import (
    SFXPlanner,
    create_sfx_planner,
    plan_sfx_for_panels,
    _detect_emotion_from_text,
    _detect_action_from_text,
    _map_intensity,
    EMOTION_KEYWORDS,
    ACTION_KEYWORDS,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_panel_neutral():
    """Create a neutral panel for testing."""
    return WebtoonPanel(
        panel_number=1,
        visual_prompt="A character standing in a room",
        dialogue=[{"character": "Character A", "text": "Hello there."}],
        emotional_intensity=5
    )


@pytest.fixture
def mock_panel_angry():
    """Create an angry panel for testing."""
    panel = WebtoonPanel(
        panel_number=2,
        visual_prompt="Character's face contorted with rage and fury",
        dialogue=[{"character": "Character A", "text": "I am so angry right now!"}],
        emotional_intensity=8
    )
    return panel


@pytest.fixture
def mock_panel_romantic():
    """Create a romantic panel for testing."""
    return WebtoonPanel(
        panel_number=3,
        visual_prompt="Two characters gazing at each other with blush on their cheeks",
        dialogue=[{"character": "Character A", "text": "I love you..."}],
        emotional_intensity=7
    )


@pytest.fixture
def mock_panel_action():
    """Create an action panel for testing."""
    return WebtoonPanel(
        panel_number=4,
        visual_prompt="Character punches the villain with great force, impact visible",
        dialogue=[],
        emotional_intensity=9
    )


@pytest.fixture
def mock_panel_sad():
    """Create a sad panel for testing."""
    return WebtoonPanel(
        panel_number=5,
        visual_prompt="Character with tears streaming down their face",
        dialogue=[{"character": "Character A", "text": "I can't believe it's over..."}],
        emotional_intensity=6
    )


@pytest.fixture
def planner():
    """Create SFX planner instance."""
    return SFXPlanner()


# ============================================================================
# Test Utility Functions
# ============================================================================

class TestEmotionDetection:
    """Test emotion detection from text."""
    
    def test_detect_anger(self):
        """Test anger detection."""
        assert _detect_emotion_from_text("I am so angry!") == "anger"
        assert _detect_emotion_from_text("This makes me furious") == "anger"
        assert _detect_emotion_from_text("He was MAD at her") == "anger"
    
    def test_detect_love(self):
        """Test love detection."""
        assert _detect_emotion_from_text("I love you") == "love"
        assert _detect_emotion_from_text("She has a crush on him") == "love"
    
    def test_detect_fear(self):
        """Test fear detection."""
        assert _detect_emotion_from_text("I'm scared") == "fear"
        assert _detect_emotion_from_text("He was terrified") == "fear"
        assert _detect_emotion_from_text("feeling nervous today") == "fear"
    
    def test_detect_sad(self):
        """Test sadness detection."""
        assert _detect_emotion_from_text("I feel so sad") == "sad"
        assert _detect_emotion_from_text("tears falling down") == "sad"
    
    def test_detect_happy(self):
        """Test happiness detection."""
        assert _detect_emotion_from_text("I'm so happy!") == "happy"
        assert _detect_emotion_from_text("He was excited") == "happy"
    
    def test_detect_surprise(self):
        """Test surprise detection."""
        assert _detect_emotion_from_text("I was surprised") == "surprise"
        assert _detect_emotion_from_text("She looked shocked") == "surprise"
    
    def test_no_emotion_detected(self):
        """Test when no emotion is detected."""
        assert _detect_emotion_from_text("The sky is blue") is None
        assert _detect_emotion_from_text("") is None


class TestActionDetection:
    """Test action detection from text."""
    
    def test_detect_impact(self):
        """Test impact action detection."""
        assert _detect_action_from_text("He punched the wall") == "impact"
        assert _detect_action_from_text("The car crashed into the fence") == "impact"
        assert _detect_action_from_text("She hit the target") == "impact"
    
    def test_detect_run(self):
        """Test running action detection."""
        assert _detect_action_from_text("running through the field") == "run"
        assert _detect_action_from_text("He sprinted away") == "run"
    
    def test_detect_fall(self):
        """Test falling action detection."""
        assert _detect_action_from_text("He started falling") == "fall"
        assert _detect_action_from_text("She tripped over a rock") == "fall"
    
    def test_detect_realization(self):
        """Test realization detection."""
        assert _detect_action_from_text("She finally realized the truth") == "realization"
        assert _detect_action_from_text("The discovery shocked him") == "realization"
    
    def test_no_action_detected(self):
        """Test when no action is detected."""
        assert _detect_action_from_text("sitting quietly") is None
        assert _detect_action_from_text("") is None


class TestIntensityMapping:
    """Test intensity mapping."""
    
    def test_low_intensity(self):
        """Test low intensity (1-3) maps to subtle."""
        assert _map_intensity(1) == EffectIntensity.SUBTLE
        assert _map_intensity(2) == EffectIntensity.SUBTLE
        assert _map_intensity(3) == EffectIntensity.SUBTLE
    
    def test_medium_intensity(self):
        """Test medium intensity (4-6) maps to medium."""
        assert _map_intensity(4) == EffectIntensity.MEDIUM
        assert _map_intensity(5) == EffectIntensity.MEDIUM
        assert _map_intensity(6) == EffectIntensity.MEDIUM
    
    def test_high_intensity(self):
        """Test high intensity (7-10) maps to intense."""
        assert _map_intensity(7) == EffectIntensity.INTENSE
        assert _map_intensity(8) == EffectIntensity.INTENSE
        assert _map_intensity(9) == EffectIntensity.INTENSE
        assert _map_intensity(10) == EffectIntensity.INTENSE


# ============================================================================
# Test SFXPlanner Initialization
# ============================================================================

class TestSFXPlannerInit:
    """Test SFXPlanner initialization."""
    
    def test_default_init(self):
        """Test default initialization."""
        planner = SFXPlanner()
        assert planner._use_llm is False
        assert planner._llm_client is None
    
    def test_init_with_llm(self):
        """Test initialization with LLM."""
        mock_client = MagicMock()
        planner = SFXPlanner(use_llm=True, llm_client=mock_client)
        assert planner._use_llm is True
        assert planner._llm_client is mock_client
    
    def test_factory_function(self):
        """Test create_sfx_planner factory function."""
        planner = create_sfx_planner()
        assert isinstance(planner, SFXPlanner)
        assert planner._use_llm is False
    
    def test_factory_function_with_llm(self):
        """Test factory function with LLM."""
        mock_client = MagicMock()
        planner = create_sfx_planner(use_llm=True, llm_client=mock_client)
        assert planner._use_llm is True


# ============================================================================
# Test SFX Planning
# ============================================================================

class TestPlanSFX:
    """Test the main plan_sfx function."""
    
    def test_plan_sfx_returns_bundles(self, planner, mock_panel_neutral):
        """Test that plan_sfx returns list of bundles."""
        bundles = planner.plan_sfx([mock_panel_neutral])
        
        assert len(bundles) == 1
        assert isinstance(bundles[0], SFXBundle)
        assert bundles[0].panel_number == 1
    
    def test_plan_sfx_multiple_panels(self, planner, mock_panel_neutral, mock_panel_angry):
        """Test planning for multiple panels."""
        bundles = planner.plan_sfx([mock_panel_neutral, mock_panel_angry])
        
        assert len(bundles) == 2
        assert bundles[0].panel_number == 1
        assert bundles[1].panel_number == 2
    
    def test_angry_panel_gets_effects(self, planner, mock_panel_angry):
        """Test that angry panel gets appropriate effects."""
        bundles = planner.plan_sfx([mock_panel_angry])
        bundle = bundles[0]
        
        # Should have some effects due to anger + high intensity
        assert bundle.has_effects
        
        # Check for expected effect types
        effect_types = [e.type for e in bundle.emotional_effects]
        # Anger should trigger dark_aura or anger_vein
        assert any(t in [EmotionalEffectType.DARK_AURA, EmotionalEffectType.ANGER_VEIN] 
                   for t in effect_types) or len(bundle.motion_effects) > 0
    
    def test_romantic_panel_gets_effects(self, planner, mock_panel_romantic):
        """Test that romantic panel gets appropriate effects."""
        bundles = planner.plan_sfx([mock_panel_romantic])
        bundle = bundles[0]
        
        # Should have romantic effects
        assert bundle.has_effects
        
        # Check for romantic effect types
        effect_types = [e.type for e in bundle.emotional_effects]
        assert any(t in [EmotionalEffectType.SPARKLES, EmotionalEffectType.HEARTS, 
                         EmotionalEffectType.BLUSH, EmotionalEffectType.FLOWERS] 
                   for t in effect_types)
    
    def test_action_panel_gets_motion_effects(self, planner, mock_panel_action):
        """Test that action panel gets motion effects."""
        bundles = planner.plan_sfx([mock_panel_action])
        bundle = bundles[0]
        
        # Should have motion or screen effects for punch/impact
        assert bundle.has_effects
        
        # Check for impact-related effects
        has_motion = len(bundle.motion_effects) > 0
        has_impact_text = len(bundle.impact_texts) > 0
        has_screen = any(e.type in [ScreenEffectType.SHAKE, ScreenEffectType.FLASH] 
                         for e in bundle.screen_effects)
        
        assert has_motion or has_impact_text or has_screen
    
    def test_sad_panel_gets_effects(self, planner, mock_panel_sad):
        """Test that sad panel gets appropriate effects."""
        bundles = planner.plan_sfx([mock_panel_sad])
        bundle = bundles[0]
        
        # Should have sad-related effects
        assert bundle.has_effects
        
        # Check for sad effect types
        effect_types = [e.type for e in bundle.emotional_effects]
        screen_types = [e.type for e in bundle.screen_effects]
        
        has_tears = EmotionalEffectType.TEARS in effect_types
        has_vignette = ScreenEffectType.VIGNETTE in screen_types
        
        assert has_tears or has_vignette or len(bundle.screen_effects) > 0
    
    def test_neutral_panel_minimal_effects(self, planner, mock_panel_neutral):
        """Test that neutral panel gets minimal or no effects."""
        bundles = planner.plan_sfx([mock_panel_neutral])
        bundle = bundles[0]
        
        # Neutral panel should have few or no effects
        # (May have vignette if intensity is considered)
        assert bundle.total_effects <= 2


class TestEffectLimiting:
    """Test that effects are properly limited."""
    
    def test_effects_limited_per_category(self, planner):
        """Test that effects are limited to max 2 per category."""
        # Create a panel that would trigger many effects
        extreme_panel = WebtoonPanel(
            panel_number=1,
            visual_prompt="Angry character punches with crash impact slam bang fury rage",
            dialogue=[{"character": "A", "text": "I'm furious angry mad!"}],
            emotional_intensity=10
        )
        
        bundles = planner.plan_sfx([extreme_panel])
        bundle = bundles[0]
        
        # Each category should have max 2 effects
        assert len(bundle.impact_texts) <= 2
        assert len(bundle.motion_effects) <= 2
        assert len(bundle.screen_effects) <= 2
        assert len(bundle.emotional_effects) <= 2


class TestHighIntensityEffects:
    """Test high intensity panel effects."""
    
    def test_high_intensity_adds_vignette(self, planner):
        """Test that high intensity panels may get vignette."""
        high_intensity_panel = WebtoonPanel(
            panel_number=1,
            visual_prompt="Intense dramatic moment",
            dialogue=[],
            emotional_intensity=9
        )
        
        bundles = planner.plan_sfx([high_intensity_panel])
        bundle = bundles[0]
        
        # High intensity should trigger vignette
        vignette_exists = any(
            e.type == ScreenEffectType.VIGNETTE 
            for e in bundle.screen_effects
        )
        assert vignette_exists


# ============================================================================
# Test Convenience Functions
# ============================================================================

class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_plan_sfx_for_panels(self, mock_panel_neutral, mock_panel_angry):
        """Test plan_sfx_for_panels convenience function."""
        panels = [mock_panel_neutral, mock_panel_angry]
        bundles = plan_sfx_for_panels(panels)
        
        assert len(bundles) == 2
        assert all(isinstance(b, SFXBundle) for b in bundles)


# ============================================================================
# Test Keyword Constants
# ============================================================================

class TestKeywordConstants:
    """Test that keyword constants are properly defined."""
    
    def test_emotion_keywords_coverage(self):
        """Test emotion keywords cover expected emotions."""
        expected_emotions = ["anger", "love", "fear", "sad", "happy", "surprise", "romantic"]
        
        for emotion in expected_emotions:
            assert emotion in EMOTION_KEYWORDS
            assert len(EMOTION_KEYWORDS[emotion]) > 0
    
    def test_action_keywords_coverage(self):
        """Test action keywords cover expected actions."""
        expected_actions = ["impact", "run", "fall", "realization"]
        
        for action in expected_actions:
            assert action in ACTION_KEYWORDS
            assert len(ACTION_KEYWORDS[action]) > 0
