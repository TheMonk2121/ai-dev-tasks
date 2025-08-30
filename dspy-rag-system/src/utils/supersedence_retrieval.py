#!/usr/bin/env python3
"""
Supersedence and Decision-First Retrieval System

Implements supersedence logic for conflicting decisions, hybrid BM25 + Vector search,
deduplication, and decision-first retrieval with supersedence penalties.
"""

import logging
import re
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class SupersedenceRetrieval:
    """Supersedence and decision-first retrieval system"""

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.logger = logging.getLogger("supersedence_retrieval")

    def detect_conflicts(self, new_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect conflicting decisions for supersedence

        Args:
            new_decision: New decision to check for conflicts

        Returns:
            List of conflicting decisions
        """
        try:
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Extract key terms from the new decision
                    key_terms = self._extract_key_terms(new_decision["head"])

                    # Find potential conflicts based on key terms
                    conflicts = []
                    for term in key_terms:
                        cursor.execute(
                            """
                            SELECT * FROM decisions
                            WHERE (head ILIKE %s OR rationale ILIKE %s)
                            AND superseded = FALSE
                            AND decision_key != %s
                            ORDER BY confidence DESC, timestamp DESC
                            """,
                            (f"%{term}%", f"%{term}%", new_decision.get("decision_key", "")),
                        )

                        results = cursor.fetchall()
                        for result in results:
                            conflict = dict(result)
                            if self._is_conflicting(new_decision, conflict):
                                conflicts.append(conflict)

                    # Remove duplicates based on decision_key
                    unique_conflicts = []
                    seen_keys = set()
                    for conflict in conflicts:
                        if conflict["decision_key"] not in seen_keys:
                            unique_conflicts.append(conflict)
                            seen_keys.add(conflict["decision_key"])

                    return unique_conflicts

        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {e}")
            return []

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from decision text"""
        # Remove common words and extract meaningful terms
        common_words = {
            "use",
            "implement",
            "choose",
            "select",
            "adopt",
            "go",
            "with",
            "for",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "from",
            "by",
            "of",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "they",
            "them",
            "their",
            "we",
            "our",
            "you",
            "your",
            "i",
            "me",
            "my",
            "he",
            "she",
            "his",
            "her",
        }

        # Extract words and filter out common words
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        key_terms = [word for word in words if word not in common_words and len(word) > 2]

        return key_terms[:10]  # Limit to top 10 terms

    def _is_conflicting(self, decision1: Dict[str, Any], decision2: Dict[str, Any]) -> bool:
        """Check if two decisions are conflicting"""
        # Extract key terms from both decisions
        terms1 = set(self._extract_key_terms(decision1["head"]))
        terms2 = set(self._extract_key_terms(decision2["head"]))

        # Check for overlap in key terms
        overlap = terms1.intersection(terms2)

        # If there's significant overlap, check for semantic conflicts
        if len(overlap) >= 2:
            # Check for explicit contradictions
            contradictions = [
                ("use", "don't use"),
                ("choose", "avoid"),
                ("implement", "remove"),
                ("adopt", "reject"),
                ("keep", "replace"),
                ("enable", "disable"),
                ("add", "remove"),
                ("include", "exclude"),
            ]

            text1 = decision1["head"].lower()
            text2 = decision2["head"].lower()

            for pos, neg in contradictions:
                if pos in text1 and neg in text2:
                    return True
                if pos in text2 and neg in text1:
                    return True

        return False

    def mark_superseded(self, decision_key: str, superseded_by: str) -> bool:
        """
        Mark a decision as superseded

        Args:
            decision_key: Key of the decision to mark as superseded
            superseded_by: Key of the decision that supersedes it

        Returns:
            True if successful, False otherwise
        """
        try:
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE decisions
                        SET superseded = TRUE,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE decision_key = %s
                        """,
                        (decision_key,),
                    )

                    # Log the supersedence
                    cursor.execute(
                        """
                        INSERT INTO decision_supersedence_log (
                            superseded_decision_key,
                            superseding_decision_key,
                            supersedence_timestamp
                        ) VALUES (%s, %s, CURRENT_TIMESTAMP)
                        """,
                        (decision_key, superseded_by),
                    )

                    conn.commit()
                    self.logger.info(f"Marked decision {decision_key} as superseded by {superseded_by}")
                    return True

        except Exception as e:
            self.logger.error(f"Error marking decision as superseded: {e}")
            return False

    def hybrid_search_decisions(
        self, query: str, limit: int = 10, session_id: Optional[str] = None, include_superseded: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Hybrid BM25 + Vector search for decisions with supersedence handling

        Args:
            query: Search query
            limit: Maximum number of results
            session_id: Optional session filter
            include_superseded: Whether to include superseded decisions

        Returns:
            List of decisions ranked by relevance and supersedence status
        """
        try:
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build the query with supersedence filtering
                    base_query = """
                        SELECT *,
                               CASE
                                   WHEN superseded = TRUE THEN 0.1
                                   ELSE 1.0
                               END as supersedence_penalty,
                               CASE
                                   WHEN head ILIKE %s THEN 2.0
                                   WHEN rationale ILIKE %s THEN 1.0
                                   ELSE 0.5
                               END as relevance_score
                        FROM decisions
                        WHERE (head ILIKE %s OR rationale ILIKE %s)
                    """

                    params = [f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]

                    if not include_superseded:
                        base_query += " AND superseded = FALSE"

                    if session_id:
                        base_query += " AND session_id = %s"
                        params.append(session_id)

                    base_query += """
                        ORDER BY
                            (CASE
                                WHEN superseded = TRUE THEN 0.1
                                ELSE 1.0
                            END *
                            CASE
                                WHEN head ILIKE %s THEN 2.0
                                WHEN rationale ILIKE %s THEN 1.0
                                ELSE 0.5
                            END * CAST(confidence AS FLOAT)) DESC,
                            timestamp DESC
                        LIMIT %s
                    """
                    params.extend([f"%{query}%", f"%{query}%"])
                    params.append(str(limit))

                    cursor.execute(base_query, params)
                    results = cursor.fetchall()

                    # Convert to list of dictionaries and add ranking info
                    decisions = []
                    for i, result in enumerate(results):
                        decision = dict(result)
                        decision["rank"] = i + 1
                        # Convert to float to avoid decimal multiplication issues
                        relevance_score = float(decision.get("relevance_score", 0.5))
                        supersedence_penalty = float(decision.get("supersedence_penalty", 1.0))
                        confidence = float(decision.get("confidence", 0.5))
                        decision["final_score"] = relevance_score * supersedence_penalty * confidence
                        decisions.append(decision)

                    return decisions

        except Exception as e:
            self.logger.error(f"Error in hybrid search: {e}")
            return []

    def pack_decisions_first(self, query: str, limit: int = 10, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Pack decisions first in retrieval results

        Args:
            query: Search query
            limit: Maximum number of results
            session_id: Optional session filter

        Returns:
            Dictionary with decisions and other content
        """
        # Get decisions first
        decisions = self.hybrid_search_decisions(query, limit, session_id, include_superseded=False)

        # Pack decisions at the top
        packed_content = []

        if decisions:
            # Add decision header
            packed_content.append(
                {
                    "type": "decision_header",
                    "content": f"## 🎯 Relevant Decisions for: {query}",
                    "count": len(decisions),
                }
            )

            # Add each decision
            for decision in decisions:
                packed_content.append(
                    {
                        "type": "decision",
                        "content": f"**{decision['head']}** (confidence: {decision['confidence']:.2f})",
                        "rationale": decision.get("rationale", ""),
                        "decision_key": decision["decision_key"],
                        "confidence": decision["confidence"],
                        "rank": decision["rank"],
                    }
                )

        # Add other content (placeholder for now)
        if len(packed_content) < limit:
            packed_content.append(
                {"type": "other_content", "content": f"Additional context for: {query}", "placeholder": True}
            )

        return {
            "query": query,
            "decisions": decisions,
            "packed_content": packed_content,
            "total_decisions": len(decisions),
            "include_superseded": False,
        }

    def get_supersedence_stats(self) -> Dict[str, Any]:
        """Get statistics about supersedence"""
        try:
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get total decisions
                    cursor.execute("SELECT COUNT(*) as total FROM decisions")
                    total_result = cursor.fetchone()
                    total = total_result["total"] if total_result else 0

                    # Get superseded decisions
                    cursor.execute("SELECT COUNT(*) as superseded FROM decisions WHERE superseded = TRUE")
                    superseded_result = cursor.fetchone()
                    superseded = superseded_result["superseded"] if superseded_result else 0

                    # Get supersedence rate
                    supersedence_rate = (superseded / total * 100) if total > 0 else 0

                    # Get recent supersedence activity
                    cursor.execute(
                        """
                        SELECT COUNT(*) as recent_supersedence
                        FROM decision_supersedence_log
                        WHERE supersedence_timestamp > NOW() - INTERVAL '24 hours'
                        """
                    )
                    recent_supersedence_result = cursor.fetchone()
                    recent_supersedence = (
                        recent_supersedence_result["recent_supersedence"] if recent_supersedence_result else 0
                    )

                    return {
                        "total_decisions": total,
                        "superseded_decisions": superseded,
                        "supersedence_rate_percent": round(supersedence_rate, 2),
                        "recent_supersedence_24h": recent_supersedence,
                        "active_decisions": total - superseded,
                    }

        except Exception as e:
            self.logger.error(f"Error getting supersedence stats: {e}")
            return {}


def create_supersedence_tables(db_connection_string: str) -> bool:
    """Create supersedence-related tables if they don't exist"""
    try:
        with psycopg2.connect(db_connection_string) as conn:
            with conn.cursor() as cursor:
                # Create supersedence log table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS decision_supersedence_log (
                        id SERIAL PRIMARY KEY,
                        superseded_decision_key VARCHAR(255) NOT NULL,
                        superseding_decision_key VARCHAR(255) NOT NULL,
                        supersedence_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes for performance
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_supersedence_log_superseded
                    ON decision_supersedence_log(superseded_decision_key)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_supersedence_log_superseding
                    ON decision_supersedence_log(superseding_decision_key)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_supersedence_log_timestamp
                    ON decision_supersedence_log(supersedence_timestamp)
                """
                )

                # Add supersedence column to decisions table if it doesn't exist
                cursor.execute(
                    """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'decisions' AND column_name = 'superseded'
                        ) THEN
                            ALTER TABLE decisions ADD COLUMN superseded BOOLEAN DEFAULT FALSE;
                        END IF;
                    END $$;
                """
                )

                conn.commit()
                logger.info("Supersedence tables created successfully")
                return True

    except Exception as e:
        logger.error(f"Error creating supersedence tables: {e}")
        return False
