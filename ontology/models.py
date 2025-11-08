from owlready2 import *

def create_hospital_kpi_ontology():
    """Create comprehensive hospital KPI ontology"""
    onto = get_ontology("http://hospital-kpis.org/hospital-kpi-ontology.owl")
    
    with onto:
        # Classes
        class Department(Thing): pass
        class KPICategory(Thing): pass
        class KPI(Thing): pass
        class Unit(Thing): pass
        class TimePeriod(Thing): pass
        class AlertLevel(Thing): pass
        
        # Subclasses
        class Efficiency(KPICategory): pass
        class QualityOfCare(KPICategory): pass
        class Safety(KPICategory): pass
        class Financial(KPICategory): pass
        class PatientSatisfaction(KPICategory): pass
        class Operational(KPICategory): pass
        
        class EmergencyDepartment(Department): pass
        class ICU(Department): pass
        class Surgery(Department): pass
        class Radiology(Department): pass
        class Pharmacy(Department): pass
        class HospitalAdministration(Department): pass
        
        class Normal(AlertLevel): pass
        class Warning(AlertLevel): pass
        class Critical(AlertLevel): pass
        
        # Properties
        class is_measured_in(InverseFunctionalProperty, ObjectProperty):
            domain = [KPI]; range = [Unit]
        
        class belongs_to_category(ObjectProperty):
            domain = [KPI]; range = [KPICategory]
        
        class belongs_to_department(ObjectProperty):
            domain = [KPI]; range = [Department]
        
        class has_alert_level(ObjectProperty):
            domain = [KPI]; range = [AlertLevel]
        
        class has_time_period(ObjectProperty):
            domain = [KPI]; range = [TimePeriod]
            
        class depends_on(ObjectProperty):
            domain = [KPI]; range = [KPI]
            
        class affects(ObjectProperty):
            domain = [KPI]; range = [KPI]
            inverse_property = depends_on
        
        class kpi_name(DataProperty, FunctionalProperty):
            domain = [KPI]; range = [str]
        
        class description(DataProperty):
            domain = [KPI]; range = [str]
        
        class actual_value(DataProperty):
            domain = [KPI]; range = [float]
        
        class target_value(DataProperty):
            domain = [KPI]; range = [float]
        
        class warning_threshold(DataProperty):
            domain = [KPI]; range = [float]
        
        class critical_threshold(DataProperty):
            domain = [KPI]; range = [float]
        
        class weight(DataProperty):
            domain = [KPI]; range = [float]
        
        class trend_direction(DataProperty):
            domain = [KPI]; range = [str]
        
        class dept_name(DataProperty, FunctionalProperty):
            domain = [Department]; range = [str]
        
        class bed_capacity(DataProperty):
            domain = [Department]; range = [int]
        
        class staff_count(DataProperty):
            domain = [Department]; range = [int]
    
    return onto