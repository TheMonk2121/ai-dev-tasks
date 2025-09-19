# src/schemas/validation.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from src.schemas.settings import settings


class ValidationConfig(BaseModel):
    """Configuration for schema validation behavior."""

    strict_mode: bool = Field(default=True, description="Enable strict validation (fail on errors vs warnings)")
    allow_missing_files: bool = Field(default=False, description="Allow cases with missing target files")
    unknown_tag_warning: bool = Field(default=True, description="Show warnings for unknown tags")
    check_file_existence: bool = Field(default=True, description="Check if expected files actually exist")
    validate_mode_requirements: bool = Field(default=True, description="Validate mode-specific field requirements")
    deduplicate_tags: bool = Field(default=True, description="Remove duplicate tags automatically")
    normalize_field_names: bool = Field(default=True, description="Normalize legacy field names automatically")

    # Custom validation rules
    required_fields: set[str] = Field(
        default={"id", "mode", "query", "tags"}, description="Fields that must be present"
    )
    allowed_modes: set[str] = Field(default={"retrieval", "reader", "decision"}, description="Allowed evaluation modes")
    known_tags: set[str] = Field(default_factory=lambda: set(settings.known_tags), description="Known/valid tags")

    @model_validator(mode="after")
    def sync_with_settings(self) -> ValidationConfig:
        """Sync with global settings if not explicitly set."""
        # Only sync if values are still at defaults
        if self.allow_missing_files is False and settings.allow_missing_files:
            self.allow_missing_files: Any = settings.allow_missing_files
        if self.unknown_tag_warning is True and not settings.unknown_tag_warning:
            self.unknown_tag_warning: Any = settings.unknown_tag_warning
        if self.check_file_existence is True and not settings.check_file_existence:
            self.check_file_existence: Any = settings.check_file_existence
        if not self.known_tags or self.known_tags == set(settings.known_tags):
            self.known_tags: Any = set(settings.known_tags)
        return self

    def is_tag_known(self, tag: str) -> bool:
        """Check if a tag is known."""
        return tag.lower() in [t.lower() for t in self.known_tags]

    def get_unknown_tags(self, tags: list[str]) -> list[str]:
        """Get list of unknown tags."""
        return [tag for tag in tags if not self.is_tag_known(tag)]


class ValidationResult(BaseModel):
    """Result of validation operation."""

    is_valid: bool = Field(description="Whether validation passed")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    cases_processed: int = Field(default=0, description="Number of cases processed")
    cases_failed: int = Field(default=0, description="Number of cases that failed")
    duplicate_ids: list[str] = Field(default_factory=list, description="Duplicate case IDs found")
    missing_files: list[dict[str, Any]] = Field(default_factory=list, description="Cases with missing files")
    unknown_tags: dict[str, list[str]] = Field(default_factory=dict, description="Cases with unknown tags")

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid: Any = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_missing_file(self, case_id: str, file_path: str, file_type: str) -> None:
        """Add a missing file entry."""
        self.missing_files.append({"case_id": case_id, "file_path": file_path, "file_type": file_type})

    def add_unknown_tags(self, case_id: str, tags: list[str]) -> None:
        """Add unknown tags for a case."""
        self.unknown_tags[case_id] = tags

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        lines = [
            f"Validation {'PASSED' if self.is_valid else 'FAILED'}",
            f"Cases processed: {self.cases_processed}",
            f"Cases failed: {self.cases_failed}",
        ]

        if self.errors:
            lines.append(f"Errors: {len(self.errors)}")
        if self.warnings:
            lines.append(f"Warnings: {len(self.warnings)}")
        if self.duplicate_ids:
            lines.append(f"Duplicate IDs: {len(self.duplicate_ids)}")
        if self.missing_files:
            lines.append(f"Missing files: {len(self.missing_files)}")
        if self.unknown_tags:
            lines.append(f"Unknown tags: {len(self.unknown_tags)}")

        return "\n".join(lines)


# Default validation config
default_validation_config = ValidationConfig()
