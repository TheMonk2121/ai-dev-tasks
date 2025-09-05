#!/usr/bin/env python3
"""
Backlog Scrubber Webhook Endpoint

Provides a webhook endpoint for n8n to trigger backlog scrubbing operations.
This can be integrated with n8n workflows for automated backlog management.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backlog_scrubber import BacklogScrubber

from utils.logger import get_logger
from utils.opentelemetry_config import trace_operation

logger = get_logger("backlog_webhook")

# Create Flask app
app = Flask(__name__)

# Global scrubber instance
scrubber = None

def get_scrubber() -> BacklogScrubber:
    """Get or create the backlog scrubber instance."""
    global scrubber
    if scrubber is None:
        backlog_path = os.getenv("BACKLOG_PATH")
        scrubber = BacklogScrubber(backlog_path)
    return scrubber

@app.route('/webhook/backlog-scrubber', methods=['POST'])
def backlog_scrubber_webhook():
    """
    Webhook endpoint for backlog scrubbing.
    
    Expected payload:
    {
        "action": "scrub",
        "backlog_path": "optional/path/to/backlog.md",
        "dry_run": false
    }
    """
    try:
        with trace_operation("backlog_webhook_scrub"):
            # Parse request
            if not request.is_json:
                raise BadRequest("Request must be JSON")

            data = request.get_json()
            action = data.get('action', 'scrub')

            # Validate action
            if action not in ['scrub', 'stats', 'validate']:
                raise BadRequest(f"Invalid action: {action}")

            # Get scrubber instance
            scrubber_instance = get_scrubber()

            # Handle different actions
            if action == 'scrub':
                return handle_scrub_action(scrubber_instance, data)
            elif action == 'stats':
                return handle_stats_action(scrubber_instance)
            elif action == 'validate':
                return handle_validate_action(scrubber_instance, data)

    except BadRequest as e:
        logger.error(f"Bad request: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 400

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def handle_scrub_action(scrubber: BacklogScrubber, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle scrub action."""
    dry_run = data.get('dry_run', False)

    if dry_run:
        # Perform dry run
        content = scrubber.read_backlog()
        scores = scrubber.parse_score_metadata(content)
        validated_scores = scrubber.validate_scores(scores)

        return jsonify({
            "success": True,
            "action": "scrub",
            "dry_run": True,
            "items_processed": len(validated_scores),
            "errors_found": scrubber.stats["errors_found"],
            "scores": [
                {
                    "score_total": score["score_total"],
                    "components": score["components"]
                }
                for score in validated_scores
            ],
            "timestamp": datetime.now().isoformat()
        })
    else:
        # Perform actual scrub
        result = scrubber.scrub_backlog()

        return jsonify({
            "success": result["success"],
            "action": "scrub",
            "dry_run": False,
            "items_processed": result["items_processed"],
            "scores_updated": result["scores_updated"],
            "errors_found": result["errors_found"],
            "timestamp": datetime.now().isoformat()
        })

def handle_stats_action(scrubber: BacklogScrubber) -> Dict[str, Any]:
    """Handle stats action."""
    stats = scrubber.get_statistics()

    return jsonify({
        "success": True,
        "action": "stats",
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    })

def handle_validate_action(scrubber: BacklogScrubber, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle validate action."""
    content = scrubber.read_backlog()
    scores = scrubber.parse_score_metadata(content)
    validated_scores = scrubber.validate_scores(scores)

    # Check for validation issues
    validation_issues = []
    for score in scores:
        if score not in validated_scores:
            validation_issues.append({
                "position": score["position"],
                "components": score["components"],
                "issue": "Invalid score components"
            })

    return jsonify({
        "success": True,
        "action": "validate",
        "total_scores": len(scores),
        "valid_scores": len(validated_scores),
        "validation_issues": validation_issues,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        get_scrubber()  # Verify scrubber is available
        return jsonify({
            "status": "healthy",
            "service": "backlog-scrubber-webhook",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics endpoint."""
    try:
        scrubber_instance = get_scrubber()
        stats = scrubber_instance.get_statistics()

        return jsonify({
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def main():
    """Main entry point for the webhook server."""
    import argparse

    parser = argparse.ArgumentParser(description="Backlog Scrubber Webhook Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5001, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--backlog-path", help="Path to backlog.md file")

    args = parser.parse_args()

    # Set environment variable if provided
    if args.backlog_path:
        os.environ["BACKLOG_PATH"] = args.backlog_path

    # Set up logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    print("Starting Backlog Scrubber Webhook Server")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Webhook URL: http://{args.host}:{args.port}/webhook/backlog-scrubber")
    print(f"Health Check: http://{args.host}:{args.port}/health")
    print(f"Statistics: http://{args.host}:{args.port}/stats")
    print()

    # Run the server
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

if __name__ == "__main__":
    main()
