#!/usr/bin/env python3
"""
Unified Retrieval API for Decision Search

Provides a single entrypoint for decision search functionality used by:
- Runtime applications
- Evaluation harness
- MCP tools

This eliminates duplicate SQL and ensures consistency across all clients.
"""

import logging
import os
import sys
from typing import Any, Dict, Optional

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.supersedence_retrieval import SupersedenceRetrieval

logger = logging.getLogger(__name__)


class UnifiedRetrievalAPI:
    """Unified API for decision retrieval across all clients"""

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.supersedence = SupersedenceRetrieval(db_connection_string)
        self.logger = logging.getLogger("unified_retrieval_api")

    def search_decisions(
        self,
        query: str,
        limit: int = 10,
        session_id: Optional[str] = None,
        include_superseded: bool = False,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Unified decision search entrypoint for all clients

        Args:
            query: Search query
            limit: Maximum number of results
            session_id: Optional session filter
            include_superseded: Whether to include superseded decisions
            debug: Whether to include debug information

        Returns:
            Dictionary with decisions and metadata
        """
        try:
            # Use supersedence retrieval for hybrid search
            decisions = self.supersedence.hybrid_search_decisions(query, limit, session_id, include_superseded)

            # Convert datetime objects to strings and Decimal to float for JSON serialization
            for decision in decisions:
                for key, value in decision.items():
                    if hasattr(value, "isoformat"):  # Check if it's a datetime object
                        decision[key] = value.isoformat()
                    elif hasattr(value, "as_tuple"):  # Check if it's a Decimal
                        decision[key] = float(value)

            # Prepare response
            response = {
                "query": query,
                "decisions": decisions,
                "total_found": len(decisions),
                "limit": limit,
                "session_id": session_id,
                "include_superseded": include_superseded,
                "api_version": "1.0",
                "source": "unified_retrieval_api",
            }

            # Add debug information if requested
            if debug:
                response["debug"] = {
                    "search_params": {
                        "query": query,
                        "limit": limit,
                        "session_id": session_id,
                        "include_superseded": include_superseded,
                    },
                    "ranking_info": [
                        {
                            "decision_key": d.get("decision_key"),
                            "rank": d.get("rank"),
                            "confidence": d.get("confidence"),
                            "final_score": d.get("final_score"),
                            "relevance_score": d.get("relevance_score"),
                            "supersedence_penalty": d.get("supersedence_penalty"),
                        }
                        for d in decisions
                    ],
                }

            self.logger.info(f"Unified search found {len(decisions)} decisions for query: {query}")
            return response

        except Exception as e:
            self.logger.error(f"Error in unified search: {e}")
            return {
                "query": query,
                "decisions": [],
                "total_found": 0,
                "limit": limit,
                "session_id": session_id,
                "include_superseded": include_superseded,
                "api_version": "1.0",
                "source": "unified_retrieval_api",
                "error": str(e),
            }

    def get_decision_by_key(self, decision_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific decision by its key

        Args:
            decision_key: Unique decision identifier

        Returns:
            Decision dictionary or None if not found
        """
        try:
            # Use the same database connection as supersedence
            import psycopg2
            from psycopg2.extras import RealDictCursor

            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT * FROM decisions WHERE decision_key = %s", (decision_key,))
                    result = cursor.fetchone()

                    if result:
                        decision = dict(result)
                        # Convert datetime objects and Decimal to float
                        for key, value in decision.items():
                            if hasattr(value, "isoformat"):
                                decision[key] = value.isoformat()
                            elif hasattr(value, "as_tuple"):  # Check if it's a Decimal
                                decision[key] = float(value)
                        return decision

                    return None

        except Exception as e:
            self.logger.error(f"Error getting decision by key {decision_key}: {e}")
            return None

    def get_decision_stats(self) -> Dict[str, Any]:
        """
        Get statistics about decisions in the system

        Returns:
            Dictionary with decision statistics
        """
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get total decisions
                    cursor.execute("SELECT COUNT(*) as total FROM decisions")
                    total_result = cursor.fetchone()
                    total = total_result["total"] if total_result else 0

                    # Get active decisions (not superseded)
                    cursor.execute("SELECT COUNT(*) as active FROM decisions WHERE superseded = FALSE")
                    active_result = cursor.fetchone()
                    active = active_result["active"] if active_result else 0

                    # Get superseded decisions
                    cursor.execute("SELECT COUNT(*) as superseded FROM decisions WHERE superseded = TRUE")
                    superseded_result = cursor.fetchone()
                    superseded = superseded_result["superseded"] if superseded_result else 0

                    # Get average confidence
                    cursor.execute("SELECT AVG(confidence) as avg_confidence FROM decisions WHERE superseded = FALSE")
                    avg_confidence_result = cursor.fetchone()
                    avg_confidence = avg_confidence_result["avg_confidence"] if avg_confidence_result else None

                    return {
                        "total_decisions": total,
                        "active_decisions": active,
                        "superseded_decisions": superseded,
                        "average_confidence": float(avg_confidence) if avg_confidence else 0.0,
                        "api_version": "1.0",
                    }

        except Exception as e:
            self.logger.error(f"Error getting decision stats: {e}")
            return {"error": str(e), "api_version": "1.0"}


# Global instance for easy access
_unified_api = None


def get_unified_api(db_connection_string: Optional[str] = None) -> UnifiedRetrievalAPI:
    """
    Get or create the global unified API instance

    Args:
        db_connection_string: Database connection string (optional if already initialized)

    Returns:
        UnifiedRetrievalAPI instance
    """
    global _unified_api

    if _unified_api is None:
        if db_connection_string is None:
            # Default to the same connection string used in the project
            db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

        _unified_api = UnifiedRetrievalAPI(db_connection_string)

    return _unified_api


def search_decisions(
    query: str,
    limit: int = 10,
    session_id: Optional[str] = None,
    include_superseded: bool = False,
    debug: bool = False,
    db_connection_string: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function for decision search

    Args:
        query: Search query
        limit: Maximum number of results
        session_id: Optional session filter
        include_superseded: Whether to include superseded decisions
        debug: Whether to include debug information
        db_connection_string: Database connection string (optional)

    Returns:
        Dictionary with decisions and metadata
    """
    api = get_unified_api(db_connection_string)
    return api.search_decisions(query, limit, session_id, include_superseded, debug)


if __name__ == "__main__":
    # Test the unified API
    import json

    # Initialize API
    api = UnifiedRetrievalAPI("postgresql://danieljacobs@localhost:5432/ai_agency")

    # Test search
    print("Testing unified retrieval API...")
    result = api.search_decisions("postgresql", 5, debug=True)
    print(json.dumps(result, indent=2))

    # Test stats
    print("\nDecision statistics:")
    stats = api.get_decision_stats()
    print(json.dumps(stats, indent=2))
