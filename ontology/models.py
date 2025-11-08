from owlready2 import *

def create_hospital_kpi_ontology():
    """
    Create a comprehensive Hospital KPI ontology with all core classes,
    object properties, and data properties.
    Returns:
        Ontology instance (owlready2.Ontology)
    """
    onto = get_ontology("http://hospital-kpis.org/hospital-kpi-ontology.owl")

    with onto:
        # ==================== CLASSES ====================
        class Department(Thing):
            pass

        class KPICategory(Thing):
            pass

        class KPI(Thing):
            pass

        class Unit(Thing):
            pass

        class TimePeriod(Thing):
            pass

        class AlertLevel(Thing):
            pass

        # ==================== SUBCLASSES ====================
        # KPI Categories
        class Efficiency(KPICategory):
            pass

        class QualityOfCare(KPICategory):
            pass

        class Safety(KPICategory):
            pass

        class Financial(KPICategory):
            pass

        class PatientSatisfaction(KPICategory):
            pass

        class Operational(KPICategory):
            pass

        # Departments
        class EmergencyDepartment(Department):
            pass

        class ICU(Department):
            pass

        class Surgery(Department):
            pass

        class Radiology(Department):
            pass

        class Pharmacy(Department):
            pass

        class HospitalAdministration(Department):
            pass

        # Alert Levels
        class Normal(AlertLevel):
            pass

        class Warning(AlertLevel):
            pass

        class Critical(AlertLevel):
            pass

        # ==================== OBJECT PROPERTIES ====================
        class is_measured_in(InverseFunctionalProperty, ObjectProperty):
            domain = [KPI]
            range = [Unit]

        class belongs_to_category(ObjectProperty):
            domain = [KPI]
            range = [KPICategory]

        class belongs_to_department(ObjectProperty):
            domain = [KPI]
            range = [Department]

        class has_alert_level(ObjectProperty):
            domain = [KPI]
            range = [AlertLevel]

        class has_time_period(ObjectProperty):
            domain = [KPI]
            range = [TimePeriod]

        class depends_on(ObjectProperty):
            domain = [KPI]
            range = [KPI]
            comment = ["Indicates KPI dependency"]

        class affects(ObjectProperty):
            domain = [KPI]
            range = [KPI]
            inverse_property = depends_on

        class comparable_to(ObjectProperty):
            domain = [KPI]
            range = [KPI]
            comment = ["KPIs that can be benchmarked together"]

        # ==================== DATA PROPERTIES ====================
        class kpi_name(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [str]

        class description(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [str]

        class actual_value(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [float]

        class target_value(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [float]

        class warning_threshold(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [float]

        class critical_threshold(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [float]

        class weight(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [float]

        class trend_direction(DataProperty, FunctionalProperty):
            domain = [KPI]
            range = [str]

        class dept_name(DataProperty, FunctionalProperty):
            domain = [Department]
            range = [str]

        class bed_capacity(DataProperty, FunctionalProperty):
            domain = [Department]
            range = [int]

        class staff_count(DataProperty, FunctionalProperty):
            domain = [Department]
            range = [int]

    return onto
