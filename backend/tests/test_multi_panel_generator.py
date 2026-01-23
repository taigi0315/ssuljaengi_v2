
import pytest
from unittest.mock import MagicMock, patch
from app.services.multi_panel_generator import MultiPanelGenerator
from app.models.story import WebtoonPanel

@pytest.fixture
def mock_image_generator():
    with patch("app.services.multi_panel_generator.image_generator") as mock_gen:
        # Mock client and config
        mock_gen.client = MagicMock()
        mock_gen._save_image_to_cache = MagicMock(return_value="/tmp/fake_image.png")
        # Mock settings used inside the method
        with patch("app.services.multi_panel_generator.get_settings") as mock_settings:
            mock_settings.return_value.model_image_gen = "gemini-2.0-flash-exp"
            yield mock_gen

@pytest.fixture
def panels():
    return [
        WebtoonPanel(
            panel_number=1,
            shot_type="Wide Shot",
            active_character_names=["Hero"],
            character_placement_and_action="Running fast towards the sunset",
            environment_details="City street with neon signs",
            atmospheric_conditions="Rainy night",
            visual_prompt="A wide shot of Hero running...",
            dialogue=[{"character": "Hero", "text": "I must hurry!"}]
        ),
        WebtoonPanel(
            panel_number=2,
            shot_type="Close Up",
            active_character_names=["Hero"],
            character_placement_and_action="Looking scared and out of breath",
            environment_details="City street background blurred",
            atmospheric_conditions="Rainy",
            visual_prompt="Close up of Hero's face...",
             dialogue=[{"character": "Hero", "text": "Can't stop now."}]
        )
    ]

@pytest.mark.asyncio
async def test_generate_multi_panel_page_success(mock_image_generator, panels):
    """Test successful generation of multi-panel page."""
    service = MultiPanelGenerator()
    
    # Mock API response
    mock_response = MagicMock()
    mock_part = MagicMock()
    # Mock bytes data for the image
    mock_part.inline_data.data = b"fake_image_bytes"
    mock_part.inline_data.mime_type = "image/png"
    mock_response.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]
    
    # Configure generate_content to return the mock response
    mock_image_generator.client.models.generate_content.return_value = mock_response

    result = await service.generate_multi_panel_page(panels, "Anime Style", ["High Contrast"])
    
    # Verifications
    assert result.startswith("data:image/png;base64,")
    mock_image_generator.client.models.generate_content.assert_called_once()
    
    # Check that prompt was built nicely
    call_args = mock_image_generator.client.models.generate_content.call_args
    call_kwargs = call_args.kwargs
    prompt = call_kwargs['contents'][0]
    
    assert "Panel 1: Wide Shot of Hero" in prompt
    assert "Running fast towards the sunset" in prompt
    assert "City street with neon signs" in prompt
    assert "Rainy night" in prompt
    assert "Style modifiers: High Contrast" in prompt
    assert "9:16" == call_kwargs['config'].image_config.aspect_ratio

@pytest.mark.asyncio
async def test_generate_multi_panel_page_no_image(mock_image_generator, panels):
    """Test handling of response with no image data."""
    service = MultiPanelGenerator()
    
    # Mock empty response
    mock_response = MagicMock()
    mock_response.candidates = [MagicMock(content=MagicMock(parts=[]))]
    mock_image_generator.client.models.generate_content.return_value = mock_response

    with pytest.raises(Exception, match="No image data returned"):
        await service.generate_multi_panel_page(panels, "Style")

@pytest.mark.asyncio
async def test_generate_multi_panel_page_no_client(mock_image_generator, panels):
    """Test fails gracefully when client is not initialized."""
    mock_image_generator.client = None
    service = MultiPanelGenerator()
    
    with pytest.raises(Exception, match="Gemini API client not initialized"):
        await service.generate_multi_panel_page(panels, "Style")
