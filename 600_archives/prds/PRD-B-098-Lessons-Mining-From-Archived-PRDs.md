# PRD: B-098 - Mine Archived PRDs for Lessons and Reference Cards

## Overview

Extract systematic lessons and cross-references from archived PRDs (600_archives/) to feed into lessons_applied, reference_cards, and backlog hygiene.

## Problem Statement

Archived PRDs contain valuable lessons learned and reference information that could improve future development efforts, but this knowledge is not systematically extracted and applied to new work.

## Success Criteria

- Lessons from archived PRDs are systematically extracted
- Reference cards are created from archived PRD patterns
- Backlog items are updated with lessons_applied and reference_cards metadata
- Knowledge from past work is leveraged in new development

## Technical Requirements

### FR-1.0 PRD Analysis Engine
- Parse archived PRD files in 600_archives/prds/
- Extract lessons learned, patterns, and reference information
- Identify reusable components and approaches

### FR-2.0 Lessons Extraction
- Extract lessons_applied metadata from archived PRDs
- Categorize lessons by type (technical, process, architectural)
- Create structured lessons database

### FR-3.0 Reference Card Generation
- Generate reference cards from archived PRD patterns
- Create cross-references between related PRDs
- Maintain reference card index

### FR-4.0 Backlog Integration
- Update backlog items with lessons_applied metadata
- Link backlog items to relevant reference cards
- Maintain backlog hygiene with extracted knowledge

## Non-Functional Requirements

### NFR-1.0 Performance
- Process all archived PRDs within 5 minutes
- Maintain searchable index of extracted knowledge

### NFR-2.0 Maintainability
- Automated extraction process
- Clear documentation of extraction rules
- Version control for extracted knowledge

## Dependencies

- 600_archives/prds/ directory structure
- Existing backlog metadata format
- Lessons learned documentation structure

## Acceptance Criteria

- All archived PRDs are processed and analyzed
- Lessons are extracted and categorized
- Reference cards are generated and indexed
- Backlog items are updated with relevant metadata
- Knowledge extraction process is documented and automated
