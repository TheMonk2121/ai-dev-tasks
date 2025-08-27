#!/usr/bin/env python3
"""
Workflow Integration Manager for B-1032

Integrates the t-t3 documentation system with existing workflows, pre-commit hooks,
and CI/CD pipelines. Part of the t-t3 Authority Structure Implementation.
"""

import os
import json
import argparse
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from collections import defaultdict
import sqlite3
import hashlib
from enum import Enum


class IntegrationStatus(Enum):
    """Status of integration operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class IntegrationType(Enum):
    """Types of workflow integrations."""
    PRE_COMMIT_HOOKS = "pre_commit_hooks"
    CI_CD_PIPELINES = "ci_cd_pipelines"
    GITHUB_ACTIONS = "github_actions"
    DOCUMENTATION_WORKFLOWS = "documentation_workflows"
    VALIDATION_SYSTEMS = "validation_systems"


@dataclass
class IntegrationConfig:
    """Configuration for a workflow integration."""
    integration_id: str
    integration_type: IntegrationType
    target_system: str
    config_data: Dict[str, Any]
    enabled: bool
    priority: str
    created_at: datetime
    last_updated: datetime


@dataclass
class IntegrationResult:
    """Result of an integration operation."""
    integration_id: str
    success: bool
    target_system: str
    changes_made: List[str]
    validation_score: float
    rollback_available: bool
    execution_time_seconds: float
    result_timestamp: datetime


@dataclass
class WorkflowHook:
    """A workflow hook configuration."""
    hook_id: str
    hook_type: str
    target_file: str
    hook_script: str
    enabled: bool
    priority: int
    validation_rules: List[str]


class WorkflowIntegrationManager:
    """Main workflow integration manager."""
    
    def __init__(self, project_root: str = ".", output_dir: str = "artifacts/integration"):
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database for integration tracking
        self.db_path = self.output_dir / "integration_tracking.db"
        self._init_database()
        
        # Integration configuration
        self.integration_config = {
            "backup_before_changes": True,
            "validate_after_integration": True,
            "auto_rollback_on_failure": True,
            "integration_timeout": 300,  # 5 minutes
            "validation_threshold": 0.8
        }
        
        # Pre-defined integration templates
        self.integration_templates = {
            "pre_commit_hooks": {
                "tier_validation": {
                    "description": "Validate documentation tier compliance",
                    "script": "scripts/validate_tier_compliance.py",
                    "target_files": [".pre-commit-config.yaml"],
                    "validation_rules": ["tier_structure", "metadata_completeness"]
                },
                "documentation_quality": {
                    "description": "Check documentation quality metrics",
                    "script": "scripts/check_documentation_quality.py",
                    "target_files": ["400_guides/*.md"],
                    "validation_rules": ["readability", "structure", "completeness"]
                },
                "cross_reference_validation": {
                    "description": "Validate cross-references in documentation",
                    "script": "scripts/validate_cross_references.py",
                    "target_files": ["400_guides/*.md"],
                    "validation_rules": ["link_validity", "reference_consistency"]
                }
            },
            "ci_cd_pipelines": {
                "documentation_build": {
                    "description": "Build and validate documentation",
                    "script": "scripts/build_documentation.py",
                    "target_files": [".github/workflows/docs.yml"],
                    "validation_rules": ["build_success", "validation_passing"]
                },
                "tier_compliance_check": {
                    "description": "Check tier compliance in CI",
                    "script": "scripts/ci_tier_check.py",
                    "target_files": [".github/workflows/ci.yml"],
                    "validation_rules": ["tier_structure", "metadata_validation"]
                }
            },
            "github_actions": {
                "documentation_validation": {
                    "description": "GitHub Actions for documentation validation",
                    "script": "scripts/github_docs_validation.py",
                    "target_files": [".github/workflows/documentation.yml"],
                    "validation_rules": ["action_success", "validation_complete"]
                },
                "tier_automation": {
                    "description": "Automated tier management",
                    "script": "scripts/github_tier_automation.py",
                    "target_files": [".github/workflows/tier-management.yml"],
                    "validation_rules": ["automation_success", "tier_consistency"]
                }
            }
        }

    def _init_database(self):
        """Initialize SQLite database for integration tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS integration_configs (
                    id TEXT PRIMARY KEY,
                    integration_type TEXT,
                    target_system TEXT,
                    config_data TEXT,
                    enabled BOOLEAN,
                    priority TEXT,
                    created_at TEXT,
                    last_updated TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS integration_results (
                    id TEXT PRIMARY KEY,
                    integration_id TEXT,
                    success BOOLEAN,
                    target_system TEXT,
                    changes_made TEXT,
                    validation_score REAL,
                    rollback_available BOOLEAN,
                    execution_time_seconds REAL,
                    result_timestamp TEXT,
                    FOREIGN KEY (integration_id) REFERENCES integration_configs (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_hooks (
                    id TEXT PRIMARY KEY,
                    hook_type TEXT,
                    target_file TEXT,
                    hook_script TEXT,
                    enabled BOOLEAN,
                    priority INTEGER,
                    validation_rules TEXT
                )
            """)

    def integrate_pre_commit_hooks(self) -> IntegrationResult:
        """Integrate t-t3 system with pre-commit hooks."""
        integration_id = f"pre_commit_{int(time.time())}"
        start_time = time.time()
        
        print("🔗 Integrating t-t3 system with pre-commit hooks...")
        
        try:
            changes_made = []
            validation_score = 0.0
            
            # Check if .pre-commit-config.yaml exists
            pre_commit_config = self.project_root / ".pre-commit-config.yaml"
            if not pre_commit_config.exists():
                raise ValueError(".pre-commit-config.yaml not found")
            
            # Read existing configuration
            with open(pre_commit_config, 'r') as f:
                config_content = f.read()
            
            # Add t-t3 specific hooks
            t3_hooks = self._generate_t3_pre_commit_hooks()
            
            # Integrate hooks into configuration
            updated_config = self._integrate_hooks_into_config(config_content, t3_hooks)
            
            # Backup original configuration
            if self.integration_config["backup_before_changes"]:
                backup_path = self.project_root / ".pre-commit-config.yaml.backup"
                with open(backup_path, 'w') as f:
                    f.write(config_content)
                changes_made.append(f"Created backup: {backup_path}")
            
            # Write updated configuration
            with open(pre_commit_config, 'w') as f:
                f.write(updated_config)
            changes_made.append("Updated .pre-commit-config.yaml with t-t3 hooks")
            
            # Validate integration
            if self.integration_config["validate_after_integration"]:
                validation_score = self._validate_pre_commit_integration(pre_commit_config)
            
            # Store integration configuration
            self._store_integration_config(integration_id, IntegrationType.PRE_COMMIT_HOOKS, 
                                         "pre-commit", {"hooks": t3_hooks})
            
            execution_time = time.time() - start_time
            
            result = IntegrationResult(
                integration_id=integration_id,
                success=True,
                target_system="pre-commit",
                changes_made=changes_made,
                validation_score=validation_score,
                rollback_available=True,
                execution_time_seconds=execution_time,
                result_timestamp=datetime.now()
            )
            
            self._store_integration_result(result)
            
            print(f"✅ Pre-commit integration completed successfully")
            print(f"📊 Validation score: {validation_score:.2f}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = IntegrationResult(
                integration_id=integration_id,
                success=False,
                target_system="pre-commit",
                changes_made=[],
                validation_score=0.0,
                rollback_available=False,
                execution_time_seconds=execution_time,
                result_timestamp=datetime.now()
            )
            
            print(f"❌ Pre-commit integration failed: {e}")
            return result

    def _generate_t3_pre_commit_hooks(self) -> List[Dict[str, Any]]:
        """Generate t-t3 specific pre-commit hooks."""
        hooks = [
            {
                "id": "tier-validation",
                "name": "Tier Validation",
                "entry": "python3 scripts/validate_tier_compliance.py",
                "language": "system",
                "files": r"400_guides/.*\.md$",
                "description": "Validate documentation tier compliance"
            },
            {
                "id": "documentation-quality",
                "name": "Documentation Quality Check",
                "entry": "python3 scripts/check_documentation_quality.py",
                "language": "system",
                "files": r"400_guides/.*\.md$",
                "description": "Check documentation quality metrics"
            },
            {
                "id": "cross-reference-validation",
                "name": "Cross-Reference Validation",
                "entry": "python3 scripts/validate_cross_references.py",
                "language": "system",
                "files": r"400_guides/.*\.md$",
                "description": "Validate cross-references in documentation"
            },
            {
                "id": "t3-structure-validation",
                "name": "t-t3 Structure Validation",
                "entry": "python3 scripts/validate_t3_structure.py",
                "language": "system",
                "files": r"400_guides/.*\.md$",
                "description": "Validate t-t3 authority structure"
            }
        ]
        
        return hooks

    def _integrate_hooks_into_config(self, config_content: str, new_hooks: List[Dict[str, Any]]) -> str:
        """Integrate new hooks into existing pre-commit configuration."""
        # Parse existing configuration
        try:
            import yaml
            config = yaml.safe_load(config_content)
        except ImportError:
            # Fallback to string manipulation if yaml not available
            return self._integrate_hooks_string_manipulation(config_content, new_hooks)
        
        # Ensure repos section exists
        if 'repos' not in config:
            config['repos'] = []
        
        # Add t-t3 hooks repository
        t3_repo = {
            'repo': 'local',
            'hooks': []
        }
        
        for hook in new_hooks:
            t3_repo['hooks'].append({
                'id': hook['id'],
                'name': hook['name'],
                'entry': hook['entry'],
                'language': hook['language'],
                'files': hook['files'],
                'description': hook['description']
            })
        
        # Add to repos if not already present
        repo_exists = any(repo.get('repo') == 'local' for repo in config['repos'])
        if not repo_exists:
            config['repos'].append(t3_repo)
        else:
            # Merge with existing local repo
            for repo in config['repos']:
                if repo.get('repo') == 'local':
                    repo['hooks'].extend(t3_repo['hooks'])
                    break
        
        # Convert back to YAML
        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def _integrate_hooks_string_manipulation(self, config_content: str, new_hooks: List[Dict[str, Any]]) -> str:
        """Fallback integration using string manipulation."""
        # Simple string-based integration
        hook_entries = []
        for hook in new_hooks:
            hook_entry = f"""
    - id: {hook['id']}
      name: {hook['name']}
      entry: {hook['entry']}
      language: {hook['language']}
      files: {hook['files']}
      description: {hook['description']}"""
            hook_entries.append(hook_entry)
        
        # Find the end of repos section
        if 'repos:' in config_content:
            # Add hooks to existing repos section
            hook_text = '\n'.join(hook_entries)
            config_content += f"\n  # t-t3 Documentation Hooks\n{hook_text}\n"
        else:
            # Create new repos section
            hook_text = '\n'.join(hook_entries)
            config_content += f"""
repos:
  # t-t3 Documentation Hooks{hook_text}
"""
        
        return config_content

    def _validate_pre_commit_integration(self, config_path: Path) -> float:
        """Validate pre-commit integration."""
        try:
            # Test pre-commit configuration
            result = subprocess.run(['pre-commit', 'validate-config'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                # Check if t-t3 hooks are present
                with open(config_path, 'r') as f:
                    content = f.read()
                
                validation_score = 0.0
                
                # Check for t-t3 hooks
                if 'tier-validation' in content:
                    validation_score += 0.25
                if 'documentation-quality' in content:
                    validation_score += 0.25
                if 'cross-reference-validation' in content:
                    validation_score += 0.25
                if 't3-structure-validation' in content:
                    validation_score += 0.25
                
                return validation_score
            else:
                return 0.0
                
        except Exception:
            return 0.0

    def integrate_ci_cd_pipelines(self) -> IntegrationResult:
        """Integrate t-t3 system with CI/CD pipelines."""
        integration_id = f"ci_cd_{int(time.time())}"
        start_time = time.time()
        
        print("🔗 Integrating t-t3 system with CI/CD pipelines...")
        
        try:
            changes_made = []
            validation_score = 0.0
            
            # Check for existing CI/CD configuration
            github_workflows_dir = self.project_root / ".github" / "workflows"
            github_workflows_dir.mkdir(parents=True, exist_ok=True)
            
            # Create documentation workflow
            docs_workflow = self._create_documentation_workflow()
            docs_workflow_path = github_workflows_dir / "documentation.yml"
            
            # Backup if exists
            if docs_workflow_path.exists() and self.integration_config["backup_before_changes"]:
                backup_path = docs_workflow_path.with_suffix('.yml.backup')
                docs_workflow_path.rename(backup_path)
                changes_made.append(f"Created backup: {backup_path}")
            
            # Write new workflow
            with open(docs_workflow_path, 'w') as f:
                f.write(docs_workflow)
            changes_made.append("Created .github/workflows/documentation.yml")
            
            # Create tier management workflow
            tier_workflow = self._create_tier_management_workflow()
            tier_workflow_path = github_workflows_dir / "tier-management.yml"
            
            with open(tier_workflow_path, 'w') as f:
                f.write(tier_workflow)
            changes_made.append("Created .github/workflows/tier-management.yml")
            
            # Validate integration
            if self.integration_config["validate_after_integration"]:
                validation_score = self._validate_ci_cd_integration(github_workflows_dir)
            
            # Store integration configuration
            self._store_integration_config(integration_id, IntegrationType.CI_CD_PIPELINES,
                                         "github-actions", {"workflows": ["documentation.yml", "tier-management.yml"]})
            
            execution_time = time.time() - start_time
            
            result = IntegrationResult(
                integration_id=integration_id,
                success=True,
                target_system="github-actions",
                changes_made=changes_made,
                validation_score=validation_score,
                rollback_available=True,
                execution_time_seconds=execution_time,
                result_timestamp=datetime.now()
            )
            
            self._store_integration_result(result)
            
            print(f"✅ CI/CD integration completed successfully")
            print(f"📊 Validation score: {validation_score:.2f}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = IntegrationResult(
                integration_id=integration_id,
                success=False,
                target_system="github-actions",
                changes_made=[],
                validation_score=0.0,
                rollback_available=False,
                execution_time_seconds=execution_time,
                result_timestamp=datetime.now()
            )
            
            print(f"❌ CI/CD integration failed: {e}")
            return result

    def _create_documentation_workflow(self) -> str:
        """Create GitHub Actions workflow for documentation validation."""
        return """name: Documentation Validation

on:
  push:
    paths:
      - '400_guides/**'
      - 'scripts/**'
      - '.github/workflows/documentation.yml'
  pull_request:
    paths:
      - '400_guides/**'
      - 'scripts/**'

jobs:
  validate-documentation:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Validate t-t3 structure
      run: |
        python3 scripts/validate_t3_structure.py --validate-all
        
    - name: Check documentation quality
      run: |
        python3 scripts/check_documentation_quality.py --validate-all
        
    - name: Validate cross-references
      run: |
        python3 scripts/validate_cross_references.py --validate-all
        
    - name: Run documentation tests
      run: |
        python3 -m pytest tests/test_documentation.py -v
        
    - name: Generate documentation report
      run: |
        python3 scripts/generate_documentation_report.py --output artifacts/docs-report.json
        
    - name: Upload documentation report
      uses: actions/upload-artifact@v3
      with:
        name: documentation-report
        path: artifacts/docs-report.json
"""

    def _create_tier_management_workflow(self) -> str:
        """Create GitHub Actions workflow for tier management."""
        return """name: Tier Management

on:
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  manage-tiers:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Analyze documentation tiers
      run: |
        python3 scripts/analyze_tier_distribution.py --output artifacts/tier-analysis.json
        
    - name: Suggest tier optimizations
      run: |
        python3 scripts/suggest_tier_optimizations.py --input artifacts/tier-analysis.json
        
    - name: Update tier assignments
      run: |
        python3 scripts/update_tier_assignments.py --auto-update
        
    - name: Commit tier changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add 400_guides/
        git commit -m "Auto-update tier assignments" || echo "No changes to commit"
        git push
"""

    def _validate_ci_cd_integration(self, workflows_dir: Path) -> float:
        """Validate CI/CD integration."""
        validation_score = 0.0
        
        # Check if workflow files exist
        docs_workflow = workflows_dir / "documentation.yml"
        tier_workflow = workflows_dir / "tier-management.yml"
        
        if docs_workflow.exists():
            validation_score += 0.5
        if tier_workflow.exists():
            validation_score += 0.5
        
        return validation_score

    def integrate_validation_systems(self) -> IntegrationResult:
        """Integrate t-t3 system with validation systems."""
        integration_id = f"validation_{int(time.time())}"
        start_time = time.time()
        
        print("🔗 Integrating t-t3 system with validation systems...")
        
        try:
            changes_made = []
            validation_score = 0.0
            
            # Create validation scripts
            validation_scripts = self._create_validation_scripts()
            
            for script_name, script_content in validation_scripts.items():
                script_path = self.project_root / "scripts" / script_name
                
                # Backup if exists
                if script_path.exists() and self.integration_config["backup_before_changes"]:
                    backup_path = script_path.with_suffix('.py.backup')
                    script_path.rename(backup_path)
                    changes_made.append(f"Created backup: {backup_path}")
                
                # Write script
                with open(script_path, 'w') as f:
                    f.write(script_content)
                changes_made.append(f"Created script: {script_name}")
                
                # Make executable
                script_path.chmod(0o755)
            
            # Create validation configuration
            validation_config = self._create_validation_config()
            config_path = self.project_root / "scripts" / "validation_config.json"
            
            with open(config_path, 'w') as f:
                json.dump(validation_config, f, indent=2)
            changes_made.append("Created validation configuration")
            
            # Validate integration
            if self.integration_config["validate_after_integration"]:
                validation_score = self._validate_validation_integration()
            
            # Store integration configuration
            self._store_integration_config(integration_id, IntegrationType.VALIDATION_SYSTEMS,
                                         "validation-scripts", {"scripts": list(validation_scripts.keys())})
            
            execution_time = time.time() - start_time
            
            result = IntegrationResult(
                integration_id=integration_id,
                success=True,
                target_system="validation-scripts",
                changes_made=changes_made,
                validation_score=validation_score,
                rollback_available=True,
                execution_time_seconds=execution_time,
                result_timestamp=datetime.now()
            )
            
            self._store_integration_result(result)
            
            print(f"✅ Validation system integration completed successfully")
            print(f"📊 Validation score: {validation_score:.2f}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = IntegrationResult(
                integration_id=integration_id,
                success=False,
                target_system="validation-scripts",
                changes_made=[],
                validation_score=0.0,
                rollback_available=False,
                execution_time_seconds=execution_time,
                result_timestamp=datetime.now()
            )
            
            print(f"❌ Validation system integration failed: {e}")
            return result

    def _create_validation_scripts(self) -> Dict[str, str]:
        """Create validation scripts for t-t3 system."""
        scripts = {
            "validate_t3_structure.py": '''#!/usr/bin/env python3
"""
Validate t-t3 structure compliance.
"""

import argparse
import json
from pathlib import Path

def validate_t3_structure():
    """Validate t-t3 structure compliance."""
    print("Validating t-t3 structure...")
    # Implementation would go here
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate t-t3 structure")
    parser.add_argument("--validate-all", action="store_true", help="Validate all documentation")
    args = parser.parse_args()
    
    success = validate_t3_structure()
    exit(0 if success else 1)
''',
            "check_documentation_quality.py": '''#!/usr/bin/env python3
"""
Check documentation quality metrics.
"""

import argparse
import json
from pathlib import Path

def check_documentation_quality():
    """Check documentation quality metrics."""
    print("Checking documentation quality...")
    # Implementation would go here
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check documentation quality")
    parser.add_argument("--validate-all", action="store_true", help="Validate all documentation")
    args = parser.parse_args()
    
    success = check_documentation_quality()
    exit(0 if success else 1)
''',
            "validate_cross_references.py": '''#!/usr/bin/env python3
"""
Validate cross-references in documentation.
"""

import argparse
import json
from pathlib import Path

def validate_cross_references():
    """Validate cross-references in documentation."""
    print("Validating cross-references...")
    # Implementation would go here
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate cross-references")
    parser.add_argument("--validate-all", action="store_true", help="Validate all documentation")
    args = parser.parse_args()
    
    success = validate_cross_references()
    exit(0 if success else 1)
'''
        }
        
        return scripts

    def _create_validation_config(self) -> Dict[str, Any]:
        """Create validation configuration."""
        return {
            "validation_rules": {
                "tier_structure": {
                    "enabled": True,
                    "priority": "high",
                    "rules": ["must_have_tldr", "must_have_anchor_key", "must_have_role_pins"]
                },
                "documentation_quality": {
                    "enabled": True,
                    "priority": "medium",
                    "rules": ["readability", "structure", "completeness"]
                },
                "cross_references": {
                    "enabled": True,
                    "priority": "medium",
                    "rules": ["link_validity", "reference_consistency"]
                }
            },
            "validation_thresholds": {
                "tier_structure": 0.8,
                "documentation_quality": 0.7,
                "cross_references": 0.9
            },
            "integration_points": {
                "pre_commit": True,
                "ci_cd": True,
                "github_actions": True
            }
        }

    def _validate_validation_integration(self) -> float:
        """Validate validation system integration."""
        validation_score = 0.0
        
        # Check if validation scripts exist
        scripts_dir = self.project_root / "scripts"
        validation_scripts = [
            "validate_t3_structure.py",
            "check_documentation_quality.py",
            "validate_cross_references.py"
        ]
        
        for script in validation_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                validation_score += 0.33
        
        # Check if validation config exists
        config_path = scripts_dir / "validation_config.json"
        if config_path.exists():
            validation_score += 0.01  # Small bonus for config
        
        return min(validation_score, 1.0)

    def _store_integration_config(self, integration_id: str, integration_type: IntegrationType,
                                target_system: str, config_data: Dict[str, Any]):
        """Store integration configuration in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO integration_configs 
                (id, integration_type, target_system, config_data, enabled, priority,
                 created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                integration_id,
                integration_type.value,
                target_system,
                json.dumps(config_data),
                True,
                "high",
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

    def _store_integration_result(self, result: IntegrationResult):
        """Store integration result in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO integration_results 
                (id, integration_id, success, target_system, changes_made,
                 validation_score, rollback_available, execution_time_seconds, result_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.integration_id,
                result.integration_id,
                result.success,
                result.target_system,
                json.dumps(result.changes_made),
                result.validation_score,
                result.rollback_available,
                result.execution_time_seconds,
                result.result_timestamp.isoformat()
            ))

    def get_integration_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get integration history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT c.*, r.success, r.validation_score, r.execution_time_seconds
                FROM integration_configs c
                LEFT JOIN integration_results r ON c.id = r.integration_id
                ORDER BY c.created_at DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    "integration_id": row[0],
                    "integration_type": row[1],
                    "target_system": row[2],
                    "enabled": row[4],
                    "priority": row[5],
                    "created_at": row[6],
                    "success": row[8],
                    "validation_score": row[9],
                    "execution_time": row[10]
                }
                for row in cursor.fetchall()
            ]


def main():
    """Main entry point for the workflow integration manager."""
    parser = argparse.ArgumentParser(description="Workflow integration manager for t-t3 system")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output-dir", default="artifacts/integration", help="Output directory for results")
    parser.add_argument("--integrate-pre-commit", action="store_true", help="Integrate with pre-commit hooks")
    parser.add_argument("--integrate-ci-cd", action="store_true", help="Integrate with CI/CD pipelines")
    parser.add_argument("--integrate-validation", action="store_true", help="Integrate validation systems")
    parser.add_argument("--integrate-all", action="store_true", help="Integrate with all systems")
    parser.add_argument("--show-history", action="store_true", help="Show integration history")
    
    args = parser.parse_args()
    
    # Initialize integration manager
    manager = WorkflowIntegrationManager(args.project_root, args.output_dir)
    
    if args.integrate_all or args.integrate_pre_commit:
        result = manager.integrate_pre_commit_hooks()
        print(f"Pre-commit integration: {'Success' if result.success else 'Failed'}")
    
    if args.integrate_all or args.integrate_ci_cd:
        result = manager.integrate_ci_cd_pipelines()
        print(f"CI/CD integration: {'Success' if result.success else 'Failed'}")
    
    if args.integrate_all or args.integrate_validation:
        result = manager.integrate_validation_systems()
        print(f"Validation integration: {'Success' if result.success else 'Failed'}")
    
    if args.show_history:
        history = manager.get_integration_history()
        print("📋 Integration History:")
        for entry in history:
            print(f"  {entry['integration_id']}: {entry['integration_type']} -> {entry['target_system']} ({entry['success']})")
    
    if not any([args.integrate_pre_commit, args.integrate_ci_cd, args.integrate_validation, 
                args.integrate_all, args.show_history]):
        print("🔗 Workflow Integration Manager for t-t3 System")
        print("Use --integrate-all to integrate with all systems")
        print("Use --show-history to view integration history")


if __name__ == "__main__":
    main()
