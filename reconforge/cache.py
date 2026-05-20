"""Simple SQLite-based caching for ReconForge results."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class ReconCache:
    """SQLite-based cache for recon results."""

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache with optional custom directory."""
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".reconforge" / "cache"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "reconforge.db"
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ttl_seconds INTEGER DEFAULT 86400
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON cache(timestamp)
            """)
            conn.commit()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache if not expired."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value, timestamp, ttl_seconds FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            value_json, timestamp_str, ttl = row
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            
            # Check if expired
            if (now - timestamp).total_seconds() > ttl:
                self.delete(key)
                return None
            
            return json.loads(value_json)

    def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 86400) -> None:
        """Store value in cache with TTL."""
        value_json = json.dumps(value)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, ttl_seconds) VALUES (?, ?, ?)",
                (key, value_json, ttl_seconds)
            )
            conn.commit()

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()

    def clear(self) -> None:
        """Clear all cache entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of deleted entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM cache 
                WHERE datetime(timestamp, '+' || ttl_seconds || ' seconds') < datetime('now')
            """)
            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT SUM(length(value)) FROM cache
            """)
            size = cursor.fetchone()[0] or 0
            
            return {
                "total_entries": total,
                "cache_size_bytes": size,
                "cache_path": str(self.db_path),
            }


# Global cache instance
_cache: Optional[ReconCache] = None


def get_cache() -> ReconCache:
    """Get or create global cache instance."""
    global _cache
    if _cache is None:
        _cache = ReconCache()
    return _cache
