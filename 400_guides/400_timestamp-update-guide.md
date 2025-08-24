# Timestamp Update Guide

## Quick Reference for Backlog Updates

### When to Update Timestamps
- ✅ When completing a backlog item
- ✅ When adding new items to the backlog
- ✅ When changing priorities or scores
- ✅ When updating implementation notes
- ✅ When modifying dependencies

### How to Update Timestamps

#### Current Format
```markdown
*Previously Updated: 2024-08-05 23:58*
*Last Updated: 2025-08-24 23:59*
```

#### Update Process
1. **Move current Last Updated to Previously Updated**
2. **Update Last Updated with current timestamp**
3. **Use 24-hour format (HH:MM)**
4. **Include time for granular tracking**

#### Example Update
**Before:**
```markdown
*Last Updated: 2025-08-24 23:59*
```

**After:**
```markdown
*Previously Updated: 2024-08-05 23:59*
*Last Updated: 2025-08-24 23:60*
```

### AI-BACKLOG-META Instructions
The backlog includes automated instructions for timestamp updates:

```yaml
timestamp_updates: |
  Update *Last Updated: YYYY-MM-DD HH:MM* timestamp when making changes
  Add *Previously Updated: YYYY-MM-DD HH:MM* line above Last Updated for history
  Use 24-hour format (HH:MM) for granular tracking
```

### Integration Points
- **Task Processing**: Update timestamps when completing tasks
- **Backlog Automation**: Include timestamp updates in automated workflows
- **Documentation**: Reference this guide in all backlog-related docs

### Benefits
- **History Tracking**: See when changes were made
- **Granular Tracking**: Time-based change tracking
- **Audit Trail**: Clear record of backlog modifications
- **Context Preservation**: Maintains change history for future reference

---

**Note**: This guide ensures consistent timestamp updates across all backlog modifications, even when working outside the main context window. 