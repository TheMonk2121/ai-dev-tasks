from __future__ import annotations
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
        from scipy.optimize import minimize
        from scipy.optimize import minimize
        from sklearn.calibration import calibration_curve
import sys
from typing import Any, Dict, List, Optional, Union
"""
Phase 4: Confidence Calibration Module

Implements temperature scaling and confidence calibration for production-ready
uncertainty quantification in the RAG system.
"""



logger = logging.getLogger(__name__)


@dataclass
class CalibrationConfig:
    """Configuration for confidence calibration."""

    # Temperature scaling parameters
    temperature_scaling: bool = True
    temperature_init: float = 1.0
    temperature_lr: float = 0.01
    temperature_epochs: int = 100

    # Isotonic regression parameters
    isotonic_calibration: bool = True
    cv_folds: int = 5

    # Platt scaling parameters
    platt_calibration: bool = False

    # Calibration thresholds
    min_confidence: float = 0.1
    max_confidence: float = 0.95
    abstain_threshold: float = 0.3

    # Output paths
    model_save_path: str = "models/calibration/"
    results_save_path: str = "metrics/calibration/"


class ConfidenceCalibrator:
    """
    Implements multiple confidence calibration methods for RAG system outputs.

    Methods:
    - Temperature scaling (Platt scaling)
    - Isotonic regression
    - Platt scaling (logistic regression)
    """

    def __init__(self, config: CalibrationConfig):
        self.config = config
        self.temperature = 1.0
        self.isotonic_calibrator = None
        self.platt_calibrator = None
        self.is_calibrated = False

        # Ensure output directories exist
        Path(self.config.model_save_path).mkdir(parents=True, exist_ok=True)
        Path(self.config.results_save_path).mkdir(parents=True, exist_ok=True)

    def calibrate_temperature(self, logits: np.ndarray, labels: np.ndarray) -> float:
        """
        Calibrate temperature scaling parameter using validation data.

        Args:
            logits: Raw model logits [n_samples, n_classes]
            labels: Ground truth labels [n_samples]

        Returns:
            Optimal temperature parameter
        """
        logger.info("Calibrating temperature scaling parameter...")

        # Convert to probabilities if needed
        if logits.ndim == 1:
            probs = self._sigmoid(logits)
        else:
            probs = self._softmax(logits)

        # Binary case: use sigmoid temperature scaling
        if probs.ndim == 1 or probs.shape[1] == 2:
            self.temperature = self._calibrate_binary_temperature(probs, labels)
        else:
            self.temperature = self._calibrate_multiclass_temperature(probs, labels)

        logger.info(f"Optimal temperature: {self.temperature:.4f}")
        return self.temperature

    def _calibrate_binary_temperature(self, probs: np.ndarray, labels: np.ndarray) -> float:
        """Calibrate temperature for binary classification."""

        def objective(t):
            calibrated_probs = self._sigmoid(np.log(probs / (1 - probs)) / t)
            return -np.mean(
                labels * np.log(calibrated_probs + 1e-10) + (1 - labels) * np.log(1 - calibrated_probs + 1e-10)
            )

        result = minimize(objective, x0=self.config.temperature_init, method="L-BFGS-B", bounds=[(0.1, 10.0)])

        return result.x[0]

    def _calibrate_multiclass_temperature(self, probs: np.ndarray, labels: np.ndarray) -> float:
        """Calibrate temperature for multiclass classification."""

        def objective(t):
            calibrated_probs = self._softmax(np.log(probs + 1e-10) / t)
            return -np.mean([np.log(calibrated_probs[i, labels[i]] + 1e-10) for i in range(len(labels))])

        result = minimize(objective, x0=self.config.temperature_init, method="L-BFGS-B", bounds=[(0.1, 10.0)])

        return result.x[0]

    def calibrate_isotonic(self, scores: np.ndarray, labels: np.ndarray) -> None:
        """
        Calibrate isotonic regression for non-parametric calibration.

        Args:
            scores: Raw confidence scores [n_samples]
            labels: Ground truth labels [n_samples]
        """
        if not self.config.isotonic_calibration:
            return

        logger.info("Calibrating isotonic regression...")

        # Use cross-validation for isotonic calibration
        self.isotonic_calibrator = CalibratedClassifierCV(
            estimator=None, cv=self.config.cv_folds, method="isotonic"  # Use isotonic regression
        )

        # Reshape for sklearn compatibility
        if scores.ndim == 1:
            scores_2d = scores.reshape(-1, 1)
        else:
            scores_2d = scores

        self.isotonic_calibrator.fit(scores_2d, labels)
        logger.info("Isotonic calibration complete")

    def calibrate_platt(self, scores: np.ndarray, labels: np.ndarray) -> None:
        """
        Calibrate Platt scaling (logistic regression) for parametric calibration.

        Args:
            scores: Raw confidence scores [n_samples]
            labels: Ground truth labels [n_samples]
        """
        if not self.config.platt_calibration:
            return

        logger.info("Calibrating Platt scaling...")

        # Use cross-validation for Platt scaling
        self.platt_calibrator = CalibratedClassifierCV(
            estimator=None, cv=self.config.cv_folds, method="sigmoid"  # Use logistic regression
        )

        # Reshape for sklearn compatibility
        if scores.ndim == 1:
            scores_2d = scores.reshape(-1, 1)
        else:
            scores_2d = scores

        self.platt_calibrator.fit(scores_2d, labels)
        logger.info("Platt scaling calibration complete")

    def calibrate_confidence(
        self, scores: np.ndarray, labels: np.ndarray, method: str = "temperature"
    ) -> dict[str, Any]:
        """
        Perform confidence calibration using specified method.

        Args:
            scores: Raw confidence scores or logits
            labels: Ground truth labels
            method: Calibration method ("temperature", "isotonic", "platt", "ensemble")

        Returns:
            Calibration results and metrics
        """
        logger.info(f"Starting confidence calibration with method: {method}")

        results = {
            "method": method,
            "temperature": None,
            "calibration_error": None,
            "ece_score": None,
            "reliability_diagram": None,
        }

        # Perform calibration based on method
        if method == "temperature" and self.config.temperature_scaling:
            self.calibrate_temperature(scores, labels)
            results["temperature"] = self.temperature

        elif method == "isotonic" and self.config.isotonic_calibration:
            self.calibrate_isotonic(scores, labels)

        elif method == "platt" and self.config.platt_calibration:
            self.calibrate_platt(scores, labels)

        elif method == "ensemble":
            # Use multiple methods and ensemble
            self.calibrate_temperature(scores, labels)
            self.calibrate_isotonic(scores, labels)
            self.calibrate_platt(scores, labels)
            results["temperature"] = self.temperature

        # Calculate calibration metrics
        calibrated_scores = self.apply_calibration(scores, method)
        results.update(self._calculate_calibration_metrics(calibrated_scores, labels))

        self.is_calibrated = True
        logger.info("Confidence calibration complete")

        return results

    def apply_calibration(self, scores: np.ndarray, method: str = "temperature") -> np.ndarray:
        """
        Apply calibrated confidence scores.

        Args:
            scores: Raw confidence scores or logits
            method: Calibration method to apply

        Returns:
            Calibrated confidence scores
        """
        if not self.is_calibrated:
            logger.warning("Calibrator not fitted. Returning original scores.")
            return scores

        if method == "temperature" and self.temperature != 1.0:
            if scores.ndim == 1:
                return self._sigmoid(np.log(scores / (1 - scores + 1e-10)) / self.temperature)
            else:
                return self._softmax(np.log(scores + 1e-10) / self.temperature)

        elif method == "isotonic" and self.isotonic_calibrator:
            if scores.ndim == 1:
                scores_2d = scores.reshape(-1, 1)
            else:
                scores_2d = scores
            return self.isotonic_calibrator.predict_proba(scores_2d)[:, 1]

        elif method == "platt" and self.platt_calibrator:
            if scores.ndim == 1:
                scores_2d = scores.reshape(-1, 1)
            else:
                scores_2d = scores
            return self.platt_calibrator.predict_proba(scores_2d)[:, 1]

        # Return original scores if no calibration method available
        return scores

    def _calculate_calibration_metrics(self, calibrated_scores: np.ndarray, labels: np.ndarray) -> dict[str, Any]:
        """Calculate calibration error and ECE score."""

        # Calculate calibration curve
        fraction_of_positives, mean_predicted_value = calibration_curve(labels, calibrated_scores, n_bins=10)

        # Calculate Expected Calibration Error (ECE)
        bin_boundaries = np.linspace(0, 1, 11)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]

        ece = 0.0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find predictions in this bin
            in_bin = np.logical_and(calibrated_scores > bin_lower, calibrated_scores <= bin_upper)
            prop_in_bin = np.mean(in_bin)
            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(labels[in_bin])
                avg_confidence_in_bin = np.mean(calibrated_scores[in_bin])
                ece += prop_in_bin * np.abs(accuracy_in_bin - avg_confidence_in_bin)

        return {
            "calibration_error": np.mean(np.abs(fraction_of_positives - mean_predicted_value)),
            "ece_score": ece,
            "reliability_diagram": {
                "fraction_of_positives": fraction_of_positives.tolist(),
                "mean_predicted_value": mean_predicted_value.tolist(),
            },
        }

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Apply sigmoid function."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Apply softmax function."""
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

    def save_calibrator(self, filepath: str) -> None:
        """Save the calibrated model to disk."""
        if not self.is_calibrated:
            logger.warning("No calibrated model to save")
            return

        save_data = {
            "config": self.config.__dict__,
            "temperature": self.temperature,
            "is_calibrated": self.is_calibrated,
        }

        # Save main calibrator data
        with open(filepath, "w") as f:
            json.dump(save_data, f, indent=2)

        # Save sklearn calibrators if they exist
        if self.isotonic_calibrator:
            isotonic_path = filepath.replace(".json", "_isotonic.pkl")
            joblib.dump(self.isotonic_calibrator, isotonic_path)

        if self.platt_calibrator:
            platt_path = filepath.replace(".json", "_platt.pkl")
            joblib.dump(self.platt_calibrator, platt_path)

        logger.info(f"Calibrator saved to {filepath}")

    def load_calibrator(self, filepath: str) -> None:
        """Load a calibrated model from disk."""
        if not os.path.exists(filepath):
            logger.error(f"Calibrator file not found: {filepath}")
            return

        # Load main calibrator data
        with open(filepath) as f:
            save_data = json.load(f)

        self.config = CalibrationConfig(**save_data["config"])
        self.temperature = save_data["temperature"]
        self.is_calibrated = save_data["is_calibrated"]

        # Load sklearn calibrators if they exist
        base_path = filepath.replace(".json", "")

        isotonic_path = base_path + "_isotonic.pkl"
        if os.path.exists(isotonic_path):
            self.isotonic_calibrator = joblib.load(isotonic_path)

        platt_path = base_path + "_platt.pkl"
        if os.path.exists(platt_path):
            self.platt_calibrator = joblib.load(platt_path)

        logger.info(f"Calibrator loaded from {filepath}")


def create_calibration_dataset(evaluation_results: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    """
    Create calibration dataset from evaluation results.

    Args:
        evaluation_results: List of evaluation results with confidence scores and labels

    Returns:
        Tuple of (scores, labels) for calibration
    """
    scores = []
    labels = []

    for result in evaluation_results:
        if "confidence_score" in result and "is_correct" in result:
            scores.append(result["confidence_score"])
            labels.append(1 if result["is_correct"] else 0)

    return np.array(scores), np.array(labels)
