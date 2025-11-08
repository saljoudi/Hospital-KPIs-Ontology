from owlready2 import *
import datetime
from .models import create_hospital_kpi_ontology

def load_kpi_data():
    """Load realistic hospital KPI instances"""
    onto = create_hospital_kpi_ontology()
    
    with onto:
        # Time periods & units
        monthly = TimePeriod("Monthly")
        quarterly = TimePeriod("Quarterly")
        percent = Unit("Percentage")
        minutes = Unit("Minutes")
        ratio = Unit("Ratio")
        
        # Departments
        ed = EmergencyDepartment("ED")
        ed.dept_name = "Emergency Department"
        ed.bed_capacity = 45
        ed.staff_count = 85
        
        icu = ICU("ICU")
        icu.dept_name = "Intensive Care Unit"
        icu.bed_capacity = 24
        icu.staff_count = 60
        
        surgery = Surgery("Surgery")
        surgery.dept_name = "Surgery Department"
        surgery.bed_capacity = 30
        surgery.staff_count = 50
        
        admin = HospitalAdministration("Admin")
        admin.dept_name = "Hospital Administration"
        
        # Emergency Department KPIs
        ed_wait = KPI("ED_Wait_Time")
        ed_wait.kpi_name = "Door-to-Doctor Time"
        ed_wait.actual_value = 32.5
        ed_wait.target_value = 30.0
        ed_wait.warning_threshold = 35.0
        ed_wait.critical_threshold = 45.0
        ed_wait.is_measured_in = [minutes]
        ed_wait.belongs_to_category = [Efficiency()]
        ed_wait.belongs_to_department = [ed]
        ed_wait.weight = 0.85
        ed_wait.has_time_period = [monthly]
        ed_wait.trend_direction = "stable"
        
        ed_lwbs = KPI("ED_LWBS")
        ed_lwbs.kpi_name = "Left Without Being Seen Rate"
        ed_lwbs.actual_value = 3.2
        ed_lwbs.target_value = 2.0
        ed_lwbs.warning_threshold = 3.0
        ed_lwbs.critical_threshold = 5.0
        ed_lwbs.is_measured_in = [percent]
        ed_lwbs.belongs_to_category = [QualityOfCare(), PatientSatisfaction()]
        ed_lwbs.belongs_to_department = [ed]
        ed_lwbs.weight = 0.95
        ed_lwbs.has_time_period = [monthly]
        ed_lwbs.trend_direction = "up"
        
        ed_mortality = KPI("ED_Mortality_Rate")
        ed_mortality.kpi_name = "ED Mortality Rate"
        ed_mortality.actual_value = 1.8
        ed_mortality.target_value = 1.5
        ed_mortality.warning_threshold = 2.0
        ed_mortality.critical_threshold = 2.5
        ed_mortality.is_measured_in = [percent]
        ed_mortality.belongs_to_category = [Safety(), QualityOfCare()]
        ed_mortality.belongs_to_department = [ed]
        ed_mortality.weight = 0.98
        ed_mortality.has_time_period = [monthly]
        ed_mortality.trend_direction = "up"
        
        # ICU KPIs
        icu_clabsi = KPI("ICU_CLABSI_Rate")
        icu_clabsi.kpi_name = "CLABSI Rate"
        icu_clabsi.actual_value = 0.85
        icu_clabsi.target_value = 0.5
        icu_clabsi.warning_threshold = 1.0
        icu_clabsi.critical_threshold = 1.5
        icu_clabsi.is_measured_in = [ratio]
        icu_clabsi.belongs_to_category = [Safety(), QualityOfCare()]
        icu_clabsi.belongs_to_department = [icu]
        icu_clabsi.weight = 0.94
        icu_clabsi.has_time_period = [quarterly]
        icu_clabsi.trend_direction = "up"
        
        icu_occupancy = KPI("ICU_Occupancy_Rate")
        icu_occupancy.kpi_name = "ICU Occupancy Rate"
        icu_occupancy.actual_value = 87.5
        icu_occupancy.target_value = 85.0
        icu_occupancy.warning_threshold = 90.0
        icu_occupancy.critical_threshold = 95.0
        icu_occupancy.is_measured_in = [percent]
        icu_occupancy.belongs_to_category = [Operational(), Efficiency()]
        icu_occupancy.belongs_to_department = [icu]
        icu_occupancy.weight = 0.80
        icu_occupancy.has_time_period = [monthly]
        icu_occupancy.trend_direction = "up"
        
        # Surgery KPIs
        surgery_ssi = KPI("Surgery_SSI_Rate")
        surgery_ssi.kpi_name = "Surgical Site Infection Rate"
        surgery_ssi.actual_value = 2.1
        surgery_ssi.target_value = 2.0
        surgery_ssi.warning_threshold = 2.5
        surgery_ssi.critical_threshold = 3.0
        surgery_ssi.is_measured_in = [percent]
        surgery_ssi.belongs_to_category = [Safety(), QualityOfCare()]
        surgery_ssi.belongs_to_department = [surgery]
        surgery_ssi.weight = 0.96
        surgery_ssi.has_time_period = [quarterly]
        surgery_ssi.trend_direction = "stable"
        
        # Admin KPIs
        admin_margin = KPI("Hospital_Operating_Margin")
        admin_margin.kpi_name = "Operating Margin"
        admin_margin.actual_value = 4.2
        admin_margin.target_value = 5.0
        admin_margin.warning_threshold = 3.0
        admin_margin.critical_threshold = 1.0
        admin_margin.is_measured_in = [percent]
        admin_margin.belongs_to_category = [Financial()]
        admin_margin.belongs_to_department = [admin]
        admin_margin.weight = 1.0
        admin_margin.has_time_period = [quarterly]
        admin_margin.trend_direction = "down"
        
        admin_satisfaction = KPI("Patient_Satisfaction_Score")
        admin_satisfaction.kpi_name = "Patient Satisfaction Score"
        admin_satisfaction.actual_value = 82.0
        admin_satisfaction.target_value = 85.0
        admin_satisfaction.warning_threshold = 80.0
        admin_satisfaction.critical_threshold = 75.0
        admin_satisfaction.is_measured_in = [percent]
        admin_satisfaction.belongs_to_category = [PatientSatisfaction(), QualityOfCare()]
        admin_satisfaction.belongs_to_department = [admin]
        admin_satisfaction.weight = 0.92
        admin_satisfaction.has_time_period = [monthly]
        admin_satisfaction.trend_direction = "stable"
        
        admin_readmission = KPI("Hospital_Readmission_Rate")
        admin_readmission.kpi_name = "30-Day Readmission Rate"
        admin_readmission.actual_value = 12.8
        admin_readmission.target_value = 11.0
        admin_readmission.warning_threshold = 13.0
        admin_readmission.critical_threshold = 15.0
        admin_readmission.is_measured_in = [percent]
        admin_readmission.belongs_to_category = [QualityOfCare(), Financial()]
        admin_readmission.belongs_to_department = [admin]
        admin_readmission.weight = 0.91
        admin_readmission.has_time_period = [monthly]
        admin_readmission.trend_direction = "up"
        
        # Relationships
        ed_wait.affects = [ed_lwbs, admin_satisfaction]
        ed_lwbs.depends_on = [ed_wait]
        icu_occupancy.affects = [icu_clabsi]
        
    return onto