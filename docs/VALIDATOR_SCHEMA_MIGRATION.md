# Validator Schema Migration Guide

This document tracks validator schema migrations and their impact.

## Schema Version History

### v1.1.0 (Current)
- **Date**: 2025-08-17
- **Status**: Active
- **Description**: Initial schema freeze for governance v1.0

## Migration Template

When changing the validator schema, update this document with:

### Schema Version: vX.Y.Z
- **Date**: YYYY-MM-DD
- **PR**: #XXX
- **Reason**: Brief description of why schema change is needed

### Compatibility Impact
- **Breaking Changes**: List any breaking changes
- **Deprecated Fields**: Fields that will be removed
- **New Fields**: New fields added to schema
- **Migration Path**: How to migrate from previous version

### Rollout Plan
- **Phase 1**: Description of rollout steps
- **Phase 2**: Additional rollout steps if needed
- **Timeline**: Expected completion date

### Rollback Plan
- **Trigger Conditions**: When to rollback
- **Rollback Steps**: How to revert to previous schema
- **Data Recovery**: How to recover any lost data

### Testing
- **Test Cases**: List of test scenarios
- **Validation**: How to validate the migration worked
- **Monitoring**: What to monitor during rollout

## Example Migration

### Schema Version: v1.2.0
- **Date**: 2025-09-01
- **PR**: #123
- **Reason**: Add support for new validator categories

### Compatibility Impact
- **Breaking Changes**: None
- **Deprecated Fields**: None
- **New Fields**: `categories.new_category`
- **Migration Path**: Backward compatible

### Rollout Plan
- **Phase 1**: Deploy new validator with v1.2.0 schema
- **Phase 2**: Update all CI workflows to use new schema
- **Timeline**: 1 week

### Rollback Plan
- **Trigger Conditions**: >5% false positives in new category
- **Rollback Steps**: Revert to v1.1.0 schema
- **Data Recovery**: No data loss expected

### Testing
- **Test Cases**: Validate new category detection works
- **Validation**: Check that existing categories still work
- **Monitoring**: Monitor false positive rate for new category
