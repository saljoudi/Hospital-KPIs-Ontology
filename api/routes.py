from flask import Blueprint, jsonify
from rdflib import Literal

def init_api(ontology):
    api_bp = Blueprint('api', __name__, url_prefix='/api')

    # ----------------------------------------------------------------------
    # /api/kpis – return all KPIs with details
    # ----------------------------------------------------------------------
    @api_bp.route('/kpis')
    def get_kpis():
        kpi_data = []
        for kpi in ontology.KPI.instances():
            dept = kpi.belongs_to_department[0].dept_name[0] if kpi.belongs_to_department else "N/A"
            kpi_data.append({
                "id": kpi.name,
                "name": str(kpi.kpi_name[0]) if kpi.kpi_name else kpi.name,
                "department": dept,
                "actual": float(kpi.actual_value[0]) if kpi.actual_value else None,
                "target": float(kpi.target_value[0]) if kpi.target_value else None,
                "trend": str(kpi.trend_direction[0]) if kpi.trend_direction else "N/A"
            })
        return jsonify(kpi_data)

    # ----------------------------------------------------------------------
    # /api/summary – executive summary
    # ----------------------------------------------------------------------
    @api_bp.route('/summary')
    def get_summary():
        kpis = ontology.KPI.instances()
        if not kpis:
            return jsonify({"error": "No KPI data found"}), 500

        total = len(kpis)
        below_target = sum(1 for k in kpis if k.actual_value and k.target_value and float(k.actual_value[0]) > float(k.target_value[0]))
        on_target = total - below_target
        avg_perf = sum(float(k.actual_value[0]) / float(k.target_value[0]) for k in kpis if k.actual_value and k.target_value) / total

        summary = {
            "total_kpis": total,
            "on_target": on_target,
            "below_target": below_target,
            "avg_performance_ratio": round(avg_perf, 2)
        }
        return jsonify(summary)

    # ----------------------------------------------------------------------
    # /api/reasoning – basic reasoning demo
    # ----------------------------------------------------------------------
    @api_bp.route('/reasoning')
    def reasoning():
        alerts, recs, log = [], [], []

        for kpi in ontology.KPI.instances():
            name = str(kpi.kpi_name[0]) if kpi.kpi_name else kpi.name
            actual = float(kpi.actual_value[0]) if kpi.actual_value else None
            warn = float(kpi.warning_threshold[0]) if kpi.warning_threshold else None
            crit = float(kpi.critical_threshold[0]) if kpi.critical_threshold else None
            trend = str(kpi.trend_direction[0]) if kpi.trend_direction else "N/A"

            if actual is None:
                continue

            if crit is not None and actual >= crit:
                alerts.append({"kpi": name, "message": f"Critical alert – value {actual} ≥ critical {crit}"})
                recs.append(f"Investigate {name} immediately. Trend: {trend}")
                log.append(f"{name}: CRITICAL alert triggered.")
            elif warn is not None and actual >= warn:
                alerts.append({"kpi": name, "message": f"Warning – value {actual} ≥ warning {warn}"})
                recs.append(f"Monitor {name} closely. Trend: {trend}")
                log.append(f"{name}: WARNING alert triggered.")
            else:
                log.append(f"{name}: Within acceptable range.")

        return jsonify({"alerts": alerts, "recommendations": recs, "log": log})

    return api_bp
