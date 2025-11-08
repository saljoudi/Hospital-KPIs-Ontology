import pandas as pd
from owlready2 import *

class KPIAnalytics:
    def __init__(self, ontology):
        self.onto = ontology
    
    def get_dashboard_data(self):
        """Prepare data for dashboard"""
        kpis = []
        for kpi in self.onto.KPI.instances():
            kpis.append({
                'id': kpi.name,
                'name': kpi.kpi_name,
                'department': kpi.belongs_to_department[0].dept_name if kpi.belongs_to_department else 'Unknown',
                'category': kpi.belongs_to_category[0].__class__.__name__ if kpi.belongs_to_category else 'Unknown',
                'actual': kpi.actual_value,
                'target': kpi.target_value,
                'status': self._get_status(kpi),
                'trend': kpi.trend_direction,
                'weight': kpi.weight
            })
        
        return pd.DataFrame(kpis)
    
    def _get_status(self, kpi):
        ratio = (kpi.actual_value / kpi.target_value) * 100
        if ratio >= 100:
            return 'good'
        elif ratio >= 95:
            return 'warning'
        return 'critical'