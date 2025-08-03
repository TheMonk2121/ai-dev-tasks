# 📁 File Naming Conventions

This document explains the naming conventions used in the AI Dev Tasks project to help you understand the file organization and add new files consistently.

## 🎯 **Naming Pattern: `[Number]_[Description].md`**

### **Number Prefixes:**

#### **`00-09` - Core Workflow Files**
Essential files that form the main development workflow:
- **`00_backlog.md`** - Product backlog with scoring system
- **`01_create-prd.md`** - PRD creation guidelines
- **`02_generate-tasks.md`** - Task generation from PRDs
- **`03_process-task-list.md`** - AI task execution

#### **`100-199` - Automation & Tools**
Advanced features and automation systems:
- **`100_backlog-automation.md`** - AI-BACKLOG-META system
- **`101_n8n-setup.md`** - n8n workflow configuration (future)
- **`102_ai-agent-config.md`** - AI agent configuration (future)
- **`103_yi-coder-integration.md`** - Yi-Coder-9B-Chat-Q6_K IDE integration (future)

#### **`200-299` - Configuration & Setup**
Configuration files and setup guides:
- **`200_naming-conventions.md`** - This file
- **`201_model-configuration.md`** - AI model configuration and setup
- **`202_environment-setup.md`** - Development environment setup (future)
- **`203_deployment-guide.md`** - Production deployment (future)

#### **`300-399` - Templates & Examples**
Reusable templates and example files:
- **`300_prd-template.md`** - Standard PRD template (future)
- **`301_task-template.md`** - Standard task template (future)
- **`302_example-prd.md`** - Example PRD (future)

#### **`400-499` - Documentation & Guides**
Comprehensive documentation and guides:
- **`400_troubleshooting.md`** - Common issues and solutions (future)
- **`401_best-practices.md`** - Development best practices (future)
- **`402_migration-guide.md`** - System migration guides (future)

## 🚀 **Adding New Files**

### **When Adding Core Workflow Files:**
- Use `04_`, `05_`, etc. for additional workflow steps
- Keep them essential and widely used
- Examples: `04_deploy-feature.md`, `05_test-feature.md`

### **When Adding Automation Tools:**
- Use `101_`, `102_`, etc. for automation features
- Focus on AI integration and automation
- Examples: `101_github-integration.md`, `102_slack-notifications.md`

### **When Adding Configuration:**
- Use `201_`, `202_`, etc. for setup and configuration
- Include step-by-step instructions
- Examples: `201_database-setup.md`, `202_ssl-config.md`

### **When Adding Templates:**
- Use `301_`, `302_`, etc. for reusable templates
- Make them copy-paste friendly
- Examples: `301_api-prd-template.md`, `302_microservice-template.md`

### **When Adding Documentation:**
- Use `401_`, `402_`, etc. for comprehensive guides
- Focus on user education and troubleshooting
- Examples: `401_performance-tuning.md`, `402_security-hardening.md`

## 📋 **File Naming Rules**

### **Format:**
```
[Number]_[kebab-case-description].md
```

### **Examples:**
- ✅ `100_backlog-automation.md`
- ✅ `201_environment-setup.md`
- ✅ `301_api-prd-template.md`
- ❌ `100_backlog_automation.md` (use hyphens, not underscores)
- ❌ `100-backlog-automation.md` (include underscore after number)

### **Description Guidelines:**
- **Use kebab-case**: lowercase with hyphens
- **Be descriptive**: clearly indicate the file's purpose
- **Keep it concise**: 2-4 words maximum
- **Use nouns**: focus on what the file contains

## 🎯 **Category Guidelines**

### **Core Workflow (00-09):**
- Essential for every development project
- Used in the main workflow sequence
- Should be referenced in README.md
- Examples: backlog, PRD creation, task generation, execution

### **Automation & Tools (100-199):**
- Advanced features that enhance the workflow
- Optional but powerful additions
- Focus on AI integration and automation
- Examples: n8n workflows, AI agent configuration, integrations

### **Configuration & Setup (200-299):**
- Setup instructions and configuration guides
- One-time setup or maintenance tasks
- Include step-by-step instructions
- Examples: environment setup, deployment, configuration, model setup

### **Templates & Examples (300-399):**
- Reusable templates and example files
- Copy-paste friendly content
- Show best practices and patterns
- Examples: PRD templates, task templates, example projects

### **Documentation & Guides (400-499):**
- Comprehensive documentation and troubleshooting
- User education and problem-solving
- Include troubleshooting and best practices
- Examples: troubleshooting guides, best practices, migration guides

## 🔄 **Migration Strategy**

### **When Renaming Existing Files:**
1. **Update all references** in other files
2. **Update README.md** file list
3. **Update SYSTEM_OVERVIEW.md** if applicable
4. **Test the workflow** to ensure nothing breaks

### **When Adding New Categories:**
1. **Update this file** with the new category
2. **Add examples** of what belongs in the category
3. **Update README.md** if the category is user-facing
4. **Consider adding** a category-specific guide

## 📊 **File Organization Benefits**

### **For Users:**
- **Quick Recognition**: Know what type of file by the number
- **Logical Grouping**: Related files are numbered together
- **Easy Navigation**: Find files by category
- **Clear Purpose**: File names indicate their role

### **For Contributors:**
- **Consistent Structure**: Clear rules for adding files
- **Scalable Organization**: Room for growth in each category
- **Maintainable**: Easy to understand and update
- **Professional**: Organized and professional appearance

### **For AI Agents:**
- **Predictable Patterns**: Can understand file organization
- **Category Awareness**: Know what type of content to expect
- **Workflow Integration**: Understand file relationships
- **Automation Friendly**: Easy to parse and categorize

## 🎯 **Current Project Structure**

### **Core Workflow (00-09):**
- `00_backlog.md` - Product backlog with AI scoring system
- `01_create-prd.md` - PRD creation guidelines
- `02_generate-tasks.md` - Task generation from PRDs
- `03_process-task-list.md` - AI task execution

### **Automation & Tools (100-199):**
- `100_backlog-automation.md` - AI-BACKLOG-META system

### **Configuration & Setup (200-299):**
- `200_naming-conventions.md` - This file
- `201_model-configuration.md` - AI model configuration and setup

### **System Documentation:**
- `README.md` - Comprehensive workflow guide
- `SYSTEM_OVERVIEW.md` - Technical system overview

### **Subsystems:**
- `dashboard/` - Real-time monitoring dashboard
- `dspy-rag-system/` - Document processing and RAG system

---

*This naming convention ensures the AI Dev Tasks project remains organized, scalable, and user-friendly as it grows.* 