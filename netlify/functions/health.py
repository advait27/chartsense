"""
Netlify Health Check Function

Simple diagnostic endpoint to verify:
1. Function is deployed correctly
2. Backend modules can be imported
3. Environment variables are set
"""

import json
import sys
import os
from pathlib import Path

def handler(event, context):
    """Health check handler"""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    diagnostics = {
        'status': 'ok',
        'python_version': sys.version,
        'environment': {}
    }
    
    # Check environment variables (don't expose values!)
    env_vars = ['HF_API_KEY', 'LOG_LEVEL', 'VISION_MODEL', 'REASONING_MODEL']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Show first 5 chars for API key, or first 20 for others
            if var == 'HF_API_KEY':
                diagnostics['environment'][var] = f"{value[:5]}..." if len(value) > 5 else "set (too short)"
            else:
                diagnostics['environment'][var] = value[:30] + "..." if len(value) > 30 else value
        else:
            diagnostics['environment'][var] = None
    
    # Try importing backend modules
    import_tests = {}
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from backend.config import HF_API_KEY, VISION_MODEL_ID, REASONING_MODEL_ID
        import_tests['backend.config'] = 'success'
        import_tests['HF_API_KEY_from_config'] = f"{HF_API_KEY[:5]}..." if HF_API_KEY and len(HF_API_KEY) > 5 else "NOT SET"
        import_tests['VISION_MODEL'] = VISION_MODEL_ID
        import_tests['REASONING_MODEL'] = REASONING_MODEL_ID
    except Exception as e:
        import_tests['backend.config'] = f'failed: {str(e)}'
    
    try:
        from backend.services.orchestrator import ChartAnalysisOrchestrator
        import_tests['backend.orchestrator'] = 'success'
    except Exception as e:
        import_tests['backend.orchestrator'] = f'failed: {str(e)}'
    
    try:
        from backend.core.hf_client import HuggingFaceClient
        import_tests['backend.hf_client'] = 'success'
    except Exception as e:
        import_tests['backend.hf_client'] = f'failed: {str(e)}'
    
    try:
        from PIL import Image
        import_tests['PIL'] = 'success'
    except Exception as e:
        import_tests['PIL'] = f'failed: {str(e)}'
    
    diagnostics['imports'] = import_tests
    
    # Check critical issues
    issues = []
    if not os.getenv('HF_API_KEY'):
        issues.append('CRITICAL: HF_API_KEY environment variable is not set in Netlify')
    elif len(os.getenv('HF_API_KEY', '')) < 10:
        issues.append('WARNING: HF_API_KEY seems too short or invalid')
    
    if issues:
        diagnostics['issues'] = issues
        diagnostics['status'] = 'has_issues'
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(diagnostics, indent=2)
    }
