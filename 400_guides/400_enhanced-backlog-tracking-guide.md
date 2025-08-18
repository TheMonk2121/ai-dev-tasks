# Enhanced Backlog Tracking Guide

<!-- CONTEXT_REFERENCE: 000_core/000_backlog.md -->

<!-- MODULE_REFERENCE: scripts/enhanced_backlog_tracking.py -->

<!-- MEMORY_CONTEXT: HIGH - Enhanced backlog tracking system guide -->

<!-- DATABASE_SYNC: REQUIRED -->

## 🔎 TL;DR

| what this file is | read when | do next |
|----|----|----|
| Comprehensive guide for enhanced backlog status tracking with timestamps | When you need to track work progress or identify stale items | Use the CLI commands to start work, update status, and check for stale items |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Enhanced backlog tracking system
  operational

- **Priority**: 🔧 Medium - Useful for workflow management

- **Points**: 2 - Low complexity, workflow enhancement

- **Dependencies**: 000_core/000_backlog.md,
  scripts/enhanced_backlog_tracking.py

- **Next Steps**: Integrate with governance system and CI/CD pipeline

## 🚀 Quick Start

### **Start Work on an Item**

``` bash
python3 scripts/enhanced_backlog_tracking.py --start-work B‑052‑d
```

### **Update Item Status**

``` bash
python3 scripts/enhanced_backlog_tracking.py --update-status B‑052‑d in-progress
```

### **Check for Stale Items**

``` bash
# Check for items in-progress > 7 days (default)
python3 scripts/enhanced_backlog_tracking.py --check-stale

# Check for items in-progress > 3 days
python3 scripts/enhanced_backlog_tracking.py --check-stale --stale-days 3
```

### **List All In-Progress Items**

``` bash
python3 scripts/enhanced_backlog_tracking.py --list-in-progress
```

### **Get Item Summary**

``` bash
python3 scripts/enhanced_backlog_tracking.py --item-summary B‑052‑d
```

## 🎯 What This System Provides

### **Enhanced Status Tracking**

- **`started_at` timestamps** - Track when work began on items
- **`last_updated` timestamps** - Track when items were last modified
- **Stale item detection** - Flag items in-progress too long
  (configurable threshold)
- **Automated alerts** - CLI commands to check for stale items
- **Item summaries** - Detailed tracking information for any item

### **Status Values Supported**

- `todo` - Not started
- `in-progress` - Currently being worked on
- `✅ done` - Completed
- `blocked` - Cannot start due to dependencies

### **Timestamp Format**

Timestamps are stored in ISO format: `YYYY-MM-DDTHH:MM:SS.microseconds`
Example: `2025-08-16T08:40:01.163126`

## 📋 Usage Examples

### **Starting Work on a New Item**

``` bash
# Start work on a backlog item
python3 scripts/enhanced_backlog_tracking.py --start-work B‑052‑d

# Output:
# ✅ Started work on B‑052‑d: CI GitHub Action (Dry-Run Gate)
#    Started at: 2025-08-16T08:40:01.163126
```

### **Updating Item Status**

``` bash
# Update status to in-progress
python3 scripts/enhanced_backlog_tracking.py --update-status B‑052‑d in-progress

# Update status to done
python3 scripts/enhanced_backlog_tracking.py --update-status B‑052‑d "✅ done"

# Output:
# ✅ Updated B‑052‑d status to 'in-progress'
#    Updated at: 2025-08-16T08:41:45.155925
```

### **Checking for Stale Items**

``` bash
# Check for items in-progress > 7 days
python3 scripts/enhanced_backlog_tracking.py --check-stale

# Check for items in-progress > 3 days
python3 scripts/enhanced_backlog_tracking.py --check-stale --stale-days 3

# Output:
# ⚠️  Found 2 stale items (in-progress > 7 days):
#    B‑052‑d: CI GitHub Action (Dry-Run Gate) (12 days in progress)
#    B‑062: Context Priority Guide Auto-Generation (8 days in progress)
```

### **Listing In-Progress Items**

``` bash
python3 scripts/enhanced_backlog_tracking.py --list-in-progress

# Output:
# 🔄 2 items currently in progress:
#    B‑052‑d: CI GitHub Action (Dry-Run Gate) (12 days) ⚠️
#    B‑062: Context Priority Guide Auto-Generation (8 days) ⚠️
```

### **Getting Item Summary**

``` bash
python3 scripts/enhanced_backlog_tracking.py --item-summary B‑052‑d

# Output:
# 📋 B‑052‑d: CI GitHub Action (Dry-Run Gate)
#    Status: in-progress
#    Started: 2025-08-04T14:30:00.123456
#    Days in progress: 12
#    Last updated: 2025-08-15T09:15:00.789012
#    ⚠️  STALE - Needs attention!
```

## 🔧 Integration with Workflows

### **Daily Standup**

``` bash
# Check what's currently in progress
python3 scripts/enhanced_backlog_tracking.py --list-in-progress

# Check for stale items that need attention
python3 scripts/enhanced_backlog_tracking.py --check-stale --stale-days 3
```

### **Starting New Work**

``` bash
# When beginning work on a new item
python3 scripts/enhanced_backlog_tracking.py --start-work B‑052‑d
```

### **Updating Progress**

``` bash
# When making progress or completing work
python3 scripts/enhanced_backlog_tracking.py --update-status B‑052‑d in-progress
python3 scripts/enhanced_backlog_tracking.py --update-status B‑052‑d "✅ done"
```

### **Weekly Review**

``` bash
# Check for items that have been in-progress too long
python3 scripts/enhanced_backlog_tracking.py --check-stale --stale-days 7
```

## 🚨 Troubleshooting

### **Common Issues**

1.  **“Item not found”**
    - Check that the backlog ID uses en dash (`B‑052‑d`) not hyphen
      (`B-052-d`)
    - Verify the item exists in `000_core/000_backlog.md`
2.  **“No items currently in progress”**
    - This is normal if no items are marked as `in-progress`
    - Use `--start-work` to begin tracking an item
3.  **Timestamps not showing**
    - Ensure the item has been started with `--start-work`
    - Check that the backlog file has the timestamp comments

### **Getting Help**

``` bash
# Show all available commands
python3 scripts/enhanced_backlog_tracking.py --help
```

## 📊 Benefits

### **Prevents Lost Work**

- Never forget about items you started
- Clear visibility into work status
- Automatic stale item detection

### **Identifies Blockers**

- Stale items often indicate blockers
- Helps identify items needing attention
- Enables proactive problem resolution

### **Improves Planning**

- Track actual time vs estimated time
- Better understanding of work patterns
- Data-driven decision making

### **Enables Accountability**

- Clear visibility into work status
- Timestamp history for audit trails
- Automated alerts for stale items

## 🔗 Related Files

- **`000_core/000_backlog.md`**: Main backlog file with status tracking
- **`scripts/enhanced_backlog_tracking.py`**: Core tracking system
- **`400_guides/400_task-generation-quick-reference.md`**: Task
  generation automation
- **`000_core/002_generate-tasks.md`**: Task generation workflow

## 📈 Future Enhancements

### **Potential Improvements**

- **Automated alerts**: Email/Slack notifications for stale items
- **Integration with CI/CD**: Automatic status updates from build
  systems
- **Dashboard integration**: Visual status tracking in mission dashboard
- **Time tracking**: Integration with time tracking systems
- **Reporting**: Generate reports on work patterns and bottlenecks

### **Configuration Options**

- **Custom stale thresholds**: Per-item or per-priority stale thresholds
- **Notification preferences**: Customize alert frequency and channels
- **Export capabilities**: Export tracking data for analysis
- **Integration APIs**: REST API for external system integration

------------------------------------------------------------------------

**Last Updated**: 2025-08-16 **Status**: ✅ **ACTIVE** - Fully
implemented and tested **Implementation**:
`scripts/enhanced_backlog_tracking.py`

<!-- README_AUTOFIX_START -->

## Auto-generated sections for 400_enhanced-backlog-tracking-guide.md

## Generated: 2025-08-18T08:03:22.742575

## Missing sections to add:

## Owner

Documentation Team

## Purpose

Describe the purpose and scope of this document

## Usage

Describe how to use this document or system

<!-- README_AUTOFIX_END -->
