# Results Management & Future Evaluations

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete guide for managing evaluation results and planning future evaluations | You need to add new evaluations, analyze results, or manage result storage | Follow the workflow for your specific task (add evaluation, analyze trends, archive old results) |

## 🎯 Purpose

Provide comprehensive guidance for managing RAGChecker evaluation results, adding new evaluations, analyzing performance trends, and maintaining a clean results archive. This guide covers the complete lifecycle from running evaluations to long-term result management.

## 📋 When to Use This Guide

- **Adding New Evaluations**: When you need to run new RAGChecker evaluations
- **Results Analysis**: When analyzing performance trends or comparing baselines
- **Storage Management**: When organizing or archiving old results
- **Quality Assurance**: When validating evaluation results and file integrity
- **Future Planning**: When setting up automated evaluation workflows

## 🎯 Expected Outcomes

After following this guide, you will be able to:
- **Organize Results**: Properly store and organize evaluation results
- **Add Evaluations**: Run new evaluations with proper file naming and storage
- **Analyze Trends**: Compare results over time and identify improvements
- **Manage Storage**: Archive old results and maintain clean directories
- **Ensure Quality**: Validate results and maintain data integrity

## 📋 Policies

### Results Management
- **File Naming**: Use consistent timestamp-based naming conventions
- **Storage Organization**: Maintain clear directory structure with active and archived results
- **Retention Policy**: Keep active results for 30 days, archive older files
- **Quality Validation**: Validate all results before considering them complete

### Evaluation Workflow
- **Standard Process**: Follow established workflow for all evaluations
- **Documentation**: Update status files and documentation with new results
- **Comparison**: Always compare new results against established baselines
- **Cost Tracking**: Monitor and track costs for cloud-based evaluations

## 📁 File Organization & Storage

### **Results Directory Structure**
```
metrics/
├── baseline_evaluations/
│   ├── ragchecker_official_evaluation_YYYYMMDD_HHMMSS.json  # Evaluation results
│   ├── ragchecker_official_input_YYYYMMDD_HHMMSS.json       # Input test data
│   ├── EVALUATION_STATUS.md                                 # Current status summary
│   └── [historical evaluation files...]                     # Previous runs
├── cost_reports/
│   ├── bedrock_usage_YYYYMMDD.json                          # Daily cost tracking
│   └── cost_summary_YYYYMM.json                             # Monthly summaries
├── archives/
│   ├── evaluations/                                         # Archived evaluation results
│   └── cost_reports/                                        # Archived cost data
└── [other metric files...]
```

### **File Naming Conventions**
- **Evaluation Results**: `ragchecker_official_evaluation_YYYYMMDD_HHMMSS.json`
- **Input Data**: `ragchecker_official_input_YYYYMMDD_HHMMSS.json`
- **Cost Reports**: `bedrock_usage_YYYYMMDD.json`
- **Status Files**: `EVALUATION_STATUS.md` (always current)

### **File Types and Purposes**
- **Evaluation Results**: Complete evaluation metrics and case-by-case results
- **Input Data**: Test cases, queries, and ground truth data used for evaluation
- **Cost Reports**: AWS Bedrock usage tracking and cost analysis
- **Status Files**: Current evaluation status and summary information

## 🔄 Adding New Evaluations

### **Standard Evaluation Workflow**

#### **Step 1: Run Official RAGChecker Evaluation**
```bash
# Basic evaluation
python3 scripts/ragchecker_official_evaluation.py

# With specific options
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --fast-mode
```

#### **Step 2: Verify New Files Created**
```bash
# Check for new evaluation files
ls -la metrics/baseline_evaluations/ragchecker_official_*.json | tail -5

# Verify file timestamps match current time
ls -la metrics/baseline_evaluations/ragchecker_official_evaluation_$(date +%Y%m%d)_*.json
```

#### **Step 3: Check Evaluation Status**
```bash
# View current status
cat metrics/baseline_evaluations/EVALUATION_STATUS.md

# Check for any errors or warnings
grep -i "error\|warning" metrics/baseline_evaluations/EVALUATION_STATUS.md
```

#### **Step 4: View Latest Results**
```bash
# Extract overall metrics
jq '.overall_metrics' metrics/baseline_evaluations/ragchecker_official_evaluation_$(date +%Y%m%d)_*.json

# View case-by-case results
jq '.case_results[] | {query_id, precision, recall, f1_score}' metrics/baseline_evaluations/ragchecker_official_evaluation_$(date +%Y%m%d)_*.json
```

### **Bedrock-Specific Evaluation**

#### **AWS Bedrock Integration**
```bash
# Run with AWS Bedrock (faster, more reliable)
python3 scripts/ragchecker_official_evaluation.py --use-bedrock

# Run with cost monitoring
python3 scripts/ragchecker_with_monitoring.py

# Run batch evaluation (fastest)
python3 scripts/ragchecker_batch_evaluation.py --concurrent 3 --optimize
```

#### **Cost Monitoring**
```bash
# Check current usage
python3 scripts/bedrock_cost_monitor.py --period today

# View budget status
python3 scripts/bedrock_cost_monitor.py --alerts

# Generate cost report
python3 scripts/bedrock_cost_monitor.py --export json --period month
```

### **Custom Evaluation Scenarios**

#### **Single Test Case Evaluation**
```bash
# Test specific query
python3 scripts/ragchecker_single_test.py --query "What is the current project status?"

# Test with custom parameters
python3 scripts/ragchecker_single_test.py --query "your query" --use-bedrock --max-words 1000
```

#### **Fast Mode Evaluation**
```bash
# Skip expensive LLM calls for quick testing
export RAGCHECKER_FAST_MODE=1
python3 scripts/ragchecker_official_evaluation.py

# Use for development and testing
export RAGCHECKER_MAX_TEST_CASES=3
python3 scripts/ragchecker_official_evaluation.py
```

#### **Custom Test Cases**
```bash
# Use custom test case file
python3 scripts/ragchecker_official_evaluation.py --test-cases custom_test_cases.json

# Create custom test cases
python3 scripts/create_custom_test_cases.py --domain "your-domain" --output custom_test_cases.json
```

## 📊 Results Analysis & Comparison

### **Performance Trend Analysis**

#### **Compare Recent Evaluations**
```bash
# List recent evaluation files
ls -la metrics/baseline_evaluations/ragchecker_official_evaluation_*.json | tail -10

# Extract F1 scores over time
for file in metrics/baseline_evaluations/ragchecker_official_evaluation_*.json; do
    echo "$(basename $file): $(jq -r '.overall_metrics.f1_score' $file)"
done | sort

# Generate performance summary
python3 scripts/evaluation_analysis.py --period 7d --metric f1_score
```

#### **Performance Visualization**
```bash
# Generate trend charts
python3 scripts/plot_evaluation_trends.py --period 30d --metrics precision,recall,f1_score

# Create performance dashboard
python3 scripts/create_performance_dashboard.py --output performance_dashboard.html
```

### **Baseline Comparison**

#### **Compare Against Established Baseline**
```bash
# Compare with specific baseline
python3 scripts/baseline_comparison.py --baseline 20250830_141742 --current latest

# Generate improvement report
python3 scripts/improvement_report.py --baseline-week 2025-08-23 --current-week 2025-08-30

# Calculate improvement percentages
python3 scripts/calculate_improvements.py --baseline-file baseline.json --current-file current.json
```

#### **Statistical Analysis**
```bash
# Perform statistical significance testing
python3 scripts/statistical_analysis.py --baseline baseline.json --current current.json

# Generate confidence intervals
python3 scripts/confidence_intervals.py --evaluations "*.json" --confidence 0.95
```

### **Cost Analysis**

#### **Cost Trends and Monitoring**
```bash
# View cost trends
python3 scripts/bedrock_cost_monitor.py --period week --trend

# Generate cost report
python3 scripts/bedrock_cost_monitor.py --export json --period month

# Compare cost vs performance
python3 scripts/cost_performance_analysis.py --period 30d
```

#### **Budget Management**
```bash
# Check budget status
python3 scripts/bedrock_cost_monitor.py --alerts

# Set budget alerts
python3 scripts/set_budget_alerts.py --daily-limit 5.00 --weekly-limit 25.00

# Generate cost optimization recommendations
python3 scripts/cost_optimization_recommendations.py --analysis-period 7d
```

## 🗄️ Results Retention & Archival

### **Retention Policy**

#### **Active Results Management**
- **Active Results**: Keep last 30 days in `metrics/baseline_evaluations/`
- **Archive**: Move older files to `metrics/archives/evaluations/`
- **Status File**: Always maintain current `EVALUATION_STATUS.md`
- **Cost Data**: Keep 12 months of cost reports
- **Input Data**: Archive after 90 days (keep for reproducibility)

#### **Archive Organization**
```
metrics/archives/
├── evaluations/
│   ├── 2025-08/                                             # Monthly archives
│   ├── 2025-07/
│   └── [older months...]
├── cost_reports/
│   ├── 2025-08/
│   └── [older months...]
└── summary_reports/
    ├── monthly_summaries/
    └── quarterly_reports/
```

### **Automated Cleanup**

#### **Archive Old Evaluation Files**
```bash
# Archive files older than 30 days
python3 scripts/archive_old_evaluations.py --days 30

# Clean up old cost reports (older than 12 months)
python3 scripts/archive_old_cost_reports.py --months 12

# Generate archival report
python3 scripts/archival_report.py --period month
```

#### **Automated Maintenance**
```bash
# Set up automated cleanup (cron job)
python3 scripts/setup_automated_cleanup.py --schedule daily

# Monitor archive size and cleanup if needed
python3 scripts/monitor_archive_size.py --max-size 10GB --cleanup
```

### **Manual Archival Process**

#### **Step-by-Step Manual Archival**
```bash
# 1. Create archive directory (if needed)
mkdir -p metrics/archives/evaluations/$(date +%Y-%m)

# 2. Move old files
mv metrics/baseline_evaluations/ragchecker_official_evaluation_2025*.json metrics/archives/evaluations/$(date +%Y-%m)/

# 3. Update status file
python3 scripts/update_evaluation_status.py --archive-complete

# 4. Generate archive summary
python3 scripts/generate_archive_summary.py --archive-dir metrics/archives/evaluations/$(date +%Y-%m)
```

#### **Archive Validation**
```bash
# Validate archived files
python3 scripts/validate_archived_files.py --archive-dir metrics/archives/evaluations/2025-08

# Check archive integrity
python3 scripts/check_archive_integrity.py --archive-dir metrics/archives/
```

## ✅ Quality Assurance & Validation

### **Results Validation Checklist**

#### **File Integrity Checks**
- [ ] **JSON Validity**: All JSON files are valid and parseable
- [ ] **Metric Completeness**: All required metrics present (precision, recall, F1)
- [ ] **Timestamp Accuracy**: File timestamps match evaluation timestamps
- [ ] **Input-Output Correlation**: Input and output files correspond correctly
- [ ] **Status File Updated**: `EVALUATION_STATUS.md` reflects current state

#### **Data Quality Validation**
- [ ] **Metric Ranges**: All metrics are within expected ranges (0-1 for percentages)
- [ ] **Consistency**: Metrics are internally consistent (F1 = 2*(P*R)/(P+R))
- [ ] **Completeness**: All test cases have corresponding results
- [ ] **Uniqueness**: No duplicate evaluation files for same timestamp

### **Validation Commands**

#### **Automated Validation**
```bash
# Validate all evaluation files
python3 scripts/validate_evaluation_files.py

# Check for missing metrics
python3 scripts/check_metric_completeness.py

# Verify file correlations
python3 scripts/verify_input_output_correlation.py
```

#### **Manual Validation**
```bash
# Check JSON syntax
jq '.' metrics/baseline_evaluations/ragchecker_official_evaluation_*.json > /dev/null

# Verify metric calculations
python3 scripts/verify_metric_calculations.py --evaluation-file latest.json

# Check for anomalies
python3 scripts/detect_anomalies.py --evaluation-file latest.json --threshold 0.1
```

## 🔮 Future Evaluation Planning

### **Scheduled Evaluations**

#### **Evaluation Schedule**
- **Daily**: Automated baseline evaluation (if changes detected)
- **Weekly**: Comprehensive performance review
- **Monthly**: Full system evaluation with all test cases
- **Quarterly**: Deep analysis and trend reporting

#### **Automated Triggers**
```bash
# Monitor for evaluation opportunities
python3 scripts/evaluation_monitor.py --watch-changes

# Auto-trigger evaluations on significant changes
python3 scripts/auto_evaluation_trigger.py --threshold 0.05

# Generate evaluation recommendations
python3 scripts/evaluation_recommendations.py --analysis-period 7d
```

### **Evaluation Triggers**

#### **Code Change Triggers**
- **RAG System Modifications**: Changes to retrieval or generation logic
- **Model Updates**: LLM or embedding model changes
- **Configuration Changes**: Parameter tuning or optimization changes
- **Feature Additions**: New RAG capabilities or integrations

#### **Performance Triggers**
- **Metric Degradation**: Significant drop in precision, recall, or F1
- **Cost Increases**: Unexpected cost spikes or budget overruns
- **Error Rate Increases**: Higher failure rates or timeout issues
- **User Feedback**: Reports of degraded performance or quality

### **Continuous Improvement**

#### **Performance Monitoring**
```bash
# Set up continuous monitoring
python3 scripts/setup_continuous_monitoring.py --metrics precision,recall,f1_score

# Configure alerts for performance degradation
python3 scripts/configure_performance_alerts.py --threshold 0.1 --window 24h

# Generate improvement recommendations
python3 scripts/generate_improvement_recommendations.py --analysis-period 30d
```

#### **Optimization Workflow**
```bash
# Identify optimization opportunities
python3 scripts/identify_optimization_opportunities.py --evaluation-file latest.json

# Generate optimization experiments
python3 scripts/generate_optimization_experiments.py --target-metric f1_score

# Track optimization progress
python3 scripts/track_optimization_progress.py --experiment-id exp_001
```

## 🔧 How-To

### **Quick Start for New Evaluations**
1. **Choose Evaluation Type**: Standard, Bedrock, or custom
2. **Run Evaluation**: Use appropriate script with desired parameters
3. **Verify Results**: Check file creation and basic metrics
4. **Update Status**: Ensure status files reflect current state
5. **Archive Old**: Move old files to archive if needed

### **Results Analysis Workflow**
1. **Gather Data**: Collect relevant evaluation files
2. **Compare Baselines**: Compare against established baselines
3. **Identify Trends**: Look for patterns and improvements
4. **Generate Reports**: Create summary reports and visualizations
5. **Plan Actions**: Identify next steps based on analysis

### **Storage Management**
1. **Assess Current State**: Review current file organization
2. **Plan Archive**: Identify files ready for archival
3. **Execute Archive**: Move files to appropriate archive locations
4. **Update Documentation**: Update status files and documentation
5. **Validate Archive**: Ensure archived files are accessible and valid

## 📋 Checklists

### **New Evaluation Checklist**
- [ ] **Environment Ready**: Virtual environment activated, dependencies installed
- [ ] **Parameters Set**: Evaluation parameters configured correctly
- [ ] **Execution Complete**: Evaluation script completed successfully
- [ ] **Files Created**: New evaluation files present in correct location
- [ ] **Results Valid**: Results pass validation checks
- [ ] **Status Updated**: Status files reflect new evaluation
- [ ] **Documentation Updated**: Any relevant documentation updated

### **Results Analysis Checklist**
- [ ] **Data Collected**: All relevant evaluation files gathered
- [ ] **Baseline Identified**: Appropriate baseline for comparison selected
- [ ] **Metrics Calculated**: All relevant metrics computed
- [ ] **Trends Identified**: Performance trends and patterns identified
- [ ] **Report Generated**: Analysis report created and documented
- [ ] **Actions Planned**: Next steps based on analysis identified

### **Archive Management Checklist**
- [ ] **Files Identified**: Files ready for archival identified
- [ ] **Archive Created**: Archive directory structure created
- [ ] **Files Moved**: Files moved to appropriate archive locations
- [ ] **Integrity Verified**: Archived files validated and accessible
- [ ] **Status Updated**: Status files updated to reflect archival
- [ ] **Documentation Updated**: Archive documentation updated

## 🔗 Interfaces

### **Scripts and Tools**
- **Evaluation Scripts**: `scripts/ragchecker_official_evaluation.py`, `scripts/ragchecker_single_test.py`
- **Analysis Tools**: `scripts/evaluation_analysis.py`, `scripts/baseline_comparison.py`
- **Archive Tools**: `scripts/archive_old_evaluations.py`, `scripts/validate_archived_files.py`
- **Monitoring Tools**: `scripts/evaluation_monitor.py`, `scripts/auto_evaluation_trigger.py`

### **File Formats**
- **JSON Results**: Standardized evaluation result format
- **Markdown Status**: Human-readable status and summary files
- **CSV Reports**: Tabular data for analysis and visualization
- **HTML Dashboards**: Interactive performance dashboards

### **Integration Points**
- **RAGChecker Framework**: Official evaluation framework integration
- **AWS Bedrock**: Cloud-based evaluation integration
- **Cost Monitoring**: Usage tracking and budget management
- **CI/CD Pipeline**: Automated evaluation integration

## 📚 Examples

### **Complete Evaluation Workflow Example**
```bash
# 1. Run evaluation
python3 scripts/ragchecker_official_evaluation.py --use-bedrock

# 2. Verify results
ls -la metrics/baseline_evaluations/ragchecker_official_evaluation_$(date +%Y%m%d)_*.json

# 3. Check metrics
jq '.overall_metrics' metrics/baseline_evaluations/ragchecker_official_evaluation_$(date +%Y%m%d)_*.json

# 4. Compare with baseline
python3 scripts/baseline_comparison.py --baseline 20250830_141742 --current latest

# 5. Archive old files
python3 scripts/archive_old_evaluations.py --days 30
```

### **Results Analysis Example**
```bash
# Generate trend analysis
python3 scripts/evaluation_analysis.py --period 7d --metric f1_score

# Create performance dashboard
python3 scripts/create_performance_dashboard.py --output dashboard.html

# Generate improvement report
python3 scripts/improvement_report.py --baseline-week 2025-08-23 --current-week 2025-08-30
```

## 📚 References

- **RAGChecker Framework**: Official RAGChecker documentation and methodology
- **AWS Bedrock**: AWS Bedrock service documentation and pricing
- **Evaluation Scripts**: `scripts/` directory for all evaluation tools
- **Metrics Directory**: `metrics/` directory for all results and reports
- **Related Guides**:
  - `400_07_ai-frameworks-dspy.md` - DSPy framework and RAG system
  - `400_04_development-workflow-and-standards.md` - Development workflow
  - `400_05_coding-and-prompting-standards.md` - Testing and quality standards

## 📋 Changelog

- **2025-08-30**: Created as comprehensive results management guide
- **2025-08-30**: Added file organization, evaluation workflows, and analysis procedures
- **2025-08-30**: Included retention policy, archival procedures, and quality assurance
- **2025-08-30**: Added future planning and continuous improvement workflows
