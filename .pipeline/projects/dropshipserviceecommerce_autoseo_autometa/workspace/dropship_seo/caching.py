"""Caching system for SEO analysis results."""

from __future__ import annotations

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any
from datetime import datetime, timedelta
import threading

from dropship_seo.models import Product, SEOReport


class CacheEntry:
    """Represents a cached result with metadata."""

    def __init__(self, key: str, value: Any, created_at: datetime, expires_at: datetime | None = None):
        self.key = key
        self.value = value
        self.created_at = created_at
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CacheEntry:
        """Create from dictionary."""
        return cls(
            key=data["key"],
            value=data["value"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
        )


class SEOCache:
    """Thread-safe caching system for SEO analysis results."""

    def __init__(
        self,
        cache_dir: str | Path = ".seo_cache",
        default_ttl_seconds: int = 3600,
        max_cache_size: int = 1000,
        use_json: bool = True,
    ):
        """Initialize the cache.

        Args:
            cache_dir: Directory to store cache files.
            default_ttl_seconds: Default time-to-live for cache entries.
            max_cache_size: Maximum number of entries in cache.
            use_json: Whether to use JSON format (True) or pickle (False).
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl_seconds = default_ttl_seconds
        self.max_cache_size = max_cache_size
        self.use_json = use_json
        self._lock = threading.RLock()
        self._cache: dict[str, CacheEntry] = {}

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, product: Product, operation: str = "analyze") -> str:
        """Generate a unique cache key for a product and operation."""
        # Create a hashable representation of the product
        product_data = {
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "price": product.price,
            "target_keywords": tuple(product.target_keywords),
            "images": tuple(product.images),
            "brand": product.brand,
            "sku": product.sku,
        }
        product_str = json.dumps(product_data, sort_keys=True, ensure_ascii=False)
        operation_hash = hashlib.md5(operation.encode()).hexdigest()
        return f"{operation_hash}:{hashlib.sha256(product_str.encode()).hexdigest()}"

    def _load_from_disk(self, key: str) -> CacheEntry | None:
        """Load a cache entry from disk."""
        cache_file = self.cache_dir / f"{key}.cache"
        if not cache_file.exists():
            return None

        try:
            if self.use_json:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                entry = CacheEntry.from_dict(data)
            else:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)

            # Add to memory cache
            self._cache[key] = entry
            return entry
        except (json.JSONDecodeError, pickle.PickleError, KeyError):
            # Corrupted cache file, remove it
            cache_file.unlink(missing_ok=True)
            return None

    def _save_to_disk(self, key: str, entry: CacheEntry) -> None:
        """Save a cache entry to disk."""
        cache_file = self.cache_dir / f"{key}.cache"

        try:
            if self.use_json:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(entry.to_dict(), f, indent=2, ensure_ascii=False)
            else:
                with open(cache_file, "wb") as f:
                    pickle.dump(entry, f)
        except (IOError, OSError):
            # Failed to save, but continue without error
            pass

    def get(self, product: Product, operation: str = "analyze") -> Any | None:
        """Get a cached result for a product.

        Args:
            product: The product to cache lookup.
            operation: The operation type (e.g., "analyze", "generate").

        Returns:
            The cached value if found and not expired, None otherwise.
        """
        key = self._generate_key(product, operation)

        with self._lock:
            # Check memory cache first
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    return entry.value
                else:
                    # Remove expired entry
                    del self._cache[key]

            # Try to load from disk
            entry = self._load_from_disk(key)
            if entry and not entry.is_expired():
                self._cache[key] = entry
                return entry.value

            return None

    def set(
        self,
        product: Product,
        value: Any,
        operation: str = "analyze",
        ttl_seconds: int | None = None,
    ) -> None:
        """Cache a result for a product.

        Args:
            product: The product to cache.
            value: The value to cache.
            operation: The operation type.
            ttl_seconds: Time-to-live in seconds. Uses default if None.
        """
        key = self._generate_key(product, operation)
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds or self.default_ttl_seconds)

        entry = CacheEntry(key=key, value=value, created_at=datetime.now(), expires_at=expires_at)

        with self._lock:
            # Check if we need to evict entries
            if len(self._cache) >= self.max_cache_size:
                self._evict_oldest()

            self._cache[key] = entry
            self._save_to_disk(key, entry)

    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if not self._cache:
            return

        # Find the oldest entry
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at,
        )
        del self._cache[oldest_key]

        # Remove from disk
        cache_file = self.cache_dir / f"{oldest_key}.cache"
        if cache_file.exists():
            cache_file.unlink()

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

            # Remove all cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

    def cleanup_expired(self) -> int:
        """Remove all expired cache entries.

        Returns:
            Number of entries removed.
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]
                cache_file = self.cache_dir / f"{key}.cache"
                if cache_file.exists():
                    cache_file.unlink()

            return len(expired_keys)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics.
        """
        with self._lock:
            total_entries = len(self._cache)
            expired_count = sum(1 for entry in self._cache.values() if entry.is_expired())

            # Count disk files
            disk_files = len(list(self.cache_dir.glob("*.cache")))

            return {
                "memory_entries": total_entries,
                "expired_entries": expired_count,
                "disk_files": disk_files,
                "cache_dir": str(self.cache_dir),
                "max_cache_size": self.max_cache_size,
                "default_ttl_seconds": self.default_ttl_seconds,
            }

    def __len__(self) -> int:
        """Return the number of entries in the cache."""
        return len(self._cache)


# Singleton instance for global cache
_global_cache: SEOCache | None = None
_global_lock = threading.Lock()


def get_cache(
    cache_dir: str | Path | None = None,
    default_ttl_seconds: int | None = None,
    max_cache_size: int | None = None,
    use_json: bool | None = None,
) -> SEOCache:
    """Get or create the global cache instance.

    Args:
        cache_dir: Cache directory path.
        default_ttl_seconds: Default TTL in seconds.
        max_cache_size: Maximum cache size.
        use_json: Whether to use JSON format.

    Returns:
        The global cache instance.
    """
    global _global_cache

    if _global_cache is None:
        with _global_lock:
            if _global_cache is None:
                _global_cache = SEOCache(
                    cache_dir=cache_dir or ".seo_cache",
                    default_ttl_seconds=default_ttl_seconds or 3600,
                    max_cache_size=max_cache_size or 1000,
                    use_json=use_json if use_json is not None else True,
                )

    return _global_cache


def clear_global_cache() -> None:
    """Clear the global cache instance."""
    global _global_cache
    with _global_lock:
        if _global_cache is not None:
            _global_cache.clear()
            _global_cache = None
