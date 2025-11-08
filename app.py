from flask import Flask, render_template, jsonify
from ontology.data import load_kpi_data
from api.routes import init_api

app = Flask(__name__)
# server = app  # for Gunicorn compatibility


# DEMO: Hardcoded secret key for demo purposes only
# In production, use environment variable: os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = 'demo-key-change-in-production'

# Load ontology
print("🏥 Loading Hospital KPI Ontology...")
ontology = load_kpi_data()

# Register API routes
api_bp = init_api(ontology)
app.register_blueprint(api_bp)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', title='Hospital KPI Ontology Dashboard')

@app.route('/api/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'ontology_loaded': True})

if __name__ == '__main__':
    port = int(__import__('os').environ.get('PORT', 10000))
    debug = __import__('os').environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

