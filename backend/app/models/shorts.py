from pydantic import BaseModel, Field
from typing import List

class ShortsScene(BaseModel):
    scene_id: int = Field(description="Sequence number of the scene")
    action: str = Field(description="Description of the act")
    image_prompt: str = Field(description="Style + Setting + Character Action (No physical descriptions)")
    video_prompt: str = Field(description="Motion instructions for video generation (micro-movements)")

class ShortsScriptMetadata(BaseModel):
    topic: str = Field(description="The topic of the shorts script")
    style: str = Field(description="The visual style, e.g., 'Reference-Based Manhwa'")

class ShortsScript(BaseModel):
    metadata: ShortsScriptMetadata
    scenes: List[ShortsScene]
