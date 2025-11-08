from flask import Blueprint, jsonify, current_app
import traceback

def init_api(ontology):
    api_bp = Blueprint('api', __name__, url_prefix='/api')

    # Utility for safe value extraction
    def safe_val(prop):
        try:
            return float(prop[0]) if prop else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # /api/kpis
    # ------------------------------------------------------------------
    @api_bp.route('/kpis')
    def get_kpis():
        try:
            kpi_data = []
            for kpi in ontology.KPI.instances():
                dept = (
                    kpi.belongs_to_department[0].dept_name[0]
                    if getattr(kpi, "belongs_to_department", None)
                    and kpi.belongs_to_department
                    and getattr(kpi.belongs_to_department[0], "dept_name", None)
                    else "N/A"
                )
                kpi_data.append({
                    "id": kpi.name,
                    "name": str(kpi.kpi_name[0]) if kpi.kpi_name else kpi.name,
                    "department": dept,
                    "actual": safe_val(kpi.actual_value),
                    "target": safe_val(kpi.target_value),
                    "trend": str(kpi.trend_direction[0]) if kpi.trend_direction else "N/A"
                })
            return jsonify(kpi_data)
        except Exception as e:
            current_app.logger.error("❌ /api/kpis failed: %s", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    # ------------------------------------------------------------------
    # /api/summary
    # ------------------------------------------------------------------
    @api_bp.route('/summary')
    def get_summary():
        try:
            kpis = ontology.KPI.instances()
            if not kpis:
                return jsonify({"error": "No KPI data found"}), 500

            total = len(kpis)
            below_target = 0
            sum_ratio = 0
            for k in kpis:
                actual = safe_val(k.actual_value)
                target = safe_val(k.target_value)
                if actual is None or target is None or target == 0:
                    continue
                if actual > target:
                    below_target += 1
                sum_ratio += actual / target

            on_target = total - below_target
            avg_perf = (sum_ratio / total) if total else 0

            summary = {
                "total_kpis": total,
                "on_target": on_target,
                "below_target": below_target,
                "avg_performance_ratio": round(avg_perf, 2)
            }
            return jsonify(summary)
        except Exception as e:
            current_app.logger.error("❌ /api/summary failed: %s", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    # ------------------------------------------------------------------
    # /api/reasoning
    # ------------------------------------------------------------------
    @api_bp.route('/reasoning')
    def reasoning():
        try:
            alerts, recs, log = [], [], []
            for kpi in ontology.KPI.instances():
                name = str(kpi.kpi_name[0]) if kpi.kpi_name else kpi.name
                actual = safe_val(kpi.actual_value)
                warn = safe_val(kpi.warning_threshold)
                crit = safe_val(kpi.critical_threshold)
                trend = str(kpi.trend_direction[0]) if kpi.trend_direction else "N/A"

                if actual is None:
                    continue

                if crit is not None and actual >= crit:
                    alerts.append({"kpi": name, "message": f"Critical alert – value {actual} ≥ {crit}"})
                    recs.append(f"Investigate {name}. Trend: {trend}")
                    log.append(f"{name}: CRITICAL alert.")
                elif warn is not None and actual >= warn:
                    alerts.append({"kpi": name, "message": f"Warning – value {actual} ≥ {warn}"})
                    recs.append(f"Monitor {name}. Trend: {trend}")
                    log.append(f"{name}: WARNING alert.")
                else:
                    log.append(f"{name}: Normal range.")

            return jsonify({"alerts": alerts, "recommendations": recs, "log": log})
        except Exception as e:
            current_app.logger.error("❌ /api/reasoning failed: %s", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    return api_bp
