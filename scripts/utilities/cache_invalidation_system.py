from __future__ import annotations
import json
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Cache Invalidation System
=========================
Task 1.2: Cache Invalidation Infrastructure for B-1054 Generation Cache Implementation

This script implements cache invalidation mechanisms including:
- TTL-based cache expiration
- Similarity threshold management
- Cache cleanup strategies
- Invalidation logging and monitoring
- Configuration-driven invalidation policies
"""

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database configuration - simplified for this script
def get_database_url():
    return os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

def validate_database_config():
    database_url = get_database_url()
    return database_url.startswith("postgresql://")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/cache_invalidation.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

class InvalidationPolicy(Enum):
    """Cache invalidation policy types"""

    TTL_BASED = "ttl_based"
    SIMILARITY_THRESHOLD = "similarity_threshold"
    FREQUENCY_BASED = "frequency_based"
    MANUAL = "manual"

@dataclass
class InvalidationConfig:
    """Configuration for cache invalidation"""

    ttl_hours: int = 24  # Default TTL: 24 hours
    similarity_threshold: float = 0.7  # Default similarity threshold
    cleanup_interval_minutes: int = 60  # Default cleanup interval
    max_cache_size_mb: int = 100  # Maximum cache size in MB
    enable_logging: bool = True
    enable_monitoring: bool = True

class CacheInvalidationSystem:
    """Cache invalidation system with multiple strategies"""

    def __init__(self, database_url: str | None = None, config: InvalidationConfig | None = None):
        """Initialize cache invalidation system"""
        self.database_url = database_url or get_database_url()
        self.config = config or InvalidationConfig()
        self.connection = None
        self.cursor = None
        self.running = False
        self.cleanup_thread = None

        # Validate database configuration
        if not validate_database_config():
            raise ValueError("Invalid database configuration")

        # Initialize statistics
        self.stats = {
            "total_invalidations": 0,
            "ttl_invalidations": 0,
            "similarity_invalidations": 0,
            "frequency_invalidations": 0,
            "manual_invalidations": 0,
            "last_cleanup": None,
            "cache_size_mb": 0,
        }

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.disconnect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Database connection closed")

    def get_cache_statistics(self) -> dict[str, Any]:
        """Get current cache statistics"""
        try:
            # Get total cache entries
            self.cursor.execute(
                """
                SELECT
                    COUNT(*) as total_entries,
                    COUNT(*) FILTER (WHERE cache_hit = TRUE) as cache_hits,
                    COUNT(*) FILTER (WHERE cache_hit = FALSE) as cache_misses,
                    AVG(similarity_score) as avg_similarity,
                    MIN(last_verified) as oldest_verification,
                    MAX(last_verified) as newest_verification
                FROM episodic_logs;
            """
            )

            stats = self.cursor.fetchone()

            # Get table size
            self.cursor.execute(
                """
                SELECT pg_size_pretty(pg_total_relation_size('episodic_logs')) as table_size
                FROM pg_class WHERE relname = 'episodic_logs';
            """
            )

            size_info = self.cursor.fetchone()

            return {
                "total_entries": stats["total_entries"] if stats else 0,
                "cache_hits": stats["cache_hits"] if stats else 0,
                "cache_misses": stats["cache_misses"] if stats else 0,
                "avg_similarity": float(stats["avg_similarity"]) if stats and stats["avg_similarity"] else 0.0,
                "oldest_verification": stats["oldest_verification"] if stats else None,
                "newest_verification": stats["newest_verification"] if stats else None,
                "table_size": size_info["table_size"] if size_info else "Unknown",
                "system_stats": self.stats,
            }

        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}

    def invalidate_by_ttl(self) -> int:
        """Invalidate cache entries based on TTL"""
        try:
            ttl_cutoff = datetime.now() - timedelta(hours=self.config.ttl_hours)

            # Find entries to invalidate
            self.cursor.execute(
                """
                SELECT id, last_verified, similarity_score
                FROM episodic_logs
                WHERE cache_hit = TRUE
                AND last_verified < %s
                ORDER BY last_verified ASC;
            """,
                (ttl_cutoff,),
            )

            expired_entries = self.cursor.fetchall()

            if not expired_entries:
                logger.info("No TTL-expired entries found")
                return 0

            # Invalidate expired entries
            expired_ids = [entry["id"] for entry in expired_entries]
            self.cursor.execute(
                """
                UPDATE episodic_logs
                SET cache_hit = FALSE,
                    similarity_score = 0.0,
                    last_verified = NOW()
                WHERE id = ANY(%s);
            """,
                (expired_ids,),
            )

            invalidated_count = self.cursor.rowcount
            self.connection.commit()

            # Update statistics
            self.stats["ttl_invalidations"] += invalidated_count
            self.stats["total_invalidations"] += invalidated_count

            logger.info(f"TTL invalidation: {invalidated_count} entries expired and invalidated")
            return invalidated_count

        except Exception as e:
            logger.error(f"Error during TTL invalidation: {e}")
            self.connection.rollback()
            return 0

    def invalidate_by_similarity_threshold(self, threshold: float | None = None) -> int:
        """Invalidate cache entries below similarity threshold"""
        try:
            similarity_threshold = threshold or self.config.similarity_threshold

            # Find entries below threshold
            self.cursor.execute(
                """
                SELECT id, similarity_score, last_verified
                FROM episodic_logs
                WHERE cache_hit = TRUE
                AND similarity_score < %s
                ORDER BY similarity_score ASC;
            """,
                (similarity_threshold,),
            )

            low_similarity_entries = self.cursor.fetchall()

            if not low_similarity_entries:
                logger.info(f"No entries below similarity threshold {similarity_threshold}")
                return 0

            # Invalidate low similarity entries
            low_similarity_ids = [entry["id"] for entry in low_similarity_entries]
            self.cursor.execute(
                """
                UPDATE episodic_logs
                SET cache_hit = FALSE,
                    similarity_score = 0.0,
                    last_verified = NOW()
                WHERE id = ANY(%s);
            """,
                (low_similarity_ids,),
            )

            invalidated_count = self.cursor.rowcount
            self.connection.commit()

            # Update statistics
            self.stats["similarity_invalidations"] += invalidated_count
            self.stats["total_invalidations"] += invalidated_count

            logger.info(f"Similarity invalidation: {invalidated_count} entries below threshold {similarity_threshold}")
            return invalidated_count

        except Exception as e:
            logger.error(f"Error during similarity invalidation: {e}")
            self.connection.rollback()
            return 0

    def invalidate_by_frequency(self, min_verification_age_hours: int = 1) -> int:
        """Invalidate cache entries based on verification frequency"""
        try:
            frequency_cutoff = datetime.now() - timedelta(hours=min_verification_age_hours)

            # Find entries that haven't been verified recently
            self.cursor.execute(
                """
                SELECT id, last_verified, similarity_score
                FROM episodic_logs
                WHERE cache_hit = TRUE
                AND last_verified < %s
                AND similarity_score < 0.8
                ORDER BY last_verified ASC;
            """,
                (frequency_cutoff,),
            )

            frequency_entries = self.cursor.fetchall()

            if not frequency_entries:
                logger.info("No frequency-based invalidation entries found")
                return 0

            # Invalidate frequency-based entries
            frequency_ids = [entry["id"] for entry in frequency_entries]
            self.cursor.execute(
                """
                UPDATE episodic_logs
                SET cache_hit = FALSE,
                    similarity_score = 0.0,
                    last_verified = NOW()
                WHERE id = ANY(%s);
            """,
                (frequency_ids,),
            )

            invalidated_count = self.cursor.rowcount
            self.connection.commit()

            # Update statistics
            self.stats["frequency_invalidations"] += invalidated_count
            self.stats["total_invalidations"] += invalidated_count

            logger.info(f"Frequency invalidation: {invalidated_count} entries invalidated")
            return invalidated_count

        except Exception as e:
            logger.error(f"Error during frequency invalidation: {e}")
            self.connection.rollback()
            return 0

    def manual_invalidation(self, entry_ids: list[int]) -> int:
        """Manually invalidate specific cache entries"""
        try:
            if not entry_ids:
                logger.info("No entry IDs provided for manual invalidation")
                return 0

            # Invalidate specified entries
            self.cursor.execute(
                """
                UPDATE episodic_logs
                SET cache_hit = FALSE,
                    similarity_score = 0.0,
                    last_verified = NOW()
                WHERE id = ANY(%s);
            """,
                (entry_ids,),
            )

            invalidated_count = self.cursor.rowcount
            self.connection.commit()

            # Update statistics
            self.stats["manual_invalidations"] += invalidated_count
            self.stats["total_invalidations"] += invalidated_count

            logger.info(f"Manual invalidation: {invalidated_count} entries invalidated")
            return invalidated_count

        except Exception as e:
            logger.error(f"Error during manual invalidation: {e}")
            self.connection.rollback()
            return 0

    def cleanup_cache(self) -> dict[str, Any]:
        """Perform comprehensive cache cleanup"""
        try:
            logger.info("Starting comprehensive cache cleanup")
            cleanup_start = datetime.now()

            # Get initial statistics
            initial_stats = self.get_cache_statistics()

            # Perform all invalidation strategies
            ttl_count = self.invalidate_by_ttl()
            similarity_count = self.invalidate_by_similarity_threshold()
            frequency_count = self.invalidate_by_frequency()

            # Get final statistics
            final_stats = self.get_cache_statistics()

            # Calculate cleanup metrics
            cleanup_duration = datetime.now() - cleanup_start
            total_invalidated = ttl_count + similarity_count + frequency_count

            cleanup_metrics = {
                "ttl_invalidations": ttl_count,
                "similarity_invalidations": similarity_count,
                "frequency_invalidations": frequency_count,
                "total_invalidated": total_invalidated,
                "cleanup_duration": str(cleanup_duration),
                "initial_cache_size": initial_stats.get("table_size", "Unknown"),
                "final_cache_size": final_stats.get("table_size", "Unknown"),
                "cache_hit_rate_before": self._calculate_cache_hit_rate(initial_stats),
                "cache_hit_rate_after": self._calculate_cache_hit_rate(final_stats),
            }

            # Update last cleanup time
            self.stats["last_cleanup"] = datetime.now()

            logger.info(f"Cache cleanup completed: {total_invalidated} entries invalidated in {cleanup_duration}")
            logger.info(f"Cleanup metrics: {cleanup_metrics}")

            return cleanup_metrics

        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return {}

    def _calculate_cache_hit_rate(self, stats: dict[str, Any]) -> float:
        """Calculate cache hit rate from statistics"""
        total_entries = stats.get("total_entries", 0)
        cache_hits = stats.get("cache_hits", 0)

        if total_entries == 0:
            return 0.0

        return (cache_hits / total_entries) * 100.0

    def start_background_cleanup(self):
        """Start background cleanup thread"""
        if self.running:
            logger.warning("Background cleanup already running")
            return

        self.running = True
        self.cleanup_thread = threading.Thread(target=self._background_cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info("Background cleanup thread started")

    def stop_background_cleanup(self):
        """Stop background cleanup thread"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
            logger.info("Background cleanup thread stopped")

    def _background_cleanup_loop(self):
        """Background cleanup loop"""
        while self.running:
            try:
                logger.info("Running scheduled cache cleanup")
                self.cleanup_cache()

                # Wait for next cleanup interval
                time.sleep(self.config.cleanup_interval_minutes * 60)

            except Exception as e:
                logger.error(f"Error in background cleanup loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def get_invalidation_report(self) -> dict[str, Any]:
        """Generate comprehensive invalidation report"""
        try:
            current_stats = self.get_cache_statistics()

            report = {
                "timestamp": datetime.now().isoformat(),
                "system_stats": self.stats,
                "current_cache_stats": current_stats,
                "configuration": {
                    "ttl_hours": self.config.ttl_hours,
                    "similarity_threshold": self.config.similarity_threshold,
                    "cleanup_interval_minutes": self.config.cleanup_interval_minutes,
                    "max_cache_size_mb": self.config.max_cache_size_mb,
                },
                "recommendations": self._generate_recommendations(current_stats),
            }

            return report

        except Exception as e:
            logger.error(f"Error generating invalidation report: {e}")
            return {}

    def _generate_recommendations(self, stats: dict[str, Any]) -> list[str]:
        """Generate recommendations based on current cache statistics"""
        recommendations = []

        cache_hit_rate = self._calculate_cache_hit_rate(stats)

        if cache_hit_rate < 50:
            recommendations.append("Cache hit rate is low. Consider adjusting similarity threshold or TTL.")

        if stats.get("total_entries", 0) > 10000:
            recommendations.append("Large number of cache entries. Consider more aggressive cleanup.")

        if self.stats["ttl_invalidations"] > self.stats["similarity_invalidations"]:
            recommendations.append("TTL-based invalidations dominate. Consider adjusting TTL settings.")

        if self.stats["similarity_invalidations"] > self.stats["ttl_invalidations"]:
            recommendations.append("Similarity-based invalidations dominate. Consider adjusting similarity threshold.")

        return recommendations

def main():
    """Main function to test cache invalidation system"""
    try:
        # Create configuration
        config = InvalidationConfig(
            ttl_hours=24,
            similarity_threshold=0.7,
            cleanup_interval_minutes=60,
            max_cache_size_mb=100,
            enable_logging=True,
            enable_monitoring=True,
        )

        # Test cache invalidation system
        with CacheInvalidationSystem(config=config) as invalidation_system:
            logger.info("Testing Cache Invalidation System")

            # Get initial statistics
            initial_stats = invalidation_system.get_cache_statistics()
            logger.info(f"Initial cache statistics: {initial_stats}")

            # Test TTL invalidation
            ttl_count = invalidation_system.invalidate_by_ttl()
            logger.info(f"TTL invalidation result: {ttl_count} entries")

            # Test similarity invalidation
            similarity_count = invalidation_system.invalidate_by_similarity_threshold(0.8)
            logger.info(f"Similarity invalidation result: {similarity_count} entries")

            # Test frequency invalidation
            frequency_count = invalidation_system.invalidate_by_frequency(2)
            logger.info(f"Frequency invalidation result: {frequency_count} entries")

            # Get final statistics
            final_stats = invalidation_system.get_cache_statistics()
            logger.info(f"Final cache statistics: {final_stats}")

            # Generate report
            report = invalidation_system.get_invalidation_report()
            logger.info(f"Invalidation report: {json.dumps(report, indent=2, default=str)}")

            logger.info("Cache invalidation system test completed successfully")

    except Exception as e:
        logger.error(f"Cache invalidation system test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
