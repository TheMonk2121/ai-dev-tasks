"""
Phase 4: Uncertainty, Calibration & Feedback Integration

Integrates confidence calibration, selective answering, and feedback loops
into the RAG system for production-ready uncertainty quantification.
"""

import logging
import time
import json
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import numpy as np

from uncertainty.confidence_calibration import (
    ConfidenceCalibrator, 
    CalibrationConfig,
    create_calibration_dataset
)
from uncertainty.selective_answering import (
    SelectiveAnswering, 
    SelectiveAnsweringConfig,
    EvidenceQuality
)
from uncertainty.feedback_loops import (
    FeedbackCollector,
    FeedbackProcessor,
    FeedbackConfig,
    FeedbackType,
    FeedbackPriority
)

logger = logging.getLogger(__name__)


@dataclass
class Phase4Config:
    """Configuration for Phase 4 uncertainty and feedback integration."""
    
    # Confidence calibration
    calibration: CalibrationConfig = None
    
    # Selective answering
    selective_answering: SelectiveAnsweringConfig = None
    
    # Feedback loops
    feedback: FeedbackConfig = None
    
    # Integration settings
    enable_confidence_calibration: bool = True
    enable_selective_answering: bool = True
    enable_feedback_loops: bool = True
    
    # Production settings
    auto_calibration: bool = True
    calibration_interval_hours: int = 24
    feedback_processing_interval_minutes: int = 30
    
    # Output paths
    phase4_output_path: str = "metrics/phase4/"
    calibration_models_path: str = "models/phase4/calibration/"
    feedback_reports_path: str = "metrics/phase4/feedback/"


class Phase4RAGSystem:
    """
    Phase 4 RAG system with uncertainty quantification and feedback loops.
    
    Features:
    - Confidence calibration with temperature scaling and isotonic regression
    - Evidence quality-based selective answering
    - User feedback collection and processing
    - Continuous improvement through feedback analysis
    """
    
    def __init__(self, config: Phase4Config):
        # Set default configs if None
        if config.calibration is None:
            config.calibration = CalibrationConfig()
        if config.selective_answering is None:
            config.selective_answering = SelectiveAnsweringConfig()
        if config.feedback is None:
            config.feedback = FeedbackConfig()
            
        self.config = config
        self._init_components()
        logger.info("Initialized Phase 4 RAG System with uncertainty quantification")
    
    def _init_components(self):
        """Initialize Phase 4 components."""
        
        # Ensure output directories exist
        Path(self.config.phase4_output_path).mkdir(parents=True, exist_ok=True)
        Path(self.config.calibration_models_path).mkdir(parents=True, exist_ok=True)
        Path(self.config.feedback_reports_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize confidence calibrator
        if self.config.enable_confidence_calibration:
            self.calibrator = ConfidenceCalibrator(self.config.calibration)
            logger.info("Confidence calibrator initialized")
        else:
            self.calibrator = None
        
        # Initialize selective answering
        if self.config.enable_selective_answering:
            self.selective_answering = SelectiveAnswering(self.config.selective_answering)
            logger.info("Selective answering initialized")
        else:
            self.selective_answering = None
        
        # Initialize feedback components
        if self.config.enable_feedback_loops:
            self.feedback_collector = FeedbackCollector(self.config.feedback)
            self.feedback_processor = FeedbackProcessor(self.config.feedback)
            logger.info("Feedback loops initialized")
        else:
            self.feedback_collector = None
            self.feedback_processor = None
    
    def process_query_with_uncertainty(
        self,
        query: str,
        evidence_chunks: List[Dict[str, Any]],
        raw_confidence_score: float,
        answer: Optional[str] = None,
        sub_claims: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a query with full uncertainty quantification and selective answering.
        
        Args:
            query: User query
            evidence_chunks: Retrieved evidence chunks with scores
            raw_confidence_score: Raw confidence score from RAG system
            answer: Generated answer (if available)
            sub_claims: Sub-claims to check coverage
            user_id: User identifier for feedback
            session_id: Session identifier for feedback
            
        Returns:
            Processed response with uncertainty quantification
        """
        
        start_time = time.time()
        logger.info(f"Processing query with uncertainty quantification: {query[:50]}...")
        
        # Step 1: Apply confidence calibration if enabled
        calibrated_confidence = self._apply_confidence_calibration(
            raw_confidence_score, evidence_chunks
        )
        
        # Step 2: Evaluate answer quality and make selective answering decision
        quality_evaluation = None
        should_abstain = False
        
        if self.selective_answering and answer:
            quality_evaluation = self.selective_answering.evaluate_answer_quality(
                query=query,
                answer=answer,
                evidence_chunks=evidence_chunks,
                confidence_score=calibrated_confidence,
                sub_claims=sub_claims
            )
            should_abstain = quality_evaluation["should_abstain"]
        
        # Step 3: Generate response
        if should_abstain:
            response = self._generate_abstention_response(
                query, quality_evaluation, evidence_chunks
            )
        else:
            response = self._generate_standard_response(
                query, answer, evidence_chunks, calibrated_confidence, quality_evaluation
            )
        
        # Step 4: Collect implicit feedback if enabled
        if self.feedback_collector:
            self._collect_implicit_feedback(
                query, answer, calibrated_confidence, evidence_chunks, 
                response_time_ms=(time.time() - start_time) * 1000,
                user_id=user_id, session_id=session_id
            )
        
        # Add metadata
        response.update({
            "phase4_metadata": {
                "confidence_calibrated": self.config.enable_confidence_calibration,
                "selective_answering_enabled": self.config.enable_selective_answering,
                "feedback_loops_enabled": self.config.enable_feedback_loops,
                "processing_time_ms": (time.time() - start_time) * 1000,
                "timestamp": time.time()
            }
        })
        
        logger.info(f"Query processed with uncertainty quantification in {response['phase4_metadata']['processing_time_ms']:.2f}ms")
        
        return response
    
    def _apply_confidence_calibration(
        self, 
        raw_confidence: float, 
        evidence_chunks: List[Dict[str, Any]]
    ) -> float:
        """Apply confidence calibration if enabled."""
        
        if not self.calibrator or not self.calibrator.is_calibrated:
            logger.debug("Confidence calibration not available, using raw confidence")
            return raw_confidence
        
        # Convert single confidence score to array for calibration
        confidence_array = np.array([raw_confidence])
        
        # Apply calibration
        calibrated_confidence = self.calibrator.apply_calibration(
            confidence_array, method="temperature"
        )[0]
        
        logger.debug(f"Confidence calibrated: {raw_confidence:.3f} -> {calibrated_confidence:.3f}")
        return calibrated_confidence
    
    def _generate_abstention_response(
        self,
        query: str,
        quality_evaluation: Dict[str, Any],
        evidence_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate response when abstaining from answering."""
        
        if not self.selective_answering:
            return {"error": "Selective answering not enabled"}
        
        response = self.selective_answering.format_abstention_response(
            query, quality_evaluation, evidence_chunks
        )
        
        # Add evidence quality metrics
        if "evidence_quality" in quality_evaluation:
            evidence_quality = quality_evaluation["evidence_quality"]
            response["evidence_quality"] = {
                "coverage_score": evidence_quality.coverage_score,
                "dispersion_score": evidence_quality.dispersion_score,
                "evidence_count": evidence_quality.evidence_count,
                "max_evidence_score": evidence_quality.max_evidence_score,
                "has_contradictions": evidence_quality.has_contradictions
            }
        
        return response
    
    def _generate_standard_response(
        self,
        query: str,
        answer: str,
        evidence_chunks: List[Dict[str, Any]],
        calibrated_confidence: float,
        quality_evaluation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate standard response with uncertainty quantification."""
        
        response = {
            "query": query,
            "answer": answer,
            "abstained": False,
            "confidence_score": calibrated_confidence,
            "evidence_chunks": evidence_chunks[:5],  # Top 5 evidence pieces
            "evidence_count": len(evidence_chunks)
        }
        
        # Add quality evaluation if available
        if quality_evaluation:
            response["quality_score"] = quality_evaluation["quality_score"]
            response["evidence_quality"] = {
                "coverage_score": quality_evaluation["evidence_quality"].coverage_score,
                "dispersion_score": quality_evaluation["evidence_quality"].dispersion_score,
                "consistency_score": quality_evaluation["consistency_score"]
            }
        
        return response
    
    def _collect_implicit_feedback(
        self,
        query: str,
        answer: str,
        confidence_score: float,
        evidence_chunks: List[Dict[str, Any]],
        response_time_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Collect implicit feedback based on system behavior."""
        
        # For now, we'll collect basic feedback
        # In production, this would integrate with user interaction tracking
        
        # Example: Collect feedback on response time
        if response_time_ms > 5000:  # 5 seconds
            self.feedback_collector.collect_feedback(
                query=query,
                answer=answer,
                feedback_type=FeedbackType.RESPONSE_SPEED,
                feedback_value=2,  # Low rating
                confidence_score=confidence_score,
                evidence_chunks=evidence_chunks,
                response_time_ms=response_time_ms,
                user_id=user_id,
                session_id=session_id,
                priority=FeedbackPriority.MEDIUM,
                tags=["implicit", "slow_response"]
            )
    
    def calibrate_confidence_model(
        self,
        evaluation_results: List[Dict[str, Any]],
        method: str = "temperature"
    ) -> Dict[str, Any]:
        """
        Calibrate the confidence model using evaluation results.
        
        Args:
            evaluation_results: List of evaluation results with confidence scores and labels
            method: Calibration method to use
            
        Returns:
            Calibration results and metrics
        """
        
        if not self.calibrator:
            logger.error("Confidence calibrator not enabled")
            return {"error": "Confidence calibrator not enabled"}
        
        logger.info(f"Starting confidence calibration with method: {method}")
        
        # Create calibration dataset
        scores, labels = create_calibration_dataset(evaluation_results)
        
        if len(scores) < 10:
            logger.warning(f"Insufficient data for calibration: {len(scores)} samples")
            return {"error": "Insufficient data for calibration", "sample_count": len(scores)}
        
        # Perform calibration
        calibration_results = self.calibrator.calibrate_confidence(
            scores, labels, method
        )
        
        # Save calibrated model
        timestamp = int(time.time())
        model_path = f"{self.config.calibration_models_path}/calibrator_{timestamp}.json"
        self.calibrator.save_calibrator(model_path)
        
        # Save calibration results
        results_path = f"{self.config.phase4_output_path}/calibration_results_{timestamp}.json"
        with open(results_path, 'w') as f:
            json.dump(calibration_results, f, indent=2)
        
        logger.info(f"Confidence calibration complete. Model saved to {model_path}")
        
        return {
            "calibration_results": calibration_results,
            "model_path": model_path,
            "results_path": results_path,
            "sample_count": len(scores)
        }
    
    def load_calibrated_model(self, model_path: str) -> bool:
        """Load a previously calibrated confidence model."""
        
        if not self.calibrator:
            logger.error("Confidence calibrator not enabled")
            return False
        
        try:
            self.calibrator.load_calibrator(model_path)
            logger.info(f"Loaded calibrated model from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load calibrated model: {e}")
            return False
    
    def process_feedback_batch(self) -> Dict[str, Any]:
        """Process a batch of user feedback."""
        
        if not self.feedback_processor:
            logger.error("Feedback processor not enabled")
            return {"error": "Feedback processor not enabled"}
        
        return self.feedback_processor.process_feedback_batch()
    
    def generate_feedback_report(self, report_type: str = "weekly") -> Dict[str, Any]:
        """Generate a feedback report."""
        
        if not self.feedback_processor:
            logger.error("Feedback processor not enabled")
            return {"error": "Feedback processor not enabled"}
        
        if report_type == "weekly":
            return self.feedback_processor.generate_weekly_report()
        else:
            logger.error(f"Unknown report type: {report_type}")
            return {"error": f"Unknown report type: {report_type}"}
    
    def collect_explicit_feedback(
        self,
        query: str,
        answer: str,
        feedback_type: FeedbackType,
        feedback_value: Union[bool, int, float, str],
        confidence_score: float,
        evidence_chunks: List[Dict[str, Any]],
        response_time_ms: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        feedback_text: Optional[str] = None,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        tags: Optional[List[str]] = None
    ) -> str:
        """Collect explicit user feedback."""
        
        if not self.feedback_collector:
            logger.error("Feedback collector not enabled")
            return ""
        
        return self.feedback_collector.collect_feedback(
            query=query,
            answer=answer,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            confidence_score=confidence_score,
            evidence_chunks=evidence_chunks,
            response_time_ms=response_time_ms,
            user_id=user_id,
            session_id=session_id,
            feedback_text=feedback_text,
            priority=priority,
            tags=tags
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current Phase 4 system status."""
        
        status = {
            "phase": "Phase 4: Uncertainty, Calibration & Feedback",
            "components": {
                "confidence_calibration": {
                    "enabled": self.config.enable_confidence_calibration,
                    "calibrated": self.calibrator.is_calibrated if self.calibrator else False,
                    "method": "temperature_scaling" if self.calibrator else None
                },
                "selective_answering": {
                    "enabled": self.config.enable_selective_answering,
                    "abstain_threshold": self.config.selective_answering.abstain_threshold if self.config.enable_selective_answering else None
                },
                "feedback_loops": {
                    "enabled": self.config.enable_feedback_loops,
                    "database_path": self.config.feedback.db_path if self.config.enable_feedback_loops else None
                }
            },
            "configuration": {
                "auto_calibration": self.config.auto_calibration,
                "calibration_interval_hours": self.config.calibration_interval_hours,
                "feedback_processing_interval_minutes": self.config.feedback_processing_interval_minutes
            }
        }
        
        # Add feedback statistics if available
        if self.feedback_collector:
            try:
                stats = self.feedback_collector.db.get_feedback_statistics()
                status["feedback_statistics"] = stats
            except Exception as e:
                logger.warning(f"Failed to get feedback statistics: {e}")
                status["feedback_statistics"] = {"error": str(e)}
        
        return status
    
    def update_configuration(self, new_config: Phase4Config) -> bool:
        """Update Phase 4 configuration."""
        
        try:
            self.config = new_config
            self._init_components()
            logger.info("Phase 4 configuration updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update Phase 4 configuration: {e}")
            return False
