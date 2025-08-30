#!/usr/bin/env python3
"""
Decision Extraction Module for LTST Memory System

Extracts decisions from conversations, identifies patterns, scores confidence,
and stores decisions in the database with stable decision keys.
"""

import hashlib
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Decision patterns and keywords
DECISION_PATTERNS = {
    "explicit_decisions": [
        r"we should\s+(.+?)(?:\.|$)",
        r"let's\s+(.+?)(?:\.|$)",
        r"i recommend\s+(.+?)(?:\.|$)",
        r"the best approach is\s+(.+?)(?:\.|$)",
        r"we will\s+(.+?)(?:\.|$)",
        r"we'll\s+(.+?)(?:\.|$)",
        r"i'll\s+(.+?)(?:\.|$)",
        r"i will\s+(.+?)(?:\.|$)",
        r"we're going to\s+(.+?)(?:\.|$)",
        r"we are going to\s+(.+?)(?:\.|$)",
    ],
    "implicit_decisions": [
        r"use\s+(.+?)(?:\.|$)",
        r"implement\s+(.+?)(?:\.|$)",
        r"choose\s+(.+?)(?:\.|$)",
        r"select\s+(.+?)(?:\.|$)",
        r"adopt\s+(.+?)(?:\.|$)",
        r"go with\s+(.+?)(?:\.|$)",
        r"stick with\s+(.+?)(?:\.|$)",
        r"keep\s+(.+?)(?:\.|$)",
    ],
    "comparison_decisions": [
        r"(\w+)\s+is better than\s+(\w+)",
        r"(\w+)\s+over\s+(\w+)",
        r"prefer\s+(\w+)\s+to\s+(\w+)",
        r"(\w+)\s+instead of\s+(\w+)",
    ],
    "technical_decisions": [
        r"use\s+(\w+)\s+for\s+(.+?)(?:\.|$)",
        r"implement\s+(\w+)\s+with\s+(.+?)(?:\.|$)",
        r"configure\s+(\w+)\s+to\s+(.+?)(?:\.|$)",
        r"set up\s+(\w+)\s+with\s+(.+?)(?:\.|$)",
    ],
}

# Confidence scoring keywords
CONFIDENCE_INDICATORS = {
    "high_confidence": [
        "definitely",
        "certainly",
        "absolutely",
        "clearly",
        "obviously",
        "without doubt",
        "no question",
        "for sure",
        "guaranteed",
    ],
    "medium_confidence": [
        "probably",
        "likely",
        "should",
        "recommend",
        "suggest",
        "think",
        "believe",
        "expect",
        "anticipate",
    ],
    "low_confidence": ["maybe", "possibly", "might", "could", "consider", "perhaps", "potentially", "tentatively"],
}


class DecisionExtractor:
    """Extracts decisions from conversations and stores them in the database"""

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.logger = logging.getLogger("decision_extractor")

    def extract_decisions_from_text(self, text: str, session_id: str, role: str = "user") -> List[Dict[str, Any]]:
        """
        Extract decisions from conversation text

        Args:
            text: Conversation text to analyze
            session_id: Session identifier
            role: Role of the speaker (user/assistant)

        Returns:
            List of extracted decisions
        """
        decisions = []

        # Normalize text
        text = text.strip()
        if not text:
            return decisions

        # Extract decisions using patterns
        for pattern_type, patterns in DECISION_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    decision = self._create_decision_from_match(match, pattern_type, text, session_id, role)
                    if decision:
                        decisions.append(decision)

        return decisions

    def _create_decision_from_match(
        self, match, pattern_type: str, full_text: str, session_id: str, role: str
    ) -> Optional[Dict[str, Any]]:
        """Create a decision object from a regex match"""
        try:
            # Extract the decision content
            if pattern_type == "comparison_decisions":
                # Handle comparison decisions (e.g., "A is better than B")
                groups = match.groups()
                if len(groups) >= 2:
                    decision_text = f"Choose {groups[0]} over {groups[1]}"
                    rationale = f"Decision made to prefer {groups[0]} instead of {groups[1]}"
                else:
                    return None
            else:
                # Handle other decision types
                decision_text = match.group(1).strip()
                rationale = self._extract_rationale(full_text, match.start(), match.end())

            # Skip if decision text is too short or too long
            if len(decision_text) < 5 or len(decision_text) > 500:
                return None

            # Calculate confidence score
            confidence = self._calculate_confidence(full_text, pattern_type)

            # Generate stable decision key
            decision_key = self._generate_decision_key(decision_text, session_id)

            # Create decision object
            decision = {
                "decision_key": decision_key,
                "head": decision_text,
                "rationale": rationale,
                "confidence": confidence,
                "pattern_type": pattern_type,
                "session_id": session_id,
                "role": role,
                "timestamp": datetime.now().isoformat(),
                "superseded": False,
                "source_text": full_text[:200] + "..." if len(full_text) > 200 else full_text,
            }

            return decision

        except Exception as e:
            self.logger.error(f"Error creating decision from match: {e}")
            return None

    def _extract_rationale(self, full_text: str, start_pos: int, end_pos: int) -> str:
        """Extract rationale from surrounding context"""
        # Get context around the decision (100 characters before and after)
        context_start = max(0, start_pos - 100)
        context_end = min(len(full_text), end_pos + 100)
        context = full_text[context_start:context_end]

        # Clean up the context
        context = re.sub(r"\s+", " ", context).strip()

        # If context is too long, truncate it
        if len(context) > 300:
            context = context[:297] + "..."

        return context

    def _calculate_confidence(self, text: str, pattern_type: str) -> float:
        """Calculate confidence score based on indicators and pattern type"""
        text_lower = text.lower()

        # Base confidence by pattern type
        base_confidence = {
            "explicit_decisions": 0.8,
            "implicit_decisions": 0.6,
            "comparison_decisions": 0.7,
            "technical_decisions": 0.75,
        }.get(pattern_type, 0.5)

        # Adjust based on confidence indicators
        confidence_adjustment = 0.0

        for confidence_level, indicators in CONFIDENCE_INDICATORS.items():
            for indicator in indicators:
                if indicator.lower() in text_lower:
                    if confidence_level == "high_confidence":
                        confidence_adjustment += 0.2
                    elif confidence_level == "medium_confidence":
                        confidence_adjustment += 0.1
                    elif confidence_level == "low_confidence":
                        confidence_adjustment -= 0.1

        # Calculate final confidence (clamped between 0.1 and 1.0)
        final_confidence = base_confidence + confidence_adjustment
        return max(0.1, min(1.0, final_confidence))

    def _generate_decision_key(self, decision_text: str, session_id: str) -> str:
        """Generate a stable and unique decision key"""
        # Create a hash from decision text and session
        content = f"{decision_text}:{session_id}"
        hash_value = hashlib.md5(content.encode("utf-8")).hexdigest()[:12]

        # Create a readable key
        clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", decision_text)
        words = clean_text.split()[:3]  # Take first 3 words
        prefix = "_".join(words).lower()

        return f"{prefix}_{hash_value}"

    def store_decisions(self, decisions: List[Dict[str, Any]]) -> bool:
        """
        Store decisions in the database

        Args:
            decisions: List of decision objects to store

        Returns:
            True if successful, False otherwise
        """
        if not decisions:
            return True

        try:
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    for decision in decisions:
                        # Check if decision already exists
                        cursor.execute(
                            """
                            SELECT decision_key FROM decisions
                            WHERE decision_key = %s
                            """,
                            (decision["decision_key"],),
                        )

                        if cursor.fetchone():
                            # Update existing decision
                            cursor.execute(
                                """
                                UPDATE decisions SET
                                    head = %s,
                                    rationale = %s,
                                    confidence = %s,
                                    pattern_type = %s,
                                    session_id = %s,
                                    role = %s,
                                    timestamp = %s,
                                    superseded = %s,
                                    source_text = %s
                                WHERE decision_key = %s
                                """,
                                (
                                    decision["head"],
                                    decision["rationale"],
                                    decision["confidence"],
                                    decision["pattern_type"],
                                    decision["session_id"],
                                    decision["role"],
                                    decision["timestamp"],
                                    decision["superseded"],
                                    decision["source_text"],
                                    decision["decision_key"],
                                ),
                            )
                        else:
                            # Insert new decision
                            cursor.execute(
                                """
                                INSERT INTO decisions (
                                    decision_key, head, rationale, confidence,
                                    pattern_type, session_id, role, timestamp,
                                    superseded, source_text
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    decision["decision_key"],
                                    decision["head"],
                                    decision["rationale"],
                                    decision["confidence"],
                                    decision["pattern_type"],
                                    decision["session_id"],
                                    decision["role"],
                                    decision["timestamp"],
                                    decision["superseded"],
                                    decision["source_text"],
                                ),
                            )

                    conn.commit()
                    self.logger.info(f"Stored {len(decisions)} decisions in database")
                    return True

        except Exception as e:
            self.logger.error(f"Error storing decisions: {e}")
            return False

    def search_decisions(self, query: str, limit: int = 10, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search decisions in the database

        Args:
            query: Search query
            limit: Maximum number of results
            session_id: Optional session filter

        Returns:
            List of matching decisions
        """
        try:
            with psycopg2.connect(self.db_connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if session_id:
                        cursor.execute(
                            """
                            SELECT * FROM decisions
                            WHERE (head ILIKE %s OR rationale ILIKE %s)
                            AND session_id = %s
                            AND superseded = FALSE
                            ORDER BY confidence DESC, timestamp DESC
                            LIMIT %s
                            """,
                            (f"%{query}%", f"%{query}%", session_id, limit),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT * FROM decisions
                            WHERE (head ILIKE %s OR rationale ILIKE %s)
                            AND superseded = FALSE
                            ORDER BY confidence DESC, timestamp DESC
                            LIMIT %s
                            """,
                            (f"%{query}%", f"%{query}%", limit),
                        )

                    results = cursor.fetchall()
                    return [dict(row) for row in results]

        except Exception as e:
            self.logger.error(f"Error searching decisions: {e}")
            return []

    def process_conversation_turn(self, session_id: str, role: str, text: str) -> List[Dict[str, Any]]:
        """
        Process a conversation turn and extract decisions

        Args:
            session_id: Session identifier
            role: Role of the speaker
            text: Conversation text

        Returns:
            List of extracted decisions
        """
        # Extract decisions from text
        decisions = self.extract_decisions_from_text(text, session_id, role)

        # Store decisions in database
        if decisions:
            self.store_decisions(decisions)

            # Check for conflicts and handle supersedence
            try:
                from .supersedence_retrieval import SupersedenceRetrieval, create_supersedence_tables

                # Create supersedence tables if they don't exist
                create_supersedence_tables(self.db_connection_string)

                # Initialize supersedence system
                supersedence = SupersedenceRetrieval(self.db_connection_string)

                # Check each decision for conflicts
                for decision in decisions:
                    conflicts = supersedence.detect_conflicts(decision)

                    if conflicts:
                        self.logger.info(f"Found {len(conflicts)} conflicts for decision: {decision['head'][:50]}...")

                        # Mark conflicting decisions as superseded
                        for conflict in conflicts:
                            if conflict["confidence"] < decision["confidence"]:
                                supersedence.mark_superseded(conflict["decision_key"], decision["decision_key"])
                                self.logger.info(f"Superseded decision: {conflict['head'][:50]}...")

            except Exception as e:
                self.logger.warning(f"Supersedence processing failed: {e}")

        return decisions


def create_decisions_table(db_connection_string: str) -> bool:
    """Create the decisions table if it doesn't exist"""
    try:
        with psycopg2.connect(db_connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS decisions (
                        id SERIAL PRIMARY KEY,
                        decision_key VARCHAR(255) UNIQUE NOT NULL,
                        head TEXT NOT NULL,
                        rationale TEXT,
                        confidence FLOAT DEFAULT 0.5,
                        pattern_type VARCHAR(50),
                        session_id VARCHAR(255),
                        role VARCHAR(50),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        superseded BOOLEAN DEFAULT FALSE,
                        source_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes for better performance
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_decisions_session_id
                    ON decisions(session_id)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_decisions_decision_key
                    ON decisions(decision_key)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_decisions_superseded
                    ON decisions(superseded)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_decisions_confidence
                    ON decisions(confidence DESC)
                """
                )

                conn.commit()
                logger.info("Decisions table created successfully")
                return True

    except Exception as e:
        logger.error(f"Error creating decisions table: {e}")
        return False
