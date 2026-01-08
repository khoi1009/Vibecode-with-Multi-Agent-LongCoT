"""
Caching Module for VibeCode

Provides caching utilities for prompts, results, and file hashes.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Entry for TTL-based caches."""
    value: Any
    timestamp: float
    ttl: float

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class PromptCache:
    """Cache for static prompt components with LRU eviction."""

    def __init__(self, max_size: int = 50):
        self._cache: Dict[str, str] = {}
        self._hits = 0
        self._misses = 0
        self.max_size = max_size

    def get_key(self, agent_id: str, skill_ids: tuple) -> str:
        """Generate cache key from agent + skills."""
        return f"{agent_id}:{':'.join(sorted(skill_ids))}"

    def get(self, key: str) -> Optional[str]:
        """Get cached prompt. Returns None if not found."""
        result = self._cache.get(key)
        if result:
            self._hits += 1
        else:
            self._misses += 1
        return result

    def set(self, key: str, value: str) -> None:
        """Set cached prompt with LRU eviction."""
        if len(self._cache) >= self.max_size:
            # Remove oldest entry (first key in dict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = value

    def clear(self) -> None:
        """Clear all cached prompts."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def hit_rate(self) -> float:
        """Return cache hit rate as 0-1 fraction."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)


class ResultCache:
    """Cache for tool/operation results with TTL-based expiration."""

    def __init__(self, default_ttl: float = 30.0):
        self._cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl

    def _hash_key(self, operation: str, *args) -> str:
        """Generate hash-based cache key."""
        content = f"{operation}:{json.dumps(args, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, operation: str, *args) -> Optional[Any]:
        """Get cached result. Returns None if not found or expired."""
        key = self._hash_key(operation, *args)
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            return entry.value
        if entry:
            del self._cache[key]  # Clean expired
        return None

    def set(self, operation: str, result: Any, *args, ttl: float = None) -> None:
        """Set cached result with optional TTL."""
        key = self._hash_key(operation, *args)
        self._cache[key] = CacheEntry(
            value=result,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl
        )

    def invalidate_by_file(self, file_path: str) -> int:
        """Invalidate all entries related to a file."""
        count = 0
        keys_to_remove = []
        file_path_str = str(file_path)
        for key, entry in self._cache.items():
            if file_path_str in str(entry.value):
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self._cache[key]
            count += 1
        return count

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()

    @property
    def size(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)


class FileHashCache:
    """Track file hashes for change detection."""

    def __init__(self):
        self._hashes: Dict[str, str] = {}

    def get_hash(self, path: Path) -> str:
        """Get MD5 hash of file content."""
        if not path.exists() or not path.is_file():
            return ""
        try:
            content = path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except (IOError, OSError):
            return ""

    def has_changed(self, path: Path) -> bool:
        """Check if file has changed since last check."""
        current_hash = self.get_hash(path)
        path_str = str(path)
        previous_hash = self._hashes.get(path_str)
        self._hashes[path_str] = current_hash
        return previous_hash is not None and previous_hash != current_hash

    def get_previous_hash(self, path: Path) -> Optional[str]:
        """Get previous hash for a file without updating."""
        return self._hashes.get(str(path))

    def clear(self) -> None:
        """Clear all tracked file hashes."""
        self._hashes.clear()


# Singleton caches for global access
_prompt_cache = PromptCache()
_result_cache = ResultCache()
_file_hash_cache = FileHashCache()


def get_prompt_cache() -> PromptCache:
    """Get the global prompt cache instance."""
    return _prompt_cache


def get_result_cache() -> ResultCache:
    """Get the global result cache instance."""
    return _result_cache


def get_file_hash_cache() -> FileHashCache:
    """Get the global file hash cache instance."""
    return _file_hash_cache
