"""
Pytest configuration and shared fixtures for fidelity validation tests.
"""

import os
import sys
import pytest

# Add backend app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set environment variables for testing
os.environ.setdefault("REDDIT_CLIENT_ID", "test_client_id")
os.environ.setdefault("REDDIT_CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("GOOGLE_API_KEY", "test_google_api_key")


@pytest.fixture
def sample_panel_data():
    """Sample panel data for testing."""
    return {
        "panel_number": 1,
        "visual_description": "A man stands in a dimly lit room, his face half-shadowed",
        "dialogue": [
            {"character": "John", "text": "We need to talk."}
        ],
        "shot_type": "medium",
        "environment": "dark room"
    }


@pytest.fixture
def sample_character_data():
    """Sample character data for testing."""
    return {
        "name": "John",
        "visual_description": "A tall man in his 30s with dark hair and a serious expression"
    }


@pytest.fixture
def sample_fidelity_state():
    """Complete sample fidelity state for testing."""
    return {
        "seed": "A detective uncovers a conspiracy",
        "original_story": "Detective Sarah investigates a series of murders...",
        "story_summary": "Sarah solves murders linked to a corporation",
        "character_motivations": {
            "Sarah": {
                "goal": "solve the case",
                "motivation": "justice for victims",
                "obstacle": "powerful enemies"
            }
        },
        "key_conflicts": [
            "Sarah vs corrupt corporation",
            "Sarah vs her own doubts"
        ],
        "plot_points": [
            "Discovery of first body",
            "Finding the connection",
            "Confronting the villain",
            "Resolution"
        ],
        "script_panels": [
            {
                "panel_number": 1,
                "visual_description": "A woman examines a crime scene",
                "dialogue": [],
                "shot_type": "wide",
                "environment": "crime scene"
            },
            {
                "panel_number": 2,
                "visual_description": "Close-up of her determined face",
                "dialogue": [{"character": "Sarah", "text": "I'll find the truth."}],
                "shot_type": "close-up",
                "environment": "crime scene"
            }
        ],
        "characters": [
            {"name": "Sarah", "visual_description": "A determined female detective in her 40s"}
        ],
        "reconstructed_story": "",
        "inferred_motivations": {},
        "inferred_conflicts": [],
        "unclear_elements": [],
        "reader_confidence": 0.0,
        "fidelity_score": 0.0,
        "information_gaps": [],
        "critique": None,
        "iteration": 1,
        "max_iterations": 3,
        "is_validated": False,
        "current_step": "initial",
        "error": None
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "story": "A sample generated story...",
        "summary": "Brief summary",
        "character_motivations": {
            "Hero": {
                "goal": "save the day",
                "motivation": "protect loved ones",
                "obstacle": "powerful villain"
            }
        },
        "key_conflicts": ["Hero vs Villain"],
        "plot_points": ["Beginning", "Middle", "End"]
    }
