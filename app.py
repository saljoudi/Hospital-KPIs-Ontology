from flask import Flask, render_template
from ontology.data import load_kpi_data
from api.routes import init_api
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Load ontology
print("🏥 Loading Hospital KPI Ontology...")
ontology = load_kpi_data()

# Register API routes
api_bp = init_api(ontology)
app.register_blueprint(api_bp)

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', title='Hospital KPI Ontology Dashboard')

@app.route('/api/health')
def health_check():
    """Health check endpoint for Render"""
    return {'status': 'healthy', 'ontology_loaded': True}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)