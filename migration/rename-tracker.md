<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->

# Migration Tracker

Populated by script

## Recent Migrations

### File Naming Convention Migration (2024-08-06)
- **Status**: ✅ Completed
- **Changes**: Converted from two-digit to three-digit prefixes
- **Files Affected**: Core workflow files (00_ → 000_, etc.)
- **Documentation**: Updated all references throughout codebase

### Memory Scaffolding Guide Migration (2024-08-06)
- **Status**: ✅ Completed
- **Changes**: Created dedicated `401_memory-scaffolding-guide.md`
- **Priority**: HIGH
- **YAML Front-Matter**: Added with `context: HIGH`

### Cache-Augmented Generation Implementation (2024-08-06)
- **Status**: ✅ Completed
- **Changes**: Added B-032-C1 to backlog
- **Database**: Cache columns added to episodic_logs
- **Testing**: Prompt evaluation harness implemented

### File Cleanup and Archive Migration (2024-08-06)
- **Status**: ✅ Completed
- **Changes**: Removed duplicate files, archived implementation notes
- **Archived**: CAG implementation patches, migration summaries
- **Backups**: Moved backup directories to 600_archives/

## Pending Migrations

None currently planned.

## Migration Guidelines

1. **File Renames**: Use Git for tracking, not static tables
2. **Documentation**: Update all references when renaming
3. **Testing**: Verify functionality after migration
4. **Rollback**: Keep backups for critical changes 