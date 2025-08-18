#!/usr/bin/env python3.12.123.11
"""
Full Consensus Framework Integration (B-104)

Implements complete consensus framework with strawman proposals,
red team/blue team roles, and consensus validation checkpoints.

Usage:
    python3 scripts/consensus_framework.py --propose "Implement new feature X"
    python3 scripts/consensus_framework.py --validate-round 1
    python3 scripts/consensus_framework.py --red-team-review proposal_001
    python3 scripts/consensus_framework.py --blue-team-review proposal_001
"""

import argparse
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

import yaml


class ConsensusStatus(Enum):
    """Consensus status enumeration."""

    DRAFT = "draft"
    PROPOSED = "proposed"
    RED_TEAM_REVIEW = "red_team_review"
    BLUE_TEAM_REVIEW = "blue_team_review"
    CONSENSUS_ROUND = "consensus_round"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class RoleType(Enum):
    """Role types in consensus framework."""

    PROPOSER = "proposer"
    RED_TEAM = "red_team"
    BLUE_TEAM = "blue_team"
    VALIDATOR = "validator"
    OBSERVER = "observer"


class ValidationLevel(Enum):
    """Validation levels for consensus checkpoints."""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    EXPERT = "expert"


@dataclass
class ConsensusParticipant:
    """Represents a participant in the consensus process."""

    id: str
    name: str
    role: RoleType
    expertise: list[str] = field(default_factory=list)
    trust_score: float = 1.0
    participation_history: list[str] = field(default_factory=list)


@dataclass
class StrawmanProposal:
    """Represents a strawman proposal for consensus building."""

    id: str
    title: str
    description: str
    proposer_id: str
    created_at: datetime
    status: ConsensusStatus = ConsensusStatus.DRAFT
    tags: list[str] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    references: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass
class ConsensusRound:
    """Represents a consensus round with feedback and refinements."""

    round_number: int
    proposal_id: str
    start_time: datetime
    end_time: datetime | None = None
    participants: list[str] = field(default_factory=list)
    feedback: list[dict] = field(default_factory=list)
    refinements: list[dict] = field(default_factory=list)
    consensus_score: float = 0.0
    validation_level: ValidationLevel = ValidationLevel.STANDARD


@dataclass
class RedTeamReview:
    """Represents a red team review (critique and challenge)."""

    id: str
    proposal_id: str
    reviewer_id: str
    review_time: datetime
    critique_points: list[str] = field(default_factory=list)
    risk_assessment: dict = field(default_factory=dict)
    challenge_questions: list[str] = field(default_factory=list)
    alternative_approaches: list[str] = field(default_factory=list)
    severity_score: float = 0.0


@dataclass
class BlueTeamReview:
    """Represents a blue team review (support and enhancement)."""

    id: str
    proposal_id: str
    reviewer_id: str
    review_time: datetime
    support_points: list[str] = field(default_factory=list)
    enhancement_suggestions: list[str] = field(default_factory=list)
    implementation_guidance: list[str] = field(default_factory=list)
    success_indicators: list[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class ConsensusCheckpoint:
    """Represents a validation checkpoint in the consensus process."""

    checkpoint_id: str
    proposal_id: str
    checkpoint_type: str
    validation_level: ValidationLevel
    timestamp: datetime
    validator_id: str
    criteria_met: list[str] = field(default_factory=list)
    criteria_failed: list[str] = field(default_factory=list)
    overall_score: float = 0.0
    passed: bool = False
    notes: str = ""


@dataclass
class ConsensusResult:
    """Final consensus result with validation and implementation guidance."""

    proposal_id: str
    final_status: ConsensusStatus
    consensus_score: float
    validation_score: float
    implementation_priority: str
    timeline_estimate: str
    resource_requirements: dict = field(default_factory=dict)
    risk_mitigation: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


class ConsensusFramework:
    """Full consensus framework with strawman proposals and role-based validation."""

    def __init__(self, config_path: str | None = None):
        self.config = self._load_config(config_path)
        self.data_dir = Path("data/consensus")
        self.proposals_file = self.data_dir / "proposals.jsonl"
        self.participants_file = self.data_dir / "participants.jsonl"
        self.rounds_file = self.data_dir / "rounds.jsonl"
        self.reviews_file = self.data_dir / "reviews.jsonl"
        self.checkpoints_file = self.data_dir / "checkpoints.jsonl"
        self.results_file = self.data_dir / "results.jsonl"
        self._ensure_data_dirs()
        self.participants = self._load_participants()

    def _load_config(self, config_path: str | None) -> dict:
        """Load configuration for the consensus framework."""
        default_config = {
            "consensus": {
                "min_participants": 3,
                "min_consensus_score": 0.7,
                "max_rounds": 5,
                "round_timeout_hours": 24,
                "validation_thresholds": {"basic": 0.5, "standard": 0.7, "strict": 0.8, "expert": 0.9},
            },
            "roles": {
                "red_team": {"min_reviewers": 1, "focus_areas": ["risks", "alternatives", "challenges"]},
                "blue_team": {"min_reviewers": 1, "focus_areas": ["support", "enhancements", "implementation"]},
                "validator": {"min_validators": 1, "focus_areas": ["quality", "feasibility", "alignment"]},
            },
            "validation": {
                "checkpoint_types": [
                    "proposal_quality",
                    "technical_feasibility",
                    "resource_availability",
                    "risk_assessment",
                    "implementation_readiness",
                ],
                "criteria_weights": {
                    "clarity": 0.2,
                    "feasibility": 0.25,
                    "impact": 0.2,
                    "risk": 0.15,
                    "alignment": 0.2,
                },
            },
        }

        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config

    def _ensure_data_dirs(self):
        """Ensure data directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        for file_path in [
            self.proposals_file,
            self.participants_file,
            self.rounds_file,
            self.reviews_file,
            self.checkpoints_file,
            self.results_file,
        ]:
            file_path.touch()

    def _load_participants(self) -> dict[str, ConsensusParticipant]:
        """Load participants from the database."""
        participants = {}

        if self.participants_file.exists():
            with open(self.participants_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            participants[data["id"]] = ConsensusParticipant(
                                id=data["id"],
                                name=data["name"],
                                role=RoleType(data["role"]),
                                expertise=data.get("expertise", []),
                                trust_score=data.get("trust_score", 1.0),
                                participation_history=data.get("participation_history", []),
                            )
                        except (json.JSONDecodeError, KeyError):
                            continue

        return participants

    def create_strawman_proposal(
        self,
        title: str,
        description: str,
        proposer_id: str,
        tags: list[str] | None = None,
        context: dict | None = None,
    ) -> StrawmanProposal:
        """Create a new strawman proposal."""
        proposal = StrawmanProposal(
            id=f"proposal_{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            proposer_id=proposer_id,
            created_at=datetime.now(),
            status=ConsensusStatus.DRAFT,
            tags=tags or [],
            context=context or {},
            references=[],
            assumptions=[],
            constraints=[],
            success_criteria=[],
        )

        # Save proposal
        with open(self.proposals_file, "a") as f:
            json.dump(
                {
                    "id": proposal.id,
                    "title": proposal.title,
                    "description": proposal.description,
                    "proposer_id": proposal.proposer_id,
                    "created_at": proposal.created_at.isoformat(),
                    "status": proposal.status.value,
                    "tags": proposal.tags,
                    "context": proposal.context,
                    "references": proposal.references,
                    "assumptions": proposal.assumptions,
                    "constraints": proposal.constraints,
                    "success_criteria": proposal.success_criteria,
                },
                f,
            )
            f.write("\n")

        return proposal

    def submit_proposal(self, proposal_id: str) -> bool:
        """Submit a proposal for consensus review."""
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            return False

        proposal.status = ConsensusStatus.PROPOSED

        # Update proposal in database
        self._update_proposal(proposal)

        # Create initial consensus round
        self._create_consensus_round(proposal_id, 1)

        return True

    def start_red_team_review(self, proposal_id: str, reviewer_id: str) -> RedTeamReview:
        """Start a red team review (critique and challenge)."""
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        # Update proposal status
        proposal.status = ConsensusStatus.RED_TEAM_REVIEW
        self._update_proposal(proposal)

        # Create red team review
        review = RedTeamReview(
            id=f"red_review_{uuid.uuid4().hex[:8]}",
            proposal_id=proposal_id,
            reviewer_id=reviewer_id,
            review_time=datetime.now(),
        )

        # Save review
        self._save_review(review, "red_team")

        return review

    def submit_red_team_review(
        self,
        review_id: str,
        critique_points: list[str],
        risk_assessment: dict,
        challenge_questions: list[str],
        alternative_approaches: list[str],
        severity_score: float,
    ) -> bool:
        """Submit a completed red team review."""
        review = self._get_review(review_id, "red_team")
        if not review:
            return False

        review.critique_points = critique_points
        review.risk_assessment = risk_assessment
        review.challenge_questions = challenge_questions
        review.alternative_approaches = alternative_approaches
        review.severity_score = severity_score

        # Update review
        self._update_review(review, "red_team")

        # Move to blue team review
        proposal = self._get_proposal(review.proposal_id)
        if proposal:
            proposal.status = ConsensusStatus.BLUE_TEAM_REVIEW
            self._update_proposal(proposal)

        return True

    def start_blue_team_review(self, proposal_id: str, reviewer_id: str) -> BlueTeamReview:
        """Start a blue team review (support and enhancement)."""
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        # Create blue team review
        review = BlueTeamReview(
            id=f"blue_review_{uuid.uuid4().hex[:8]}",
            proposal_id=proposal_id,
            reviewer_id=reviewer_id,
            review_time=datetime.now(),
        )

        # Save review
        self._save_review(review, "blue_team")

        return review

    def submit_blue_team_review(
        self,
        review_id: str,
        support_points: list[str],
        enhancement_suggestions: list[str],
        implementation_guidance: list[str],
        success_indicators: list[str],
        confidence_score: float,
    ) -> bool:
        """Submit a completed blue team review."""
        review = self._get_review(review_id, "blue_team")
        if not review:
            return False

        review.support_points = support_points
        review.enhancement_suggestions = enhancement_suggestions
        review.implementation_guidance = implementation_guidance
        review.success_indicators = success_indicators
        review.confidence_score = confidence_score

        # Update review
        self._update_review(review, "blue_team")

        # Move to consensus round
        proposal = self._get_proposal(review.proposal_id)
        if proposal:
            proposal.status = ConsensusStatus.CONSENSUS_ROUND
            self._update_proposal(proposal)

        return True

    def create_consensus_round(self, proposal_id: str, round_number: int) -> ConsensusRound:
        """Create a new consensus round."""
        round_obj = ConsensusRound(
            round_number=round_number,
            proposal_id=proposal_id,
            start_time=datetime.now(),
            validation_level=ValidationLevel.STANDARD,
        )

        # Save round
        with open(self.rounds_file, "a") as f:
            json.dump(
                {
                    "round_number": round_obj.round_number,
                    "proposal_id": round_obj.proposal_id,
                    "start_time": round_obj.start_time.isoformat(),
                    "end_time": round_obj.end_time.isoformat() if round_obj.end_time else None,
                    "participants": round_obj.participants,
                    "feedback": round_obj.feedback,
                    "refinements": round_obj.refinements,
                    "consensus_score": round_obj.consensus_score,
                    "validation_level": round_obj.validation_level.value,
                },
                f,
            )
            f.write("\n")

        return round_obj

    def add_consensus_feedback(
        self,
        proposal_id: str,
        round_number: int,
        participant_id: str,
        feedback: str,
        refinements: list[str] | None = None,
    ) -> bool:
        """Add feedback to a consensus round."""
        round_obj = self._get_round(proposal_id, round_number)
        if not round_obj:
            return False

        feedback_entry = {
            "participant_id": participant_id,
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "refinements": refinements or [],
        }

        round_obj.feedback.append(feedback_entry)
        round_obj.participants.append(participant_id)

        # Update round
        self._update_round(round_obj)

        return True

    def calculate_consensus_score(self, proposal_id: str, round_number: int) -> float:
        """Calculate consensus score for a round."""
        round_obj = self._get_round(proposal_id, round_number)
        if not round_obj or not round_obj.feedback:
            return 0.0

        # Simple consensus calculation based on feedback sentiment
        # In a real implementation, this would use more sophisticated NLP
        positive_keywords = ["agree", "support", "good", "excellent", "approve", "yes"]
        negative_keywords = ["disagree", "concern", "risk", "no", "reject", "problem"]

        total_score = 0.0
        feedback_count = len(round_obj.feedback)

        for feedback_entry in round_obj.feedback:
            feedback_text = feedback_entry["feedback"].lower()

            positive_count = sum(1 for word in positive_keywords if word in feedback_text)
            negative_count = sum(1 for word in negative_keywords if word in feedback_text)

            if positive_count > negative_count:
                total_score += 1.0
            elif positive_count == negative_count:
                total_score += 0.5
            else:
                total_score += 0.0

        consensus_score = total_score / feedback_count if feedback_count > 0 else 0.0
        round_obj.consensus_score = consensus_score

        # Update round
        self._update_round(round_obj)

        return consensus_score

    def create_validation_checkpoint(
        self, proposal_id: str, checkpoint_type: str, validator_id: str, validation_level: ValidationLevel
    ) -> ConsensusCheckpoint:
        """Create a validation checkpoint."""
        checkpoint = ConsensusCheckpoint(
            checkpoint_id=f"checkpoint_{uuid.uuid4().hex[:8]}",
            proposal_id=proposal_id,
            checkpoint_type=checkpoint_type,
            validation_level=validation_level,
            timestamp=datetime.now(),
            validator_id=validator_id,
        )

        # Save checkpoint
        with open(self.checkpoints_file, "a") as f:
            json.dump(
                {
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "proposal_id": checkpoint.proposal_id,
                    "checkpoint_type": checkpoint.checkpoint_type,
                    "validation_level": checkpoint.validation_level.value,
                    "timestamp": checkpoint.timestamp.isoformat(),
                    "validator_id": checkpoint.validator_id,
                    "criteria_met": checkpoint.criteria_met,
                    "criteria_failed": checkpoint.criteria_failed,
                    "overall_score": checkpoint.overall_score,
                    "passed": checkpoint.passed,
                    "notes": checkpoint.notes,
                },
                f,
            )
            f.write("\n")

        return checkpoint

    def validate_checkpoint(
        self,
        checkpoint_id: str,
        criteria_met: list[str],
        criteria_failed: list[str],
        overall_score: float,
        notes: str = "",
    ) -> bool:
        """Validate a checkpoint with criteria assessment."""
        checkpoint = self._get_checkpoint(checkpoint_id)
        if not checkpoint:
            return False

        checkpoint.criteria_met = criteria_met
        checkpoint.criteria_failed = criteria_failed
        checkpoint.overall_score = overall_score
        checkpoint.notes = notes

        # Determine if checkpoint passed
        threshold = self.config["consensus"]["validation_thresholds"][checkpoint.validation_level.value]
        checkpoint.passed = overall_score >= threshold

        # Update checkpoint
        self._update_checkpoint(checkpoint)

        return checkpoint.passed

    def finalize_consensus(self, proposal_id: str) -> ConsensusResult:
        """Finalize consensus and generate implementation guidance."""
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")

        # Get all rounds for this proposal
        rounds = self._get_proposal_rounds(proposal_id)
        if not rounds:
            raise ValueError(f"No consensus rounds found for proposal {proposal_id}")

        # Calculate final consensus score
        final_consensus_score = sum(round_obj.consensus_score for round_obj in rounds) / len(rounds)

        # Get validation checkpoints
        checkpoints = self._get_proposal_checkpoints(proposal_id)
        validation_score = sum(cp.overall_score for cp in checkpoints) / len(checkpoints) if checkpoints else 0.0

        # Determine final status
        min_consensus_score = self.config["consensus"]["min_consensus_score"]
        if final_consensus_score >= min_consensus_score and validation_score >= 0.7:
            final_status = ConsensusStatus.VALIDATED
        else:
            final_status = ConsensusStatus.REJECTED

        # Update proposal status
        proposal.status = final_status
        self._update_proposal(proposal)

        # Generate consensus result
        result = ConsensusResult(
            proposal_id=proposal_id,
            final_status=final_status,
            consensus_score=final_consensus_score,
            validation_score=validation_score,
            implementation_priority=self._calculate_priority(final_consensus_score, validation_score),
            timeline_estimate=self._estimate_timeline(proposal),
            resource_requirements=self._assess_resources(proposal),
            risk_mitigation=self._extract_risk_mitigation(proposal_id),
            success_metrics=self._generate_success_metrics(proposal),
            next_steps=self._generate_next_steps(proposal_id, final_status),
        )

        # Save result
        with open(self.results_file, "a") as f:
            json.dump(
                {
                    "proposal_id": result.proposal_id,
                    "final_status": result.final_status.value,
                    "consensus_score": result.consensus_score,
                    "validation_score": result.validation_score,
                    "implementation_priority": result.implementation_priority,
                    "timeline_estimate": result.timeline_estimate,
                    "resource_requirements": result.resource_requirements,
                    "risk_mitigation": result.risk_mitigation,
                    "success_metrics": result.success_metrics,
                    "next_steps": result.next_steps,
                },
                f,
            )
            f.write("\n")

        return result

    def _get_proposal(self, proposal_id: str) -> StrawmanProposal | None:
        """Get a proposal by ID."""
        if self.proposals_file.exists():
            with open(self.proposals_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["id"] == proposal_id:
                                return StrawmanProposal(
                                    id=data["id"],
                                    title=data["title"],
                                    description=data["description"],
                                    proposer_id=data["proposer_id"],
                                    created_at=datetime.fromisoformat(data["created_at"]),
                                    status=ConsensusStatus(data["status"]),
                                    tags=data.get("tags", []),
                                    context=data.get("context", {}),
                                    references=data.get("references", []),
                                    assumptions=data.get("assumptions", []),
                                    constraints=data.get("constraints", []),
                                    success_criteria=data.get("success_criteria", []),
                                )
                        except (json.JSONDecodeError, KeyError):
                            continue
        return None

    def _update_proposal(self, proposal: StrawmanProposal):
        """Update a proposal in the database."""
        # This is a simplified update - in production, you'd want proper database operations
        proposals = []
        if self.proposals_file.exists():
            with open(self.proposals_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["id"] != proposal.id:
                                proposals.append(data)
                        except json.JSONDecodeError:
                            continue

        # Add updated proposal
        proposals.append(
            {
                "id": proposal.id,
                "title": proposal.title,
                "description": proposal.description,
                "proposer_id": proposal.proposer_id,
                "created_at": proposal.created_at.isoformat(),
                "status": proposal.status.value,
                "tags": proposal.tags,
                "context": proposal.context,
                "references": proposal.references,
                "assumptions": proposal.assumptions,
                "constraints": proposal.constraints,
                "success_criteria": proposal.success_criteria,
            }
        )

        # Write back to file
        with open(self.proposals_file, "w") as f:
            for proposal_data in proposals:
                json.dump(proposal_data, f)
                f.write("\n")

    def _create_consensus_round(self, proposal_id: str, round_number: int):
        """Create a consensus round."""
        return self.create_consensus_round(proposal_id, round_number)

    def _get_round(self, proposal_id: str, round_number: int) -> ConsensusRound | None:
        """Get a consensus round."""
        if self.rounds_file.exists():
            with open(self.rounds_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["proposal_id"] == proposal_id and data["round_number"] == round_number:
                                return ConsensusRound(
                                    round_number=data["round_number"],
                                    proposal_id=data["proposal_id"],
                                    start_time=datetime.fromisoformat(data["start_time"]),
                                    end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
                                    participants=data.get("participants", []),
                                    feedback=data.get("feedback", []),
                                    refinements=data.get("refinements", []),
                                    consensus_score=data.get("consensus_score", 0.0),
                                    validation_level=ValidationLevel(data.get("validation_level", "standard")),
                                )
                        except (json.JSONDecodeError, KeyError):
                            continue
        return None

    def _update_round(self, round_obj: ConsensusRound):
        """Update a consensus round."""
        # Similar to _update_proposal, this would be a proper database operation
        rounds = []
        if self.rounds_file.exists():
            with open(self.rounds_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if not (
                                data["proposal_id"] == round_obj.proposal_id
                                and data["round_number"] == round_obj.round_number
                            ):
                                rounds.append(data)
                        except json.JSONDecodeError:
                            continue

        # Add updated round
        rounds.append(
            {
                "round_number": round_obj.round_number,
                "proposal_id": round_obj.proposal_id,
                "start_time": round_obj.start_time.isoformat(),
                "end_time": round_obj.end_time.isoformat() if round_obj.end_time else None,
                "participants": round_obj.participants,
                "feedback": round_obj.feedback,
                "refinements": round_obj.refinements,
                "consensus_score": round_obj.consensus_score,
                "validation_level": round_obj.validation_level.value,
            }
        )

        # Write back to file
        with open(self.rounds_file, "w") as f:
            for round_data in rounds:
                json.dump(round_data, f)
                f.write("\n")

    def _save_review(self, review, review_type: str):
        """Save a review to the database."""
        with open(self.reviews_file, "a") as f:
            review_data = {
                "id": review.id,
                "proposal_id": review.proposal_id,
                "reviewer_id": review.reviewer_id,
                "review_time": review.review_time.isoformat(),
                "review_type": review_type,
            }

            if review_type == "red_team":
                review_data.update(
                    {
                        "critique_points": review.critique_points,
                        "risk_assessment": review.risk_assessment,
                        "challenge_questions": review.challenge_questions,
                        "alternative_approaches": review.alternative_approaches,
                        "severity_score": review.severity_score,
                    }
                )
            elif review_type == "blue_team":
                review_data.update(
                    {
                        "support_points": review.support_points,
                        "enhancement_suggestions": review.enhancement_suggestions,
                        "implementation_guidance": review.implementation_guidance,
                        "success_indicators": review.success_indicators,
                        "confidence_score": review.confidence_score,
                    }
                )

            json.dump(review_data, f)
            f.write("\n")

    def _get_review(self, review_id: str, review_type: str):
        """Get a review by ID and type."""
        if self.reviews_file.exists():
            with open(self.reviews_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["id"] == review_id and data["review_type"] == review_type:
                                if review_type == "red_team":
                                    return RedTeamReview(
                                        id=data["id"],
                                        proposal_id=data["proposal_id"],
                                        reviewer_id=data["reviewer_id"],
                                        review_time=datetime.fromisoformat(data["review_time"]),
                                        critique_points=data.get("critique_points", []),
                                        risk_assessment=data.get("risk_assessment", {}),
                                        challenge_questions=data.get("challenge_questions", []),
                                        alternative_approaches=data.get("alternative_approaches", []),
                                        severity_score=data.get("severity_score", 0.0),
                                    )
                                elif review_type == "blue_team":
                                    return BlueTeamReview(
                                        id=data["id"],
                                        proposal_id=data["proposal_id"],
                                        reviewer_id=data["reviewer_id"],
                                        review_time=datetime.fromisoformat(data["review_time"]),
                                        support_points=data.get("support_points", []),
                                        enhancement_suggestions=data.get("enhancement_suggestions", []),
                                        implementation_guidance=data.get("implementation_guidance", []),
                                        success_indicators=data.get("success_indicators", []),
                                        confidence_score=data.get("confidence_score", 0.0),
                                    )
                        except (json.JSONDecodeError, KeyError):
                            continue
        return None

    def _update_review(self, review, review_type: str):
        """Update a review in the database."""
        # Similar to other update methods, this would be a proper database operation
        reviews = []
        if self.reviews_file.exists():
            with open(self.reviews_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if not (data["id"] == review.id and data["review_type"] == review_type):
                                reviews.append(data)
                        except json.JSONDecodeError:
                            continue

        # Add updated review
        review_data = {
            "id": review.id,
            "proposal_id": review.proposal_id,
            "reviewer_id": review.reviewer_id,
            "review_time": review.review_time.isoformat(),
            "review_type": review_type,
        }

        if review_type == "red_team":
            review_data.update(
                {
                    "critique_points": review.critique_points,
                    "risk_assessment": review.risk_assessment,
                    "challenge_questions": review.challenge_questions,
                    "alternative_approaches": review.alternative_approaches,
                    "severity_score": review.severity_score,
                }
            )
        elif review_type == "blue_team":
            review_data.update(
                {
                    "support_points": review.support_points,
                    "enhancement_suggestions": review.enhancement_suggestions,
                    "implementation_guidance": review.implementation_guidance,
                    "success_indicators": review.success_indicators,
                    "confidence_score": review.confidence_score,
                }
            )

        reviews.append(review_data)

        # Write back to file
        with open(self.reviews_file, "w") as f:
            for review_data in reviews:
                json.dump(review_data, f)
                f.write("\n")

    def _get_checkpoint(self, checkpoint_id: str) -> ConsensusCheckpoint | None:
        """Get a checkpoint by ID."""
        if self.checkpoints_file.exists():
            with open(self.checkpoints_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["checkpoint_id"] == checkpoint_id:
                                return ConsensusCheckpoint(
                                    checkpoint_id=data["checkpoint_id"],
                                    proposal_id=data["proposal_id"],
                                    checkpoint_type=data["checkpoint_type"],
                                    validation_level=ValidationLevel(data["validation_level"]),
                                    timestamp=datetime.fromisoformat(data["timestamp"]),
                                    validator_id=data["validator_id"],
                                    criteria_met=data.get("criteria_met", []),
                                    criteria_failed=data.get("criteria_failed", []),
                                    overall_score=data.get("overall_score", 0.0),
                                    passed=data.get("passed", False),
                                    notes=data.get("notes", ""),
                                )
                        except (json.JSONDecodeError, KeyError):
                            continue
        return None

    def _update_checkpoint(self, checkpoint: ConsensusCheckpoint):
        """Update a checkpoint in the database."""
        checkpoints = []
        if self.checkpoints_file.exists():
            with open(self.checkpoints_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["checkpoint_id"] != checkpoint.checkpoint_id:
                                checkpoints.append(data)
                        except json.JSONDecodeError:
                            continue

        # Add updated checkpoint
        checkpoints.append(
            {
                "checkpoint_id": checkpoint.checkpoint_id,
                "proposal_id": checkpoint.proposal_id,
                "checkpoint_type": checkpoint.checkpoint_type,
                "validation_level": checkpoint.validation_level.value,
                "timestamp": checkpoint.timestamp.isoformat(),
                "validator_id": checkpoint.validator_id,
                "criteria_met": checkpoint.criteria_met,
                "criteria_failed": checkpoint.criteria_failed,
                "overall_score": checkpoint.overall_score,
                "passed": checkpoint.passed,
                "notes": checkpoint.notes,
            }
        )

        # Write back to file
        with open(self.checkpoints_file, "w") as f:
            for checkpoint_data in checkpoints:
                json.dump(checkpoint_data, f)
                f.write("\n")

    def _get_proposal_rounds(self, proposal_id: str) -> list[ConsensusRound]:
        """Get all rounds for a proposal."""
        rounds = []
        if self.rounds_file.exists():
            with open(self.rounds_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["proposal_id"] == proposal_id:
                                rounds.append(
                                    ConsensusRound(
                                        round_number=data["round_number"],
                                        proposal_id=data["proposal_id"],
                                        start_time=datetime.fromisoformat(data["start_time"]),
                                        end_time=(
                                            datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
                                        ),
                                        participants=data.get("participants", []),
                                        feedback=data.get("feedback", []),
                                        refinements=data.get("refinements", []),
                                        consensus_score=data.get("consensus_score", 0.0),
                                        validation_level=ValidationLevel(data.get("validation_level", "standard")),
                                    )
                                )
                        except (json.JSONDecodeError, KeyError):
                            continue
        return rounds

    def _get_proposal_checkpoints(self, proposal_id: str) -> list[ConsensusCheckpoint]:
        """Get all checkpoints for a proposal."""
        checkpoints = []
        if self.checkpoints_file.exists():
            with open(self.checkpoints_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["proposal_id"] == proposal_id:
                                checkpoints.append(
                                    ConsensusCheckpoint(
                                        checkpoint_id=data["checkpoint_id"],
                                        proposal_id=data["proposal_id"],
                                        checkpoint_type=data["checkpoint_type"],
                                        validation_level=ValidationLevel(data["validation_level"]),
                                        timestamp=datetime.fromisoformat(data["timestamp"]),
                                        validator_id=data["validator_id"],
                                        criteria_met=data.get("criteria_met", []),
                                        criteria_failed=data.get("criteria_failed", []),
                                        overall_score=data.get("overall_score", 0.0),
                                        passed=data.get("passed", False),
                                        notes=data.get("notes", ""),
                                    )
                                )
                        except (json.JSONDecodeError, KeyError):
                            continue
        return checkpoints

    def _calculate_priority(self, consensus_score: float, validation_score: float) -> str:
        """Calculate implementation priority based on scores."""
        overall_score = (consensus_score + validation_score) / 2

        if overall_score >= 0.9:
            return "critical"
        elif overall_score >= 0.8:
            return "high"
        elif overall_score >= 0.7:
            return "medium"
        else:
            return "low"

    def _estimate_timeline(self, proposal: StrawmanProposal) -> str:
        """Estimate implementation timeline."""
        # Simple estimation based on proposal complexity
        complexity = len(proposal.description.split()) / 100  # Words per 100
        if complexity < 0.5:
            return "1-2 weeks"
        elif complexity < 1.0:
            return "2-4 weeks"
        elif complexity < 2.0:
            return "1-2 months"
        else:
            return "2-3 months"

    def _assess_resources(self, proposal: StrawmanProposal) -> dict:
        """Assess resource requirements."""
        # Simple resource assessment
        return {
            "developer_hours": len(proposal.description.split()) * 0.5,
            "review_hours": len(proposal.description.split()) * 0.1,
            "testing_hours": len(proposal.description.split()) * 0.3,
            "documentation_hours": len(proposal.description.split()) * 0.2,
        }

    def _extract_risk_mitigation(self, proposal_id: str) -> list[str]:
        """Extract risk mitigation strategies from reviews."""
        risk_mitigation = []

        # Get red team reviews
        if self.reviews_file.exists():
            with open(self.reviews_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data["proposal_id"] == proposal_id and data["review_type"] == "red_team":
                                risk_assessment = data.get("risk_assessment", {})
                                if "mitigation" in risk_assessment:
                                    risk_mitigation.extend(risk_assessment["mitigation"])
                        except (json.JSONDecodeError, KeyError):
                            continue

        return risk_mitigation

    def _generate_success_metrics(self, proposal: StrawmanProposal) -> list[str]:
        """Generate success metrics for the proposal."""
        metrics = []

        # Add default metrics
        metrics.extend(
            [
                "Implementation completed on time",
                "All acceptance criteria met",
                "Code review passed",
                "Tests passing",
                "Documentation updated",
            ]
        )

        # Add proposal-specific metrics
        if proposal.success_criteria:
            metrics.extend(proposal.success_criteria)

        return metrics

    def _generate_next_steps(self, proposal_id: str, final_status: ConsensusStatus) -> list[str]:
        """Generate next steps based on final status."""
        if final_status == ConsensusStatus.VALIDATED:
            return [
                "Create implementation task in backlog",
                "Assign resources and timeline",
                "Set up monitoring and tracking",
                "Schedule regular progress reviews",
                "Prepare rollback plan",
            ]
        else:
            return [
                "Archive proposal with rejection reasons",
                "Extract lessons learned",
                "Update proposal template if needed",
                "Consider alternative approaches",
            ]


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Full Consensus Framework")
    parser.add_argument("--propose", help="Create a new strawman proposal")
    parser.add_argument("--description", help="Proposal description")
    parser.add_argument("--proposer", help="Proposer ID")
    parser.add_argument("--submit", help="Submit proposal for review")
    parser.add_argument("--red-team-review", help="Start red team review for proposal")
    parser.add_argument("--blue-team-review", help="Start blue team review for proposal")
    parser.add_argument("--add-feedback", help="Add feedback to consensus round")
    parser.add_argument("--round", type=int, help="Round number for feedback")
    parser.add_argument("--participant", help="Participant ID for feedback")
    parser.add_argument("--feedback", help="Feedback text")
    parser.add_argument("--validate-checkpoint", help="Create validation checkpoint")
    parser.add_argument("--checkpoint-type", help="Type of checkpoint")
    parser.add_argument("--validator", help="Validator ID")
    parser.add_argument("--finalize", help="Finalize consensus for proposal")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    framework = ConsensusFramework(args.config)

    if args.propose and args.description and args.proposer:
        proposal = framework.create_strawman_proposal(
            title=args.propose, description=args.description, proposer_id=args.proposer
        )
        print(f"Created proposal: {proposal.id}")
        print(f"Title: {proposal.title}")
        print(f"Status: {proposal.status.value}")

    if args.submit:
        success = framework.submit_proposal(args.submit)
        if success:
            print(f"Proposal {args.submit} submitted for review")
        else:
            print(f"Failed to submit proposal {args.submit}")

    if args.red_team_review and args.participant:
        try:
            review = framework.start_red_team_review(args.red_team_review, args.participant)
            print(f"Started red team review: {review.id}")
        except ValueError as e:
            print(f"Error: {e}")

    if args.blue_team_review and args.participant:
        try:
            review = framework.start_blue_team_review(args.blue_team_review, args.participant)
            print(f"Started blue team review: {review.id}")
        except ValueError as e:
            print(f"Error: {e}")

    if args.add_feedback and args.round and args.participant and args.feedback:
        success = framework.add_consensus_feedback(
            proposal_id=args.add_feedback,
            round_number=args.round,
            participant_id=args.participant,
            feedback=args.feedback,
        )
        if success:
            print("Feedback added successfully")
        else:
            print("Failed to add feedback")

    if args.validate_checkpoint and args.checkpoint_type and args.validator:
        checkpoint = framework.create_validation_checkpoint(
            proposal_id=args.validate_checkpoint,
            checkpoint_type=args.checkpoint_type,
            validator_id=args.validator,
            validation_level=ValidationLevel.STANDARD,
        )
        print(f"Created checkpoint: {checkpoint.checkpoint_id}")

    if args.finalize:
        try:
            result = framework.finalize_consensus(args.finalize)
            print(f"Consensus finalized for proposal: {args.finalize}")
            print(f"Final status: {result.final_status.value}")
            print(f"Consensus score: {result.consensus_score:.2f}")
            print(f"Validation score: {result.validation_score:.2f}")
            print(f"Implementation priority: {result.implementation_priority}")
            print(f"Timeline estimate: {result.timeline_estimate}")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
