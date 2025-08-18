#!/usr/bin/env python3.12.123.11
"""
Config-Driven Metadata Extractor for DSPy RAG System
Uses YAML configuration to extract metadata with scoring and ranking.
"""

import logging
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dateutil import parser as date_parser

# Schema validation (M-1)
try:
    from jsonschema import ValidationError, validate

    _SCHEMA = {
        "type": "object",
        "properties": {
            "categories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "keywords"],
                    "properties": {
                        "name": {"type": "string"},
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "weight": {"type": "number"},
                    },
                },
            },
            "date_patterns": {"type": "array", "items": {"type": "object", "required": ["pattern"]}},
        },
        "additionalProperties": True,
    }
    SCHEMA_AVAILABLE = True
except ImportError:
    SCHEMA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("jsonschema not available - schema validation disabled")

logger = logging.getLogger(__name__)

# Regex safety guard (M-2)
_BAD_RE = re.compile(r"\.[\*\+]\]?\(")  # crude but fast heuristic


def _compile_safe(pattern: str) -> re.Pattern:
    """Compile regex pattern with safety check"""
    if _BAD_RE.search(pattern):
        raise ValueError(f"Unsafe regex: {pattern}")
    return re.compile(pattern, re.IGNORECASE)


# LRU cache for date parsing (M-3)
@lru_cache(maxsize=1024)
def _cached_parse(date_str: str):
    """Cached date parsing for performance"""
    return date_parser.parse(date_str, fuzzy=True)


class ConfigDrivenMetadataExtractor:
    """Config-driven metadata extraction with scoring and ranking"""

    def __init__(self, config_path: str = "config/metadata_rules.yaml"):
        """
        Initialize the metadata extractor with configuration

        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._compile_patterns()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file with proper error handling and schema validation (M-1)"""
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)

            # Schema validation (M-1)
            if SCHEMA_AVAILABLE:
                try:
                    validate(config, _SCHEMA)
                except ValidationError as ve:
                    logger.error("Invalid config schema: %s", ve.message)
                    raise

            logger.info(f"Loaded metadata configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}, using defaults")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load metadata configuration: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration if YAML loading fails"""
        return {
            "categories": [{"name": "Uncategorized", "priority": "medium", "weight": 0, "keywords": [], "tags": []}],
            "file_types": {},
            "priority_rules": {},
            "content_keywords": [],
            "date_patterns": [],
            "version_patterns": [],
            "size_categories": {"small": 1048576, "medium": 10485760, "large": 104857600},
        }

    def _compile_patterns(self):
        """Compile regex patterns for better performance with safety checks (M-2)"""
        self.date_patterns = []
        for pattern_config in self.config.get("date_patterns", []):
            try:
                self.date_patterns.append(
                    {
                        "pattern": _compile_safe(pattern_config["pattern"]),  # M-2: Safe compilation
                        "format": pattern_config.get("format", "%Y-%m-%d"),
                    }
                )
            except ValueError as e:
                logger.error(f"Unsafe regex pattern in date_patterns: {e}")
                raise

        self.version_patterns = []
        for pattern_config in self.config.get("version_patterns", []):
            try:
                self.version_patterns.append(
                    {
                        "pattern": _compile_safe(pattern_config["pattern"]),  # M-2: Safe compilation
                        "group": pattern_config.get("group", 1),
                    }
                )
            except ValueError as e:
                logger.error(f"Unsafe regex pattern in version_patterns: {e}")
                raise

    def extract_metadata(self, document_path: str, content_preview: str = None) -> dict[str, Any]:
        """
        Extract metadata from document using config-driven rules

        Args:
            document_path: Path to the document
            content_preview: Optional content preview for analysis

        Returns:
            Dictionary containing extracted metadata
        """
        try:
            path = Path(document_path)

            # Validate file exists and is accessible
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {document_path}")

            if not path.is_file():
                raise ValueError(f"Path is not a file: {document_path}")

            # Get file stats with error handling
            try:
                stat = path.stat()
                file_size = stat.st_size
                created_at = stat.st_ctime
                modified_at = stat.st_mtime
            except OSError as e:
                logger.error(f"Failed to get file stats for {document_path}: {e}")
                raise

            filename = path.name
            file_type = path.suffix.lower().lstrip(".")

            # Initialize metadata
            metadata = {
                "filename": filename,
                "file_size": file_size,
                "file_type": file_type,
                "created_at": created_at,
                "modified_at": modified_at,
                "category": "Uncategorized",
                "tags": set(),  # Use set to avoid duplicates
                "priority": "medium",
                "notes": "",
                "content_type": "unknown",
                "processing_status": "pending",
                "extracted_at": datetime.now().isoformat(),
                "confidence_score": 0.0,
            }

            # Extract category and tags using scoring
            category_result = self._extract_category_with_scoring(filename)
            metadata.update(category_result)

            # Extract file type specific metadata
            file_type_metadata = self._extract_file_type_metadata(file_type, filename)
            metadata.update(file_type_metadata)

            # Extract priority
            priority_result = self._extract_priority(filename)
            metadata["priority"] = priority_result["priority"]
            metadata["priority_reasons"] = priority_result["reasons"]

            # Extract dates and versions
            date_result = self._extract_dates_and_versions(filename)
            metadata.update(date_result)

            # Extract size category
            metadata["size_category"] = self._get_size_category(file_size)

            # Extract content-based metadata
            if content_preview:
                content_metadata = self._extract_content_metadata(content_preview)
                metadata["tags"].update(content_metadata["tags"])

            # Convert tags set to sorted list
            metadata["tags"] = sorted(list(metadata["tags"]))

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata for {document_path}: {e}")
            raise

    def _extract_category_with_scoring(self, filename: str) -> dict[str, Any]:
        """Extract category using scoring system with improved accuracy"""
        filename_lower = filename.lower()

        # Tokenize filename for more accurate keyword matching
        words = set(re.split(r"\W+", filename_lower))

        best_category = "Uncategorized"
        best_score = 0
        all_tags = set()

        # Calculate max possible score for normalization
        max_possible_score = 0
        for category in self.config.get("categories", []):
            max_possible_score += category.get("weight", 1) * len(category.get("keywords", []))

        for category in self.config.get("categories", []):
            score = 0
            category_tags = set()

            # Score based on keyword matches (tokenized)
            for keyword in category.get("keywords", []):
                keyword_lower = keyword.lower()
                if keyword_lower in words:  # Exact word match
                    score += category.get("weight", 1)
                    category_tags.update(category.get("tags", []))
                elif keyword_lower in filename_lower:  # Substring fallback
                    score += category.get("weight", 1) * 0.5  # Lower score for substring
                    category_tags.update(category.get("tags", []))

            # Update best category if score is higher
            if score > best_score:
                best_score = score
                best_category = category["name"]
                all_tags = category_tags

        # Normalize confidence score
        confidence = min(best_score / max(max_possible_score, 1), 1.0)

        return {"category": best_category, "tags": all_tags, "confidence_score": confidence}

    def _extract_file_type_metadata(self, file_type: str, filename: str) -> dict[str, Any]:
        """Extract file type specific metadata"""
        file_type_config = self.config.get("file_types", {}).get(file_type, {})

        metadata = {
            "content_type": file_type_config.get("content_type", "unknown"),
            "tags": set(file_type_config.get("tags", [])),
        }

        # Apply special rules for file types
        filename_lower = filename.lower()
        for rule in file_type_config.get("special_rules", []):
            if "if_contains" in rule:
                for keyword in rule["if_contains"]:
                    if keyword.lower() in filename_lower:
                        metadata["tags"].update(rule.get("add_tags", []))

        return metadata

    def _extract_priority(self, filename: str) -> dict[str, Any]:
        """Extract priority with reasons"""
        filename_lower = filename.lower()
        priority = "medium"
        reasons = []

        # Check high priority keywords
        high_priority_config = self.config.get("priority_rules", {}).get("high_priority", {})
        for keyword in high_priority_config.get("keywords", []):
            if keyword.lower() in filename_lower:
                priority = "high"
                reasons.append(f"Contains '{keyword}'")

        # Check low priority keywords
        low_priority_config = self.config.get("priority_rules", {}).get("low_priority", {})
        for keyword in low_priority_config.get("keywords", []):
            if keyword.lower() in filename_lower:
                priority = "low"
                reasons.append(f"Contains '{keyword}'")

        return {"priority": priority, "reasons": reasons}

    def _extract_dates_and_versions(self, filename: str) -> dict[str, Any]:
        """Extract dates and versions from filename with improved error handling and caching (M-3)"""
        metadata = {}

        # Extract dates with limited parsing to avoid CPU spikes
        for pattern_config in self.date_patterns:
            match = pattern_config["pattern"].search(filename)
            if match:
                try:
                    date_str = match.group()
                    # Limit the string passed to dateutil for performance
                    if len(date_str) > 50:
                        date_str = date_str[:50]

                    # Use cached date parsing for performance (M-3)
                    parsed_date = _cached_parse(date_str)

                    # Validate year range
                    if 1900 <= parsed_date.year <= 2100:
                        metadata["extracted_date"] = parsed_date.strftime("%Y-%m-%d")
                        break
                except Exception as e:
                    logger.debug(f"Failed to parse date '{date_str}' from filename: {e}")
                    continue

        # Extract versions with improved group handling
        for pattern_config in self.version_patterns:
            match = pattern_config["pattern"].search(filename)
            if match:
                group_num = pattern_config["group"]
                if group_num <= len(match.groups()) and match.group(group_num):
                    metadata["version"] = match.group(group_num)
                    break

        return metadata

    def _get_size_category(self, file_size: int) -> str:
        """Get size category based on file size"""
        size_categories = self.config.get("size_categories", {})

        if file_size <= size_categories.get("small", 1048576):
            return "small"
        elif file_size <= size_categories.get("medium", 10485760):
            return "medium"
        else:
            return "large"

    def _extract_content_metadata(self, content: str) -> dict[str, Any]:
        """Extract metadata from content preview with proper implementation"""
        content_lower = content.lower()
        tags = set()

        # Check for content keywords with case-insensitive matching
        for keyword in self.config.get("content_keywords", []):
            if keyword.lower() in content_lower:
                tags.add(keyword)

        return {"tags": tags}

    def reload_config(self):
        """Reload configuration from file"""
        self.config = self._load_config()
        self._compile_patterns()
        logger.info("Metadata configuration reloaded")

    def get_category_info(self, category_name: str) -> dict[str, Any] | None:
        """Get information about a specific category"""
        for category in self.config.get("categories", []):
            if category["name"] == category_name:
                return category
        return None

    def list_categories(self) -> list[dict[str, Any]]:
        """List all available categories"""
        return self.config.get("categories", [])


# Alias for backward compatibility
MetadataExtractor = ConfigDrivenMetadataExtractor
