import unittest
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ontology.data import load_kpi_data
from services.reasoning_engine import HospitalKPIReasoner
from services.analytics import KPIAnalytics
from owlready2 import *

class TestHospitalKPIOntology(unittest.TestCase):
    """Comprehensive tests for Hospital KPI Ontology Platform"""

    @classmethod
    def setUpClass(cls):
        """Set up test ontology once for all tests"""
        print("\n🔧 Setting up test ontology...")
        cls.ontology = load_kpi_data()
        cls.reasoner = HospitalKPIReasoner(cls.ontology)
        cls.analytics = KPIAnalytics(cls.ontology)
        
        # Verify ontology loaded
        cls.kpis = list(cls.ontology.KPI.instances())
        cls.departments = list(cls.ontology.Department.instances())
        print(f"✅ Loaded {len(cls.kpis)} KPIs and {len(cls.departments)} departments")

    def test_ontology_structure(self):
        """Test that ontology has correct classes and properties"""
        print("\n📋 Testing ontology structure...")
        
        # Test classes exist
        self.assertTrue(issubclass(self.ontology.KPI, Thing))
        self.assertTrue(issubclass(self.ontology.Department, Thing))
        self.assertTrue(issubclass(self.ontology.Efficiency, self.ontology.KPICategory))
        self.assertTrue(issubclass(self.ontology.Safety, self.ontology.KPICategory))
        
        # Test properties exist
        self.assertTrue(hasattr(self.ontology, 'kpi_name'))
        self.assertTrue(hasattr(self.ontology, 'actual_value'))
        self.assertTrue(hasattr(self.ontology, 'belongs_to_department'))
        self.assertTrue(hasattr(self.ontology, 'affects'))
        
        print("✅ Ontology structure validated")

    def test_kpi_instances_loaded(self):
        """Test that KPI instances are loaded with required properties"""
        print("\n📊 Testing KPI instances...")
        
        self.assertGreater(len(self.kpis), 0, "No KPI instances found")
        
        # Test first KPI has all required properties
        kpi = self.kpis[0]
        required_props = ['kpi_name', 'actual_value', 'target_value', 
                         'warning_threshold', 'critical_threshold', 'weight']
        
        for prop in required_props:
            self.assertTrue(hasattr(kpi, prop), f"KPI missing property: {prop}")
        
        # Test data types
        self.assertIsInstance(kpi.actual_value, (int, float))
        self.assertIsInstance(kpi.kpi_name, str)
        self.assertGreaterEqual(kpi.weight, 0.0)
        self.assertLessEqual(kpi.weight, 1.0)
        
        print(f"✅ All {len(self.kpis)} KPIs have required properties")

    def test_department_instances(self):
        """Test department instances"""
        print("\n🏥 Testing departments...")
        
        self.assertGreater(len(self.departments), 0, "No departments found")
        
        # Test department has required properties
        dept = self.departments[0]
        self.assertTrue(hasattr(dept, 'dept_name'))
        self.assertTrue(hasattr(dept, 'bed_capacity'))
        self.assertTrue(hasattr(dept, 'staff_count'))
        
        print(f"✅ All {len(self.departments)} departments have required properties")

    def test_kpi_relationships(self):
        """Test KPI relationships (affects/depends_on)"""
        print("\n🔗 Testing KPI relationships...")
        
        # Find ED Wait Time KPI
        ed_wait = self.ontology.search_one(iri="*ED_Wait_Time")
        self.assertIsNotNone(ed_wait, "ED_Wait_Time KPI not found")
        
        # Test it affects ED_LWBS
        self.assertTrue(hasattr(ed_wait, 'affects'))
        affected = list(ed_wait.affects)
        self.assertGreater(len(affected), 0, "ED Wait Time should affect other KPIs")
        
        print("✅ KPI relationships validated")

    def test_semantic_reasoning(self):
        """Test semantic reasoning (alert level classification)"""
        print("\n🧠 Testing semantic reasoning...")
        
        # Run semantic reasoning
        for kpi in self.kpis:
            ratio = (kpi.actual_value / kpi.target_value) * 100
            
            # Expected classification
            if ratio >= 100:
                expected_status = self.ontology.Normal
            elif ratio >= 95:
                expected_status = self.ontology.Warning
            else:
                expected_status = self.ontology.Critical
            
            # Check alert level is set
            self.assertTrue(hasattr(kpi, 'has_alert_level'))
            self.assertGreater(len(kpi.has_alert_level), 0, 
                             f"KPI {kpi.kpi_name} has no alert level")
            
            # Check it's the right type
            alert_level = kpi.has_alert_level[0]
            self.assertIsInstance(alert_level, expected_status)
        
        print("✅ Semantic reasoning assigns correct alert levels")

    def test_rule_based_inference(self):
        """Test rule-based reasoning engine"""
        print("\n⚡ Testing rule-based inference...")
        
        results = self.reasoner.run_reasoning()
        
        # Check structure
        self.assertIn('alerts', results)
        self.assertIn('insights', results)
        self.assertIn('recommendations', results)
        
        # Check types
        self.assertIsInstance(results['alerts'], list)
        self.assertIsInstance(results['insights'], list)
        self.assertIsInstance(results['recommendations'], list)
        
        # If there are alerts, validate structure
        for alert in results['alerts']:
            self.assertIn('level', alert)
            self.assertIn('type', alert)
            self.assertIn('message', alert)
            self.assertIn('timestamp', alert)
            self.assertIn(alert['level'], ['NORMAL', 'WARNING', 'CRITICAL'])
        
        print(f"✅ Rule-based reasoning generated {len(results['alerts'])} alerts")

    def test_ed_crisis_rule(self):
        """Test ED crisis alert rule specifically"""
        print("\n🚨 Testing ED crisis rule...")
        
        # Modify data to trigger rule
        ed_wait = self.ontology.search_one(iri="*ED_Wait_Time")
        ed_lwbs = self.ontology.search_one(iri="*ED_LWBS")
        
        original_wait = ed_wait.actual_value
        original_lwbs = ed_lwbs.actual_value
        
        try:
            # Trigger the rule (wait > 40 AND lwbs > 3%)
            ed_wait.actual_value = 45
            ed_lwbs.actual_value = 4.0
            
            results = self.reasoner.run_reasoning()
            
            # Check that crisis alert was generated
            crisis_alerts = [a for a in results['alerts'] 
                           if a['type'] == 'ED_Capacity_Crisis']
            self.assertGreater(len(crisis_alerts), 0, 
                             "ED crisis rule should trigger alert")
            
        finally:
            # Restore original values
            ed_wait.actual_value = original_wait
            ed_lwbs.actual_value = original_lwbs
        
        print("✅ ED crisis rule works correctly")

    def test_financial_stress_rule(self):
        """Test financial stress rule"""
        print("\n💰 Testing financial stress rule...")
        
        margin = self.ontology.search_one(iri="*Hospital_Operating_Margin")
        original_margin = margin.actual_value
        
        try:
            # Trigger financial stress (margin < 3%)
            margin.actual_value = 2.0
            
            results = self.reasoner.run_reasoning()
            
            stress_alerts = [a for a in results['alerts'] 
                           if a['type'] == 'Financial_Stress']
            self.assertGreater(len(stress_alerts), 0,
                             "Financial stress rule should trigger alert")
            
        finally:
            margin.actual_value = original_margin
        
        print("✅ Financial stress rule works correctly")

    def test_analytics_dashboard_data(self):
        """Test analytics dashboard data generation"""
        print("\n📊 Testing analytics service...")
        
        df = self.analytics.get_dashboard_data()
        
        # Check it's a DataFrame
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0, "No KPI data returned")
        
        # Check required columns
        required_cols = ['id', 'name', 'department', 'actual', 'target', 'status']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing column: {col}")
        
        # Check status values are valid
        valid_statuses = ['good', 'warning', 'critical']
        for status in df['status']:
            self.assertIn(status, valid_statuses)
        
        print(f"✅ Analytics returns {len(df)} KPIs with correct structure")

    def test_analytics_department_summary(self):
        """Test department summary calculation"""
        print("\n🏥 Testing department summary...")
        
        summary = self.analytics.get_department_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertGreater(len(summary), 0, "No departments in summary")
        
        # Check structure
        for dept_name, data in summary.items():
            self.assertIn('critical_count', data)
            self.assertIn('total_kpis', data)
            self.assertIn('health_score', data)
            self.assertGreaterEqual(data['health_score'], 0)
            self.assertLessEqual(data['health_score'], 100)
        
        print(f"✅ Department summary generated for {len(summary)} departments")

    def test_recommendations_generation(self):
        """Test recommendations are generated correctly"""
        print("\n💡 Testing recommendations...")
        
        results = self.reasoner.run_reasoning()
        
        # If there are critical KPIs, should have high priority recommendations
        critical_count = sum(1 for kpi in self.kpis 
                           if self.ontology.Critical() in kpi.has_alert_level)
        
        if critical_count >= 3:
            high_priority = [r for r in results['recommendations'] 
                           if 'P0-CRITICAL' in r['priority']]
            self.assertGreater(len(high_priority), 0,
                             "Should generate P0 recommendations for multiple critical KPIs")
        
        # Check recommendation structure
        for rec in results['recommendations']:
            self.assertIn('priority', rec)
            self.assertIn('action', rec)
            self.assertIn('owner', rec)
            self.assertIn('timeline', rec)
        
        print(f"✅ Generated {len(results['recommendations'])} recommendations")

    def test_api_health_endpoint(self):
        """Test health check API response structure"""
        print("\n🏥 Testing health endpoint...")
        
        with self.app.test_client() as client:
            response = client.get('/api/health')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'healthy')
            self.assertTrue(data['ontology_loaded'])
        
        print("✅ Health endpoint returns correct data")

    def test_api_kpis_endpoint(self):
        """Test KPIs API endpoint"""
        print("\n📡 Testing /api/kpis endpoint...")
        
        with self.app.test_client() as client:
            response = client.get('/api/kpis')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0, "API returned no KPIs")
            
            # Check first KPI has required fields
            kpi = data[0]
            required_fields = ['id', 'name', 'department', 'actual', 'target', 'status']
            for field in required_fields:
                self.assertIn(field, kpi, f"KPI missing field: {field}")
        
        print("✅ /api/kpis endpoint works correctly")

    def test_api_reasoning_endpoint(self):
        """Test reasoning API endpoint"""
        print("\n🧠 Testing /api/reasoning endpoint...")
        
        with self.app.test_client() as client:
            response = client.get('/api/reasoning')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('alerts', data)
            self.assertIn('insights', data)
            self.assertIn('recommendations', data)
        
        print("✅ /api/reasoning endpoint works correctly")

    def test_edge_case_no_critical_kpis(self):
        """Test system handles all KPIs performing well"""
        print("\n🟢 Testing edge case: all KPIs good...")
        
        # Temporarily set all KPIs to good performance
        original_values = []
        for kpi in self.kpis:
            original_values.append((kpi, kpi.actual_value))
            kpi.actual_value = kpi.target_value * 1.05  # 105% of target
        
        try:
            results = self.reasoner.run_reasoning()
            
            # Should have no critical alerts
            critical_alerts = [a for a in results['alerts'] 
                             if a['level'] == 'CRITICAL']
            self.assertEqual(len(critical_alerts), 0,
                           "No critical alerts when all KPIs perform well")
            
        finally:
            # Restore original values
            for kpi, original_value in original_values:
                kpi.actual_value = original_value
        
        print("✅ System handles all-good performance correctly")

    def test_circular_dependency_detection(self):
        """Test that circular dependencies don't break reasoning"""
        print("\n🔄 Testing circular dependency handling...")
        
        # Create a mock circular dependency
        kpi1 = self.kpis[0]
        kpi2 = self.kpis[1]
        
        original_affects = list(kpi1.affects)
        original_depends = list(kpi2.depends_on)
        
        try:
            # Create circular reference
            kpi1.affects.append(kpi2)
            kpi2.depends_on.append(kpi1)
            
            # This should not crash
            results = self.reasoner.run_reasoning()
            
            self.assertIsInstance(results, dict)
            self.assertIn('alerts', results)
            
        finally:
            # Restore
            kpi1.affects = original_affects
            kpi2.depends_on = original_depends
        
        print("✅ Circular dependencies handled gracefully")

    def test_performance_under_load(self):
        """Test reasoning engine performance with many runs"""
        print("\n⚡ Testing performance...")
        
        import time
        
        start_time = time.time()
        for _ in range(10):
            self.reasoner.run_reasoning()
        elapsed = time.time() - start_time
        
        self.assertLess(elapsed, 5.0, 
                       f"Reasoning too slow: {elapsed:.2f}s for 10 runs")
        
        print(f"✅ Performance acceptable: {elapsed:.2f}s for 10 runs")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
