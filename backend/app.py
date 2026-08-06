"""
================================================================================
AI AGENT - FLASK BACKEND API
================================================================================
"""

import os
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys

# Add parent folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import ExpenseCategorizationAgent

app = Flask(__name__)
CORS(app)  # Enable CORS for React

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'AI Agent API is running'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    print("\n📤 Upload called")
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    print(f"📄 File: {file.filename}")
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    print(f"✅ File saved to: {filepath}")
    
    try:
        print("🤖 Running agent...")
        agent = ExpenseCategorizationAgent()
        agent.run(filepath)
        print("✅ Agent finished")
        return jsonify({'success': True, 'message': 'File processed successfully'})
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        with open('expense_report.json', 'r') as f:
            report = json.load(f)
        return jsonify(report)
    except FileNotFoundError:
        return jsonify({'error': 'No report found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        with open('iteration_log.json', 'r') as f:
            logs = json.load(f)
        return jsonify(logs)
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory():
    try:
        with open('memory_cache.json', 'r') as f:
            memory = json.load(f)
        return jsonify(memory)
    except FileNotFoundError:
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 AI AGENT - BACKEND API")
    print("📍 http://127.0.0.1:5001")
    print("="*60 + "\n")
    app.run(debug=True, port=5001)