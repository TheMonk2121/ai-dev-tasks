"""Memory consolidation graph with advanced NLP capabilities.

This module provides a comprehensive orchestration for consolidating
conversation turns into durable memory artifacts using advanced NLP
techniques including summarization, fact extraction, and entity linking.
It is gated by `Settings.use_memory_graph` and is safe to import when disabled.
"""

from __future__ import annotations

import re
import time
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

try:
    from src.config.settings import get_settings
except ImportError:
    # Fallback for when running from scripts
    def get_settings():
        class Settings:
            use_memory_graph = True

        return Settings()


@dataclass
class Turn:
    role: str
    content: str
    timestamp: float | None = None


@dataclass
class Fact:
    """Structured fact extracted from conversation."""

    text: str
    fact_type: str  # 'action', 'decision', 'requirement', 'constraint', 'entity', 'metric'
    confidence: float
    source_turn: int
    entities: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.entities is None:
            self.entities = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Entity:
    """Named entity with context and relationships."""

    text: str
    entity_type: str  # 'person', 'organization', 'technology', 'concept', 'file', 'url'
    confidence: float
    context: str
    mentions: list[int] = None  # Turn indices where entity appears
    aliases: list[str] = None

    def __post_init__(self):
        if self.mentions is None:
            self.mentions = []
        if self.aliases is None:
            self.aliases = []


@dataclass
class EntityLink:
    """Relationship between entities."""

    source_entity: str
    target_entity: str
    relationship_type: str  # 'mentions', 'depends_on', 'implements', 'conflicts_with', 'similar_to'
    confidence: float
    context: str


@dataclass
class ConsolidationResult:
    summary: str
    facts: list[Fact]
    entities: list[Entity]
    entity_links: list[EntityLink]
    upserts: dict[str, int]
    processing_metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.processing_metadata is None:
            self.processing_metadata = {}


def collect_turns(raw: Iterable[dict[str, Any]]) -> list[Turn]:
    """Collect turns from raw records with enhanced metadata."""
    out: list[Turn] = []
    for i, r in enumerate(raw or []):
        role = str(r.get("role", "user"))
        content = str(r.get("content") or r.get("text") or "")
        if not content:
            continue

        # Extract timestamp if available
        timestamp = None
        if "timestamp" in r:
            timestamp = float(r["timestamp"])
        elif "created_at" in r:
            timestamp = float(r["created_at"])

        out.append(Turn(role=role, content=content, timestamp=timestamp))
    return out


def summarize(turns: list[Turn]) -> str:
    """Generate comprehensive conversation summary using advanced NLP techniques."""
    if not turns:
        return ""

    if len(turns) == 1:
        # Single turn - return truncated content
        return turns[0].content[:500].strip()

    try:
        # Use sentence-transformers for semantic summarization
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Extract key sentences using semantic similarity
        all_sentences = []
        for turn in turns:
            # Split into sentences (simple approach)
            sentences = re.split(r"[.!?]+", turn.content)
            sentences = [s.strip() for s in sentences if s.strip()]
            all_sentences.extend(sentences)

        if len(all_sentences) <= 3:
            # Few sentences - return first few
            return " ".join(all_sentences[:3])

        # Compute embeddings for all sentences
        embeddings = model.encode(all_sentences)

        # Simple approach: select sentences with highest average similarity to all others
        # This avoids sklearn clustering which can cause recursion issues
        similarities = []
        for i, emb1 in enumerate(embeddings):
            total_sim = 0
            for j, emb2 in enumerate(embeddings):
                if i != j:
                    # Calculate cosine similarity manually
                    dot_product = sum(a * b for a, b in zip(emb1, emb2))
                    norm1 = sum(a * a for a in emb1) ** 0.5
                    norm2 = sum(b * b for b in emb2) ** 0.5
                    if norm1 > 0 and norm2 > 0:
                        total_sim += dot_product / (norm1 * norm2)
            similarities.append(total_sim / (len(embeddings) - 1))

        # Select top 3 most representative sentences
        top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:3]
        selected_sentences = [(i, all_sentences[i]) for i in sorted(top_indices)]

        # Create summary
        summary = ". ".join([sent for _, sent in selected_sentences])

        # Ensure summary is not too long
        if len(summary) > 1000:
            summary = summary[:1000] + "..."

        return summary.strip()

    except Exception as e:
        # Fallback to heuristic summarization
        print(f"Advanced summarization failed: {e}, using fallback")
        return _heuristic_summarize(turns)


def _heuristic_summarize(turns: list[Turn]) -> str:
    """Fallback heuristic summarization when advanced methods fail."""
    if not turns:
        return ""

    # Extract key information using simple heuristics
    key_phrases = []

    for turn in turns:
        content = turn.content.lower()

        # Look for important patterns
        if any(word in content for word in ["implement", "create", "build", "develop"]):
            key_phrases.append("Implementation discussed")
        if any(word in content for word in ["fix", "bug", "error", "issue"]):
            key_phrases.append("Issues identified")
        if any(word in content for word in ["test", "testing", "validate"]):
            key_phrases.append("Testing mentioned")
        if any(word in content for word in ["deploy", "production", "release"]):
            key_phrases.append("Deployment discussed")

    # Combine with recent content
    recent_content = turns[-1].content[:300] if turns else ""

    if key_phrases:
        summary = f"{', '.join(set(key_phrases))}. {recent_content}"
    else:
        summary = recent_content

    return summary.strip()


def extract_facts(turns: list[Turn], summary: str) -> list[Fact]:
    """Extract structured facts from conversation using pattern-based and NLP techniques."""
    if not turns and not summary:
        return []

    facts = []

    # Pattern-based fact extraction
    fact_patterns = {
        "action": [
            r"(?:need to|should|must|will|going to)\s+([^.!?]+)",
            r"(?:implement|create|build|develop|fix|add|remove|update|modify)\s+([^.!?]+)",
            r"(?:deploy|release|publish|launch)\s+([^.!?]+)",
            r"let'?s\s+(?:create|build|implement|develop)\s+(.+)",
        ],
        "decision": [
            r"(?:decided|chose|selected|opted for)\s+([^.!?]+)",
            r"(?:agreed|concluded|determined)\s+([^.!?]+)",
            r"(?:will use|going with|sticking with)\s+([^.!?]+)",
        ],
        "requirement": [
            r"(?:required|needed|necessary)\s+([^.!?]+)",
            r"(?:must have|should have|need)\s+([^.!?]+)",
            r"(?:must|should|need to)\s+(?:achieve|have|be|do|get|reach|meet)\s+([^.!?]+)",
            r"(?:constraint|limitation|restriction)\s+([^.!?]+)",
            r"must\s+achieve\s+(.+)",
        ],
        "constraint": [
            r"(?:cannot|cannot|cant|wont|will not)\s+([^.!?]+)",
            r"(?:avoid|prevent|block|restrict)\s+([^.!?]+)",
            r"(?:limited by|constrained by|restricted to)\s+([^.!?]+)",
        ],
        "metric": [
            r"(\d+(?:\.\d+)?%?)\s+(?:performance|accuracy|speed|efficiency|coverage)",
            r"(?:achieve|target|goal|aim for)\s+(\d+(?:\.\d+)?%?)",
            r"(?:improve|increase|reduce|decrease)\s+([^.!?]+)\s+by\s+(\d+(?:\.\d+)?%?)",
        ],
        "entity": [
            r"([a-zA-Z_][a-zA-Z0-9_.]*\.(?:py|js|ts|md|json|yaml|yml|sql|sh|bat))\s+(?:file|module|class|function|method|script)",
            r"(?:file|module|class|function|method|script)\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
            r"(?:database|table|column|index)\s+([a-zA-Z_][a-zA-Z0-9_.]*)",
            r"(?:API|endpoint|service)\s+([a-zA-Z_][a-zA-Z0-9_./]*)",
        ],
    }

    # Extract facts from each turn
    for turn_idx, turn in enumerate(turns):
        content = turn.content

        for fact_type, patterns in fact_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                match_list = list(matches)
                for match in match_list:
                    fact_text = match.group(1).strip()
                    if len(fact_text) > 10:  # Filter out very short matches
                        confidence = _calculate_fact_confidence(fact_text, fact_type)

                        fact = Fact(
                            text=fact_text,
                            fact_type=fact_type,
                            confidence=confidence,
                            source_turn=turn_idx,
                            entities=_extract_entities_from_text(fact_text),
                            metadata={"pattern": pattern, "role": turn.role, "timestamp": turn.timestamp},
                        )
                        facts.append(fact)

    # Extract facts from summary if provided
    if summary and summary != "".join(turn.content for turn in turns):
        for fact_type, patterns in fact_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, summary, re.IGNORECASE)
                for match in matches:
                    fact_text = match.group(1).strip()
                    if len(fact_text) > 10:
                        confidence = (
                            _calculate_fact_confidence(fact_text, fact_type) * 0.8
                        )  # Lower confidence for summary

                        fact = Fact(
                            text=fact_text,
                            fact_type=fact_type,
                            confidence=confidence,
                            source_turn=-1,  # -1 indicates summary source
                            entities=_extract_entities_from_text(fact_text),
                            metadata={"pattern": pattern, "source": "summary"},
                        )
                        facts.append(fact)

    # Deduplicate similar facts
    facts = _deduplicate_facts(facts)

    # Sort by confidence and importance
    facts.sort(key=lambda f: (f.confidence, _fact_importance_score(f)), reverse=True)

    return facts


def _calculate_fact_confidence(fact_text: str, fact_type: str) -> float:
    """Calculate confidence score for a fact based on various factors."""
    confidence = 0.5  # Base confidence

    # Length factor (longer facts are often more specific)
    length_factor = min(len(fact_text) / 100, 1.0)
    confidence += length_factor * 0.2

    # Fact type specific factors
    if fact_type == "action":
        if any(word in fact_text.lower() for word in ["implement", "create", "build"]):
            confidence += 0.2
    elif fact_type == "decision":
        if any(word in fact_text.lower() for word in ["decided", "chose", "agreed"]):
            confidence += 0.3
    elif fact_type == "requirement":
        if any(word in fact_text.lower() for word in ["must", "required", "necessary"]):
            confidence += 0.2
    elif fact_type == "metric":
        if re.search(r"\d+(?:\.\d+)?%?", fact_text):
            confidence += 0.3

    # Specificity factor (more specific terms)
    specific_terms = ["file", "function", "class", "database", "API", "service", "module"]
    if any(term in fact_text.lower() for term in specific_terms):
        confidence += 0.1

    return min(confidence, 1.0)


def _extract_entities_from_text(text: str) -> list[str]:
    """Extract potential entities from text using simple patterns."""
    entities = []

    # File paths and names
    file_patterns = [
        r"[a-zA-Z_][a-zA-Z0-9_]*\.(py|js|ts|md|json|yaml|yml|sql|sh|bat)",
        r"/[a-zA-Z0-9_./-]+\.(py|js|ts|md|json|yaml|yml|sql|sh|bat)",
        r"[a-zA-Z_][a-zA-Z0-9_]*\.py",
    ]

    for pattern in file_patterns:
        matches = re.findall(pattern, text)
        entities.extend(matches)

    # Function and class names
    code_patterns = [
        r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    ]

    for pattern in code_patterns:
        matches = re.findall(pattern, text)
        entities.extend(matches)

    # URLs and APIs
    url_patterns = [
        r"https?://[^\s]+",
        r"[a-zA-Z_][a-zA-Z0-9_]*/[a-zA-Z0-9_./-]+",  # GitHub-style paths
    ]

    for pattern in url_patterns:
        matches = re.findall(pattern, text)
        entities.extend(matches)

    return list(set(entities))  # Remove duplicates


def _deduplicate_facts(facts: list[Fact]) -> list[Fact]:
    """Remove duplicate or very similar facts."""
    if not facts:
        return []

    # Group facts by type and similarity
    unique_facts = []

    for fact in facts:
        is_duplicate = False

        for existing in unique_facts:
            if fact.fact_type == existing.fact_type and _text_similarity(fact.text, existing.text) > 0.8:
                # Keep the one with higher confidence
                if fact.confidence > existing.confidence:
                    unique_facts.remove(existing)
                    unique_facts.append(fact)
                is_duplicate = True
                break

        if not is_duplicate:
            unique_facts.append(fact)

    return unique_facts


def _text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity using word overlap."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union if union > 0 else 0.0


def _fact_importance_score(fact: Fact) -> float:
    """Calculate importance score for fact ranking."""
    importance = 0.0

    # Fact type importance
    type_scores = {
        "decision": 1.0,
        "requirement": 0.9,
        "constraint": 0.8,
        "action": 0.7,
        "metric": 0.6,
        "entity": 0.5,
    }
    importance += type_scores.get(fact.fact_type, 0.5)

    # Length factor
    importance += min(len(fact.text) / 200, 0.3)

    # Entity count factor
    importance += min(len(fact.entities) / 5, 0.2)

    return importance


def extract_entities(turns: list[Turn], facts: list[Fact]) -> list[Entity]:
    """Extract and consolidate entities from conversation turns and facts."""
    entities = []
    entity_texts = set()

    # Extract entities from facts
    for fact in facts:
        for entity_text in fact.entities:
            if entity_text not in entity_texts:
                entity_texts.add(entity_text)

                # Determine entity type
                entity_type = _classify_entity_type(entity_text)

                # Find context and mentions
                context, mentions = _find_entity_context(entity_text, turns)

                entity = Entity(
                    text=entity_text,
                    entity_type=entity_type,
                    confidence=_calculate_entity_confidence(entity_text, entity_type, context),
                    context=context,
                    mentions=mentions,
                    aliases=_find_entity_aliases(entity_text, turns),
                )
                entities.append(entity)

    # Extract additional entities from turns
    for turn_idx, turn in enumerate(turns):
        additional_entities = _extract_entities_from_turn(turn)
        for entity_text in additional_entities:
            if entity_text not in entity_texts:
                entity_texts.add(entity_text)

                entity_type = _classify_entity_type(entity_text)
                context, mentions = _find_entity_context(entity_text, turns)

                entity = Entity(
                    text=entity_text,
                    entity_type=entity_type,
                    confidence=_calculate_entity_confidence(entity_text, entity_type, context),
                    context=context,
                    mentions=mentions,
                    aliases=_find_entity_aliases(entity_text, turns),
                )
                entities.append(entity)

    # Deduplicate and merge similar entities
    entities = _deduplicate_entities(entities)

    return entities


def link_entities(facts: list[Fact], entities: list[Entity]) -> list[EntityLink]:
    """Create sophisticated entity links using semantic similarity and co-occurrence."""
    if not facts or not entities:
        return []

    links = []

    try:
        # Use sentence-transformers for semantic similarity
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Create entity embeddings
        entity_texts = [entity.text for entity in entities]
        entity_embeddings = model.encode(entity_texts)

        # Find entity co-occurrences in facts
        for fact in facts:
            fact_entities = fact.entities
            if len(fact_entities) < 2:
                continue

            # Create links between entities mentioned in the same fact
            for i, entity1 in enumerate(fact_entities):
                for j, entity2 in enumerate(fact_entities[i + 1 :], i + 1):
                    # Find entity objects
                    entity1_obj = next((e for e in entities if e.text == entity1), None)
                    entity2_obj = next((e for e in entities if e.text == entity2), None)

                    if entity1_obj and entity2_obj:
                        # Calculate semantic similarity
                        idx1 = entity_texts.index(entity1)
                        idx2 = entity_texts.index(entity2)

                        similarity = _cosine_similarity(entity_embeddings[idx1], entity_embeddings[idx2])

                        # Determine relationship type
                        rel_type = _determine_relationship_type(entity1_obj, entity2_obj, fact, similarity)

                        if similarity > 0.3:  # Threshold for meaningful similarity
                            link = EntityLink(
                                source_entity=entity1,
                                target_entity=entity2,
                                relationship_type=rel_type,
                                confidence=similarity,
                                context=fact.text,
                            )
                            links.append(link)

        # Find semantic similarity links between all entities
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i + 1 :], i + 1):
                similarity = _cosine_similarity(entity_embeddings[i], entity_embeddings[j])

                if similarity > 0.5:  # Higher threshold for semantic similarity
                    # Check if link already exists
                    existing_link = any(
                        (link.source_entity == entity1.text and link.target_entity == entity2.text)
                        or (link.source_entity == entity2.text and link.target_entity == entity1.text)
                        for link in links
                    )

                    if not existing_link:
                        link = EntityLink(
                            source_entity=entity1.text,
                            target_entity=entity2.text,
                            relationship_type="similar_to",
                            confidence=similarity,
                            context="Semantic similarity",
                        )
                        links.append(link)

    except Exception as e:
        print(f"Advanced entity linking failed: {e}, using fallback")
        # Fallback to simple co-occurrence links
        links = _fallback_entity_linking(facts, entities)

    return links


def _classify_entity_type(entity_text: str) -> str:
    """Classify entity type based on patterns and context."""
    entity_lower = entity_text.lower()

    # File patterns
    if any(entity_lower.endswith(ext) for ext in [".py", ".js", ".ts", ".md", ".json", ".yaml", ".yml", ".sql"]):
        return "file"

    # URL patterns
    if entity_text.startswith(("http://", "https://")):
        return "url"

    # Code patterns
    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", entity_text):
        if any(word in entity_lower for word in ["class", "function", "method", "def", "class"]):
            return "code"
        elif any(word in entity_lower for word in ["api", "service", "endpoint"]):
            return "service"
        elif any(word in entity_lower for word in ["database", "table", "column", "index"]):
            return "database"

    # Technology patterns
    tech_terms = ["python", "javascript", "typescript", "react", "vue", "angular", "django", "flask", "fastapi"]
    if any(tech in entity_lower for tech in tech_terms):
        return "technology"

    # Default to concept
    return "concept"


def _find_entity_context(entity_text: str, turns: list[Turn]) -> tuple[str, list[int]]:
    """Find context and mention indices for an entity."""
    context_parts = []
    mentions = []

    for turn_idx, turn in enumerate(turns):
        if entity_text.lower() in turn.content.lower():
            mentions.append(turn_idx)
            # Extract surrounding context
            content_lower = turn.content.lower()
            entity_lower = entity_text.lower()
            start = content_lower.find(entity_lower)

            if start != -1:
                # Get 50 characters before and after
                context_start = max(0, start - 50)
                context_end = min(len(turn.content), start + len(entity_text) + 50)
                context = turn.content[context_start:context_end].strip()
                context_parts.append(context)

    # Combine contexts
    context = " ... ".join(context_parts[:3])  # Limit to 3 contexts

    return context, mentions


def _calculate_entity_confidence(entity_text: str, entity_type: str, context: str) -> float:
    """Calculate confidence score for an entity."""
    confidence = 0.5  # Base confidence

    # Length factor
    confidence += min(len(entity_text) / 50, 0.3)

    # Type-specific factors
    if entity_type == "file":
        if "." in entity_text and len(entity_text.split(".")[-1]) <= 4:
            confidence += 0.3
    elif entity_type == "url":
        if entity_text.startswith(("http://", "https://")):
            confidence += 0.4
    elif entity_type == "code":
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", entity_text):
            confidence += 0.2

    # Context factor
    if context and len(context) > 20:
        confidence += 0.2

    return min(confidence, 1.0)


def _find_entity_aliases(entity_text: str, turns: list[Turn]) -> list[str]:
    """Find potential aliases for an entity."""
    aliases = set()

    # Simple alias patterns
    if "." in entity_text:
        # File without extension
        base_name = entity_text.split(".")[0]
        aliases.add(base_name)

    # Look for abbreviated forms
    words = entity_text.split("_")
    if len(words) > 1:
        # First letters of words
        abbreviation = "".join(word[0] for word in words if word)
        aliases.add(abbreviation)

    return list(aliases)


def _extract_entities_from_turn(turn: Turn) -> list[str]:
    """Extract entities from a single turn."""
    entities = []

    # Use the same patterns as fact extraction
    patterns = [
        r"[a-zA-Z_][a-zA-Z0-9_]*\.(py|js|ts|md|json|yaml|yml|sql|sh|bat)",
        r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"https?://[^\s]+",
        r"[a-zA-Z_][a-zA-Z0-9_]*/[a-zA-Z0-9_./-]+",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, turn.content)
        entities.extend(matches)

    return list(set(entities))


def _deduplicate_entities(entities: list[Entity]) -> list[Entity]:
    """Remove duplicate entities and merge similar ones."""
    if not entities:
        return []

    unique_entities = []

    for entity in entities:
        is_duplicate = False

        for existing in unique_entities:
            if (
                entity.text.lower() == existing.text.lower()
                or entity.text.lower() in existing.aliases
                or existing.text.lower() in entity.aliases
            ):

                # Merge entities
                existing.mentions.extend(entity.mentions)
                existing.mentions = list(set(existing.mentions))  # Remove duplicates
                existing.aliases.extend(entity.aliases)
                existing.aliases = list(set(existing.aliases))

                # Keep higher confidence
                if entity.confidence > existing.confidence:
                    existing.confidence = entity.confidence
                    existing.context = entity.context

                is_duplicate = True
                break

        if not is_duplicate:
            unique_entities.append(entity)

    return unique_entities


def _determine_relationship_type(entity1: Entity, entity2: Entity, fact: Fact, similarity: float) -> str:
    """Determine the type of relationship between two entities."""
    # Co-occurrence in same fact
    if fact.fact_type == "action":
        return "implements"
    elif fact.fact_type == "requirement":
        return "depends_on"
    elif fact.fact_type == "constraint":
        return "conflicts_with"
    else:
        return "mentions"


def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def _fallback_entity_linking(facts: list[Fact], entities: list[Entity]) -> list[EntityLink]:
    """Fallback entity linking using simple co-occurrence."""
    links = []

    for fact in facts:
        fact_entities = fact.entities
        if len(fact_entities) < 2:
            continue

        for i, entity1 in enumerate(fact_entities):
            for entity2 in fact_entities[i + 1 :]:
                link = EntityLink(
                    source_entity=entity1,
                    target_entity=entity2,
                    relationship_type="mentions",
                    confidence=0.5,
                    context=fact.text,
                )
                links.append(link)

    return links


def upsert_vector(facts: list[dict[str, Any]]) -> int:
    """Stub: return count of vector upserts."""
    return len(facts)


def upsert_fts(facts: list[dict[str, Any]]) -> int:
    """Stub: return count of FTS upserts."""
    return len(facts)


def run(raw_turns: Iterable[dict[str, Any]]) -> ConsolidationResult:
    """Execute the consolidation graph with advanced NLP capabilities."""
    settings = get_settings()
    if not settings.use_memory_graph:
        return ConsolidationResult(
            summary="",
            facts=[],
            entities=[],
            entity_links=[],
            upserts={"vector": 0, "fts": 0},
            processing_metadata={"enabled": False},
        )

    start_time = time.time()

    # Collect and process turns
    turns = collect_turns(raw_turns)

    # Generate comprehensive summary
    summary = summarize(turns)

    # Extract structured facts
    facts = extract_facts(turns, summary)

    # Extract and consolidate entities
    entities = extract_entities(turns, facts)

    # Create entity links
    entity_links = link_entities(facts, entities)

    # Upsert to storage (stubs for now)
    up_vector = upsert_vector([fact.__dict__ for fact in facts])
    up_fts = upsert_fts([fact.__dict__ for fact in facts])

    processing_time = time.time() - start_time

    return ConsolidationResult(
        summary=summary,
        facts=facts,
        entities=entities,
        entity_links=entity_links,
        upserts={"vector": up_vector, "fts": up_fts},
        processing_metadata={
            "processing_time": processing_time,
            "turns_processed": len(turns),
            "facts_extracted": len(facts),
            "entities_found": len(entities),
            "links_created": len(entity_links),
            "enabled": True,
        },
    )
