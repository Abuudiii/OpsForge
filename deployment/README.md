# Deployment Files

This folder contains the deployment-ready files for the OpsForge project.

## Files:
- `demo.py` - Flask application for infrastructure creation
- `claude_api.py` - Claude API integration module

## Setup:
1. Install dependencies: `pip install anthropic flask python-dotenv`
2. Set environment variable: `ANTHROPIC_API_KEY=your_key_here`
3. Run the Flask app: `python demo.py`

## Usage:
Send POST requests to `/htn` endpoint with JSON payload containing `modifiedInfo` field.
