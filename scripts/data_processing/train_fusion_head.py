from __future__ import annotations
import argparse
import json
import logging
import os
import random
import sys
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from train.fusion_dataset import build_pairs, load_gold_cases
from train.fusion_head import FusionHead
from src.dspy_modules.retriever.fusion_head import load_feature_spec
#!/usr/bin/env python3
"""
Training script for learned fusion head.

This script trains a PyTorch neural network to learn optimal fusion weights
for combining multiple retrieval signals (BM25, vector similarity, etc.).
"""

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# sys.path.insert(0, str(project_root / "dspy-rag-system"))  # REMOVED: DSPy venv consolidated into main project

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def pairwise_loss(pos_scores: torch.Tensor, neg_scores: torch.Tensor, margin: float = 0.2) -> torch.Tensor:
    """
    Compute pairwise ranking loss.

    Args:
        pos_scores: Positive example scores
        neg_scores: Negative example scores
        margin: Margin for ranking loss

    Returns:
        Pairwise loss tensor
    """
    return torch.relu(margin - (pos_scores - neg_scores)).mean()

def bce_loss(scores: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
    """
    Compute binary cross-entropy loss.

    Args:
        scores: Predicted scores
        labels: Binary labels (0 or 1)

    Returns:
        BCE loss tensor
    """
    return nn.functional.binary_cross_entropy_with_logits(scores, labels.float())

def compute_pairwise_accuracy(pos_scores: torch.Tensor, neg_scores: torch.Tensor) -> float:
    """
    Compute pairwise accuracy (fraction of pairs where pos > neg).

    Args:
        pos_scores: Positive example scores
        neg_scores: Negative example scores

    Returns:
        Pairwise accuracy as float
    """
    with torch.no_grad():
        correct = (pos_scores > neg_scores).float().mean().item()
    return correct

def train_epoch(
    model: nn.Module, dataloader: DataLoader, optimizer: optim.Optimizer, loss_fn: str, device: torch.device
) -> tuple[float, float]:
    """
    Train model for one epoch.

    Args:
        model: PyTorch model
        dataloader: Training data loader
        optimizer: Optimizer
        loss_fn: Loss function type ('pairwise' or 'bce')
        device: Device to run on

    Returns:
        Tuple of (average_loss, pairwise_accuracy)
    """
    model.train()
    total_loss = 0.0
    total_pairs = 0
    correct_pairs = 0

    for batch in dataloader:
        pos_features, neg_features = batch
        pos_features = pos_features.to(device)
        neg_features = neg_features.to(device)

        optimizer.zero_grad()

        # Forward pass
        pos_scores = model(pos_features)
        neg_scores = model(neg_features)

        # Compute loss
        if loss_fn == "pairwise":
            loss = pairwise_loss(pos_scores, neg_scores)
        else:  # bce
            # For BCE, we treat positive examples as label 1, negative as label 0
            pos_labels = torch.ones_like(pos_scores)
            neg_labels = torch.zeros_like(neg_scores)
            all_scores = torch.cat([pos_scores, neg_scores])
            all_labels = torch.cat([pos_labels, neg_labels])
            loss = bce_loss(all_scores, all_labels)

        # Backward pass
        loss.backward()
        optimizer.step()

        # Track metrics
        total_loss += loss.item()
        total_pairs += pos_features.size(0)
        correct_pairs += (pos_scores > neg_scores).sum().item()

    avg_loss = total_loss / len(dataloader)
    pairwise_acc = correct_pairs / total_pairs if total_pairs > 0 else 0.0

    return avg_loss, pairwise_acc

def validate_epoch(model: nn.Module, dataloader: DataLoader, loss_fn: str, device: torch.device) -> tuple[float, float]:
    """
    Validate model for one epoch.

    Args:
        model: PyTorch model
        dataloader: Validation data loader
        loss_fn: Loss function type
        device: Device to run on

    Returns:
        Tuple of (average_loss, pairwise_accuracy)
    """
    model.eval()
    total_loss = 0.0
    total_pairs = 0
    correct_pairs = 0

    with torch.no_grad():
        for batch in dataloader:
            pos_features, neg_features = batch
            pos_features = pos_features.to(device)
            neg_features = neg_features.to(device)

            # Forward pass
            pos_scores = model(pos_features)
            neg_scores = model(neg_features)

            # Compute loss
            if loss_fn == "pairwise":
                loss = pairwise_loss(pos_scores, neg_scores)
            else:  # bce
                pos_labels = torch.ones_like(pos_scores)
                neg_labels = torch.zeros_like(neg_scores)
                all_scores = torch.cat([pos_scores, neg_scores])
                all_labels = torch.cat([pos_labels, neg_labels])
                loss = bce_loss(all_scores, all_labels)

            # Track metrics
            total_loss += loss.item()
            total_pairs += pos_features.size(0)
            correct_pairs += (pos_scores > neg_scores).sum().item()

    avg_loss = total_loss / len(dataloader)
    pairwise_acc = correct_pairs / total_pairs if total_pairs > 0 else 0.0

    return avg_loss, pairwise_acc

def main():
    parser = argparse.ArgumentParser(description="Train fusion head for retrieval scoring")

    # Data arguments
    parser.add_argument("--cases", default="evals/gold/v1/gold_cases.jsonl", help="Path to gold cases JSONL file")
    parser.add_argument("--pairs-per-query", type=int, default=8, help="Number of positive/negative pairs per query")
    parser.add_argument("--k-pool", type=int, default=60, help="Number of candidates to retrieve per query")
    parser.add_argument(
        "--embed-model",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence transformer model for embeddings",
    )

    # Model arguments
    parser.add_argument("--loss", choices=["pairwise", "bce"], default="pairwise", help="Loss function type")
    parser.add_argument("--hidden", type=int, default=0, help="Hidden layer size (0 for linear model)")
    parser.add_argument("--epochs", type=int, default=12, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")

    # Training arguments
    parser.add_argument("--seed", type=int, default=13, help="Random seed")
    parser.add_argument("--val-split", type=float, default=0.2, help="Validation split ratio")

    # Output arguments
    parser.add_argument("--ckpt-out", default="configs/learned_fusion.pt", help="Output checkpoint path")
    parser.add_argument("--report-out", default="metrics/fusion_head_report.json", help="Output metrics report path")
    parser.add_argument("--feature-spec", default="configs/feature_spec_v1.json", help="Feature specification file")

    args = parser.parse_args()

    # Set random seeds
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # Load feature specification
    feature_names = load_feature_spec(args.feature_spec)
    in_dim = len(feature_names)
    logger.info(f"Feature specification: {feature_names} (dim={in_dim})")

    # Load gold cases
    logger.info(f"Loading gold cases from {args.cases}")
    cases = load_gold_cases(args.cases)
    logger.info(f"Loaded {len(cases)} gold cases")

    # Build training pairs
    logger.info("Building training pairs...")
    pairs = build_pairs(cases, args.pairs_per_query, args.k_pool, args.embed_model, feature_names)

    if len(pairs) == 0:
        logger.error("No training pairs generated. Check gold cases and retrieval system.")
        return 1

    logger.info(f"Generated {len(pairs)} training pairs")

    # Convert to tensors
    pos_features = torch.tensor([pair[0] for pair in pairs], dtype=torch.float32)
    neg_features = torch.tensor([pair[1] for pair in pairs], dtype=torch.float32)

    # Create train/val split
    n_total = len(pairs)
    n_val = int(n_total * args.val_split)
    n_train = n_total - n_val

    indices = torch.randperm(n_total)
    train_indices = indices[:n_train]
    val_indices = indices[n_train:]

    train_pos = pos_features[train_indices]
    train_neg = neg_features[train_indices]
    val_pos = pos_features[val_indices]
    val_neg = neg_features[val_indices]

    # Create data loaders
    train_dataset = TensorDataset(train_pos, train_neg)
    val_dataset = TensorDataset(val_pos, val_neg)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

    logger.info(f"Train: {n_train} pairs, Val: {n_val} pairs")

    # Create model
    model = FusionHead(in_dim=in_dim, hidden=args.hidden)
    model.to(device)

    logger.info(f"Model created: {model.get_num_parameters()} parameters")

    # Create optimizer
    optimizer = optim.AdamW(model.parameters(), lr=args.lr)

    # Training loop
    best_val_acc = 0.0
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []

    logger.info("Starting training...")
    for epoch in range(args.epochs):
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, args.loss, device)

        # Validate
        val_loss, val_acc = validate_epoch(model, val_loader, args.loss, device)

        # Track metrics
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)

        logger.info(
            f"Epoch {epoch+1}/{args.epochs}: "
            f"Train Loss={train_loss:.4f}, Train Acc={train_acc:.4f}, "
            f"Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}"
        )

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), args.ckpt_out)
            logger.info(f"New best model saved (val_acc={val_acc:.4f})")

    # Create output directory if needed
    os.makedirs(os.path.dirname(args.report_out), exist_ok=True)

    # Save training report
    report = {
        "in_dim": in_dim,
        "hidden": args.hidden,
        "loss": args.loss,
        "epochs": args.epochs,
        "seed": args.seed,
        "train_pairs": n_train,
        "val_pairs": n_val,
        "total_pairs": n_total,
        "final_train_loss": train_losses[-1],
        "final_val_loss": val_losses[-1],
        "final_train_acc": train_accs[-1],
        "final_val_acc": val_accs[-1],
        "best_val_acc": best_val_acc,
        "train_losses": train_losses,
        "val_losses": val_losses,
        "train_accs": train_accs,
        "val_accs": val_accs,
        "feature_names": feature_names,
        "model_params": model.get_num_parameters(),
    }

    with open(args.report_out, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Training complete. Model saved to {args.ckpt_out}")
    logger.info(f"Report saved to {args.report_out}")
    logger.info(f"Best validation accuracy: {best_val_acc:.4f}")

    return 0

if __name__ == "__main__":
    sys.exit(main())