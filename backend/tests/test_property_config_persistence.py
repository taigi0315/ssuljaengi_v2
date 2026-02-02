"""
Property-based test for Enhanced Panel Generation - Property 9: Configuration Persistence and Flexibility

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

Property 9: Configuration Persistence and Flexibility
For any configuration change to panel count targets, single-panel ratios, or genre-specific settings, 
the changes should persist across system restarts and be applied to subsequent generations.
"""

import pytest
import tempfile
import os
import json
from hypothesis import given, strategies as st, assume
from app.config.enhanced_panel_config import (
    EnhancedPanelConfig, 
    get_enhanced_panel_config, 
    update_enhanced_panel_config,
    GenreType
)
from app.utils.persistence import JsonStore
from typing import Dict, Tuple


class TestProperty9ConfigurationPersistenceAndFlexibility:
    """
    Property 9: Configuration Persistence and Flexibility
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
    
    For any configuration change to panel count targets, single-panel ratios, or 
    genre-specific settings, the changes should persist and be applied correctly.
    """
    
    def test_default_configuration_values(self):
        """
        Test that default configuration values are correctly set.
        **Validates: Requirements 7.1, 7.2**
        """
        config = EnhancedPanelConfig()
        
        # Test core panel count settings (Requirement 7.1)
        assert config.panel_count_min == 20
        assert config.panel_count_max == 50
        assert config.panel_count_ideal_min == 25
        assert config.panel_count_ideal_max == 40
        
        # Test image generation strategy settings (Requirement 7.2)
        assert config.single_panel_ratio == 0.6
        assert config.max_multi_panel_size == 3
        
        # Test genre-specific targets exist (Requirement 7.2)
        assert GenreType.ROMANCE in config.genre_specific_targets
        assert GenreType.ACTION in config.genre_specific_targets
        assert GenreType.DEFAULT in config.genre_specific_targets
    
    @given(
        panel_min=st.integers(min_value=10, max_value=25),
        panel_max=st.integers(min_value=40, max_value=80),
        ideal_min=st.integers(min_value=15, max_value=35),
        ideal_max=st.integers(min_value=30, max_value=60)
    )
    def test_panel_count_configuration_flexibility(self, panel_min, panel_max, ideal_min, ideal_max):
        """
        Property: For any valid panel count configuration, the system should accept and apply the settings.
        **Validates: Requirements 7.1, 7.3**
        """
        # Ensure valid relationships between values
        assume(panel_min < panel_max)
        assume(ideal_min >= panel_min)
        assume(ideal_max <= panel_max)
        assume(ideal_min < ideal_max)
        
        # Create configuration with custom values
        config = EnhancedPanelConfig(
            panel_count_min=panel_min,
            panel_count_max=panel_max,
            panel_count_ideal_min=ideal_min,
            panel_count_ideal_max=ideal_max
        )
        
        # Verify values are correctly set
        assert config.panel_count_min == panel_min
        assert config.panel_count_max == panel_max
        assert config.panel_count_ideal_min == ideal_min
        assert config.panel_count_ideal_max == ideal_max
        
        # Test validation works with new values
        assert config.validate_panel_count(ideal_min) == True
        assert config.validate_panel_count(ideal_max) == True
        assert config.validate_panel_count(panel_min - 1) == False
        assert config.validate_panel_count(panel_max + 1) == False
    
    @given(
        single_panel_ratio=st.floats(min_value=0.1, max_value=0.9),
        max_multi_panel_size=st.integers(min_value=2, max_value=5)
    )
    def test_image_strategy_configuration_flexibility(self, single_panel_ratio, max_multi_panel_size):
        """
        Property: For any valid image strategy configuration, the system should accept and apply the settings.
        **Validates: Requirements 7.3, 7.4**
        """
        config = EnhancedPanelConfig(
            single_panel_ratio=single_panel_ratio,
            max_multi_panel_size=max_multi_panel_size
        )
        
        # Verify values are correctly set
        assert config.single_panel_ratio == single_panel_ratio
        assert config.max_multi_panel_size == max_multi_panel_size
        
        # Test functionality with new values
        assert config.should_use_single_panel(single_panel_ratio - 0.1) == True
        assert config.should_use_single_panel(single_panel_ratio + 0.1) == False
    
    @given(
        genre_min=st.integers(min_value=15, max_value=30),
        genre_max=st.integers(min_value=35, max_value=60)
    )
    def test_genre_specific_configuration_flexibility(self, genre_min, genre_max):
        """
        Property: For any valid genre-specific configuration, the system should accept and apply the settings.
        **Validates: Requirements 7.2, 7.3**
        """
        assume(genre_min < genre_max)
        
        # Create custom genre-specific targets
        custom_targets = {
            GenreType.ROMANCE: (genre_min, genre_max),
            GenreType.ACTION: (genre_min + 5, genre_max + 5),
            GenreType.DEFAULT: (25, 40)
        }
        
        config = EnhancedPanelConfig(genre_specific_targets=custom_targets)
        
        # Verify genre-specific targets are correctly set
        romance_range = config.get_panel_range_for_genre("romance")
        assert romance_range == (genre_min, genre_max)
        
        action_range = config.get_panel_range_for_genre("action")
        assert action_range == (genre_min + 5, genre_max + 5)
        
        # Test validation with genre-specific targets
        assert config.validate_panel_count(genre_min, "romance") == True
        assert config.validate_panel_count(genre_max, "romance") == True
        assert config.validate_panel_count(genre_min - 1, "romance") == False
        assert config.validate_panel_count(genre_max + 1, "romance") == False
    
    @given(
        act1_ratio=st.floats(min_value=0.20, max_value=0.30),
        act2_ratio=st.floats(min_value=0.45, max_value=0.55),
        act3_ratio=st.floats(min_value=0.20, max_value=0.30)
    )
    def test_act_distribution_configuration_flexibility(self, act1_ratio, act2_ratio, act3_ratio):
        """
        Property: For any valid act distribution configuration, the system should accept and apply the settings.
        **Validates: Requirements 7.3, 7.5**
        """
        # Ensure ratios are within valid bounds and sum to approximately 1.0
        total_ratio = act1_ratio + act2_ratio + act3_ratio
        
        # Normalize while keeping within bounds
        act1_ratio = min(0.35, max(0.15, act1_ratio / total_ratio))
        act2_ratio = min(0.60, max(0.40, act2_ratio / total_ratio))
        act3_ratio = min(0.35, max(0.15, act3_ratio / total_ratio))
        
        # Adjust to ensure they sum to 1.0
        current_total = act1_ratio + act2_ratio + act3_ratio
        if abs(current_total - 1.0) > 0.05:
            # Skip this test case if we can't get valid ratios
            assume(False)
        
        config = EnhancedPanelConfig(
            act1_panel_ratio=act1_ratio,
            act2_panel_ratio=act2_ratio,
            act3_panel_ratio=act3_ratio
        )
        
        # Verify ratios are correctly set
        assert abs(config.act1_panel_ratio - act1_ratio) < 0.01
        assert abs(config.act2_panel_ratio - act2_ratio) < 0.01
        assert abs(config.act3_panel_ratio - act3_ratio) < 0.01
        
        # Test act distribution calculation
        distribution = config.calculate_act_distribution(30)
        total_panels = distribution["act1_panels"] + distribution["act2_panels"] + distribution["act3_panels"]
        assert total_panels == 30
        
        # Verify approximate ratios
        actual_act1_ratio = distribution["act1_panels"] / 30
        actual_act2_ratio = distribution["act2_panels"] / 30
        actual_act3_ratio = distribution["act3_panels"] / 30
        
        # Allow for rounding differences
        assert abs(actual_act1_ratio - act1_ratio) < 0.15
        assert abs(actual_act2_ratio - act2_ratio) < 0.15
        assert abs(actual_act3_ratio - act3_ratio) < 0.15
    
    def test_global_configuration_persistence(self):
        """
        Test that global configuration instance persists across calls.
        **Validates: Requirements 7.5**
        """
        # Get initial configuration
        config1 = get_enhanced_panel_config()
        initial_min = config1.panel_count_min
        
        # Get configuration again - should be same instance
        config2 = get_enhanced_panel_config()
        assert config1 is config2, "Global configuration should return same instance"
        assert config2.panel_count_min == initial_min
        
        # Update configuration
        updated_config = update_enhanced_panel_config(panel_count_min=25)
        assert updated_config.panel_count_min == 25
        
        # Get configuration again - should have updated value
        config3 = get_enhanced_panel_config()
        assert config3.panel_count_min == 25
    
    @given(
        total_panels=st.integers(min_value=20, max_value=50),
        seed=st.integers(min_value=1, max_value=1000)
    )
    def test_configuration_consistency_across_operations(self, total_panels, seed):
        """
        Property: Configuration should remain consistent across different operations.
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
        """
        config = EnhancedPanelConfig()
        
        # Test panel validation consistency
        is_valid = config.validate_panel_count(total_panels)
        expected_valid = config.panel_count_min <= total_panels <= config.panel_count_max
        assert is_valid == expected_valid
        
        # Test ideal range consistency
        ideal_min, ideal_max = config.get_ideal_panel_range()
        assert ideal_min == config.panel_count_ideal_min
        assert ideal_max == config.panel_count_ideal_max
        
        # Test act distribution consistency
        distribution = config.calculate_act_distribution(total_panels)
        calculated_total = sum(distribution.values())
        assert calculated_total == total_panels
        
        # Test single panel ratio consistency
        current_ratio = 0.5  # Example current ratio
        should_use_single = config.should_use_single_panel(current_ratio)
        expected_should_use = current_ratio < config.single_panel_ratio
        assert should_use_single == expected_should_use
    
    def test_configuration_validation_edge_cases(self):
        """
        Test configuration validation handles edge cases correctly.
        **Validates: Requirements 7.1, 7.3**
        """
        # Test invalid configurations are rejected
        with pytest.raises(ValueError):
            # ideal_min >= ideal_max
            EnhancedPanelConfig(panel_count_ideal_min=40, panel_count_ideal_max=25)
        
        with pytest.raises(ValueError):
            # ideal_min < panel_min
            EnhancedPanelConfig(panel_count_min=30, panel_count_ideal_min=25)
        
        with pytest.raises(ValueError):
            # ideal_max > panel_max
            EnhancedPanelConfig(panel_count_max=40, panel_count_ideal_max=45)
        
        with pytest.raises(ValueError):
            # Act ratios don't sum to ~1.0
            EnhancedPanelConfig(
                act1_panel_ratio=0.5,
                act2_panel_ratio=0.5,
                act3_panel_ratio=0.5  # Total = 1.5, should fail
            )
    
    @given(
        genre_name=st.sampled_from(["romance", "action", "fantasy", "comedy", "unknown_genre"]),
        panel_count=st.integers(min_value=10, max_value=60)
    )
    def test_genre_specific_validation_consistency(self, genre_name, panel_count):
        """
        Property: Genre-specific validation should be consistent with genre targets.
        **Validates: Requirements 7.2, 7.3**
        """
        config = EnhancedPanelConfig()
        
        # Get genre range
        genre_min, genre_max = config.get_panel_range_for_genre(genre_name)
        
        # Test validation consistency
        is_valid_for_genre = config.validate_panel_count(panel_count, genre_name)
        expected_valid = genre_min <= panel_count <= genre_max
        
        assert is_valid_for_genre == expected_valid, \
            f"Genre {genre_name} validation inconsistent for {panel_count} panels"
    
    def test_configuration_immutability_after_creation(self):
        """
        Test that configuration values remain stable after creation.
        **Validates: Requirements 7.5**
        """
        config = EnhancedPanelConfig(
            panel_count_min=22,
            panel_count_max=48,
            single_panel_ratio=0.7
        )
        
        # Store initial values
        initial_min = config.panel_count_min
        initial_max = config.panel_count_max
        initial_ratio = config.single_panel_ratio
        
        # Perform various operations
        config.validate_panel_count(30)
        config.get_panel_range_for_genre("romance")
        config.calculate_act_distribution(35)
        config.should_use_single_panel(0.5)
        
        # Verify values haven't changed
        assert config.panel_count_min == initial_min
        assert config.panel_count_max == initial_max
        assert config.single_panel_ratio == initial_ratio
    
    @given(
        panel_min=st.integers(min_value=15, max_value=25),
        panel_max=st.integers(min_value=45, max_value=60),
        single_ratio=st.floats(min_value=0.4, max_value=0.8)
    )
    def test_configuration_file_persistence_across_restarts(self, panel_min, panel_max, single_ratio):
        """
        Property: Configuration changes should persist across system restarts via file storage.
        **Validates: Requirements 7.5**
        """
        assume(panel_min < panel_max)
        
        # Create temporary file for testing persistence
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create configuration data
            config_data = {
                "panel_count_min": panel_min,
                "panel_count_max": panel_max,
                "panel_count_ideal_min": max(panel_min, 20),
                "panel_count_ideal_max": min(panel_max, 45),
                "single_panel_ratio": single_ratio,
                "max_multi_panel_size": 3
            }
            
            # Simulate first system instance - save configuration
            config_store = JsonStore(temp_path)
            config_store["enhanced_panel_config"] = config_data
            config_store._save_sync()  # Force immediate save
            
            # Verify file was created and contains data
            assert os.path.exists(temp_path), "Configuration file should be created"
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert "enhanced_panel_config" in saved_data
            assert saved_data["enhanced_panel_config"]["panel_count_min"] == panel_min
            assert saved_data["enhanced_panel_config"]["panel_count_max"] == panel_max
            assert abs(saved_data["enhanced_panel_config"]["single_panel_ratio"] - single_ratio) < 0.001
            
            # Simulate system restart - create new store instance
            new_config_store = JsonStore(temp_path)
            
            # Verify configuration persisted across "restart"
            restored_config = new_config_store["enhanced_panel_config"]
            assert restored_config["panel_count_min"] == panel_min
            assert restored_config["panel_count_max"] == panel_max
            assert abs(restored_config["single_panel_ratio"] - single_ratio) < 0.001
            
            # Create EnhancedPanelConfig from persisted data
            restored_panel_config = EnhancedPanelConfig(**restored_config)
            
            # Verify functionality works with restored configuration
            assert restored_panel_config.panel_count_min == panel_min
            assert restored_panel_config.panel_count_max == panel_max
            assert abs(restored_panel_config.single_panel_ratio - single_ratio) < 0.001
            
            # Test that restored config functions correctly
            test_panel_count = (panel_min + panel_max) // 2
            assert restored_panel_config.validate_panel_count(test_panel_count) == True
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_configuration_persistence_with_genre_specific_settings(self):
        """
        Test that genre-specific configuration changes persist across system restarts.
        **Validates: Requirements 7.2, 7.5**
        """
        # Create temporary file for testing persistence
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Create custom genre-specific targets
            custom_genre_targets = {
                GenreType.ROMANCE: (22, 32),
                GenreType.ACTION: (35, 48),
                GenreType.FANTASY: (30, 45),
                GenreType.DEFAULT: (25, 40)
            }
            
            config_data = {
                "panel_count_min": 20,
                "panel_count_max": 50,
                "panel_count_ideal_min": 25,
                "panel_count_ideal_max": 40,
                "single_panel_ratio": 0.65,
                "max_multi_panel_size": 3,
                "genre_specific_targets": custom_genre_targets
            }
            
            # Save configuration to file
            config_store = JsonStore(temp_path)
            config_store["enhanced_panel_config"] = config_data
            config_store._save_sync()
            
            # Simulate system restart
            new_config_store = JsonStore(temp_path)
            restored_config_data = new_config_store["enhanced_panel_config"]
            
            # Create configuration from persisted data
            restored_config = EnhancedPanelConfig(**restored_config_data)
            
            # Verify genre-specific targets persisted correctly
            assert restored_config.get_panel_range_for_genre("romance") == (22, 32)
            assert restored_config.get_panel_range_for_genre("action") == (35, 48)
            assert restored_config.get_panel_range_for_genre("fantasy") == (30, 45)
            
            # Test validation with persisted genre targets
            assert restored_config.validate_panel_count(25, "romance") == True
            assert restored_config.validate_panel_count(40, "action") == True
            assert restored_config.validate_panel_count(35, "fantasy") == True
            
            # Test that invalid counts are still rejected
            assert restored_config.validate_panel_count(15, "romance") == False
            assert restored_config.validate_panel_count(60, "action") == False
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @given(
        act1_ratio=st.floats(min_value=0.20, max_value=0.30),
        act2_ratio=st.floats(min_value=0.45, max_value=0.55),
        progress_threshold=st.integers(min_value=25, max_value=40)
    )
    def test_configuration_persistence_with_performance_settings(self, act1_ratio, act2_ratio, progress_threshold):
        """
        Property: Performance and act distribution settings should persist across system restarts.
        **Validates: Requirements 7.3, 7.4, 7.5**
        """
        # Calculate act3_ratio to ensure total ≈ 1.0
        act3_ratio = 1.0 - act1_ratio - act2_ratio
        
        # Ensure act3_ratio is within valid bounds
        assume(0.15 <= act3_ratio <= 0.35)
        
        # Create temporary file for testing persistence
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            config_data = {
                "panel_count_min": 20,
                "panel_count_max": 50,
                "panel_count_ideal_min": 25,
                "panel_count_ideal_max": 40,
                "single_panel_ratio": 0.6,
                "max_multi_panel_size": 3,
                "act1_panel_ratio": act1_ratio,
                "act2_panel_ratio": act2_ratio,
                "act3_panel_ratio": act3_ratio,
                "enable_progress_tracking": True,
                "progress_threshold": progress_threshold,
                "enable_caching": True
            }
            
            # Save configuration
            config_store = JsonStore(temp_path)
            config_store["enhanced_panel_config"] = config_data
            config_store._save_sync()
            
            # Simulate system restart
            new_config_store = JsonStore(temp_path)
            restored_config_data = new_config_store["enhanced_panel_config"]
            
            # Create configuration from persisted data
            restored_config = EnhancedPanelConfig(**restored_config_data)
            
            # Verify act distribution settings persisted
            assert abs(restored_config.act1_panel_ratio - act1_ratio) < 0.01
            assert abs(restored_config.act2_panel_ratio - act2_ratio) < 0.01
            assert abs(restored_config.act3_panel_ratio - act3_ratio) < 0.01
            
            # Verify performance settings persisted
            assert restored_config.enable_progress_tracking == True
            assert restored_config.progress_threshold == progress_threshold
            assert restored_config.enable_caching == True
            
            # Test functionality with persisted settings
            distribution = restored_config.calculate_act_distribution(30)
            total_panels = sum(distribution.values())
            assert total_panels == 30
            
            # Verify approximate ratios match persisted values
            actual_act1_ratio = distribution["act1_panels"] / 30
            actual_act2_ratio = distribution["act2_panels"] / 30
            
            assert abs(actual_act1_ratio - act1_ratio) < 0.15  # Allow for rounding
            assert abs(actual_act2_ratio - act2_ratio) < 0.15
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_configuration_persistence_handles_file_corruption(self):
        """
        Test that configuration persistence gracefully handles corrupted files.
        **Validates: Requirements 7.5**
        """
        # Create temporary file for testing persistence
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Write corrupted JSON to file
            with open(temp_path, 'w') as f:
                f.write('{"invalid": json content}')  # Invalid JSON
            
            # JsonStore should handle corruption gracefully
            config_store = JsonStore(temp_path, default_data={})
            
            # Should initialize with empty data due to corruption
            assert len(config_store) == 0
            
            # Should be able to save valid configuration after corruption
            valid_config = {
                "panel_count_min": 20,
                "panel_count_max": 50,
                "single_panel_ratio": 0.6
            }
            
            config_store["enhanced_panel_config"] = valid_config
            config_store._save_sync()
            
            # Verify recovery by creating new store instance
            recovered_store = JsonStore(temp_path)
            assert "enhanced_panel_config" in recovered_store
            assert recovered_store["enhanced_panel_config"]["panel_count_min"] == 20
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_configuration_applied_to_subsequent_generations(self):
        """
        Test that persisted configuration changes are applied to subsequent generations.
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
        """
        # Create temporary file for testing persistence
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Define custom configuration for testing
            custom_config_data = {
                "panel_count_min": 22,
                "panel_count_max": 48,
                "panel_count_ideal_min": 28,
                "panel_count_ideal_max": 42,
                "single_panel_ratio": 0.75,
                "max_multi_panel_size": 2,
                "genre_specific_targets": {
                    GenreType.ROMANCE: (25, 35),
                    GenreType.ACTION: (30, 45),
                    GenreType.DEFAULT: (28, 42)
                }
            }
            
            # Save custom configuration
            config_store = JsonStore(temp_path)
            config_store["enhanced_panel_config"] = custom_config_data
            config_store._save_sync()
            
            # Simulate multiple "generations" using the persisted configuration
            for generation in range(3):
                # Each generation creates a new config instance from persisted data
                generation_store = JsonStore(temp_path)
                config_data = generation_store["enhanced_panel_config"]
                generation_config = EnhancedPanelConfig(**config_data)
                
                # Verify custom settings are applied consistently
                assert generation_config.panel_count_min == 22
                assert generation_config.panel_count_max == 48
                assert generation_config.max_multi_panel_size == 2
                
                # Test that validation uses custom settings
                assert generation_config.validate_panel_count(25) == True  # Within custom range
                assert generation_config.validate_panel_count(20) == False  # Below custom min
                assert generation_config.validate_panel_count(50) == False  # Above custom max
                
                # Test genre-specific settings are applied
                romance_range = generation_config.get_panel_range_for_genre("romance")
                assert romance_range == (25, 35)
                
                # Check single_panel_ratio based on generation
                if generation == 0:
                    # First generation should have original value
                    assert generation_config.single_panel_ratio == 0.75
                    assert generation_config.should_use_single_panel(0.7) == True  # Below 0.75
                    assert generation_config.should_use_single_panel(0.8) == False  # Above 0.75
                elif generation >= 1:
                    # After update, should have new value
                    assert generation_config.single_panel_ratio == 0.8
                    assert generation_config.should_use_single_panel(0.75) == True  # Below 0.8
                    assert generation_config.should_use_single_panel(0.85) == False  # Above 0.8
                
                # Simulate configuration update during first generation
                if generation == 0:  # Update after first generation
                    updated_data = config_data.copy()
                    updated_data["single_panel_ratio"] = 0.8
                    generation_store["enhanced_panel_config"] = updated_data
                    generation_store._save_sync()
            
            # Verify final state has the updated configuration
            final_store = JsonStore(temp_path)
            final_config_data = final_store["enhanced_panel_config"]
            final_config = EnhancedPanelConfig(**final_config_data)
            
            # Should have the updated single_panel_ratio
            assert final_config.single_panel_ratio == 0.8
            assert final_config.should_use_single_panel(0.75) == True  # Below 0.8
            assert final_config.should_use_single_panel(0.85) == False  # Above 0.8
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    # Run the property tests
    pytest.main([__file__, "-v"])