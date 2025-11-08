from flask import Blueprint, jsonify, current_app
import traceback

def init_api(ontology):
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    def safe_float(val_list):
        """Return first float value or None."""
        try:
            if val_list and len(val_list) > 0:
                return float(val_list[0])
        except Exception:
            return None
        return None

    # ------------------------------------------------------------
    # /api/kpis
    # ------------------------------------------------------------
    @api_bp.route("/kpis")
    def get_kpis():
        try:
            kpis = []
            for kpi in ontology.KPI.instances():
                dept = (
                    kpi.belongs_to_department[0].dept_name[0]
                    if getattr(kpi, "belongs_to_department", None)
                    and kpi.belongs_to_department
                    and getattr(kpi.belongs_to_department[0], "dept_name", None)
                    else "N/A"
                )
                kpis.append({
                    "id": kpi.name,
                    "name": str(kpi.kpi_name[0]) if getattr(kpi, "kpi_name", None) else kpi.name,
                    "department": dept,
                    "actual": safe_float(getattr(kpi, "actual_value", [])),
                    "target": safe_float(getattr(kpi, "target_value", [])),
                    "trend": str(kpi.trend_direction[0]) if getattr(kpi, "trend_direction", None) else "N/A"
                })
            return jsonify(kpis)
        except Exception as e:
            current_app.logger.error("❌ /api/kpis failed:\n%s", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    # ------------------------------------------------------------
    # /api/summary
    # ------------------------------------------------------------
    @api_bp.route("/summary")
    def get_summary():
        try:
            kpis = ontology.KPI.instances()
            total = len(kpis)
            if total == 0:
                return jsonify({"error": "No KPI data found"}), 500

            below_target = 0
            ratio_sum = 0
            valid_count = 0

            for kpi in kpis:
                actual = safe_float(getattr(kpi, "actual_value", []))
                target = safe_float(getattr(kpi, "target_value", []))
                if actual is None or target in (None, 0):
                    continue
                valid_count += 1
                ratio_sum += actual / target
                if actual > target:
                    below_target += 1

            on_target = valid_count - below_target
            avg_perf = round(ratio_sum / valid_count, 2) if valid_count else 0

            return jsonify({
                "total_kpis": valid_count,
                "on_target": on_target,
                "below_target": below_target,
                "avg_performance_ratio": avg_perf
            })
        except Exception as e:
            current_app.logger.error("❌ /api/summary failed:\n%s", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    # ------------------------------------------------------------
    # /api/reasoning
    # ------------------------------------------------------------
    @api_bp.route("/reasoning")
    def reasoning():
        try:
            alerts, recs, logs = [], [], []
            for kpi in ontology.KPI.instances():
                name = str(kpi.kpi_name[0]) if getattr(kpi, "kpi_name", None) else kpi.name
                actual = safe_float(getattr(kpi, "actual_value", []))
                warn = safe_float(getattr(kpi, "warning_threshold", []))
                crit = safe_float(getattr(kpi, "critical_threshold", []))
                trend = str(kpi.trend_direction[0]) if getattr(kpi, "trend_direction", None) else "N/A"

                if actual is None:
                    continue

                if crit is not None and actual >= crit:
                    alerts.append({"kpi": name, "message": f"Critical: {actual} ≥ {crit}"})
                    recs.append(f"Investigate {name} immediately (trend {trend})")
                    logs.append(f"{name}: CRITICAL")
                elif warn is not None and actual >= warn:
                    alerts.append({"kpi": name, "message": f"Warning: {actual} ≥ {warn}"})
                    recs.append(f"Monitor {name} closely (trend {trend})")
                    logs.append(f"{name}: WARNING")
                else:
                    logs.append(f"{name}: Normal")

            return jsonify({"alerts": alerts, "recommendations": recs, "log": logs})
        except Exception as e:
            current_app.logger.error("❌ /api/reasoning failed:\n%s", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    return api_bp
