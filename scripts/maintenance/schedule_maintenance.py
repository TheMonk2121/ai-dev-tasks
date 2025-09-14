from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

#!/usr/bin/env python3
"""
Maintenance Scheduler for AI Development Tasks

Schedules and manages automated maintenance tasks:
- Daily cleanup of temporary files
- Weekly cleanup of old logs and cache
- Monthly cleanup of monitoring data
- Database maintenance
"""

class MaintenanceScheduler:
    """Schedules and manages maintenance tasks"""

    def __init__(self, project_root: str | None = None):
        self.project_root = project_root or os.getcwd()
        self.script_path = os.path.join(self.project_root, "scripts", "maintenance_cleanup.py")

    def create_cron_jobs(self) -> str:
        """Create cron job entries for maintenance tasks"""
        cron_entries = [
            "# AI Development Tasks Maintenance Schedule",
            "# Daily cleanup at 2 AM",
            "0 2 * * * cd {project_root} && {python} {script} --temp-files --python-cache --verbose >> logs/maintenance_daily.log 2>&1",
            "",
            "# Weekly cleanup at 3 AM on Sundays",
            "0 3 * * 0 cd {project_root} && {python} {script} --logs --test-artifacts --hypothesis --verbose >> logs/maintenance_weekly.log 2>&1",
            "",
            "# Monthly cleanup at 4 AM on the 1st",
            "0 4 1 * * cd {project_root} && {python} {script} --monitoring --database --verbose >> logs/maintenance_monthly.log 2>&1",
            "",
            "# Full cleanup at 5 AM on the 1st of each quarter",
            "0 5 1 1,4,7,10 * cd {project_root} && {python} {script} --verbose >> logs/maintenance_quarterly.log 2>&1",
        ]

        python_cmd = "uv run python" if self._has_uv() else "python3"

        formatted_entries = []
        for entry in cron_entries:
            if entry.startswith("#") or entry == "":
                formatted_entries.append(entry)
            else:
                formatted_entries.append(
                    entry.format(project_root=self.project_root, python=python_cmd, script=self.script_path)
                )

        return "\n".join(formatted_entries)

    def _has_uv(self) -> bool:
        """Check if uv is available"""
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def install_cron_jobs(self, dry_run: bool = False) -> bool:
        """Install cron jobs for maintenance tasks"""
        cron_entries = self.create_cron_jobs()

        if dry_run:
            print("DRY RUN - Cron jobs that would be installed:")
            print(cron_entries)
            return True

        try:
            # Create logs directory if it doesn't exist
            logs_dir = os.path.join(self.project_root, "logs")
            os.makedirs(logs_dir, exist_ok=True)

            # Get current crontab
            try:
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                current_crontab = result.stdout
            except subprocess.CalledProcessError:
                current_crontab = ""

            # Check if our jobs are already installed
            if "AI Development Tasks Maintenance" in current_crontab:
                print("⚠️  Maintenance cron jobs already installed")
                return True

            # Add our jobs to crontab
            new_crontab = current_crontab + "\n" + cron_entries + "\n"

            # Install new crontab
            process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)

            if process.returncode == 0:
                print("✅ Maintenance cron jobs installed successfully")
                return True
            else:
                print("❌ Failed to install cron jobs")
                return False

        except Exception as e:
            print(f"❌ Error installing cron jobs: {e}")
            return False

    def remove_cron_jobs(self) -> bool:
        """Remove maintenance cron jobs"""
        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_crontab = result.stdout

            # Remove our maintenance jobs
            lines = current_crontab.split("\n")
            filtered_lines = []
            skip_next = False

            for line in lines:
                if "AI Development Tasks Maintenance" in line:
                    skip_next = True
                    continue
                elif skip_next and (line.startswith("#") or line.strip() == ""):
                    continue
                elif skip_next and not line.startswith("#"):
                    skip_next = False
                    filtered_lines.append(line)
                else:
                    filtered_lines.append(line)

            new_crontab = "\n".join(filtered_lines)

            # Install filtered crontab
            process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)

            if process.returncode == 0:
                print("✅ Maintenance cron jobs removed successfully")
                return True
            else:
                print("❌ Failed to remove cron jobs")
                return False

        except Exception as e:
            print(f"❌ Error removing cron jobs: {e}")
            return False

    def show_cron_jobs(self) -> bool:
        """Show current cron jobs"""
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                print("Current cron jobs:")
                print(result.stdout)
                return True
            else:
                print("No cron jobs found")
                return False
        except Exception as e:
            print(f"❌ Error showing cron jobs: {e}")
            return False

    def run_manual_maintenance(self, task: str = "full") -> bool:
        """Run maintenance task manually"""
        try:
            cmd = [sys.executable, self.script_path]

            if task == "daily":
                cmd.extend(["--temp-files", "--python-cache"])
            elif task == "weekly":
                cmd.extend(["--logs", "--test-artifacts", "--hypothesis"])
            elif task == "monthly":
                cmd.extend(["--monitoring", "--database"])
            elif task == "full":
                pass  # Run full cleanup
            else:
                print(f"❌ Unknown task: {task}")
                return False

            cmd.extend(["--verbose"])

            print(f"Running {task} maintenance...")
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running maintenance: {e}")
            return False

    def create_maintenance_script(self) -> str:
        """Create a standalone maintenance script"""
        script_content = f"""#!/bin/bash
# AI Development Tasks Maintenance Script
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PROJECT_ROOT="{self.project_root}"
SCRIPT_PATH="{self.script_path}"
LOG_DIR="$PROJECT_ROOT/logs"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Function to run maintenance with logging
run_maintenance() {{
    local task=$1
    local log_file="$LOG_DIR/maintenance_$task_$(date +%Y%m%d_%H%M%S).log"
    
    echo "Starting $task maintenance at $(date)" | tee -a "$log_file"
    
    cd "$PROJECT_ROOT"
    uv run python "$SCRIPT_PATH" --$task --verbose 2>&1 | tee -a "$log_file"
    
    echo "Completed $task maintenance at $(date)" | tee -a "$log_file"
}}

# Run maintenance based on argument
case "$1" in
    daily)
        run_maintenance "temp-files --python-cache"
        ;;
    weekly)
        run_maintenance "logs --test-artifacts --hypothesis"
        ;;
    monthly)
        run_maintenance "monitoring --database"
        ;;
    full)
        run_maintenance "verbose"
        ;;
    *)
        echo "Usage: $0 {{daily|weekly|monthly|full}}"
        exit 1
        ;;
esac
"""

        script_path = os.path.join(self.project_root, "scripts", "run_maintenance.sh")
        with open(script_path, "w") as f:
            f.write(script_content)

        # Make it executable
        os.chmod(script_path, 0o755)

        return script_path

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Development Tasks Maintenance Scheduler")
    parser.add_argument("--install", action="store_true", help="Install cron jobs")
    parser.add_argument("--remove", action="store_true", help="Remove cron jobs")
    parser.add_argument("--show", action="store_true", help="Show current cron jobs")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed without installing")
    parser.add_argument("--run", choices=["daily", "weekly", "monthly", "full"], help="Run maintenance task manually")
    parser.add_argument("--create-script", action="store_true", help="Create standalone maintenance script")
    parser.add_argument("--project-root", default=os.getcwd(), help="Project root directory")

    args = parser.parse_args()

    scheduler = MaintenanceScheduler(project_root=args.project_root)

    if args.install:
        scheduler.install_cron_jobs(dry_run=args.dry_run)
    elif args.remove:
        scheduler.remove_cron_jobs()
    elif args.show:
        scheduler.show_cron_jobs()
    elif args.run:
        scheduler.run_manual_maintenance(args.run)
    elif args.create_script:
        script_path = scheduler.create_maintenance_script()
        print(f"✅ Created maintenance script: {script_path}")
    else:
        # Show available cron jobs
        print("Maintenance cron jobs that would be installed:")
        print(scheduler.create_cron_jobs())
        print("\nUse --install to install them or --dry-run to see what would be installed")

if __name__ == "__main__":
    main()