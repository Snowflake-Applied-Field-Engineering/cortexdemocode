"""
REST API server for Cortex Guard
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from cortex_guard import CortexGuard
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize Cortex Guard
guard = CortexGuard()

# Simple in-memory stats
stats = {
    'total_checks': 0,
    'blocked': 0,
    'safe': 0,
    'threats_by_type': {}
}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'cortex-guard',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/v1/check', methods=['POST'])
def check():
    """
    Check a single text input
    
    Request body:
    {
        "text": "string to analyze"
    }
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing required field: text'}), 400
    
    text = data['text']
    
    # Perform check
    result = guard.check(text)
    
    # Update stats
    stats['total_checks'] += 1
    if result.is_safe:
        stats['safe'] += 1
    else:
        stats['blocked'] += 1
        threat_type = result.threat_type.value
        stats['threats_by_type'][threat_type] = stats['threats_by_type'].get(threat_type, 0) + 1
    
    return jsonify({
        'is_safe': result.is_safe,
        'threat_type': result.threat_type.value,
        'severity': result.severity.value,
        'confidence': result.confidence,
        'message': result.message,
        'details': result.details,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/v1/batch', methods=['POST'])
def batch_check():
    """
    Check multiple text inputs
    
    Request body:
    {
        "texts": ["string1", "string2", ...]
    }
    """
    data = request.get_json()
    
    if not data or 'texts' not in data:
        return jsonify({'error': 'Missing required field: texts'}), 400
    
    texts = data['texts']
    
    if not isinstance(texts, list):
        return jsonify({'error': 'texts must be an array'}), 400
    
    # Perform batch check
    results = guard.batch_check(texts)
    
    # Update stats
    for result in results:
        stats['total_checks'] += 1
        if result.is_safe:
            stats['safe'] += 1
        else:
            stats['blocked'] += 1
            threat_type = result.threat_type.value
            stats['threats_by_type'][threat_type] = stats['threats_by_type'].get(threat_type, 0) + 1
    
    return jsonify({
        'results': [
            {
                'text': text,
                'is_safe': result.is_safe,
                'threat_type': result.threat_type.value,
                'severity': result.severity.value,
                'confidence': result.confidence,
                'message': result.message,
                'details': result.details
            }
            for text, result in zip(texts, results)
        ],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    return jsonify({
        'stats': stats,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/v1/stats/reset', methods=['POST'])
def reset_stats():
    """Reset statistics"""
    global stats
    stats = {
        'total_checks': 0,
        'blocked': 0,
        'safe': 0,
        'threats_by_type': {}
    }
    return jsonify({'message': 'Statistics reset successfully'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Cortex Guard API server on port {port}")
    print(f"API documentation: http://localhost:{port}/health")
    app.run(debug=True, host='0.0.0.0', port=port)

