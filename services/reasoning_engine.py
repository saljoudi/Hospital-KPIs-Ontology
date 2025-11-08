import pandas as pd
from datetime import datetime

class HospitalKPIReasoner:
    def __init__(self, ontology):
        self.onto = ontology
        self.results = {'alerts': [], 'insights': [], 'recommendations': []}
    
    def run_reasoning(self):
        """Execute reasoning pipeline"""
        self._semantic_reasoning()
        self._rule_based_inference()
        self._generate_recommendations()
        return self.results
    
    def _semantic_reasoning(self):
        """Classify KPI performance"""
        for kpi in self.onto.KPI.instances():
            ratio = (kpi.actual_value / kpi.target_value) * 100
            
            if ratio >= 100:
                kpi.has_alert_level = [self.onto.Normal()]
            elif ratio >= 95:
                kpi.has_alert_level = [self.onto.Warning()]
            else:
                kpi.has_alert_level = [self.onto.Critical()]
    
    def _rule_based_inference(self):
        """Apply business rules"""
        # Rule 1: ED Crisis
        if (self._find_kpi('ED_Wait_Time').actual_value > 40 and
            self._find_kpi('ED_LWBS').actual_value > 3.0):
            self._create_alert('CRITICAL', 'ED Capacity Crisis', 
                             'ED wait time >40min + LWBS >3% indicates capacity issues')
        
        # Rule 2: Financial Stress
        if self._find_kpi('Hospital_Operating_Margin').actual_value < 3.0:
            self._create_alert('WARNING', 'Financial Stress', 
                             'Operating margin below 3% - review cost structure')
    
    def _generate_recommendations(self):
        """Generate actionable insights"""
        critical_count = sum(1 for kpi in self.onto.KPI.instances() 
                           if self.onto.Critical() in kpi.has_alert_level)
        
        if critical_count >= 3:
            self.results['recommendations'].append({
                'priority': 'HIGH',
                'action': 'Executive review required - multiple critical KPIs detected',
                'owner': 'CEO/COO',
                'timeline': '24 hours'
            })
    
    def _find_kpi(self, name):
        for kpi in self.onto.KPI.instances():
            if kpi.name == name:
                return kpi
        return None
    
    def _create_alert(self, level, alert_type, message):
        self.results['alerts'].append({
            'level': level,
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })