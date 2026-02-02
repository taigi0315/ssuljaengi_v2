# Enhanced Panel Generation API Documentation

This document describes the new and updated API endpoints for the enhanced panel generation system that supports 20-50 panels with intelligent image generation strategies.

## Overview

The enhanced panel generation system introduces several new API endpoints and updates existing ones to support:

- Configurable panel count targets (20-50 panels)
- Genre-specific panel count ranges
- Enhanced multi-panel size limits (max 3 panels per image)
- Detailed error responses for validation failures
- Configuration management for panel generation settings

## New Configuration Endpoints

### GET /webtoon/config/panel-settings

Get current enhanced panel generation configuration.

**Response:**
```json
{
  "panel_count_settings": {
    "min": 20,
    "max": 50,
    "ideal_min": 25,
    "ideal_max": 40
  },
  "image_generation_settings": {
    "single_panel_ratio": 0.6,
    "max_multi_panel_size": 3
  },
  "scene_structure_settings": {
    "max_panels_per_scene": 8,
    "min_panels_per_scene": 1
  },
  "three_act_distribution": {
    "act1_ratio": 0.25,
    "act2_ratio": 0.50,
    "act3_ratio": 0.25
  },
  "genre_specific_targets": {
    "romance": [25, 35],
    "action": [35, 50],
    "fantasy": [35, 50]
  },
  "performance_settings": {
    "enable_caching": true,
    "enable_progress_tracking": true,
    "progress_threshold": 30
  }
}
```

### PUT /webtoon/config/panel-settings

Update enhanced panel generation configuration.

**Request Body:**
```json
{
  "panel_count_min": 22,
  "panel_count_max": 45,
  "single_panel_ratio": 0.65,
  "max_multi_panel_size": 3,
  "enable_caching": true
}
```

**Response:**
```json
{
  "message": "Panel configuration updated successfully",
  "updated_fields": ["panel_count_min", "single_panel_ratio"],
  "current_settings": {
    "panel_count_min": 22,
    "panel_count_max": 50,
    "panel_count_ideal_min": 25,
    "panel_count_ideal_max": 40,
    "single_panel_ratio": 0.65,
    "max_multi_panel_size": 3
  }
}
```

### GET /webtoon/config/panel-settings/genres

List all supported genres with their panel count targets.

**Response:**
```json
{
  "supported_genres": [
    {
      "key": "romance",
      "name": "Romance",
      "panel_range": {"min": 25, "max": 35},
      "recommended_panels": 30
    },
    {
      "key": "action",
      "name": "Action",
      "panel_range": {"min": 35, "max": 50},
      "recommended_panels": 42
    }
  ],
  "total_genres": 9
}
```

### GET /webtoon/config/panel-settings/genre/{genre}

Get panel count targets for a specific genre.

**Parameters:**
- `genre` (path): Genre name (e.g., "romance", "action", "fantasy")

**Response:**
```json
{
  "genre": "romance",
  "panel_count_range": {"min": 25, "max": 35},
  "ideal_range": {"min": 25, "max": 35},
  "recommended_panels": 30
}
```

### POST /webtoon/config/panel-settings/validate

Validate a panel count against current configuration.

**Query Parameters:**
- `panel_count` (required): Number of panels to validate
- `genre` (optional): Genre for genre-specific validation

**Response:**
```json
{
  "panel_count": 30,
  "context": "genre 'romance'",
  "is_valid": true,
  "validation_range": {"min": 25, "max": 35},
  "ideal_range": {"min": 25, "max": 35},
  "is_in_ideal_range": true,
  "recommendations": [
    "Panel count is in the ideal range for optimal storytelling"
  ]
}
```

## Updated Existing Endpoints

### POST /webtoon/generate

Enhanced with panel count validation and detailed error responses.

**Enhanced Error Responses:**

For insufficient panels:
```json
{
  "error_type": "insufficient_panels",
  "message": "Generated script has 15 panels, but romance genre requires at least 25 panels for quality storytelling",
  "current_panel_count": 15,
  "required_minimum": 25,
  "recommended_range": "25-35",
  "suggestions": [
    "Try providing a longer or more detailed story",
    "Consider adding more character interactions",
    "Include more scene descriptions for visual development"
  ],
  "retryable": true
}
```

For excessive panels:
```json
{
  "error_type": "excessive_panels",
  "message": "Generated script has 55 panels, which exceeds the 50 panel limit for romance genre",
  "current_panel_count": 55,
  "maximum_allowed": 50,
  "recommended_range": "25-35",
  "suggestions": [
    "Try providing a more concise story",
    "Focus on key story moments",
    "Reduce detailed scene descriptions"
  ],
  "retryable": true
}
```

### POST /webtoon/page/generate

Enhanced with multi-panel size validation.

**Enhanced Error Responses:**

For multi-panel size exceeded:
```json
{
  "error_type": "multi_panel_size_exceeded",
  "message": "Requested 5 panels exceeds the maximum of 3 panels per multi-panel image",
  "requested_panels": 5,
  "maximum_allowed": 3,
  "suggestions": [
    "Split into multiple requests with max 3 panels each",
    "Use single-panel generation for better image quality",
    "Consider using the automatic page grouping endpoint instead"
  ],
  "retryable": false
}
```

### POST /webtoon/{script_id}/page/{page_number}/image

Enhanced with validation and detailed error responses.

**Enhanced Error Responses:**

For page exceeding multi-panel limits:
```json
{
  "error_type": "page_exceeds_multi_panel_limit",
  "message": "Page 3 contains 4 panels, exceeding the maximum of 3 panels per multi-panel image",
  "page_number": 3,
  "panel_count": 4,
  "maximum_allowed": 3,
  "layout_type": "four_panel",
  "suggestions": [
    "Use single-panel generation for individual panels",
    "Adjust panel grouping configuration",
    "Generate panels individually and combine manually"
  ],
  "retryable": false
}
```

## New Analysis Endpoints

### GET /webtoon/{script_id}/enhanced-stats

Get comprehensive enhanced panel generation statistics and compliance analysis.

**Response:**
```json
{
  "script_id": "abc123",
  "generation_info": {
    "timestamp": 1703123456.789,
    "config_version": "enhanced_v1",
    "genre": "romance"
  },
  "panel_analysis": {
    "total_panels": 32,
    "is_valid_count": true,
    "is_ideal_count": true,
    "genre_range": {"min": 25, "max": 35},
    "ideal_range": {"min": 25, "max": 35},
    "three_act_distribution": {
      "act1_panels": 8,
      "act2_panels": 16,
      "act3_panels": 8
    }
  },
  "scene_analysis": {
    "total_scenes": 12,
    "panels_per_scene": [3, 2, 4, 2, 3, 3, 2, 4, 2, 3, 2, 2],
    "average_panels_per_scene": 2.7,
    "max_panels_per_scene": 4,
    "min_panels_per_scene": 2
  },
  "image_strategy_analysis": {
    "total_pages": 18,
    "single_panel_pages": 12,
    "multi_panel_pages": 6,
    "actual_single_ratio": 0.667,
    "target_single_ratio": 0.6,
    "meets_single_ratio_target": true,
    "oversized_multi_panel_pages": []
  },
  "compliance": {
    "status": "compliant",
    "issues": [],
    "recommendations": [
      "Ideal panel count for romance: 25-35",
      "Target single-panel ratio: 0.6",
      "Max panels per multi-panel image: 3"
    ]
  },
  "performance_metrics": {
    "api_calls_saved": 14,
    "estimated_generation_time": "16.0s"
  }
}
```

## Error Response Format

All enhanced endpoints use a consistent error response format:

```json
{
  "error_type": "validation_error_type",
  "message": "Human-readable error message",
  "retryable": true,
  "suggestions": [
    "Actionable suggestion 1",
    "Actionable suggestion 2"
  ],
  "additional_context": {
    "field": "value"
  }
}
```

## Error Types

- `insufficient_panels`: Panel count below minimum threshold
- `excessive_panels`: Panel count above maximum threshold
- `multi_panel_size_exceeded`: Multi-panel request exceeds size limits
- `page_exceeds_multi_panel_limit`: Page contains too many panels for multi-panel generation
- `invalid_panel_indices`: Invalid panel indices in request
- `no_valid_panels`: No valid panels found for generation
- `page_not_found`: Requested page number not found
- `no_panels_found`: Script has no panels
- `generation_failure`: General generation failure
- `page_generation_failure`: Page-specific generation failure
- `page_image_generation_failure`: Page image generation failure

## Configuration Persistence

All configuration changes made through the API endpoints persist across system restarts. The configuration is stored in memory and can be updated dynamically without requiring server restart.

## Backward Compatibility

All existing API endpoints continue to work as before. The enhanced features are additive and do not break existing functionality. Legacy multi-panel generation (2-5 panels) is still supported alongside the new enhanced limits.

## Testing

Use the provided test script to verify all endpoints:

```bash
python test_enhanced_api_endpoints.py
```

This script tests all new configuration endpoints and validates the enhanced error responses.