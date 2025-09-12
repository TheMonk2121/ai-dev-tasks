from __future__ import annotations
import sys
from unittest.mock import MagicMock
"""Mock RAGChecker to prevent Torch imports in unit tests."""



# Mock the RAGChecker modules to prevent Torch imports
class MockRAGCheckerEvaluator:
    """Mock RAGChecker evaluator for unit tests."""

    def __init__(self, *args, **kwargs):
        self.mock_data = {"status": "mocked", "results": []}

    def evaluate(self, *args, **kwargs):
        return self.mock_data

    def __getattr__(self, name):
        # Return a mock for any attribute access
        return MagicMock()


# Mock the entire ragchecker module
mock_ragchecker = MagicMock()
mock_ragchecker.OfficialRAGCheckerEvaluator = MockRAGCheckerEvaluator

# Mock sentence_transformers to prevent Torch imports
mock_sentence_transformers = MagicMock()
mock_sentence_transformers.SentenceTransformer = MagicMock()

# Mock transformers to prevent Torch imports
mock_transformers = MagicMock()

# Mock torch to prevent import issues
mock_torch = MagicMock()

# Apply mocks to sys.modules
sys.modules["ragchecker"] = mock_ragchecker
sys.modules["sentence_transformers"] = mock_sentence_transformers
sys.modules["transformers"] = mock_transformers
sys.modules["torch"] = mock_torch

# Also mock common torch submodules
sys.modules["torch.nn"] = MagicMock()
sys.modules["torch.utils"] = MagicMock()
sys.modules["torch.utils.data"] = MagicMock()