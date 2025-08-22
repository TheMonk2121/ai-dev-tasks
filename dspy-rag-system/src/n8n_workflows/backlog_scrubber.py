#!/usr/bin/env python3
"""
n8n Backlog Scrubber Workflow

Automatically calculates and updates scoring metadata in the backlog file.
This can be used as a standalone tool or integrated with n8n workflows.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.logger import get_logger
from utils.opentelemetry_config import trace_operation

logger = get_logger("backlog_scrubber")

class BacklogScrubber:
    """Automated backlog scoring and metadata management"""
    
    def __init__(self, backlog_path: str = None):
        """
        Initialize the backlog scrubber.
        
        Args:
            backlog_path: Path to the backlog.md file
        """
        if backlog_path is None:
            # Default to the main backlog file
            project_root = Path(__file__).parent.parent.parent.parent
            backlog_path = project_root / "000_backlog.md"
        
        self.backlog_path = Path(backlog_path)
        self.backup_path = self.backlog_path.with_suffix('.backup')
        
        # Scoring formula: (BV + TC + RR + LE) / Effort
        self.scoring_formula = lambda bv, tc, rr, le, effort: (bv + tc + rr + le) / effort
        
        # Regex patterns
        self.score_pattern = re.compile(r'<!--score:\s*({[^}]+})\s*-->')
        self.score_total_pattern = re.compile(r'<!--score_total:\s*([\d.]+)\s*-->')
        
        # Statistics
        self.stats = {
            "items_processed": 0,
            "scores_updated": 0,
            "errors_found": 0,
            "last_run": None
        }
    
    def read_backlog(self) -> str:
        """
        Read the backlog file.
        
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If backlog file doesn't exist
        """
        try:
            with trace_operation("backlog_scrubber_read_file"):
                if not self.backlog_path.exists():
                    raise FileNotFoundError(f"Backlog file not found: {self.backlog_path}")
                
                content = self.backlog_path.read_text(encoding='utf-8')
                logger.info(f"Read backlog file: {self.backlog_path}")
                return content
                
        except Exception as e:
            logger.error(f"Failed to read backlog file: {e}")
            raise
    
    def parse_score_metadata(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse scoring metadata from the backlog content.
        
        Args:
            content: Backlog file content
            
        Returns:
            List of parsed score metadata
        """
        scores = []
        
        try:
            with trace_operation("backlog_scrubber_parse_scores"):
                # Find all score comments
                matches = self.score_pattern.finditer(content)
                
                for match in matches:
                    try:
                        # Parse metadata (handles unquoted property names)
                        metadata_str = match.group(1)
                        
                        # Convert unquoted property names to valid JSON
                        # Replace bv: with "bv":, tc: with "tc":, etc.
                        json_str = metadata_str.replace('bv:', '"bv":')
                        json_str = json_str.replace('tc:', '"tc":')
                        json_str = json_str.replace('rr:', '"rr":')
                        json_str = json_str.replace('le:', '"le":')
                        json_str = json_str.replace('effort:', '"effort":')
                        json_str = json_str.replace('deps:', '"deps":')
                        
                        metadata = json.loads(json_str)
                        
                        # Extract scoring components
                        bv = metadata.get('bv', 0)
                        tc = metadata.get('tc', 0)
                        rr = metadata.get('rr', 0)
                        le = metadata.get('le', 0)
                        effort = metadata.get('effort', 1)
                        
                        # Calculate score
                        score_total = self.scoring_formula(bv, tc, rr, le, effort)
                        
                        scores.append({
                            'match': match.group(0),
                            'metadata': metadata,
                            'score_total': round(score_total, 1),
                            'position': match.start(),
                            'components': {
                                'bv': bv,
                                'tc': tc,
                                'rr': rr,
                                'le': le,
                                'effort': effort
                            }
                        })
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse score metadata: {e}")
                        self.stats["errors_found"] += 1
                    except Exception as e:
                        logger.error(f"Error processing score metadata: {e}")
                        self.stats["errors_found"] += 1
                
                self.stats["items_processed"] = len(scores)
                logger.info(f"Parsed {len(scores)} score metadata entries")
                return scores
                
        except Exception as e:
            logger.error(f"Failed to parse score metadata: {e}")
            return []
    
    def update_score_totals(self, content: str, scores: List[Dict[str, Any]]) -> str:
        """
        Update score totals in the backlog content.
        
        Args:
            content: Original backlog content
            scores: Parsed score metadata
            
        Returns:
            Updated content with score totals
        """
        try:
            with trace_operation("backlog_scrubber_update_scores"):
                updated_content = content
                updates_made = 0
                
                for score in scores:
                    # Create the new score total comment
                    new_score_total = f'<!--score_total: {score["score_total"]}-->'
                    
                    # Find existing score total comment after this score comment
                    score_end = score['position'] + len(score['match'])
                    remaining_content = updated_content[score_end:]
                    
                    # Look for existing score_total comment
                    total_match = self.score_total_pattern.search(remaining_content)
                    
                    if total_match:
                        # Replace existing score total
                        old_total = total_match.group(0)
                        start_pos = score_end + total_match.start()
                        end_pos = score_end + total_match.end()
                        
                        if old_total != new_score_total:
                            updated_content = (
                                updated_content[:start_pos] +
                                new_score_total +
                                updated_content[end_pos:]
                            )
                            updates_made += 1
                    else:
                        # Add new score total after the score comment
                        updated_content = (
                            updated_content[:score_end] +
                            '\n' + new_score_total +
                            updated_content[score_end:]
                        )
                        updates_made += 1
                
                self.stats["scores_updated"] = updates_made
                logger.info(f"Updated {updates_made} score totals")
                return updated_content
                
        except Exception as e:
            logger.error(f"Failed to update score totals: {e}")
            return content
    
    def create_backup(self) -> bool:
        """
        Create a backup of the current backlog file.
        
        Returns:
            True if backup created successfully
        """
        try:
            if self.backlog_path.exists():
                import shutil
                shutil.copy2(self.backlog_path, self.backup_path)
                logger.info(f"Created backup: {self.backup_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def write_backlog(self, content: str) -> bool:
        """
        Write the updated backlog content.
        
        Args:
            content: Updated backlog content
            
        Returns:
            True if write successful
        """
        try:
            with trace_operation("backlog_scrubber_write_file"):
                # Create backup first
                self.create_backup()
                
                # Write updated content
                self.backlog_path.write_text(content, encoding='utf-8')
                logger.info(f"Updated backlog file: {self.backlog_path}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to write backlog file: {e}")
            return False
    
    def validate_scores(self, scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and filter scores.
        
        Args:
            scores: Parsed scores
            
        Returns:
            Validated scores
        """
        validated = []
        
        for score in scores:
            components = score['components']
            
            # Check for valid ranges
            if (0 <= components['bv'] <= 10 and
                0 <= components['tc'] <= 10 and
                0 <= components['rr'] <= 10 and
                0 <= components['le'] <= 10 and
                components['effort'] > 0):
                validated.append(score)
            else:
                logger.warning(f"Invalid score components: {components}")
                self.stats["errors_found"] += 1
        
        return validated
    
    def scrub_backlog(self) -> Dict[str, Any]:
        """
        Main method to scrub the backlog file.
        
        Returns:
            Statistics about the operation
        """
        try:
            with trace_operation("backlog_scrubber_main"):
                logger.info("Starting backlog scrub operation")
                
                # Read backlog file
                content = self.read_backlog()
                
                # Parse score metadata
                scores = self.parse_score_metadata(content)
                
                # Validate scores
                validated_scores = self.validate_scores(scores)
                
                # Update score totals
                updated_content = self.update_score_totals(content, validated_scores)
                
                # Write updated content
                success = self.write_backlog(updated_content)
                
                # Update statistics
                self.stats["last_run"] = datetime.now().isoformat()
                
                if success:
                    logger.info("Backlog scrub completed successfully")
                else:
                    logger.error("Backlog scrub failed")
                
                return {
                    "success": success,
                    "stats": self.stats.copy(),
                    "items_processed": len(validated_scores),
                    "scores_updated": self.stats["scores_updated"],
                    "errors_found": self.stats["errors_found"]
                }
                
        except Exception as e:
            logger.error(f"Backlog scrub failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "stats": self.stats.copy()
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current statistics.
        
        Returns:
            Current statistics
        """
        return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset statistics."""
        self.stats = {
            "items_processed": 0,
            "scores_updated": 0,
            "errors_found": 0,
            "last_run": None
        }

def main():
    """Main entry point for the backlog scrubber."""
    import argparse
    
    parser = argparse.ArgumentParser(description="n8n Backlog Scrubber")
    parser.add_argument("--backlog-path", type=str, help="Path to backlog.md file")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize scrubber
    scrubber = BacklogScrubber(args.backlog_path)
    
    if args.dry_run:
        # Read and parse without writing
        content = scrubber.read_backlog()
        scores = scrubber.parse_score_metadata(content)
        validated_scores = scrubber.validate_scores(scores)
        
        print("Backlog Scrubber - Dry Run")
        print("=" * 40)
        print(f"Items processed: {len(validated_scores)}")
        print(f"Errors found: {scrubber.stats['errors_found']}")
        print()
        
        for score in validated_scores:
            components = score['components']
            print(f"Score: {score['score_total']}")
            print(f"  BV: {components['bv']}, TC: {components['tc']}, RR: {components['rr']}, LE: {components['le']}, Effort: {components['effort']}")
            print()
    else:
        # Run the scrubber
        result = scrubber.scrub_backlog()
        
        if result["success"]:
            print("✅ Backlog scrub completed successfully!")
            print(f"Items processed: {result['items_processed']}")
            print(f"Scores updated: {result['scores_updated']}")
            print(f"Errors found: {result['errors_found']}")
        else:
            print("❌ Backlog scrub failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 