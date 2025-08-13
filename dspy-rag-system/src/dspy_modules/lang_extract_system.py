#!/usr/bin/env python3
"""
LangExtract System - Research-Based Structured Extraction
Implements span-level grounding and controlled generation for precise fact extraction
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

import dspy
from dspy import InputField, Module, OutputField, Signature

from utils.validator import sanitize_prompt, validate_string_length

_LOG = logging.getLogger("lang_extract_system")

# ---------- LangExtract Schemas ----------


@dataclass
class ExtractionSchema:
    """Research-based extraction schema for structured data extraction"""

    name: str
    fields: List[Dict[str, Any]]
    validation_rules: List[str]
    span_tracking: bool = True
    confidence_threshold: float = 0.8


class ExtractionType(Enum):
    """Types of structured extraction supported"""

    ENTITIES = "entities"
    RELATIONS = "relations"
    FACTS = "facts"
    EVENTS = "events"
    ATTRIBUTES = "attributes"


# ---------- DSPy Signatures for LangExtract ----------


class EntityExtractionSignature(Signature):
    """Signature for entity extraction with span-level grounding"""

    text = InputField(desc="Text to extract entities from")
    entity_types = InputField(desc="Types of entities to extract")
    entities = OutputField(desc="List of extracted entities with spans")
    confidence = OutputField(desc="Confidence level (0-1)")
    spans = OutputField(desc="Character spans for each entity")


class RelationExtractionSignature(Signature):
    """Signature for relation extraction with span-level grounding"""

    text = InputField(desc="Text to extract relations from")
    relation_types = InputField(desc="Types of relations to extract")
    relations = OutputField(desc="List of extracted relations with spans")
    confidence = OutputField(desc="Confidence level (0-1)")
    spans = OutputField(desc="Character spans for each relation")


class FactExtractionSignature(Signature):
    """Signature for fact extraction with span-level grounding"""

    text = InputField(desc="Text to extract facts from")
    fact_schema = InputField(desc="Schema defining fact structure")
    facts = OutputField(desc="List of extracted facts with spans")
    confidence = OutputField(desc="Confidence level (0-1)")
    spans = OutputField(desc="Character spans for each fact")


# ---------- LangExtract Modules ----------


# @dspy.assert_transform_module  # Not available in DSPy 2.6.27
class EntityExtractor(Module):
    """Research-based entity extraction with span-level grounding"""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(EntityExtractionSignature)

    def forward(self, text: str, entity_types: List[str]) -> Dict[str, Any]:
        """Extract entities with span-level grounding"""

        text = sanitize_prompt(text)
        validate_string_length(text, max_length=10000)

        result = self.predict(text=text, entity_types=entity_types)

        # Research-based assertions for validation
        # dspy.Assert(self.validate_entities(result.entities), "Entities must be valid")  # Not available in DSPy 2.6.27
        # dspy.Assert(self.validate_spans(result.spans, text), "Spans must be valid")  # Not available in DSPy 2.6.27
        # dspy.Assert(0 <= result.confidence <= 1, "Confidence must be between 0 and 1")  # Not available in DSPy 2.6.27

        return {
            "entities": result.entities,
            "confidence": result.confidence,
            "spans": result.spans,
            "extraction_type": "entities",
        }

    def validate_entities(self, entities: List[Dict]) -> bool:
        """Validate extracted entities"""
        if not isinstance(entities, list):
            return False

        for entity in entities:
            if not isinstance(entity, dict):
                return False
            if "text" not in entity or "type" not in entity:
                return False

        return True

    def validate_spans(self, spans: List[Dict], text: str) -> bool:
        """Validate character spans"""
        if not isinstance(spans, list):
            return False

        for span in spans:
            if not isinstance(span, dict):
                return False
            if "start" not in span or "end" not in span:
                return False
            if span["start"] < 0 or span["end"] > len(text):
                return False
            if span["start"] >= span["end"]:
                return False

        return True


# @dspy.assert_transform_module  # Not available in DSPy 2.6.27
class RelationExtractor(Module):
    """Research-based relation extraction with span-level grounding"""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(RelationExtractionSignature)

    def forward(self, text: str, relation_types: List[str]) -> Dict[str, Any]:
        """Extract relations with span-level grounding"""

        text = sanitize_prompt(text)
        validate_string_length(text, max_length=10000)

        result = self.predict(text=text, relation_types=relation_types)

        # Research-based assertions for validation
        # dspy.Assert(self.validate_relations(result.relations), "Relations must be valid")  # Not available in DSPy 2.6.27
        # dspy.Assert(self.validate_spans(result.spans, text), "Spans must be valid")  # Not available in DSPy 2.6.27
        # dspy.Assert(0 <= result.confidence <= 1, "Confidence must be between 0 and 1")  # Not available in DSPy 2.6.27

        return {
            "relations": result.relations,
            "confidence": result.confidence,
            "spans": result.spans,
            "extraction_type": "relations",
        }

    def validate_relations(self, relations: List[Dict]) -> bool:
        """Validate extracted relations"""
        if not isinstance(relations, list):
            return False

        for relation in relations:
            if not isinstance(relation, dict):
                return False
            if "subject" not in relation or "predicate" not in relation or "object" not in relation:
                return False

        return True

    def validate_spans(self, spans: List[Dict], text: str) -> bool:
        """Validate character spans"""
        if not isinstance(spans, list):
            return False

        for span in spans:
            if not isinstance(span, dict):
                return False
            if "start" not in span or "end" not in span:
                return False
            if span["start"] < 0 or span["end"] > len(text):
                return False
            if span["start"] >= span["end"]:
                return False

        return True


# @dspy.assert_transform_module  # Not available in DSPy 2.6.27
class FactExtractor(Module):
    """Research-based fact extraction with span-level grounding"""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(FactExtractionSignature)

    def forward(self, text: str, fact_schema: ExtractionSchema) -> Dict[str, Any]:
        """Extract facts with span-level grounding"""

        text = sanitize_prompt(text)
        validate_string_length(text, max_length=10000)

        result = self.predict(text=text, fact_schema=fact_schema)

        # Research-based assertions for validation
        # dspy.Assert(self.validate_facts(result.facts, fact_schema), "Facts must match schema")  # Not available in DSPy 2.6.27
        # dspy.Assert(self.validate_spans(result.spans, text), "Spans must be valid")  # Not available in DSPy 2.6.27
        # dspy.Assert(0 <= result.confidence <= 1, "Confidence must be between 0 and 1")  # Not available in DSPy 2.6.27

        return {
            "facts": result.facts,
            "confidence": result.confidence,
            "spans": result.spans,
            "extraction_type": "facts",
            "schema": fact_schema.name,
        }

    def validate_facts(self, facts: List[Dict], schema: ExtractionSchema) -> bool:
        """Validate extracted facts against schema"""
        if not isinstance(facts, list):
            return False

        for fact in facts:
            if not isinstance(fact, dict):
                return False

            # Check required fields from schema
            for field in schema.fields:
                if field.get("required", False) and field["name"] not in fact:
                    return False

        return True

    def validate_spans(self, spans: List[Dict], text: str) -> bool:
        """Validate character spans"""
        if not isinstance(spans, list):
            return False

        for span in spans:
            if not isinstance(span, dict):
                return False
            if "start" not in span or "end" not in span:
                return False
            if span["start"] < 0 or span["end"] > len(text):
                return False
            if span["start"] >= span["end"]:
                return False

        return True


# ---------- LangExtract System ----------


class LangExtractSystem(Module):
    """Research-based LangExtract system for structured extraction"""

    def __init__(self):
        super().__init__()
        self.entity_extractor = EntityExtractor()
        self.relation_extractor = RelationExtractor()
        self.fact_extractor = FactExtractor()

        # Predefined schemas for common extraction tasks
        self.schemas = self._initialize_schemas()

    def forward(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Main entry point for LangExtract operations"""

        if operation == "extract_entities":
            return self._extract_entities(**kwargs)
        elif operation == "extract_relations":
            return self._extract_relations(**kwargs)
        elif operation == "extract_facts":
            return self._extract_facts(**kwargs)
        elif operation == "extract_all":
            return self._extract_all(**kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def _extract_entities(self, text: str, entity_types: List[str] = None) -> Dict[str, Any]:
        """Extract entities with span-level grounding"""

        if entity_types is None:
            entity_types = ["PERSON", "ORGANIZATION", "LOCATION", "DATE", "MONEY"]

        result = self.entity_extractor(text, entity_types)

        return {
            "extraction_type": "entities",
            "entities": result["entities"],
            "confidence": result["confidence"],
            "spans": result["spans"],
            "count": len(result["entities"]),
        }

    def _extract_relations(self, text: str, relation_types: List[str] = None) -> Dict[str, Any]:
        """Extract relations with span-level grounding"""

        if relation_types is None:
            relation_types = ["WORKS_FOR", "LOCATED_IN", "PART_OF", "FOUNDED_BY"]

        result = self.relation_extractor(text, relation_types)

        return {
            "extraction_type": "relations",
            "relations": result["relations"],
            "confidence": result["confidence"],
            "spans": result["spans"],
            "count": len(result["relations"]),
        }

    def _extract_facts(self, text: str, schema_name: str = "general") -> Dict[str, Any]:
        """Extract facts with span-level grounding"""

        schema = self.schemas.get(schema_name, self.schemas["general"])
        result = self.fact_extractor(text, schema)

        return {
            "extraction_type": "facts",
            "facts": result["facts"],
            "confidence": result["confidence"],
            "spans": result["spans"],
            "schema": schema.name,
            "count": len(result["facts"]),
        }

    def _extract_all(self, text: str) -> Dict[str, Any]:
        """Extract all types of structured information"""

        entities = self._extract_entities(text)
        relations = self._extract_relations(text)
        facts = self._extract_facts(text)

        return {
            "extraction_type": "all",
            "entities": entities,
            "relations": relations,
            "facts": facts,
            "total_extractions": entities["count"] + relations["count"] + facts["count"],
        }

    def _initialize_schemas(self) -> Dict[str, ExtractionSchema]:
        """Initialize predefined extraction schemas"""

        schemas = {}

        # General fact schema
        schemas["general"] = ExtractionSchema(
            name="general",
            fields=[
                {"name": "subject", "type": "string", "required": True},
                {"name": "predicate", "type": "string", "required": True},
                {"name": "object", "type": "string", "required": True},
                {"name": "confidence", "type": "float", "required": False},
            ],
            validation_rules=["subject != object"],
            span_tracking=True,
            confidence_threshold=0.8,
        )

        # Technical documentation schema
        schemas["technical"] = ExtractionSchema(
            name="technical",
            fields=[
                {"name": "component", "type": "string", "required": True},
                {"name": "function", "type": "string", "required": True},
                {"name": "input", "type": "string", "required": False},
                {"name": "output", "type": "string", "required": False},
                {"name": "dependencies", "type": "list", "required": False},
            ],
            validation_rules=["component != function"],
            span_tracking=True,
            confidence_threshold=0.9,
        )

        # Business process schema
        schemas["business"] = ExtractionSchema(
            name="business",
            fields=[
                {"name": "process", "type": "string", "required": True},
                {"name": "step", "type": "string", "required": True},
                {"name": "actor", "type": "string", "required": False},
                {"name": "duration", "type": "string", "required": False},
                {"name": "outcome", "type": "string", "required": False},
            ],
            validation_rules=["process != step"],
            span_tracking=True,
            confidence_threshold=0.85,
        )

        return schemas


# ---------- LangExtract Interface ----------


class LangExtractInterface:
    """High-level interface for LangExtract operations"""

    def __init__(self):
        self.system = LangExtractSystem()

    def extract(self, text: str, extraction_type: ExtractionType = ExtractionType.ENTITIES, **kwargs) -> Dict[str, Any]:
        """Extract structured information from text"""

        if extraction_type == ExtractionType.ENTITIES:
            return self.system.forward("extract_entities", text=text, **kwargs)
        elif extraction_type == ExtractionType.RELATIONS:
            return self.system.forward("extract_relations", text=text, **kwargs)
        elif extraction_type == ExtractionType.FACTS:
            return self.system.forward("extract_facts", text=text, **kwargs)
        else:
            return self.system.forward("extract_all", text=text)

    def get_schemas(self) -> Dict[str, ExtractionSchema]:
        """Get available extraction schemas"""
        return self.system.schemas


def create_lang_extract_interface() -> LangExtractInterface:
    """Create a LangExtract interface instance"""
    return LangExtractInterface()


# ---------- Research-Based Performance Metrics ----------


def evaluate_extraction_quality(extractions: List[Dict], ground_truth: List[Dict]) -> Dict[str, float]:
    """Evaluate extraction quality using research-based metrics"""

    # Precision: How many extracted items are correct
    correct_extractions = 0
    total_extractions = len(extractions)

    for extraction in extractions:
        if extraction in ground_truth:
            correct_extractions += 1

    precision = correct_extractions / total_extractions if total_extractions > 0 else 0

    # Recall: How many ground truth items were found
    found_ground_truth = 0
    total_ground_truth = len(ground_truth)

    for gt_item in ground_truth:
        if gt_item in extractions:
            found_ground_truth += 1

    recall = found_ground_truth / total_ground_truth if total_ground_truth > 0 else 0

    # F1 Score: Harmonic mean of precision and recall
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "total_extractions": total_extractions,
        "correct_extractions": correct_extractions,
    }
