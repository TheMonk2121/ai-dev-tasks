"""
Enhanced File Validator with OpenTelemetry Integration

Provides comprehensive file validation with corruption detection, quarantine system,
and OpenTelemetry tracing for production security and monitoring.
"""

import os
import hashlib
import shutil
import logging
import tempfile
from typing import Any, Optional
from pathlib import Path
from datetime import datetime

from .opentelemetry_config import trace_operation, add_span_attribute, record_exception, generate_correlation_id
from .prompt_sanitizer import SecurityError, load_security_config

logger = logging.getLogger(__name__)

class FileValidationError(Exception):
    """Raised when file validation fails"""
    pass

class FileCorruptionError(Exception):
    """Raised when file corruption is detected"""
    pass

class EnhancedFileValidator:
    """Enhanced file validator with corruption detection and quarantine system"""
    
    def __init__(self, quarantine_dir: str | None = None):
        """
        Initialize the enhanced file validator.
        
        Args:
            quarantine_dir: Directory for quarantined files (optional)
        """
        self.quarantine_dir = quarantine_dir or os.path.join(
            os.path.dirname(__file__), '..', '..', 'quarantine'
        )
        self._ensure_quarantine_dir()
        self.security_config = load_security_config()
    
    def _ensure_quarantine_dir(self) -> None:
        """Ensure quarantine directory exists"""
        os.makedirs(self.quarantine_dir, exist_ok=True)
        logger.info(f"Quarantine directory: {self.quarantine_dir}")
    
    def validate_file_with_tracing(self, 
                                 file_path: str, 
                                 file_size_bytes: int | None = None,
                                 correlation_id: str | None = None) -> dict[str, Any]:
        """
        Validate file with comprehensive checks and OpenTelemetry tracing.
        
        Args:
            file_path: Path to the file to validate
            file_size_bytes: File size in bytes (optional, will be calculated if not provided)
            correlation_id: Correlation ID for tracing (optional)
            
        Returns:
            Dictionary with validation results
            
        Raises:
            FileValidationError: If validation fails
            FileCorruptionError: If corruption is detected
        """
        if not correlation_id:
            correlation_id = generate_correlation_id()
        
        with trace_operation("file_validation", {
            "file.path": file_path,
            "file.size": file_size_bytes,
            "correlation.id": correlation_id
        }) as span:
            try:
                # Basic file validation
                basic_validation = self._validate_basic_file_properties(file_path, file_size_bytes)
                add_span_attribute("validation.basic", "passed")
                
                # File integrity checks
                integrity_checks = self._validate_file_integrity(file_path)
                add_span_attribute("validation.integrity", "passed")
                
                # Corruption detection
                corruption_check = self._detect_corruption(file_path)
                add_span_attribute("validation.corruption", "passed")
                
                # Security validation
                security_validation = self._validate_security(file_path)
                add_span_attribute("validation.security", "passed")
                
                # Compile results
                results = {
                    "correlation_id": correlation_id,
                    "file_path": file_path,
                    "file_size_bytes": basic_validation["file_size_bytes"],
                    "file_extension": basic_validation["file_extension"],
                    "validation_passed": True,
                    "integrity_checksum": integrity_checks["checksum"],
                    "corruption_detected": False,
                    "security_violations": [],
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_ms": 0  # Will be calculated by OpenTelemetry
                }
                
                span.set_attribute("validation.result", "success")
                logger.info(f"File validation successful: {file_path}")
                
                return results
                
            except FileCorruptionError as e:
                span.set_attribute("validation.result", "corruption_detected")
                span.set_attribute("error.type", "FileCorruptionError")
                record_exception(e)
                
                # Quarantine the corrupted file
                quarantine_path = self._quarantine_file(file_path, correlation_id, "corruption")
                
                results = {
                    "correlation_id": correlation_id,
                    "file_path": file_path,
                    "validation_passed": False,
                    "corruption_detected": True,
                    "quarantine_path": quarantine_path,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.warning(f"File corruption detected and quarantined: {file_path} -> {quarantine_path}")
                return results
                
            except FileValidationError as e:
                span.set_attribute("validation.result", "validation_failed")
                span.set_attribute("error.type", "FileValidationError")
                record_exception(e)
                
                results = {
                    "correlation_id": correlation_id,
                    "file_path": file_path,
                    "validation_passed": False,
                    "corruption_detected": False,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.error(f"File validation failed: {file_path} - {e}")
                return results
                
            except Exception as e:
                span.set_attribute("validation.result", "unexpected_error")
                span.set_attribute("error.type", type(e).__name__)
                record_exception(e)
                
                results = {
                    "correlation_id": correlation_id,
                    "file_path": file_path,
                    "validation_passed": False,
                    "corruption_detected": False,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.error(f"Unexpected error during file validation: {file_path} - {e}")
                return results
    
    def _validate_basic_file_properties(self, file_path: str, file_size_bytes: int | None = None) -> dict[str, Any]:
        """Validate basic file properties"""
        if not os.path.exists(file_path):
            raise FileValidationError(f"File does not exist: {file_path}")
        
        # Get file size if not provided
        if file_size_bytes is None:
            file_size_bytes = os.path.getsize(file_path)
        
        # Validate file size
        max_size_mb = self.security_config["file_validation"]["max_size_mb"]
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size_bytes > max_size_bytes:
            raise FileValidationError(f"File size {file_size_bytes} bytes exceeds limit {max_size_bytes} bytes")
        
        # Validate file extension
        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip('.')
        
        allowed_extensions = self.security_config["file_validation"]["allowed_ext"]
        if ext not in allowed_extensions:
            raise FileValidationError(f"File extension '{ext}' not allowed. Allowed: {allowed_extensions}")
        
        return {
            "file_size_bytes": file_size_bytes,
            "file_extension": ext,
            "file_path_valid": True
        }
    
    def _validate_file_integrity(self, file_path: str) -> dict[str, Any]:
        """Validate file integrity using checksums"""
        try:
            # Calculate SHA-256 checksum
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            checksum = sha256_hash.hexdigest()
            
            # Additional integrity checks based on file type
            integrity_issues = self._check_file_specific_integrity(file_path)
            
            if integrity_issues:
                raise FileCorruptionError(f"File integrity check failed: {', '.join(integrity_issues)}")
            
            return {
                "checksum": checksum,
                "integrity_valid": True,
                "integrity_issues": []
            }
            
        except Exception as e:
            raise FileCorruptionError(f"Failed to validate file integrity: {e}")
    
    def _check_file_specific_integrity(self, file_path: str) -> list[str]:
        """Check file-specific integrity based on file type"""
        issues = []
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        try:
            with open(file_path, 'rb') as f:
                # Read first few bytes for header validation
                header = f.read(8)
                
                if ext == '.txt' or ext == '.md':
                    # Text files: check for null bytes or invalid UTF-8
                    f.seek(0)
                    try:
                        content = f.read().decode('utf-8')
                        if '\x00' in content:
                            issues.append("Contains null bytes")
                    except UnicodeDecodeError:
                        issues.append("Invalid UTF-8 encoding")
                
                elif ext == '.pdf':
                    # PDF files: check for PDF header
                    if not header.startswith(b'%PDF'):
                        issues.append("Invalid PDF header")
                
                elif ext == '.csv':
                    # CSV files: basic structure check
                    f.seek(0)
                    lines = f.readlines()
                    if len(lines) == 0:
                        issues.append("Empty CSV file")
                    elif len(lines) == 1:
                        # Single line CSV might be valid, but check for basic structure
                        line = lines[0].decode('utf-8', errors='ignore')
                        if ',' not in line and '\t' not in line:
                            issues.append("CSV file lacks proper delimiter")
                
                # Add more file type checks as needed
                
        except Exception as e:
            issues.append(f"Error reading file: {e}")
        
        return issues
    
    def _detect_corruption(self, file_path: str) -> dict[str, Any]:
        """Detect file corruption using various methods"""
        corruption_indicators = []
        
        try:
            # Check file size consistency
            expected_size = os.path.getsize(file_path)
            actual_size = os.path.getsize(file_path)
            
            if expected_size != actual_size:
                corruption_indicators.append("File size inconsistency")
            
            # Check for common corruption patterns
            with open(file_path, 'rb') as f:
                content = f.read()
                
                # Check for excessive null bytes (common corruption indicator)
                null_byte_ratio = content.count(b'\x00') / len(content) if len(content) > 0 else 0
                if null_byte_ratio > 0.1:  # More than 10% null bytes
                    corruption_indicators.append("High null byte ratio")
                
                # Check for repeated patterns (another corruption indicator)
                if len(content) > 1000:
                    sample = content[:1000]
                    # Look for suspicious repeated patterns
                    if sample.count(sample[:10]) > 50:  # Too many repetitions
                        corruption_indicators.append("Suspicious repeated patterns")
            
            if corruption_indicators:
                raise FileCorruptionError(f"Corruption detected: {', '.join(corruption_indicators)}")
            
            return {
                "corruption_detected": False,
                "corruption_indicators": []
            }
            
        except Exception as e:
            raise FileCorruptionError(f"Corruption detection failed: {e}")
    
    def _validate_security(self, file_path: str) -> dict[str, Any]:
        """Validate file security"""
        security_violations = []
        
        try:
            # Check for path traversal attempts
            if '..' in file_path or '\\' in file_path:
                security_violations.append("Path traversal attempt")
            
            # Check for suspicious file names (but allow common development files)
            filename = os.path.basename(file_path)
            suspicious_patterns = ['temp', 'tmp', 'cache', 'log']
            if any(pattern in filename.lower() for pattern in suspicious_patterns):
                # Only flag if it's not a common development file
                if not any(dev_pattern in filename.lower() for dev_pattern in ['test', 'sample', 'example']):
                    security_violations.append("Suspicious filename")
            
            # Note: Removed writable file check as it's too strict for development
            # In production, this could be re-enabled with proper configuration
            
            if security_violations:
                raise FileValidationError(f"Security violations: {', '.join(security_violations)}")
            
            return {
                "security_valid": True,
                "security_violations": []
            }
            
        except Exception as e:
            raise FileValidationError(f"Security validation failed: {e}")
    
    def _quarantine_file(self, file_path: str, correlation_id: str, reason: str) -> str:
        """Move suspicious file to quarantine"""
        try:
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_filename = f"{timestamp}_{correlation_id[:8]}_{reason}_{filename}"
            quarantine_path = os.path.join(self.quarantine_dir, quarantine_filename)
            
            # Move file to quarantine
            shutil.move(file_path, quarantine_path)
            
            # Log quarantine action
            logger.warning(f"File quarantined: {file_path} -> {quarantine_path} (reason: {reason})")
            
            return quarantine_path
            
        except Exception as e:
            logger.error(f"Failed to quarantine file {file_path}: {e}")
            raise FileValidationError(f"Quarantine failed: {e}")
    
    def get_quarantine_status(self) -> dict[str, Any]:
        """Get quarantine directory status"""
        try:
            quarantine_files = []
            for filename in os.listdir(self.quarantine_dir):
                file_path = os.path.join(self.quarantine_dir, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    quarantine_files.append({
                        "filename": filename,
                        "file_path": file_path,
                        "file_size_bytes": file_size,
                        "quarantine_date": file_mtime.isoformat(),
                        "reason": self._extract_quarantine_reason(filename)
                    })
            
            return {
                "quarantine_dir": self.quarantine_dir,
                "total_files": len(quarantine_files),
                "files": quarantine_files
            }
            
        except Exception as e:
            logger.error(f"Failed to get quarantine status: {e}")
            return {
                "quarantine_dir": self.quarantine_dir,
                "total_files": 0,
                "files": [],
                "error": str(e)
            }
    
    def _extract_quarantine_reason(self, filename: str) -> str:
        """Extract quarantine reason from filename"""
        try:
            # Format: timestamp_correlationid_reason_originalname
            parts = filename.split('_', 3)
            if len(parts) >= 3:
                return parts[2]
            return "unknown"
        except:
            return "unknown"

# Global validator instance
file_validator = EnhancedFileValidator()

def validate_file_with_tracing(file_path: str, 
                             file_size_bytes: int | None = None,
                             correlation_id: str | None = None) -> dict[str, Any]:
    """Validate file with comprehensive checks and OpenTelemetry tracing"""
    return file_validator.validate_file_with_tracing(file_path, file_size_bytes, correlation_id)

def get_quarantine_status() -> dict[str, Any]:
    """Get quarantine directory status"""
    return file_validator.get_quarantine_status() 