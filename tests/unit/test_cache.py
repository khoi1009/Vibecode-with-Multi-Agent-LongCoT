"""
Unit tests for cache module.

Tests prompt caching, result caching, and file hash tracking.
"""

import pytest
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.cache import PromptCache, ResultCache, FileHashCache, get_prompt_cache, get_result_cache, get_file_hash_cache


class TestPromptCache:
    """Test suite for PromptCache class."""

    @pytest.mark.unit
    def test_get_key(self):
        """Test cache key generation."""
        cache = PromptCache()
        key = cache.get_key("02", ("skill1", "skill2"))
        assert key == "02:skill1:skill2"

    @pytest.mark.unit
    def test_set_and_get(self):
        """Test basic set/get operations."""
        cache = PromptCache()
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        assert result == "test_value"

    @pytest.mark.unit
    def test_get_missing(self):
        """Test getting non-existent key returns None."""
        cache = PromptCache()
        result = cache.get("missing_key")
        assert result is None

    @pytest.mark.unit
    def test_hit_rate(self):
        """Test hit rate calculation."""
        cache = PromptCache()
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        assert cache.hit_rate == 0.5

    @pytest.mark.unit
    def test_lru_eviction(self):
        """Test that oldest entry is evicted when full."""
        cache = PromptCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    @pytest.mark.unit
    def test_clear(self):
        """Test cache clearing."""
        cache = PromptCache()
        cache.set("key1", "value1")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.hit_rate == 0.0


class TestResultCache:
    """Test suite for ResultCache class."""

    @pytest.mark.unit
    def test_set_and_get(self):
        """Test basic set/get operations."""
        cache = ResultCache()
        cache.set("operation", "result", "arg1", "arg2")
        result = cache.get("operation", "arg1", "arg2")
        assert result == "result"

    @pytest.mark.unit
    def test_ttl_expiration(self):
        """Test that entries expire after TTL."""
        cache = ResultCache(default_ttl=0.1)
        cache.set("operation", "result", ttl=0.1)
        time.sleep(0.2)  # Wait for expiration
        result = cache.get("operation")
        assert result is None

    @pytest.mark.unit
    def test_custom_ttl(self):
        """Test custom TTL per entry."""
        cache = ResultCache(default_ttl=1.0)
        cache.set("fast_expire", "result", ttl=0.1)
        cache.set("slow_expire", "result", ttl=1.0)
        time.sleep(0.2)
        assert cache.get("fast_expire") is None
        assert cache.get("slow_expire") == "result"

    @pytest.mark.unit
    def test_hash_key_different(self):
        """Test that different args produce different keys."""
        cache = ResultCache()
        cache.set("op", "result1", "a")
        cache.set("op", "result2", "b")
        assert cache.get("op", "a") == "result1"
        assert cache.get("op", "b") == "result2"

    @pytest.mark.unit
    def test_clear(self):
        """Test cache clearing."""
        cache = ResultCache()
        cache.set("op", "result")
        cache.clear()
        assert cache.get("op") is None


class TestFileHashCache:
    """Test suite for FileHashCache class."""

    @pytest.mark.unit
    def test_get_hash(self, temp_workspace):
        """Test file hash generation."""
        cache = FileHashCache()
        test_file = temp_workspace / "test.txt"
        test_file.write_text("hello")
        hash1 = cache.get_hash(test_file)
        assert hash1 != ""
        assert len(hash1) == 32  # MD5 hex length

    @pytest.mark.unit
    def test_has_changed_detects_change(self, temp_workspace):
        """Test change detection."""
        cache = FileHashCache()
        test_file = temp_workspace / "test.txt"
        test_file.write_text("hello")

        # First check - should return False (no previous hash)
        assert cache.has_changed(test_file) is False

        # Modify file
        test_file.write_text("world")

        # Second check - should return True
        assert cache.has_changed(test_file) is True

    @pytest.mark.unit
    def test_get_previous_hash(self, temp_workspace):
        """Test getting previous hash without updating."""
        cache = FileHashCache()
        test_file = temp_workspace / "test.txt"
        test_file.write_text("hello")

        # Record initial hash
        cache.has_changed(test_file)

        # Get previous without updating
        prev = cache.get_previous_hash(test_file)
        assert prev is not None
        assert len(prev) == 32

    @pytest.mark.unit
    def test_non_existent_file(self, temp_workspace):
        """Test hash for non-existent file."""
        cache = FileHashCache()
        missing_file = temp_workspace / "missing.txt"
        hash_val = cache.get_hash(missing_file)
        assert hash_val == ""


class TestCacheSingletons:
    """Test suite for cache singleton functions."""

    @pytest.mark.unit
    def test_get_prompt_cache(self):
        """Test getting prompt cache singleton."""
        cache1 = get_prompt_cache()
        cache2 = get_prompt_cache()
        assert cache1 is cache2

    @pytest.mark.unit
    def test_get_result_cache(self):
        """Test getting result cache singleton."""
        cache1 = get_result_cache()
        cache2 = get_result_cache()
        assert cache1 is cache2

    @pytest.mark.unit
    def test_get_file_hash_cache(self):
        """Test getting file hash cache singleton."""
        cache1 = get_file_hash_cache()
        cache2 = get_file_hash_cache()
        assert cache1 is cache2
