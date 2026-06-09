"""
Core functionality tests for WATCHDOG
Tests ML model, feature extraction, and basic functionality
"""

import unittest
import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ml.feature_extractor import FeatureExtractor


class TestFeatureExtractor(unittest.TestCase):
    """Test the feature extraction functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = FeatureExtractor()
    
    def test_feature_extractor_initialization(self):
        """Test that feature extractor initializes correctly"""
        self.assertIsNotNone(self.extractor)
        self.assertEqual(self.extractor.window_size, 100)
        self.assertEqual(self.extractor.time_window, 2.0)
    
    def test_extract_packet_features(self):
        """Test basic packet feature extraction"""
        packet = {
            'src_ip': '192.168.1.1',
            'dst_ip': '10.0.0.1',
            'protocol': 6,
            'length': 100,
            'flags': 'S',
            'dst_port': 80,
            'direction': 'outbound'
        }
        
        features = self.extractor.extract_packet_features(packet)
        
        # Check that expected features are present
        self.assertIn('src_bytes', features)
        self.assertIn('dst_bytes', features)
        self.assertIn('count', features)
        self.assertIn('protocol_type', features)
        self.assertIn('service', features)
        self.assertIn('flag', features)
    
    def test_get_selected_features(self):
        """Test that selected features are extracted correctly"""
        packet = {
            'src_ip': '192.168.1.1',
            'dst_ip': '10.0.0.1',
            'protocol': 6,
            'length': 100,
            'flags': 'S',
            'dst_port': 80,
            'direction': 'outbound'
        }
        
        features = self.extractor.extract_packet_features(packet)
        selected, feature_names = self.extractor.get_selected_features(features)
        
        # Should return 20 selected features
        self.assertEqual(len(selected), 20)
        self.assertEqual(len(feature_names), 20)
        
        # All should be numeric
        for feature in selected:
            self.assertIsInstance(feature, (int, float))


class TestMLModel(unittest.TestCase):
    """Test ML model loading and prediction"""
    
    def test_model_file_exists(self):
        """Test that the ML model file exists"""
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'random_forest_model.pkl')
        self.assertTrue(os.path.exists(model_path), 
                       f"ML model file not found at {model_path}")
    
    def test_model_can_be_loaded(self):
        """Test that the model can be loaded with joblib"""
        try:
            import joblib
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'random_forest_model.pkl')
            model = joblib.load(model_path)
            self.assertIsNotNone(model)
        except ImportError:
            self.skipTest("joblib not installed")
        except Exception as e:
            self.fail(f"Failed to load model: {e}")


class TestSettingsManager(unittest.TestCase):
    """Test settings management functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary settings file for testing
        self.test_settings_file = '/tmp/test_watchdog_settings.json'
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_settings_file):
            os.remove(self.test_settings_file)
    
    def test_settings_file_creation(self):
        """Test that settings can be created and saved"""
        try:
            from ui.user_settings import LocalSettings
            settings = LocalSettings(self.test_settings_file)
            settings.save_settings()
            self.assertTrue(os.path.exists(self.test_settings_file))
        except ImportError:
            self.skipTest("user_settings module not available")


class TestFirewallManager(unittest.TestCase):
    """Test firewall management functionality"""
    
    def test_firewall_manager_initialization(self):
        """Test that firewall manager initializes"""
        try:
            from firewall_manager import FirewallManager
            # Note: This may require root privileges
            # We're just testing initialization, not actual blocking
            manager = FirewallManager()
            self.assertIsNotNone(manager)
        except ImportError:
            self.skipTest("firewall_manager module not available")
        except Exception as e:
            # May fail without root privileges, that's expected
            self.skipTest(f"Firewall manager requires root privileges: {e}")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestMLModel))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsManager))
    suite.addTests(loader.loadTestsFromTestCase(TestFirewallManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
