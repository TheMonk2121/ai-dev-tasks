"""
README governance constants - single source of truth for validator and autofix.
"""

# Required sections and their synonyms
REQUIRED_SECTIONS = {
    "purpose": ["purpose", "overview", "description", "what is", "about"],
    "usage": ["usage", "how to use", "getting started", "quick start", "examples"],
    "owner": ["owner", "maintainer", "contact", "responsible"],
    "last_reviewed": ["last reviewed", "last updated", "reviewed", "updated"],
}

# Section headers that should be preserved (not replaced)
PRESERVED_HEADERS = {
    "purpose": ["# ", "## ", "### "],
    "usage": ["# ", "## ", "### "],
    "owner": ["## ", "### "],
    "last_reviewed": ["## ", "### "],
}

# Default section templates
SECTION_TEMPLATES = {
    "purpose": "## Purpose\n\n[Describe the purpose and scope of this document]",
    "usage": "## Usage\n\n[Describe how to use this document or system]",
    "owner": "## Owner\n\n[Document owner/maintainer information]",
    "last_reviewed": "## Last Reviewed\n\n[Date when this document was last reviewed]",
}

# Marker patterns for autofix
AUTOFIX_MARKER_START = "<!-- README_AUTOFIX_START -->"
AUTOFIX_MARKER_END = "<!-- README_AUTOFIX_END -->"

# Scope configuration
README_SCOPE_DIRS = ["400_guides/", "000_core/", "100_memory/", "200_setup/", "300_examples/", "500_reference-cards.md"]

README_IGNORE_SEGMENTS = ["node_modules", "vendor", "600_archives", ".git", "__pycache__", ".pytest_cache"]

# Owner inference patterns (exact prefix matches)
OWNER_PATTERNS = {
    "400_guides/": "Documentation Team",
    "000_core/": "Core Team",
    "100_memory/": "Memory Team",
    "200_setup/": "DevOps Team",
    "300_examples/": "Examples Team",
    "500_reference-cards.md": "Reference Team",
}
