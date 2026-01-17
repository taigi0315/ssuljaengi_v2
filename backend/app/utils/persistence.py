"""
Persistence utility for storing application data to JSON files.

This module provides a simple file-based storage mechanism to preserve
application state across server restarts.
"""
import json
import logging
import os
import asyncio
from typing import Dict, Any, Optional, TypeVar, Generic

logger = logging.getLogger(__name__)

T = TypeVar("T")

class JsonStore(Generic[T]):
    """
    A persistent dictionary-like store backed by a JSON file.
    
    Data is loaded from the file on initialization and saved to the file
    whenever the save method is called.
    """
    
    def __init__(self, file_path: str, default_data: Optional[Dict[str, T]] = None):
        """
        Initialize the JSON store.
        
        Args:
            file_path: Absolute path to the JSON file
            default_data: Default data to use if file doesn't exist
        """
        self.file_path = file_path
        self._data: Dict[str, T] = {}
        self._lock = asyncio.Lock()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Load existing data or initialize with default
        self._load(default_data)
        
    def _load(self, default_data: Optional[Dict[str, T]] = None) -> None:
        """Load data from JSON file."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                logger.info(f"Loaded {len(self._data)} items from {self.file_path}")
            else:
                self._data = default_data or {}
                self._save_sync()
                logger.info(f"Initialized new store at {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to load store {self.file_path}: {e}")
            self._data = default_data or {}
            
    def _save_sync(self) -> None:
        """Synchronous save to file (internal use)."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save store {self.file_path}: {e}")

    async def save(self) -> None:
        """Save current state to the JSON file."""
        async with self._lock:
            # We run the synchronous file I/O in a separate thread to avoid blocking the event loop
            await asyncio.to_thread(self._save_sync)
            
    # Dictionary-like methods
    
    def __getitem__(self, key: str) -> T:
        return self._data[key]
        
    def __setitem__(self, key: str, value: T) -> None:
        self._data[key] = value
        # Note: We don't auto-save on setitem to allow batch updates.
        # Callers should call save() explicitly when needed.
        
    def __delitem__(self, key: str) -> None:
        del self._data[key]
        
    def __contains__(self, key: str) -> bool:
        return key in self._data
        
    def __len__(self) -> int:
        return len(self._data)
        
    def __iter__(self):
        return iter(self._data)
        
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
        
    def items(self):
        return self._data.items()
        
    def keys(self):
        return self._data.keys()
        
    def values(self):
        return self._data.values()
        
    def clear(self) -> None:
        self._data.clear()
        
    def update(self, other: Dict[str, T]) -> None:
        self._data.update(other)
