from flask import Blueprint, jsonify, request
from services.analytics import KPIAnalytics
from services.reasoning_engine import HospitalKPIReasoner

api_bp = Blueprint('api', __name__)

def init_api(ontology):
    analytics = KPIAnalytics(ontology)
    reasoner = HospitalKPIReasoner(ontology)
    
    @api_bp.route('/api/kpis', methods=['GET'])
    def get_kpis():
        data = analytics.get_dashboard_data()
        return jsonify(data.to_dict('records'))
    
    @api_bp.route('/api/reasoning', methods=['GET'])
    def run_reasoning():
        results = reasoner.run_reasoning()
        return jsonify(results)
    
    @api_bp.route('/api/kpi/<kpi_id>', methods=['GET'])
    def get_kpi_detail(kpi_id):
        kpi = ontology.search_one(iri=f"*{kpi_id}")
        if not kpi:
            return jsonify({'error': 'KPI not found'}), 404
        
        return jsonify({
            'id': kpi.name,
            'name': kpi.kpi_name,
            'description': kpi.description,
            'actual': kpi.actual_value,
            'target': kpi.target_value,
            'status': analytics._get_status(kpi)
        })
    
    return api_bp