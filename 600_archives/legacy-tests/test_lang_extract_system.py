#!/usr/bin/env python3
"""
Test LangExtract System
Validates research-based structured extraction with span-level grounding
"""

import unittest

from src.dspy_modules.lang_extract_system import (
    EntityExtractor,
    ExtractionType,
    LangExtractInterface,
    LangExtractSystem,
    evaluate_extraction_quality,
)


class TestLangExtractSystem(unittest.TestCase):
    """Test LangExtract system functionality"""

    def setUp(self):
        """Set up test environment"""
        self.system = LangExtractSystem()
        self.interface = LangExtractInterface()

        # Test text for extraction
        self.test_text = """
        John Smith works for Microsoft Corporation in Seattle, Washington.
        He joined the company in 2020 and leads the Azure cloud platform team.
        The team develops cloud infrastructure solutions for enterprise customers.
        """

        # Test technical text
        self.technical_text = """
        The DSPy framework provides declarative prompt programming capabilities.
        It uses teleprompter optimization to improve prompt performance.
        The system integrates with PostgreSQL for vector storage.
        """

    def test_entity_extraction(self):
        """Test entity extraction with span-level grounding"""

        result = self.system.forward("extract_entities", text=self.test_text)

        # Validate result structure
        self.assertIn("extraction_type", result)
        self.assertEqual(result["extraction_type"], "entities")
        self.assertIn("entities", result)
        self.assertIn("confidence", result)
        self.assertIn("spans", result)
        self.assertIn("count", result)

        # Validate confidence score
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

        # Validate entities list
        self.assertIsInstance(result["entities"], list)
        self.assertEqual(result["count"], len(result["entities"]))

    def test_relation_extraction(self):
        """Test relation extraction with span-level grounding"""

        result = self.system.forward("extract_relations", text=self.test_text)

        # Validate result structure
        self.assertIn("extraction_type", result)
        self.assertEqual(result["extraction_type"], "relations")
        self.assertIn("relations", result)
        self.assertIn("confidence", result)
        self.assertIn("spans", result)
        self.assertIn("count", result)

        # Validate confidence score
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

        # Validate relations list
        self.assertIsInstance(result["relations"], list)
        self.assertEqual(result["count"], len(result["relations"]))

    def test_fact_extraction(self):
        """Test fact extraction with span-level grounding"""

        result = self.system.forward("extract_facts", text=self.test_text)

        # Validate result structure
        self.assertIn("extraction_type", result)
        self.assertEqual(result["extraction_type"], "facts")
        self.assertIn("facts", result)
        self.assertIn("confidence", result)
        self.assertIn("spans", result)
        self.assertIn("schema", result)
        self.assertIn("count", result)

        # Validate confidence score
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)

        # Validate facts list
        self.assertIsInstance(result["facts"], list)
        self.assertEqual(result["count"], len(result["facts"]))

    def test_extract_all(self):
        """Test comprehensive extraction of all types"""

        result = self.system.forward("extract_all", text=self.test_text)

        # Validate result structure
        self.assertIn("extraction_type", result)
        self.assertEqual(result["extraction_type"], "all")
        self.assertIn("entities", result)
        self.assertIn("relations", result)
        self.assertIn("facts", result)
        self.assertIn("total_extractions", result)

        # Validate sub-results
        self.assertIn("extraction_type", result["entities"])
        self.assertIn("extraction_type", result["relations"])
        self.assertIn("extraction_type", result["facts"])

        # Validate total count
        total = result["entities"]["count"] + result["relations"]["count"] + result["facts"]["count"]
        self.assertEqual(result["total_extractions"], total)

    def test_interface_extraction(self):
        """Test high-level interface extraction"""

        # Test entity extraction
        result = self.interface.extract(self.test_text, ExtractionType.ENTITIES)

        self.assertIn("extraction_type", result)
        self.assertEqual(result["extraction_type"], "entities")

        # Test relation extraction
        result = self.interface.extract(self.test_text, ExtractionType.RELATIONS)

        self.assertIn("extraction_type", result)
        self.assertEqual(result["extraction_type"], "relations")

        # Test fact extraction
        result = self.interface.extract(self.test_text, ExtractionType.FACTS)

        self.assertIn("extraction_type", result)
        self.assertEqual(result["extraction_type"], "facts")

    def test_schema_validation(self):
        """Test extraction schema validation"""

        schemas = self.interface.get_schemas()

        # Validate schema structure
        self.assertIn("general", schemas)
        self.assertIn("technical", schemas)
        self.assertIn("business", schemas)

        # Validate general schema
        general_schema = schemas["general"]
        self.assertEqual(general_schema.name, "general")
        self.assertIsInstance(general_schema.fields, list)
        self.assertIsInstance(general_schema.validation_rules, list)
        self.assertIsInstance(general_schema.span_tracking, bool)
        self.assertIsInstance(general_schema.confidence_threshold, float)

        # Validate technical schema
        technical_schema = schemas["technical"]
        self.assertEqual(technical_schema.name, "technical")
        self.assertGreater(len(technical_schema.fields), 0)
        self.assertGreater(technical_schema.confidence_threshold, 0.8)

    def test_span_validation(self):
        """Test span-level grounding validation"""

        # Test valid spans
        valid_spans = [{"start": 0, "end": 10}, {"start": 5, "end": 15}, {"start": 20, "end": 30}]

        # Test invalid spans
        invalid_spans = [
            {"start": -1, "end": 10},  # Negative start
            {"start": 15, "end": 10},  # Start > end
            {"start": 5, "end": 1000},  # End > text length
            {"start": 5},  # Missing end
            {"end": 10},  # Missing start
        ]

        # Test span validation methods
        entity_extractor = EntityExtractor()

        # Valid spans should pass
        self.assertTrue(entity_extractor.validate_spans(valid_spans, self.test_text))

        # Invalid spans should fail
        for invalid_span in invalid_spans:
            self.assertFalse(entity_extractor.validate_spans([invalid_span], self.test_text))

    def test_quality_evaluation(self):
        """Test extraction quality evaluation metrics"""

        # Test data
        extractions = [
            {"text": "John Smith", "type": "PERSON"},
            {"text": "Microsoft", "type": "ORGANIZATION"},
            {"text": "Seattle", "type": "LOCATION"},
        ]

        ground_truth = [
            {"text": "John Smith", "type": "PERSON"},
            {"text": "Microsoft Corporation", "type": "ORGANIZATION"},
            {"text": "Seattle", "type": "LOCATION"},
            {"text": "Washington", "type": "LOCATION"},
        ]

        # Evaluate quality
        metrics = evaluate_extraction_quality(extractions, ground_truth)

        # Validate metrics structure
        self.assertIn("precision", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("f1_score", metrics)
        self.assertIn("total_extractions", metrics)
        self.assertIn("correct_extractions", metrics)

        # Validate metric values
        self.assertGreaterEqual(metrics["precision"], 0)
        self.assertLessEqual(metrics["precision"], 1)
        self.assertGreaterEqual(metrics["recall"], 0)
        self.assertLessEqual(metrics["recall"], 1)
        self.assertGreaterEqual(metrics["f1_score"], 0)
        self.assertLessEqual(metrics["f1_score"], 1)

        # Validate counts
        self.assertEqual(metrics["total_extractions"], 3)
        self.assertGreaterEqual(metrics["correct_extractions"], 0)
        self.assertLessEqual(metrics["correct_extractions"], 3)

    def test_dspy_assertions(self):
        """Test DSPy assertions for validation"""

        # Test that assertions are properly applied
        entity_extractor = EntityExtractor()

        # This should work with valid input
        try:
            result = entity_extractor(text=self.test_text, entity_types=["PERSON", "ORGANIZATION"])
            self.assertIn("entities", result)
            self.assertIn("confidence", result)
            self.assertIn("spans", result)
        except Exception as e:
            # If assertions fail, that's expected behavior
            self.assertIn("Assert", str(e))

    def test_research_based_features(self):
        """Test research-based features implementation"""

        # Test span-level grounding
        result = self.system.forward("extract_entities", text=self.test_text)

        # Validate span information is included
        self.assertIn("spans", result)
        if result["spans"]:
            for span in result["spans"]:
                self.assertIn("start", span)
                self.assertIn("end", span)
                self.assertIsInstance(span["start"], int)
                self.assertIsInstance(span["end"], int)

        # Test confidence validation
        self.assertIn("confidence", result)
        confidence = result["confidence"]
        self.assertIsInstance(confidence, (int, float))
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)

        # Test extraction count
        self.assertIn("count", result)
        count = result["count"]
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
