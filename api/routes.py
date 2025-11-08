from flask import Blueprint, jsonify, request
import traceback

def init_api(ontology):
    api_bp = Blueprint('api', __name__)
    from services.analytics import KPIAnalytics
    from services.reasoning_engine import HospitalKPIReasoner
    
    analytics = KPIAnalytics(ontology)
    reasoner = HospitalKPIReasoner(ontology)
    
    @api_bp.route('/api/reasoning', methods=['GET'])
    def run_reasoning():
        """Execute reasoning engine with detailed logging"""
        print("🔍 REASONING ENDPOINT HIT - Starting analysis...")
        try:
            results = reasoner.run_reasoning()
            print(f"✅ Reasoning complete: {len(results['alerts'])} alerts, {len(results['recommendations'])} recommendations")
            return jsonify(results)
        except Exception as e:
            print(f"❌ Reasoning error: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500
    
    # Keep your other routes...
    @api_bp.route('/api/kpis', methods=['GET'])
    def get_kpis():
        try:
            df = analytics.get_dashboard_data()
            return jsonify(df.to_dict('records'))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @api_bp.route('/api/departments', methods=['GET'])
    def get_departments():
        try:
            summary = analytics.get_department_summary()
            return jsonify(summary)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return api_bp
