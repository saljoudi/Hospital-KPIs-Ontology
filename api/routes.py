from flask import Blueprint, jsonify, request
from services.analytics import KPIAnalytics
from services.reasoning_engine import HospitalKPIReasoner

def init_api(ontology):
    '''Initialize API routes with ontology instance'''
    api_bp = Blueprint('api', __name__)
    
    # Move instantiation inside the function to avoid circular imports
    analytics = KPIAnalytics(ontology)
    reasoner = HospitalKPIReasoner(ontology)
    
    @api_bp.route('/api/kpis', methods=['GET'])
    def get_kpis():
        '''Get all KPIs with performance data'''
        try:
            df = analytics.get_dashboard_data()
            return jsonify(df.to_dict('records'))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api_bp.route('/api/reasoning', methods=['GET'])
    def run_reasoning():
        '''Execute reasoning engine and return insights'''
        try:
            results = reasoner.run_reasoning()
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api_bp.route('/api/departments', methods=['GET'])
    def get_departments():
        '''Get department performance summary'''
        try:
            summary = analytics.get_department_summary()
            return jsonify(summary)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return api_bp
