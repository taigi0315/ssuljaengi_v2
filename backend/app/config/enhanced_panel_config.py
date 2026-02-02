"""
Enhanced Panel Configuration for the webtoon generation system.

This module provides configuration classes for the enhanced panel generation
system that supports 20-50 panels with flexible scene structures and
intelligent image generation strategies.
"""

from pydantic import BaseModel, Field
from typing import Dict, Tuple, Optional
from enum import Enum


class GenreType(str, Enum):
    """Supported genre types for panel generation."""
    ROMANCE = "romance"
    DRAMA = "drama"
    ACTION = "action"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    SUSPENSE = "suspense"
    COMEDY = "comedy"
    SLICE_OF_LIFE = "slice_of_life"
    DEFAULT = "default"


class EnhancedPanelConfig(BaseModel):
    """
    Configuration class for enhanced panel generation system.
    
    Supports configurable panel count settings, genre-specific targets,
    and image generation strategy preferences.
    """
    
    # Core panel count settings
    panel_count_min: int = Field(
        default=20,
        description="Minimum number of panels for a complete webtoon story",
        ge=10,
        le=100
    )
    
    panel_count_max: int = Field(
        default=50,
        description="Maximum number of panels before story becomes too long",
        ge=20,
        le=100
    )
    
    panel_count_ideal_min: int = Field(
        default=25,
        description="Ideal minimum panel count for optimal storytelling",
        ge=15,
        le=80
    )
    
    panel_count_ideal_max: int = Field(
        default=40,
        description="Ideal maximum panel count for optimal storytelling",
        ge=20,
        le=80
    )
    
    # Image generation strategy settings
    single_panel_ratio: float = Field(
        default=0.6,
        description="Minimum ratio of panels that should be single-panel images",
        ge=0.0,
        le=1.0
    )
    
    max_multi_panel_size: int = Field(
        default=3,
        description="Maximum number of panels allowed in a multi-panel image",
        ge=2,
        le=5
    )
    
    # Scene structure settings
    max_panels_per_scene: int = Field(
        default=8,
        description="Maximum number of panels allowed per scene",
        ge=1,
        le=10
    )
    
    min_panels_per_scene: int = Field(
        default=1,
        description="Minimum number of panels allowed per scene",
        ge=1,
        le=5
    )
    
    # Three-act distribution settings
    act1_panel_ratio: float = Field(
        default=0.25,
        description="Percentage of panels allocated to Act 1 (setup)",
        ge=0.15,
        le=0.35
    )
    
    act2_panel_ratio: float = Field(
        default=0.50,
        description="Percentage of panels allocated to Act 2 (development)",
        ge=0.40,
        le=0.60
    )
    
    act3_panel_ratio: float = Field(
        default=0.25,
        description="Percentage of panels allocated to Act 3 (resolution)",
        ge=0.15,
        le=0.35
    )
    
    # Genre-specific panel count targets
    genre_specific_targets: Dict[str, Tuple[int, int]] = Field(
        default_factory=lambda: {
            GenreType.ROMANCE: (25, 35),      # Romance benefits from more intimate panels
            GenreType.DRAMA: (30, 45),        # Drama needs panels for emotional development
            GenreType.ACTION: (35, 50),       # Action requires more panels for sequences
            GenreType.FANTASY: (35, 50),      # Fantasy needs world-building panels
            GenreType.THRILLER: (25, 40),     # Thriller uses tension-building sequences
            GenreType.SUSPENSE: (25, 40),     # Suspense similar to thriller
            GenreType.COMEDY: (20, 35),       # Comedy can be more concise
            GenreType.SLICE_OF_LIFE: (20, 30), # Slice-of-life focuses on moments
            GenreType.DEFAULT: (25, 40),      # Default fallback range
        },
        description="Genre-specific panel count target ranges (min, max)"
    )
    
    # Performance and optimization settings
    enable_caching: bool = Field(
        default=True,
        description="Enable caching for similar panel descriptions"
    )
    
    enable_progress_tracking: bool = Field(
        default=True,
        description="Enable progress indicators for large panel generations"
    )
    
    progress_threshold: int = Field(
        default=30,
        description="Panel count threshold above which progress tracking is enabled",
        ge=10,
        le=100
    )
    
    # Backward compatibility settings
    preserve_legacy_multi_panel: bool = Field(
        default=True,
        description="Preserve existing multi-panel functionality for backward compatibility"
    )
    
    legacy_multi_panel_max_size: int = Field(
        default=5,
        description="Maximum panel count for legacy multi-panel images",
        ge=2,
        le=7
    )
    
    def get_panel_range_for_genre(self, genre: str) -> Tuple[int, int]:
        """
        Get the panel count range for a specific genre.
        
        Args:
            genre: The genre type (case-insensitive)
            
        Returns:
            Tuple of (min_panels, max_panels) for the genre
        """
        # Normalize genre string
        genre_key = genre.lower().replace("-", "_").replace(" ", "_")
        
        # Try to find exact match first
        if genre_key in self.genre_specific_targets:
            return self.genre_specific_targets[genre_key]
        
        # Try to find partial match
        for key, value in self.genre_specific_targets.items():
            if genre_key in key or key in genre_key:
                return value
        
        # Return default if no match found
        return self.genre_specific_targets[GenreType.DEFAULT]
    
    def validate_panel_count(self, panel_count: int, genre: Optional[str] = None) -> bool:
        """
        Validate if a panel count is within acceptable range.
        
        Args:
            panel_count: Number of panels to validate
            genre: Optional genre for genre-specific validation
            
        Returns:
            True if panel count is valid, False otherwise
        """
        if genre:
            min_panels, max_panels = self.get_panel_range_for_genre(genre)
            return min_panels <= panel_count <= max_panels
        
        return self.panel_count_min <= panel_count <= self.panel_count_max
    
    def validate_scene_panel_count(self, scene_panel_count: int) -> bool:
        """
        Validate if a scene panel count is within acceptable range.
        
        Args:
            scene_panel_count: Number of panels in a single scene to validate
            
        Returns:
            True if scene panel count is valid, False otherwise
        """
        return self.min_panels_per_scene <= scene_panel_count <= self.max_panels_per_scene
    
    def get_ideal_panel_range(self, genre: Optional[str] = None) -> Tuple[int, int]:
        """
        Get the ideal panel count range.
        
        Args:
            genre: Optional genre for genre-specific range
            
        Returns:
            Tuple of (ideal_min, ideal_max) panel counts
        """
        if genre:
            genre_min, genre_max = self.get_panel_range_for_genre(genre)
            # Use genre range but constrain to ideal bounds
            ideal_min = max(genre_min, self.panel_count_ideal_min)
            ideal_max = min(genre_max, self.panel_count_ideal_max)
            return (ideal_min, ideal_max)
        
        return (self.panel_count_ideal_min, self.panel_count_ideal_max)
    
    def calculate_act_distribution(self, total_panels: int) -> Dict[str, int]:
        """
        Calculate panel distribution across three acts.
        
        Args:
            total_panels: Total number of panels to distribute
            
        Returns:
            Dictionary with act1_panels, act2_panels, act3_panels counts
        """
        act1_panels = max(1, round(total_panels * self.act1_panel_ratio))
        act2_panels = max(1, round(total_panels * self.act2_panel_ratio))
        act3_panels = max(1, total_panels - act1_panels - act2_panels)
        
        # Ensure we don't exceed total panels due to rounding
        total_calculated = act1_panels + act2_panels + act3_panels
        if total_calculated != total_panels:
            # Adjust act2 (largest act) to match total
            act2_panels += (total_panels - total_calculated)
        
        return {
            "act1_panels": act1_panels,
            "act2_panels": act2_panels,
            "act3_panels": act3_panels
        }
    
    def should_use_single_panel(self, current_single_ratio: float) -> bool:
        """
        Determine if next panel should be single-panel based on current ratio.
        
        Args:
            current_single_ratio: Current ratio of single panels
            
        Returns:
            True if next panel should be single-panel
        """
        return current_single_ratio < self.single_panel_ratio
    
    def model_post_init(self, __context) -> None:
        """Validate configuration after initialization."""
        # Ensure ideal range is within min/max bounds
        if self.panel_count_ideal_min < self.panel_count_min:
            raise ValueError("panel_count_ideal_min cannot be less than panel_count_min")
        
        if self.panel_count_ideal_max > self.panel_count_max:
            raise ValueError("panel_count_ideal_max cannot be greater than panel_count_max")
        
        if self.panel_count_ideal_min >= self.panel_count_ideal_max:
            raise ValueError("panel_count_ideal_min must be less than panel_count_ideal_max")
        
        # Ensure act ratios sum to approximately 1.0
        total_ratio = self.act1_panel_ratio + self.act2_panel_ratio + self.act3_panel_ratio
        if abs(total_ratio - 1.0) > 0.05:  # Allow 5% tolerance
            raise ValueError(f"Act ratios must sum to 1.0, got {total_ratio}")


# Global enhanced panel configuration instance
_enhanced_panel_config: Optional[EnhancedPanelConfig] = None


def get_enhanced_panel_config() -> EnhancedPanelConfig:
    """
    Get the global enhanced panel configuration instance.
    
    Returns:
        The global EnhancedPanelConfig instance
    """
    global _enhanced_panel_config
    if _enhanced_panel_config is None:
        _enhanced_panel_config = EnhancedPanelConfig()
    return _enhanced_panel_config


def update_enhanced_panel_config(**kwargs) -> EnhancedPanelConfig:
    """
    Update the global enhanced panel configuration with new values.
    
    Args:
        **kwargs: Configuration parameters to update
        
    Returns:
        The updated EnhancedPanelConfig instance
    """
    global _enhanced_panel_config
    current_config = get_enhanced_panel_config()
    
    # Create new config with updated values
    config_dict = current_config.model_dump()
    config_dict.update(kwargs)
    
    _enhanced_panel_config = EnhancedPanelConfig(**config_dict)
    return _enhanced_panel_config