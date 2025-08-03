# Deep Research Analysis Request: Metadata Extractor Module

## Context for Code Review

You're reviewing a **config-driven metadata extractor** for the DSPy RAG system that extracts structured metadata from documents using YAML configuration rules. This is a critical component that affects data quality and retrieval accuracy for the entire RAG system.

Your job is to act as a senior engineer performing a system-aware code review of this metadata extraction implementation.

### Instructions:

1. **Identify architectural strengths and weaknesses** in the metadata extraction logic
2. **Evaluate performance characteristics** and optimization opportunities
3. **Assess error handling** and resilience patterns
4. **Review configuration management** and flexibility
5. **Analyze data quality** and accuracy of extraction
6. **Check for edge cases** and boundary conditions
7. **Suggest improvements** for production readiness and scalability
8. **Provide specific test code** for every suggested improvement

This is a **production-critical component** that needs to handle diverse file types and provide accurate metadata for the RAG system.

## Development Environment & Tools

- **Python 3.9** (not 3.10+ features like `match` statements)
- **PyYAML** for configuration management
- **dateutil** for date parsing
- **regex** for pattern matching
- **PostgreSQL with pgvector** for backend storage
- **Local development** - no cloud dependencies
- **Production focus** - needs to handle real-world document processing

## Recent Improvements Made

We've already implemented critical fixes in other modules:

### Enhanced DSPy RAG System:
- ✅ **DSPy signature correction** with proper domain context handling
- ✅ **Safe complexity score** with zero-division guard
- ✅ **TTL cache** for module selector with expiration
- ✅ **ReAct loop guard** to prevent infinite loops

### Dashboard Module:
- ✅ **Upload security hardening** with path traversal protection
- ✅ **Rate limiting** with token bucket implementation
- ✅ **Thread-safe history** with bounded deque
- ✅ **Executor shutdown** with proper cleanup

### VectorStore Module:
- ✅ **pgvector adapter** for direct numpy storage
- ✅ **Connection pooling** with SimpleConnectionPool
- ✅ **Singleton model** with @lru_cache for SentenceTransformer
- ✅ **Bulk inserts** with execute_values for efficiency

## Current Code for Review

Please review the following Metadata Extractor module code:

### Metadata Extractor (`src/utils/metadata_extractor.py`)

```python
#!/usr/bin/env python3
"""
Config-Driven Metadata Extractor for DSPy RAG System
Uses YAML configuration to extract metadata with scoring and ranking.
"""

import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class ConfigDrivenMetadataExtractor:
    """Config-driven metadata extraction with scoring and ranking"""
    
    def __init__(self, config_path: str = "config/metadata_rules.yaml"):
        """
        Initialize the metadata extractor with configuration
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._compile_patterns()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with proper error handling"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded metadata configuration from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}, using defaults")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load metadata configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if YAML loading fails"""
        return {
            'categories': [
                {
                    'name': 'Uncategorized',
                    'priority': 'medium',
                    'weight': 0,
                    'keywords': [],
                    'tags': []
                }
            ],
            'file_types': {},
            'priority_rules': {},
            'content_keywords': [],
            'date_patterns': [],
            'version_patterns': [],
            'size_categories': {'small': 1048576, 'medium': 10485760, 'large': 104857600}
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        self.date_patterns = []
        for pattern_config in self.config.get('date_patterns', []):
            self.date_patterns.append({
                'pattern': re.compile(pattern_config['pattern'], re.IGNORECASE),
                'format': pattern_config.get('format', '%Y-%m-%d')
            })
        
        self.version_patterns = []
        for pattern_config in self.config.get('version_patterns', []):
            self.version_patterns.append({
                'pattern': re.compile(pattern_config['pattern'], re.IGNORECASE),
                'group': pattern_config.get('group', 1)
            })
    
    def extract_metadata(self, document_path: str, content_preview: str = None) -> Dict[str, Any]:
        """
        Extract metadata from document using config-driven rules
        
        Args:
            document_path: Path to the document
            content_preview: Optional content preview for analysis
            
        Returns:
            Dictionary containing extracted metadata
        """
        try:
            path = Path(document_path)
            
            # Validate file exists and is accessible
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {document_path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {document_path}")
            
            # Get file stats with error handling
            try:
                stat = path.stat()
                file_size = stat.st_size
                created_at = stat.st_ctime
                modified_at = stat.st_mtime
            except OSError as e:
                logger.error(f"Failed to get file stats for {document_path}: {e}")
                raise
            
            filename = path.name
            file_type = path.suffix.lower().lstrip('.')
            
            # Initialize metadata
            metadata = {
                "filename": filename,
                "file_size": file_size,
                "file_type": file_type,
                "created_at": created_at,
                "modified_at": modified_at,
                "category": "Uncategorized",
                "tags": set(),  # Use set to avoid duplicates
                "priority": "medium",
                "notes": "",
                "content_type": "unknown",
                "processing_status": "pending",
                "extracted_at": datetime.now().isoformat(),
                "confidence_score": 0.0
            }
            
            # Extract category and tags using scoring
            category_result = self._extract_category_with_scoring(filename)
            metadata.update(category_result)
            
            # Extract file type specific metadata
            file_type_metadata = self._extract_file_type_metadata(file_type, filename)
            metadata.update(file_type_metadata)
            
            # Extract priority
            priority_result = self._extract_priority(filename)
            metadata['priority'] = priority_result['priority']
            metadata['priority_reasons'] = priority_result['reasons']
            
            # Extract dates and versions
            date_result = self._extract_dates_and_versions(filename)
            metadata.update(date_result)
            
            # Extract size category
            metadata['size_category'] = self._get_size_category(file_size)
            
            # Extract content-based metadata
            if content_preview:
                content_metadata = self._extract_content_metadata(content_preview)
                metadata['tags'].update(content_metadata['tags'])
            
            # Convert tags set to sorted list
            metadata['tags'] = sorted(list(metadata['tags']))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata for {document_path}: {e}")
            raise
    
    def _extract_category_with_scoring(self, filename: str) -> Dict[str, Any]:
        """Extract category using scoring system with improved accuracy"""
        filename_lower = filename.lower()
        
        # Tokenize filename for more accurate keyword matching
        words = set(re.split(r'\W+', filename_lower))
        
        best_category = "Uncategorized"
        best_score = 0
        all_tags = set()
        
        # Calculate max possible score for normalization
        max_possible_score = 0
        for category in self.config.get('categories', []):
            max_possible_score += category.get('weight', 1) * len(category.get('keywords', []))
        
        for category in self.config.get('categories', []):
            score = 0
            category_tags = set()
            
            # Score based on keyword matches (tokenized)
            for keyword in category.get('keywords', []):
                keyword_lower = keyword.lower()
                if keyword_lower in words:  # Exact word match
                    score += category.get('weight', 1)
                    category_tags.update(category.get('tags', []))
                elif keyword_lower in filename_lower:  # Substring fallback
                    score += category.get('weight', 1) * 0.5  # Lower score for substring
                    category_tags.update(category.get('tags', []))
            
            # Update best category if score is higher
            if score > best_score:
                best_score = score
                best_category = category['name']
                all_tags = category_tags
        
        # Normalize confidence score
        confidence = min(best_score / max(max_possible_score, 1), 1.0)
        
        return {
            'category': best_category,
            'tags': all_tags,
            'confidence_score': confidence
        }
    
    def _extract_file_type_metadata(self, file_type: str, filename: str) -> Dict[str, Any]:
        """Extract file type specific metadata"""
        file_type_config = self.config.get('file_types', {}).get(file_type, {})
        
        metadata = {
            'content_type': file_type_config.get('content_type', 'unknown'),
            'tags': set(file_type_config.get('tags', []))
        }
        
        # Apply special rules for file types
        filename_lower = filename.lower()
        for rule in file_type_config.get('special_rules', []):
            if 'if_contains' in rule:
                for keyword in rule['if_contains']:
                    if keyword.lower() in filename_lower:
                        metadata['tags'].update(rule.get('add_tags', []))
        
        return metadata
    
    def _extract_priority(self, filename: str) -> Dict[str, Any]:
        """Extract priority with reasons"""
        filename_lower = filename.lower()
        priority = "medium"
        reasons = []
        
        # Check high priority keywords
        high_priority_config = self.config.get('priority_rules', {}).get('high_priority', {})
        for keyword in high_priority_config.get('keywords', []):
            if keyword.lower() in filename_lower:
                priority = "high"
                reasons.append(f"Contains '{keyword}'")
        
        # Check low priority keywords
        low_priority_config = self.config.get('priority_rules', {}).get('low_priority', {})
        for keyword in low_priority_config.get('keywords', []):
            if keyword.lower() in filename_lower:
                priority = "low"
                reasons.append(f"Contains '{keyword}'")
        
        return {
            'priority': priority,
            'reasons': reasons
        }
    
    def _extract_dates_and_versions(self, filename: str) -> Dict[str, Any]:
        """Extract dates and versions from filename with improved error handling"""
        metadata = {}
        
        # Extract dates with limited parsing to avoid CPU spikes
        for pattern_config in self.date_patterns:
            match = pattern_config['pattern'].search(filename)
            if match:
                try:
                    date_str = match.group()
                    # Limit the string passed to dateutil for performance
                    if len(date_str) > 50:
                        date_str = date_str[:50]
                    
                    # Try to parse the date with validation
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    
                    # Validate year range
                    if 1900 <= parsed_date.year <= 2100:
                        metadata['extracted_date'] = parsed_date.strftime('%Y-%m-%d')
                        break
                except Exception as e:
                    logger.debug(f"Failed to parse date '{date_str}' from filename: {e}")
                    continue
        
        # Extract versions with improved group handling
        for pattern_config in self.version_patterns:
            match = pattern_config['pattern'].search(filename)
            if match:
                group_num = pattern_config['group']
                if group_num <= len(match.groups()) and match.group(group_num):
                    metadata['version'] = match.group(group_num)
                    break
        
        return metadata
    
    def _get_size_category(self, file_size: int) -> str:
        """Get size category based on file size"""
        size_categories = self.config.get('size_categories', {})
        
        if file_size <= size_categories.get('small', 1048576):
            return 'small'
        elif file_size <= size_categories.get('medium', 10485760):
            return 'medium'
        else:
            return 'large'
    
    def _extract_content_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from content preview with proper implementation"""
        content_lower = content.lower()
        tags = set()
        
        # Check for content keywords with case-insensitive matching
        for keyword in self.config.get('content_keywords', []):
            if keyword.lower() in content_lower:
                tags.add(keyword)
        
        return {
            'tags': tags
        }
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config = self._load_config()
        self._compile_patterns()
        logger.info("Metadata configuration reloaded")
    
    def get_category_info(self, category_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific category"""
        for category in self.config.get('categories', []):
            if category['name'] == category_name:
                return category
        return None
    
    def list_categories(self) -> List[Dict[str, Any]]:
        """List all available categories"""
        return self.config.get('categories', [])
```

## Critical Request: Test Code for Every Improvement

**IMPORTANT**: For every improvement you suggest, please provide the **actual test code** to validate that improvement. This is crucial because:

1. **We want to test the implementation, not just the idea**
2. **Deep research approaches testing differently** - we want to see your testing methodology
3. **Production readiness** requires comprehensive test coverage
4. **We need specific, runnable test code** for every suggested fix

### Test Requirements:
- **Unit tests** for individual functions/methods
- **Integration tests** for complete metadata extraction pipeline
- **Performance tests** with benchmarks and thresholds
- **Error handling tests** for file system and parsing failures
- **Configuration tests** for YAML loading and validation
- **Edge case tests** for boundary conditions and unusual inputs
- **Complete setup/teardown** with proper isolation
- **Specific assertions** and expected outcomes
- **Performance benchmarks** where applicable

Please provide the **complete test code** for every improvement you suggest, not just test descriptions. We want to see your testing approach and implementation.

## Review Focus Areas

Given this is a metadata extractor, please focus on:

### **🔴 Critical Priority:**
1. **Performance**: Is the extraction fast enough for production use?
2. **Accuracy**: Does it correctly categorize and tag documents?
3. **Error Handling**: Are all failure scenarios properly handled?
4. **Configuration Management**: Is the YAML config system robust?

### **🟠 High Priority:**
1. **Memory Usage**: Are there memory leaks or inefficient patterns?
2. **Scalability**: Can it handle large numbers of documents?
3. **Data Quality**: Is the extracted metadata useful for RAG?
4. **Maintainability**: Is the code easy to extend and modify?

### **🟡 Medium Priority:**
1. **Logging**: Is logging comprehensive enough for debugging?
2. **Validation**: Are inputs and outputs properly validated?
3. **Caching**: Could performance be improved with caching?
4. **Testing**: Is the code testable and well-structured?

## Specific Areas of Concern:

### **1. Performance and Scalability**
- Is regex compilation efficient for large configs?
- Does date parsing cause performance issues?
- Are there memory leaks in pattern matching?
- Can it handle thousands of documents efficiently?

### **2. Data Quality and Accuracy**
- Does the scoring system produce accurate categories?
- Are date and version extraction reliable?
- Does content analysis provide useful tags?
- Is confidence scoring meaningful?

### **3. Error Handling and Resilience**
- Are file system errors handled gracefully?
- Does YAML parsing handle malformed configs?
- Are regex patterns safe from catastrophic backtracking?
- Does date parsing handle edge cases?

### **4. Configuration Management**
- Is the YAML config system flexible enough?
- Can rules be updated without restarting?
- Are config validation errors clear?
- Is the default config comprehensive?

### **5. Production Readiness**
- Is logging comprehensive enough for monitoring?
- Are there proper metrics for performance tracking?
- Can it handle concurrent access safely?
- Is the API stable and well-documented?

## Advanced Analysis Request

### **Performance-Specific Concerns:**
1. **Regex Optimization**: Are patterns optimized for performance?
2. **Memory Management**: Are large configs handled efficiently?
3. **Caching Strategy**: Could results be cached for repeated files?
4. **Batch Processing**: Could multiple files be processed together?

### **Data Quality Concerns:**
1. **Scoring Algorithm**: Is the category scoring algorithm optimal?
2. **Keyword Matching**: Are keyword matches accurate and efficient?
3. **Date Parsing**: Is date extraction reliable across formats?
4. **Version Detection**: Does version extraction handle various formats?

### **Configuration Concerns:**
1. **YAML Validation**: Is the config schema validated?
2. **Rule Conflicts**: How are conflicting rules resolved?
3. **Default Behavior**: Are defaults sensible for all file types?
4. **Hot Reloading**: Can config be updated without restart?

### **Integration Concerns:**
1. **RAG Integration**: Does metadata improve retrieval quality?
2. **Database Storage**: Is metadata efficiently stored and retrieved?
3. **API Design**: Is the interface clean and consistent?
4. **Error Propagation**: Are errors properly handled up the stack?

Please provide your analysis with specific, actionable improvements and the complete test code to validate each improvement. Focus on making this production-ready for high-volume document processing with enhanced DSPy capabilities. 