#!/usr/bin/env python3
"""Cache separation manager for workload isolation in B-1070."""

import json
import logging
import os
import shutil
import time
from pathlib import Path


logger = logging.getLogger(__name__)

# Cache directory configurations
CACHE_CONFIGS = {
    "ltst_memory": {
        "base_dir": ".ragcache_ltst",
        "subdirs": ["vector_cache", "context_cache", "session_cache", "embedding_cache"],
        "max_size_mb": 2048,  # 2GB for memory system
        "cleanup_threshold": 0.8,  # Cleanup when 80% full
    },
    "ragchecker_eval": {
        "base_dir": ".ragcache_eval",
        "subdirs": ["query_cache", "result_cache", "metric_cache", "temp_cache"],
        "max_size_mb": 512,  # 512MB for evaluations
        "cleanup_threshold": 0.7,  # Cleanup when 70% full
    },
    "default": {
        "base_dir": ".ragcache_default",
        "subdirs": ["general_cache", "temp_cache"],
        "max_size_mb": 256,  # 256MB default
        "cleanup_threshold": 0.8,
    },
}


class CacheSeparationManager:
    """Manages separate cache directories for different workloads."""

    def __init__(self, project_root: str | None = None):
        """Initialize the cache separation manager."""
        if project_root is None:
            # Try to find project root
            current_path = Path(__file__).resolve()
            for parent in current_path.parents:
                if (parent / "pyproject.toml").exists() or (parent / "requirements.txt").exists():
                    project_root = str(parent)
                    break

        if not project_root:
            project_root = os.getcwd()

        self.project_root = Path(project_root)
        self.current_role = "default"
        self.cache_dirs: dict[str, Path] = {}

        # Initialize cache directories
        self._initialize_cache_dirs()

    def _initialize_cache_dirs(self):
        """Initialize cache directory structure."""
        for role, config in CACHE_CONFIGS.items():
            base_dir = self.project_root / config["base_dir"]
            self.cache_dirs[role] = base_dir

            # Create base directory if it doesn't exist
            base_dir.mkdir(exist_ok=True)

            # Create subdirectories
            for subdir in config["subdirs"]:
                (base_dir / subdir).mkdir(exist_ok=True)

            logger.debug(f"Initialized cache directory for {role}: {base_dir}")

    def set_role(self, role: str) -> bool:
        """Set the current workload role."""
        if role not in CACHE_CONFIGS:
            logger.warning(f"Unknown role '{role}', using 'default'")
            role = "default"

        self.current_role = role
        logger.info(f"Cache role set to: {role}")
        return True

    def get_cache_dir(self, role: str | None = None, subdir: str | None = None) -> Path:
        """Get the cache directory for a specific role and optional subdirectory."""
        if role is None:
            role = self.current_role

        if role not in self.cache_dirs:
            logger.warning(f"Unknown role '{role}', using 'default'")
            role = "default"

        cache_dir = self.cache_dirs[role]

        if subdir:
            subdir_path = cache_dir / subdir
            if subdir_path.exists():
                return subdir_path
            else:
                logger.warning(f"Subdirectory '{subdir}' not found in {role} cache")
                return cache_dir

        return cache_dir

    def get_cache_info(self, role: str | None = None) -> dict:
        """Get information about a cache directory."""
        if role is None:
            role = self.current_role

        cache_dir = self.get_cache_dir(role)
        config = CACHE_CONFIGS[role]

        # Calculate current size
        total_size = self._calculate_dir_size(cache_dir)
        total_size_mb = total_size / (1024 * 1024)

        # Check subdirectory sizes
        subdir_sizes = {}
        for subdir in config["subdirs"]:
            subdir_path = cache_dir / subdir
            if subdir_path.exists():
                subdir_sizes[subdir] = self._calculate_dir_size(subdir_path) / (1024 * 1024)

        return {
            "role": role,
            "base_dir": str(cache_dir),
            "current_size_mb": round(total_size_mb, 2),
            "max_size_mb": config["max_size_mb"],
            "usage_percent": round((total_size_mb / config["max_size_mb"]) * 100, 1),
            "cleanup_threshold": config["cleanup_threshold"],
            "subdir_sizes": subdir_sizes,
            "needs_cleanup": total_size_mb > (config["max_size_mb"] * config["cleanup_threshold"]),
        }

    def _calculate_dir_size(self, directory: Path) -> int:
        """Calculate the total size of a directory in bytes."""
        total_size = 0
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except (PermissionError, OSError) as e:
            logger.warning(f"Error calculating size for {directory}: {e}")

        return total_size

    def cleanup_cache(self, role: str | None = None, force: bool = False) -> bool:
        """Clean up cache for a specific role."""
        if role is None:
            role = self.current_role

        cache_info = self.get_cache_info(role)

        if not force and not cache_info["needs_cleanup"]:
            logger.info(f"Cache for {role} doesn't need cleanup (usage: {cache_info['usage_percent']}%)")
            return True

        logger.info(f"Cleaning up cache for {role} (usage: {cache_info['usage_percent']}%)")

        try:
            cache_dir = self.get_cache_dir(role)
            config = CACHE_CONFIGS[role]

            # Clean up subdirectories
            for subdir in config["subdirs"]:
                subdir_path = cache_dir / subdir
                if subdir_path.exists():
                    self._cleanup_subdir(subdir_path)

            # Clean up base directory (remove any orphaned files)
            for item in cache_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    logger.debug(f"Removed orphaned file: {item}")

            logger.info(f"Cache cleanup completed for {role}")
            return True

        except Exception as e:
            logger.error(f"Error cleaning up cache for {role}: {e}")
            return False

    def _cleanup_subdir(self, subdir_path: Path):
        """Clean up a specific subdirectory."""
        try:
            # Remove all files in subdirectory
            for item in subdir_path.iterdir():
                if item.is_file():
                    item.unlink()
                    logger.debug(f"Removed file: {item}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    logger.debug(f"Removed directory: {item}")

            # Recreate empty subdirectory
            subdir_path.mkdir(exist_ok=True)

        except Exception as e:
            logger.warning(f"Error cleaning up subdirectory {subdir_path}: {e}")

    def get_cache_path(self, role: str | None = None, subdir: str | None = None, filename: str | None = None) -> Path:
        """Get a specific cache file path."""
        cache_dir = self.get_cache_dir(role, subdir)

        if filename:
            return cache_dir / filename
        return cache_dir

    def list_cache_files(self, role: str | None = None, subdir: str | None = None) -> list[Path]:
        """List all files in a cache directory."""
        cache_dir = self.get_cache_dir(role, subdir)

        files = []
        try:
            for item in cache_dir.iterdir():
                if item.is_file():
                    files.append(item)
        except (PermissionError, OSError) as e:
            logger.warning(f"Error listing files in {cache_dir}: {e}")

        return files

    def clear_all_caches(self) -> bool:
        """Clear all cache directories."""
        logger.info("Clearing all cache directories")

        success = True
        for role in CACHE_CONFIGS.keys():
            if not self.cleanup_cache(role, force=True):
                success = False

        return success

    def get_cache_status_summary(self) -> dict:
        """Get a summary of all cache statuses."""
        summary = {"total_caches": len(CACHE_CONFIGS), "caches": {}, "total_size_mb": 0, "overall_status": "healthy"}

        for role in CACHE_CONFIGS.keys():
            cache_info = self.get_cache_info(role)
            summary["caches"][role] = cache_info
            summary["total_size_mb"] += cache_info["current_size_mb"]

            if cache_info["needs_cleanup"]:
                summary["overall_status"] = "needs_cleanup"

        return summary

    def save_cache_report(self, filepath: str | None = None) -> str:
        """Save a cache status report to a file."""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"metrics/system_diagnostics/cache_status_{timestamp}.json"

        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        report = self.get_cache_status_summary()

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Cache report saved to: {filepath}")
        return filepath


def main():
    """Test the CacheSeparationManager."""

    logging.basicConfig(level=logging.INFO)

    print("🧪 Testing CacheSeparationManager")
    print("=" * 50)

    manager = CacheSeparationManager()

    # Test different roles
    for role in ["default", "ltst_memory", "ragchecker_eval"]:
        print(f"\n🗂️  Testing cache role: {role}")

        # Set role
        manager.set_role(role)

        # Get cache info
        cache_info = manager.get_cache_info(role)
        print(f"   Base dir: {cache_info['base_dir']}")
        print(f"   Current size: {cache_info['current_size_mb']}MB / {cache_info['max_size_mb']}MB")
        print(f"   Usage: {cache_info['usage_percent']}%")
        print(f"   Needs cleanup: {cache_info['needs_cleanup']}")

        # List files
        files = manager.list_cache_files(role)
        print(f"   Files: {len(files)}")

        # Test cleanup if needed
        if cache_info["needs_cleanup"]:
            print("   Running cleanup...")
            success = manager.cleanup_cache(role)
            print(f"   Cleanup success: {success}")

    # Get overall summary
    print("\n📊 Overall Cache Status:")
    summary = manager.get_cache_status_summary()
    print(f"   Total size: {summary['total_size_mb']}MB")
    print(f"   Status: {summary['overall_status']}")

    # Save report
    report_file = manager.save_cache_report()
    print(f"   Report saved: {report_file}")

    print("\n✅ CacheSeparationManager test completed")


if __name__ == "__main__":
    main()
