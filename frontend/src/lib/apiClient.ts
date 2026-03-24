/**
 * API client for the Gossiptoon backend.
 * Uses NEXT_PUBLIC_API_URL for the base URL, falling back to localhost:8000.
 */

import type {
  CharacterImage,
  Character,
  SearchResponse,
  WorkflowStatus,
  WebtoonScript,
  SceneImage,
  PageImage,
  StoryResponse,
  ShortsScript,
  GenerateSceneImageRequest,
} from '@/types';

export type { GenerateSceneImageRequest };

function getBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Search ────────────────────────────────────────────────────────────────────

export interface SearchPostsRequest {
  timeRange: string;
  subreddits: string[];
  postCount: number;
}

export function searchPosts(request: SearchPostsRequest): Promise<SearchResponse> {
  return apiFetch<SearchResponse>('/search', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ── Story ─────────────────────────────────────────────────────────────────────

export interface GenerateStoryRequest {
  postId: string;
  postTitle: string;
  postContent: string;
  genre: string;
  options?: Record<string, unknown>;
}

export function generateStory(
  request: GenerateStoryRequest,
): Promise<{ workflowId: string }> {
  return apiFetch<{ workflowId: string }>('/story/generate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export function getStoryStatus(workflowId: string): Promise<WorkflowStatus> {
  return apiFetch<WorkflowStatus>(`/story/status/${workflowId}`);
}

export function getStory(storyId: string): Promise<StoryResponse> {
  return apiFetch<StoryResponse>(`/story/${storyId}`);
}

// ── Webtoon Script ────────────────────────────────────────────────────────────

export function generateWebtoonScript(
  storyId: string,
  storyContent?: string,
  imageStyle?: string,
  genre?: string,
): Promise<WebtoonScript> {
  return apiFetch<WebtoonScript>('/webtoon/generate', {
    method: 'POST',
    body: JSON.stringify({
      story_id: storyId,
      story_content: storyContent,
      image_style: imageStyle,
      genre,
    }),
  });
}

export function getGenres(): Promise<{ id: string; name: string; description: string; preview_image?: string }[]> {
  return apiFetch('/webtoon/genres');
}

export function getImageStyles(): Promise<unknown> {
  return apiFetch('/webtoon/image-styles');
}

interface PageLayout {
  page_number: number;
  panel_indices: number[];
  layout_type: string;
  is_single_panel: boolean;
  reasoning?: string;
}

export function getScriptLayout(scriptId: string): Promise<PageLayout[]> {
  return apiFetch<PageLayout[]>(`/webtoon/${scriptId}/layout`);
}

// ── Character Images ──────────────────────────────────────────────────────────

export interface GenerateCharacterImageRequestApi {
  script_id: string;
  character_name: string;
  description: string;
  gender: string;
  image_style: string;
  reference_image_url?: string;
}

export function generateCharacterImage(
  request: GenerateCharacterImageRequestApi,
): Promise<CharacterImage> {
  return apiFetch<CharacterImage>('/webtoon/character/image', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export function selectCharacterImage(scriptId: string, imageId: string): Promise<unknown> {
  return apiFetch(
    `/webtoon/character/image/select?script_id=${encodeURIComponent(scriptId)}&image_id=${encodeURIComponent(imageId)}`,
    { method: 'POST' },
  );
}

export function importCharacterImage(
  scriptId: string,
  characterName: string,
  imageUrl: string,
  description: string,
): Promise<CharacterImage> {
  return apiFetch<CharacterImage>('/webtoon/character/image/import', {
    method: 'POST',
    body: JSON.stringify({
      script_id: scriptId,
      character_name: characterName,
      image_url: imageUrl,
      description,
    }),
  });
}

// ── Character Library ─────────────────────────────────────────────────────────

export interface SavedCharacter {
  id: string;
  character: Character;
  image_url?: string;
  created_at: string;
  tags: string[];
}

export function getLibraryCharacters(): Promise<SavedCharacter[]> {
  return apiFetch<SavedCharacter[]>('/library/characters');
}

export function deleteCharacter(charId: string): Promise<unknown> {
  return apiFetch(`/library/character/${encodeURIComponent(charId)}`, { method: 'DELETE' });
}

export function saveCharacterToLibrary(
  character: Character,
  imageUrl?: string,
  tags: string[] = [],
): Promise<SavedCharacter> {
  return apiFetch<SavedCharacter>('/library/character', {
    method: 'POST',
    body: JSON.stringify({ character, image_url: imageUrl, tags }),
  });
}

// ── Scene Images ──────────────────────────────────────────────────────────────

export function generateSceneImage(request: GenerateSceneImageRequest): Promise<SceneImage> {
  return apiFetch<SceneImage>('/webtoon/scene/image', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export function selectSceneImage(
  scriptId: string,
  panelNumber: number,
  imageId: string,
): Promise<unknown> {
  return apiFetch(
    `/webtoon/scene/image/select?script_id=${encodeURIComponent(scriptId)}&panel_number=${panelNumber}&image_id=${encodeURIComponent(imageId)}`,
    { method: 'POST' },
  );
}

// ── Page Images ───────────────────────────────────────────────────────────────

export function generatePageImage(
  scriptId: string,
  pageNumber: number,
  panelIndices: number[],
  styleModifiers?: string[],
): Promise<PageImage> {
  return apiFetch<PageImage>('/webtoon/page/generate', {
    method: 'POST',
    body: JSON.stringify({
      script_id: scriptId,
      page_number: pageNumber,
      panel_indices: panelIndices,
      style_modifiers: styleModifiers,
    }),
  });
}

export function selectPageImage(scriptId: string, imageId: string): Promise<unknown> {
  return apiFetch(
    `/webtoon/page/image/select?script_id=${encodeURIComponent(scriptId)}&image_id=${encodeURIComponent(imageId)}`,
    { method: 'POST' },
  );
}

// ── Shorts ────────────────────────────────────────────────────────────────────

export function generateShortsScript(topic?: string): Promise<ShortsScript> {
  return apiFetch<ShortsScript>('/webtoon/shorts/generate', {
    method: 'POST',
    body: JSON.stringify({ topic: topic ?? null }),
  });
}
