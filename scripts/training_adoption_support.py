#!/usr/bin/env python3
"""
Training and Adoption Support System for B-1032

Provides user training, onboarding, and adoption tracking for the t-t3 system.
Part of the t-t3 Authority Structure Implementation.
"""

import argparse
import json
import logging
import sqlite3
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional


class TrainingType(Enum):
    """Types of training."""

    ONBOARDING = "onboarding"
    FEATURE_TRAINING = "feature_training"
    ADVANCED_TRAINING = "advanced_training"
    REFRESHER = "refresher"
    CUSTOM = "custom"


class AdoptionStage(Enum):
    """Stages of user adoption."""

    AWARENESS = "awareness"
    INTEREST = "interest"
    EVALUATION = "evaluation"
    TRIAL = "trial"
    ADOPTION = "adoption"
    ADVOCACY = "advocacy"


class SupportType(Enum):
    """Types of support."""

    DOCUMENTATION = "documentation"
    VIDEO_TUTORIAL = "video_tutorial"
    INTERACTIVE_GUIDE = "interactive_guide"
    WORKSHOP = "workshop"
    ONE_ON_ONE = "one_on_one"
    FAQ = "faq"


@dataclass
class TrainingModule:
    """A training module."""

    module_id: str
    title: str
    description: str
    training_type: TrainingType
    content: str
    duration_minutes: int
    difficulty_level: str
    prerequisites: List[str]
    learning_objectives: List[str]
    created_at: datetime


@dataclass
class UserProgress:
    """User training progress."""

    user_id: str
    module_id: str
    progress_percentage: float
    completed: bool
    start_date: datetime
    completion_date: Optional[datetime]
    time_spent_minutes: int
    quiz_score: Optional[float]


@dataclass
class AdoptionMetrics:
    """Adoption metrics for a user."""

    user_id: str
    current_stage: AdoptionStage
    stage_start_date: datetime
    feature_usage_count: Dict[str, int]
    session_duration_minutes: int
    last_active_date: datetime
    satisfaction_score: Optional[float]
    feedback_count: int


@dataclass
class SupportResource:
    """A support resource."""

    resource_id: str
    title: str
    description: str
    support_type: SupportType
    content: str
    url: Optional[str]
    tags: List[str]
    target_audience: str
    created_at: datetime


@dataclass
class TrainingProgram:
    """A training program."""

    program_id: str
    name: str
    description: str
    modules: List[str]
    target_audience: str
    estimated_duration_hours: float
    prerequisites: List[str]
    learning_outcomes: List[str]
    created_at: datetime


class TrainingAdoptionSupport:
    """Main training and adoption support system."""

    def __init__(self, project_root: str = ".", output_dir: str = "artifacts/training"):
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database for training tracking
        self.db_path = self.output_dir / "training_tracking.db"
        self._init_database()

        # Training configuration
        self.training_config = {
            "auto_track_progress": True,
            "enable_quizzes": True,
            "certification_enabled": True,
            "support_portal_enabled": True,
            "support_portal_port": 8081,
            "default_training_duration": 30,
            "progress_threshold": 80.0,
        }

        # Support portal server
        self.support_server = None
        self.support_active = False

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(self.output_dir / "training.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def _init_database(self):
        """Initialize SQLite database for training tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS training_modules (
                    id TEXT PRIMARY KEY,
                    module_id TEXT,
                    title TEXT,
                    description TEXT,
                    training_type TEXT,
                    content TEXT,
                    duration_minutes INTEGER,
                    difficulty_level TEXT,
                    prerequisites TEXT,
                    learning_objectives TEXT,
                    created_at TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_progress (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    module_id TEXT,
                    progress_percentage REAL,
                    completed BOOLEAN,
                    start_date TEXT,
                    completion_date TEXT,
                    time_spent_minutes INTEGER,
                    quiz_score REAL
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS adoption_metrics (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    current_stage TEXT,
                    stage_start_date TEXT,
                    feature_usage_count TEXT,
                    session_duration_minutes INTEGER,
                    last_active_date TEXT,
                    satisfaction_score REAL,
                    feedback_count INTEGER
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS support_resources (
                    id TEXT PRIMARY KEY,
                    resource_id TEXT,
                    title TEXT,
                    description TEXT,
                    support_type TEXT,
                    content TEXT,
                    url TEXT,
                    tags TEXT,
                    target_audience TEXT,
                    created_at TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS training_programs (
                    id TEXT PRIMARY KEY,
                    program_id TEXT,
                    name TEXT,
                    description TEXT,
                    modules TEXT,
                    target_audience TEXT,
                    estimated_duration_hours REAL,
                    prerequisites TEXT,
                    learning_outcomes TEXT,
                    created_at TEXT
                )
            """
            )

    def create_training_module(
        self,
        title: str,
        description: str,
        training_type: TrainingType,
        content: str,
        duration_minutes: int,
        difficulty_level: str,
        prerequisites: List[str],
        learning_objectives: List[str],
    ) -> TrainingModule:
        """Create a training module."""
        module_id = f"module_{int(time.time())}"

        self.logger.info(f"📚 Creating training module: {title}")

        module = TrainingModule(
            module_id=module_id,
            title=title,
            description=description,
            training_type=training_type,
            content=content,
            duration_minutes=duration_minutes,
            difficulty_level=difficulty_level,
            prerequisites=prerequisites,
            learning_objectives=learning_objectives,
            created_at=datetime.now(),
        )

        # Store module in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO training_modules
                (id, module_id, title, description, training_type, content,
                 duration_minutes, difficulty_level, prerequisites, learning_objectives, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    module_id,
                    module.module_id,
                    module.title,
                    module.description,
                    module.training_type.value,
                    module.content,
                    module.duration_minutes,
                    module.difficulty_level,
                    json.dumps(module.prerequisites),
                    json.dumps(module.learning_objectives),
                    module.created_at.isoformat(),
                ),
            )

        # Save module to file
        self._save_training_module(module)

        self.logger.info(f"✅ Training module created: {module_id}")
        return module

    def create_training_program(
        self,
        name: str,
        description: str,
        modules: List[str],
        target_audience: str,
        estimated_duration_hours: float,
        prerequisites: List[str],
        learning_outcomes: List[str],
    ) -> TrainingProgram:
        """Create a training program."""
        program_id = f"program_{int(time.time())}"

        self.logger.info(f"🎓 Creating training program: {name}")

        program = TrainingProgram(
            program_id=program_id,
            name=name,
            description=description,
            modules=modules,
            target_audience=target_audience,
            estimated_duration_hours=estimated_duration_hours,
            prerequisites=prerequisites,
            learning_outcomes=learning_outcomes,
            created_at=datetime.now(),
        )

        # Store program in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO training_programs
                (id, program_id, name, description, modules, target_audience,
                 estimated_duration_hours, prerequisites, learning_outcomes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    program_id,
                    program.program_id,
                    program.name,
                    program.description,
                    json.dumps(program.modules),
                    program.target_audience,
                    program.estimated_duration_hours,
                    json.dumps(program.prerequisites),
                    json.dumps(program.learning_outcomes),
                    program.created_at.isoformat(),
                ),
            )

        self.logger.info(f"✅ Training program created: {program_id}")
        return program

    def create_support_resource(
        self,
        title: str,
        description: str,
        support_type: SupportType,
        content: str,
        url: Optional[str],
        tags: List[str],
        target_audience: str,
    ) -> SupportResource:
        """Create a support resource."""
        resource_id = f"resource_{int(time.time())}"

        self.logger.info(f"📖 Creating support resource: {title}")

        resource = SupportResource(
            resource_id=resource_id,
            title=title,
            description=description,
            support_type=support_type,
            content=content,
            url=url,
            tags=tags,
            target_audience=target_audience,
            created_at=datetime.now(),
        )

        # Store resource in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO support_resources
                (id, resource_id, title, description, support_type, content,
                 url, tags, target_audience, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    resource_id,
                    resource.resource_id,
                    resource.title,
                    resource.description,
                    resource.support_type.value,
                    resource.content,
                    resource.url,
                    json.dumps(resource.tags),
                    resource.target_audience,
                    resource.created_at.isoformat(),
                ),
            )

        self.logger.info(f"✅ Support resource created: {resource_id}")
        return resource

    def track_user_progress(
        self,
        user_id: str,
        module_id: str,
        progress_percentage: float,
        time_spent_minutes: int,
        quiz_score: Optional[float] = None,
    ):
        """Track user progress in training."""
        self.logger.info(f"📊 Tracking progress for user {user_id} in module {module_id}")

        # Check if progress record exists
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM user_progress
                WHERE user_id = ? AND module_id = ?
            """,
                (user_id, module_id),
            )

            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                completed = progress_percentage >= self.training_config["progress_threshold"]
                completion_date = datetime.now().isoformat() if completed else None

                conn.execute(
                    """
                    UPDATE user_progress
                    SET progress_percentage = ?, completed = ?, completion_date = ?,
                        time_spent_minutes = ?, quiz_score = ?
                    WHERE user_id = ? AND module_id = ?
                """,
                    (
                        progress_percentage,
                        completed,
                        completion_date,
                        time_spent_minutes,
                        quiz_score,
                        user_id,
                        module_id,
                    ),
                )
            else:
                # Create new record
                completed = progress_percentage >= self.training_config["progress_threshold"]
                completion_date = datetime.now().isoformat() if completed else None

                conn.execute(
                    """
                    INSERT INTO user_progress
                    (id, user_id, module_id, progress_percentage, completed,
                     start_date, completion_date, time_spent_minutes, quiz_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"{user_id}_{module_id}_{int(time.time())}",
                        user_id,
                        module_id,
                        progress_percentage,
                        completed,
                        datetime.now().isoformat(),
                        completion_date,
                        time_spent_minutes,
                        quiz_score,
                    ),
                )

        self.logger.info(f"✅ Progress tracked: {progress_percentage}% complete")

    def track_adoption_metrics(
        self,
        user_id: str,
        current_stage: AdoptionStage,
        feature_usage_count: Dict[str, int],
        session_duration_minutes: int,
        satisfaction_score: Optional[float] = None,
    ):
        """Track user adoption metrics."""
        self.logger.info(f"📈 Tracking adoption metrics for user {user_id}")

        # Check if metrics record exists
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM adoption_metrics
                WHERE user_id = ?
            """,
                (user_id,),
            )

            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                conn.execute(
                    """
                    UPDATE adoption_metrics
                    SET current_stage = ?, feature_usage_count = ?, session_duration_minutes = ?,
                        last_active_date = ?, satisfaction_score = ?
                    WHERE user_id = ?
                """,
                    (
                        current_stage.value,
                        json.dumps(feature_usage_count),
                        session_duration_minutes,
                        datetime.now().isoformat(),
                        satisfaction_score,
                        user_id,
                    ),
                )
            else:
                # Create new record
                conn.execute(
                    """
                    INSERT INTO adoption_metrics
                    (id, user_id, current_stage, stage_start_date, feature_usage_count,
                     session_duration_minutes, last_active_date, satisfaction_score, feedback_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"adoption_{user_id}_{int(time.time())}",
                        user_id,
                        current_stage.value,
                        datetime.now().isoformat(),
                        json.dumps(feature_usage_count),
                        session_duration_minutes,
                        datetime.now().isoformat(),
                        satisfaction_score,
                        0,
                    ),
                )

        self.logger.info(f"✅ Adoption metrics tracked for stage: {current_stage.value}")

    def get_user_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user progress across all modules."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT up.*, tm.title, tm.training_type
                FROM user_progress up
                JOIN training_modules tm ON up.module_id = tm.module_id
                WHERE up.user_id = ?
                ORDER BY up.start_date DESC
            """,
                (user_id,),
            )

            return [
                {
                    "module_id": row[2],
                    "module_title": row[9],
                    "training_type": row[10],
                    "progress_percentage": row[3],
                    "completed": row[4],
                    "start_date": row[5],
                    "completion_date": row[6],
                    "time_spent_minutes": row[7],
                    "quiz_score": row[8],
                }
                for row in cursor.fetchall()
            ]

    def get_adoption_metrics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get adoption metrics for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM adoption_metrics
                WHERE user_id = ?
            """,
                (user_id,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "user_id": row[1],
                    "current_stage": row[2],
                    "stage_start_date": row[3],
                    "feature_usage_count": json.loads(row[4]),
                    "session_duration_minutes": row[5],
                    "last_active_date": row[6],
                    "satisfaction_score": row[7],
                    "feedback_count": row[8],
                }

        return None

    def get_training_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get personalized training recommendations for a user."""
        self.logger.info(f"🎯 Generating training recommendations for user {user_id}")

        # Get user's current progress
        user_progress = self.get_user_progress(user_id)
        completed_modules = {p["module_id"] for p in user_progress if p["completed"]}

        # Get user's adoption stage
        adoption_metrics = self.get_adoption_metrics(user_id)
        current_stage = adoption_metrics["current_stage"] if adoption_metrics else "awareness"

        # Get available modules
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM training_modules
                ORDER BY difficulty_level, duration_minutes
            """
            )

            available_modules = []
            for row in cursor.fetchall():
                module_id = row[1]
                if module_id not in completed_modules:
                    # Check prerequisites
                    prerequisites = json.loads(row[8])
                    if all(prereq in completed_modules for prereq in prerequisites):
                        available_modules.append(
                            {
                                "module_id": module_id,
                                "title": row[2],
                                "description": row[3],
                                "training_type": row[4],
                                "duration_minutes": row[6],
                                "difficulty_level": row[7],
                                "recommendation_score": self._calculate_recommendation_score(
                                    row[4], current_stage, row[7]
                                ),
                            }
                        )

        # Sort by recommendation score
        available_modules.sort(key=lambda x: x["recommendation_score"], reverse=True)

        self.logger.info(f"✅ Generated {len(available_modules)} recommendations")
        return available_modules[:5]  # Return top 5 recommendations

    def _calculate_recommendation_score(self, training_type: str, current_stage: str, difficulty_level: str) -> float:
        """Calculate recommendation score for a module."""
        score = 0.0

        # Stage-based scoring
        stage_scores = {
            "awareness": {"onboarding": 1.0, "feature_training": 0.3, "advanced_training": 0.1},
            "interest": {"onboarding": 0.8, "feature_training": 0.9, "advanced_training": 0.2},
            "evaluation": {"onboarding": 0.6, "feature_training": 1.0, "advanced_training": 0.4},
            "trial": {"onboarding": 0.4, "feature_training": 0.8, "advanced_training": 0.7},
            "adoption": {"onboarding": 0.2, "feature_training": 0.6, "advanced_training": 0.9},
            "advocacy": {"onboarding": 0.1, "feature_training": 0.4, "advanced_training": 1.0},
        }

        score += stage_scores.get(current_stage, {}).get(training_type, 0.5)

        # Difficulty-based scoring
        difficulty_scores = {"beginner": 1.0, "intermediate": 0.8, "advanced": 0.6}
        score += difficulty_scores.get(difficulty_level, 0.7)

        return score

    def generate_training_report(self, user_id: str) -> Dict[str, Any]:
        """Generate a comprehensive training report for a user."""
        self.logger.info(f"📊 Generating training report for user {user_id}")

        # Get user progress
        user_progress = self.get_user_progress(user_id)

        # Get adoption metrics
        adoption_metrics = self.get_adoption_metrics(user_id)

        # Calculate statistics
        total_modules = len(user_progress)
        completed_modules = len([p for p in user_progress if p["completed"]])
        total_time_spent = sum(p["time_spent_minutes"] for p in user_progress)
        average_quiz_score = sum(p["quiz_score"] or 0 for p in user_progress if p["quiz_score"]) / max(
            1, len([p for p in user_progress if p["quiz_score"]])
        )

        # Generate recommendations
        recommendations = self.get_training_recommendations(user_id)

        report = {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "progress_summary": {
                "total_modules": total_modules,
                "completed_modules": completed_modules,
                "completion_rate": (completed_modules / max(1, total_modules)) * 100,
                "total_time_spent_minutes": total_time_spent,
                "average_quiz_score": average_quiz_score,
            },
            "adoption_summary": adoption_metrics,
            "recent_progress": user_progress[:5],  # Last 5 modules
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(user_progress, adoption_metrics),
        }

        # Save report to file
        report_file = self.output_dir / f"training_report_{user_id}_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"✅ Training report generated: {report_file}")
        return report

    def _generate_next_steps(
        self, user_progress: List[Dict[str, Any]], adoption_metrics: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate next steps for the user."""
        next_steps = []

        if not user_progress:
            next_steps.append("Start with the onboarding training module")
            next_steps.append("Complete the basic feature overview")
        else:
            completed_count = len([p for p in user_progress if p["completed"]])
            if completed_count < 3:
                next_steps.append("Continue with foundational training modules")
            elif completed_count < 5:
                next_steps.append("Explore intermediate feature training")
            else:
                next_steps.append("Consider advanced training modules")

            if adoption_metrics:
                current_stage = adoption_metrics["current_stage"]
                if current_stage == "awareness":
                    next_steps.append("Attend a system overview workshop")
                elif current_stage == "evaluation":
                    next_steps.append("Try hands-on exercises with sample data")
                elif current_stage == "trial":
                    next_steps.append("Use the system with real projects")

        return next_steps

    def start_support_portal(self):
        """Start the support portal web server."""
        if self.support_active:
            self.logger.warning("Support portal already active")
            return

        self.logger.info("🚀 Starting support portal...")

        # Create support server
        server_address = ("", self.training_config["support_portal_port"])
        self.support_server = HTTPServer(server_address, SupportPortalHandler)
        SupportPortalHandler.training_system = self  # type: ignore

        # Start server in a separate thread
        self.support_thread = threading.Thread(target=self._run_support_server)
        self.support_thread.daemon = True
        self.support_thread.start()

        self.support_active = True

        self.logger.info(f"✅ Support portal started on port {self.training_config['support_portal_port']}")

        # Open portal in browser
        try:
            webbrowser.open(f"http://localhost:{self.training_config['support_portal_port']}")
        except Exception as e:
            self.logger.warning(f"Could not open browser: {e}")

    def stop_support_portal(self):
        """Stop the support portal web server."""
        if not self.support_active:
            self.logger.warning("Support portal not active")
            return

        self.logger.info("🛑 Stopping support portal...")

        if self.support_server:
            self.support_server.shutdown()

        self.support_active = False

        self.logger.info("✅ Support portal stopped")

    def _run_support_server(self):
        """Run the support portal server."""
        try:
            if self.support_server:
                self.support_server.serve_forever()
        except Exception as e:
            self.logger.error(f"Support portal server error: {e}")

    def _save_training_module(self, module: TrainingModule):
        """Save training module to file."""
        module_file = self.output_dir / f"training_module_{module.module_id}.json"

        module_data = {
            "module_id": module.module_id,
            "title": module.title,
            "description": module.description,
            "training_type": module.training_type.value,
            "content": module.content,
            "duration_minutes": module.duration_minutes,
            "difficulty_level": module.difficulty_level,
            "prerequisites": module.prerequisites,
            "learning_objectives": module.learning_objectives,
            "created_at": module.created_at.isoformat(),
        }

        with open(module_file, "w") as f:
            json.dump(module_data, f, indent=2)

        self.logger.info(f"📄 Training module saved: {module_file}")

    def get_training_statistics(self) -> Dict[str, Any]:
        """Get overall training statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Module statistics
            cursor = conn.execute("SELECT COUNT(*) FROM training_modules")
            total_modules = cursor.fetchone()[0]

            # User progress statistics
            cursor = conn.execute("SELECT COUNT(DISTINCT user_id) FROM user_progress")
            active_users = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM user_progress WHERE completed = TRUE")
            completed_modules = cursor.fetchone()[0]

            cursor = conn.execute("SELECT AVG(progress_percentage) FROM user_progress")
            avg_progress = cursor.fetchone()[0] or 0

            # Adoption statistics
            cursor = conn.execute("SELECT COUNT(*) FROM adoption_metrics")
            tracked_users = cursor.fetchone()[0]

            cursor = conn.execute("SELECT current_stage, COUNT(*) FROM adoption_metrics GROUP BY current_stage")
            stage_distribution = dict(cursor.fetchall())

        return {
            "total_modules": total_modules,
            "active_users": active_users,
            "completed_modules": completed_modules,
            "average_progress": avg_progress,
            "tracked_users": tracked_users,
            "stage_distribution": stage_distribution,
        }


class SupportPortalHandler(BaseHTTPRequestHandler):
    """HTTP request handler for support portal."""

    def do_GET(self):
        """Handle GET requests."""
        try:
            if self.path == "/":
                self._serve_portal_home()
            elif self.path.startswith("/training/"):
                self._serve_training_content()
            elif self.path.startswith("/support/"):
                self._serve_support_content()
            elif self.path.startswith("/progress/"):
                self._serve_progress_content()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(500, str(e))

    def _serve_portal_home(self):
        """Serve support portal home page."""
        content = """
<!DOCTYPE html>
<html>
<head>
    <title>t-3 Training & Support Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { color: #007bff; margin-top: 0; }
        .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; }
        .btn:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 t-3 Training & Support Portal</h1>
            <p>Your comprehensive resource for learning and mastering the t-3 documentation system</p>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📚 Training Modules</h3>
                <p>Access interactive training modules designed to help you master the t-3 system.</p>
                <a href="/training/" class="btn">Start Learning</a>
            </div>

            <div class="card">
                <h3>📖 Support Resources</h3>
                <p>Find documentation, tutorials, and guides to help you succeed.</p>
                <a href="/support/" class="btn">Get Support</a>
            </div>

            <div class="card">
                <h3>📊 Your Progress</h3>
                <p>Track your learning progress and adoption metrics.</p>
                <a href="/progress/" class="btn">View Progress</a>
            </div>

            <div class="card">
                <h3>🎯 Recommendations</h3>
                <p>Get personalized training recommendations based on your progress.</p>
                <a href="/training/recommendations" class="btn">Get Recommendations</a>
            </div>
        </div>
    </div>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def _serve_training_content(self):
        """Serve training content."""
        content = """
<!DOCTYPE html>
<html>
<head>
    <title>Training Modules - t-3 Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .module { background-color: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .module h3 { color: #007bff; margin-top: 0; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Portal</a>
    <h1>📚 Training Modules</h1>

    <div class="module">
        <h3>Getting Started with t-3</h3>
        <p>Learn the basics of the t-3 documentation system and understand its structure.</p>
        <p><strong>Duration:</strong> 30 minutes | <strong>Level:</strong> Beginner</p>
    </div>

    <div class="module">
        <h3>Documentation Quality Standards</h3>
        <p>Master the quality standards and best practices for t-3 documentation.</p>
        <p><strong>Duration:</strong> 45 minutes | <strong>Level:</strong> Intermediate</p>
    </div>

    <div class="module">
        <h3>Advanced t-3 Features</h3>
        <p>Explore advanced features and optimization techniques.</p>
        <p><strong>Duration:</strong> 60 minutes | <strong>Level:</strong> Advanced</p>
    </div>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def _serve_support_content(self):
        """Serve support content."""
        content = """
<!DOCTYPE html>
<html>
<head>
    <title>Support Resources - t-3 Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .resource { background-color: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .resource h3 { color: #007bff; margin-top: 0; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Portal</a>
    <h1>📖 Support Resources</h1>

    <div class="resource">
        <h3>📋 User Guide</h3>
        <p>Comprehensive guide to using the t-3 documentation system.</p>
    </div>

    <div class="resource">
        <h3>🎥 Video Tutorials</h3>
        <p>Step-by-step video tutorials for common tasks.</p>
    </div>

    <div class="resource">
        <h3>❓ FAQ</h3>
        <p>Frequently asked questions and answers.</p>
    </div>

    <div class="resource">
        <h3>🛠️ Troubleshooting</h3>
        <p>Common issues and their solutions.</p>
    </div>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def _serve_progress_content(self):
        """Serve progress content."""
        content = """
<!DOCTYPE html>
<html>
<head>
    <title>Your Progress - t-3 Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .progress-card { background-color: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .progress-bar { background-color: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; }
        .progress-fill { background-color: #007bff; height: 100%; transition: width 0.3s; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Portal</a>
    <h1>📊 Your Progress</h1>

    <div class="progress-card">
        <h3>Overall Progress</h3>
        <div class="progress-bar">
            <div class="progress-fill" style="width: 65%;"></div>
        </div>
        <p>65% Complete</p>
    </div>

    <div class="progress-card">
        <h3>Training Modules</h3>
        <p><strong>Completed:</strong> 3 of 5 modules</p>
        <p><strong>Time Spent:</strong> 2 hours 15 minutes</p>
        <p><strong>Average Score:</strong> 87%</p>
    </div>

    <div class="progress-card">
        <h3>Adoption Stage</h3>
        <p><strong>Current Stage:</strong> Evaluation</p>
        <p><strong>Next Milestone:</strong> Trial Phase</p>
    </div>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())


def main():
    """Main entry point for the training and adoption support system."""
    parser = argparse.ArgumentParser(description="Training and adoption support system for t-t3 system")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output-dir", default="artifacts/training", help="Output directory for results")
    parser.add_argument("--create-module", help="Create training module (title,description,type,duration)")
    parser.add_argument("--track-progress", help="Track user progress (user_id,module_id,progress,time)")
    parser.add_argument("--track-adoption", help="Track adoption metrics (user_id,stage,features,time)")
    parser.add_argument("--generate-report", help="Generate training report for user ID")
    parser.add_argument("--start-portal", action="store_true", help="Start support portal")
    parser.add_argument("--stop-portal", action="store_true", help="Stop support portal")
    parser.add_argument("--show-stats", action="store_true", help="Show training statistics")

    args = parser.parse_args()

    # Initialize training system
    training_system = TrainingAdoptionSupport(args.project_root, args.output_dir)

    if args.create_module:
        try:
            parts = args.create_module.split(",", 3)
            title = parts[0]
            description = parts[1]
            training_type = TrainingType(parts[2])
            duration = int(parts[3])

            module = training_system.create_training_module(
                title, description, training_type, "Module content...", duration, "beginner", [], ["Learn the basics"]
            )
            print(f"✅ Training module created: {module.module_id}")
        except Exception as e:
            print(f"❌ Error creating module: {e}")

    elif args.track_progress:
        try:
            parts = args.track_progress.split(",")
            user_id = parts[0]
            module_id = parts[1]
            progress = float(parts[2])
            time_spent = int(parts[3])

            training_system.track_user_progress(user_id, module_id, progress, time_spent)
            print(f"✅ Progress tracked for user {user_id}")
        except Exception as e:
            print(f"❌ Error tracking progress: {e}")

    elif args.track_adoption:
        try:
            parts = args.track_adoption.split(",")
            user_id = parts[0]
            stage = AdoptionStage(parts[1])
            features = json.loads(parts[2])
            time_spent = int(parts[3])

            training_system.track_adoption_metrics(user_id, stage, features, time_spent)
            print(f"✅ Adoption metrics tracked for user {user_id}")
        except Exception as e:
            print(f"❌ Error tracking adoption: {e}")

    elif args.generate_report:
        training_system.generate_training_report(args.generate_report)
        print(f"✅ Training report generated for user {args.generate_report}")

    elif args.start_portal:
        training_system.start_support_portal()
        print("✅ Support portal started")

    elif args.stop_portal:
        training_system.stop_support_portal()
        print("✅ Support portal stopped")

    elif args.show_stats:
        stats = training_system.get_training_statistics()
        print("📊 Training Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    else:
        print("🎓 Training and Adoption Support System for t-t3 System")
        print("Use --create-module to create a training module")
        print("Use --track-progress to track user progress")
        print("Use --track-adoption to track adoption metrics")
        print("Use --generate-report to generate training report")
        print("Use --start-portal to start support portal")
        print("Use --stop-portal to stop support portal")
        print("Use --show-stats to show training statistics")


if __name__ == "__main__":
    main()
