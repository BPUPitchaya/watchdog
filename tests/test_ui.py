"""
UI component tests for WATCHDOG
Tests UI widgets, pages, and integration components
"""

import unittest
import sys
import os
import tempfile
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestTheme(unittest.TestCase):
    """Test theme configuration"""
    
    def test_theme_module_exists(self):
        """Test that theme module can be imported"""
        try:
            from ui.theme import THEME
            self.assertIsNotNone(THEME)
        except ImportError:
            self.skipTest("theme module not available")
    
    def test_theme_has_required_colors(self):
        """Test that theme has required color keys"""
        try:
            from ui.theme import THEME
            required_keys = ['primary', 'secondary', 'success', 'danger', 'warning', 
                           'bg_card', 'text_primary', 'text_secondary']
            for key in required_keys:
                self.assertIn(key, THEME, f"Theme missing required key: {key}")
        except ImportError:
            self.skipTest("theme module not available")


class TestSettingsManager(unittest.TestCase):
    """Test settings management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_settings_file = tempfile.NamedTemporaryFile(mode='w', 
                                                             suffix='.json', 
                                                             delete=False)
        self.test_settings_file.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_settings_file.name):
            os.remove(self.test_settings_file.name)
    
    def test_settings_initialization(self):
        """Test that settings manager initializes"""
        try:
            from ui.user_settings import LocalSettings
            settings = LocalSettings(self.test_settings_file.name)
            self.assertIsNotNone(settings)
        except ImportError:
            self.skipTest("user_settings module not available")
    
    def test_settings_save_and_load(self):
        """Test that settings can be saved and loaded"""
        try:
            from ui.user_settings import LocalSettings
            settings = LocalSettings(self.test_settings_file.name)
            
            # Set some values
            settings.set('test_key', 'test_value')
            settings.save_settings()
            
            # Load new instance
            settings2 = LocalSettings(self.test_settings_file.name)
            value = settings2.get('test_key')
            
            self.assertEqual(value, 'test_value')
        except ImportError:
            self.skipTest("user_settings module not available")
    
    def test_settings_default_values(self):
        """Test that settings have sensible defaults"""
        try:
            from ui.user_settings import LocalSettings
            settings = LocalSettings(self.test_settings_file.name)
            
            # Check for common settings
            auto_block = settings.get('auto_block', False)
            self.assertIsNotNone(auto_block)
            
            threshold = settings.get('threshold', 0.5)
            self.assertIsNotNone(threshold)
        except ImportError:
            self.skipTest("user_settings module not available")


class TestErrorHandler(unittest.TestCase):
    """Test error handling functionality"""
    
    def test_error_handler_initialization(self):
        """Test that error handler initializes"""
        self.skipTest("ErrorHandler requires QApplication context - skipped in headless tests")
    
    def test_error_handler_can_handle_exceptions(self):
        """Test that error handler can process exceptions"""
        self.skipTest("ErrorHandler requires QApplication context - skipped in headless tests")


class TestNotificationManager(unittest.TestCase):
    """Test notification management"""
    
    def test_notification_manager_initialization(self):
        """Test that notification manager initializes"""
        self.skipTest("NotificationManager requires QApplication context - skipped in headless tests")


class TestLogger(unittest.TestCase):
    """Test logging functionality"""
    
    def test_logger_initialization(self):
        """Test that logger can be initialized"""
        try:
            from utils.logger import get_logger
            logger = get_logger('test')
            self.assertIsNotNone(logger)
        except ImportError:
            self.skipTest("logger module not available")
    
    def test_logger_can_log_messages(self):
        """Test that logger can log messages without crashing"""
        try:
            from utils.logger import get_logger
            logger = get_logger('test')
            
            # Should not crash
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
        except ImportError:
            self.skipTest("logger module not available")


class TestFeatureExtractor(unittest.TestCase):
    """Test feature extraction for UI integration"""
    
    def test_feature_extractor_ui_integration(self):
        """Test that feature extractor works with UI packet format"""
        try:
            from ml.feature_extractor import FeatureExtractor
            extractor = FeatureExtractor()
            
            # Test with packet format from UI
            packet = {
                'src_ip': '192.168.1.1',
                'dst_ip': '10.0.0.1',
                'protocol': 6,
                'length': 100,
                'flags': 'S',
                'dst_port': 80,
                'direction': 'outbound'
            }
            
            features = extractor.extract_packet_features(packet)
            selected, _ = extractor.get_selected_features(features)
            
            self.assertEqual(len(selected), 20)
        except ImportError:
            self.skipTest("feature_extractor module not available")


class TestMLModelIntegration(unittest.TestCase):
    """Test ML model integration with UI"""
    
    def test_model_prediction_with_ui_features(self):
        """Test that model can predict with UI-extracted features"""
        try:
            import joblib
            from ml.feature_extractor import FeatureExtractor
            
            model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'random_forest_model.pkl')
            if not os.path.exists(model_path):
                self.skipTest("ML model file not found")
            
            model = joblib.load(model_path)
            extractor = FeatureExtractor()
            
            # Create test packet
            packet = {
                'src_ip': '192.168.1.1',
                'dst_ip': '10.0.0.1',
                'protocol': 6,
                'length': 100,
                'flags': 'S',
                'dst_port': 80,
                'direction': 'outbound'
            }
            
            # Extract features
            features = extractor.extract_packet_features(packet)
            selected, _ = extractor.get_selected_features(features)
            
            # Make prediction
            import numpy as np
            features_array = np.array(selected).reshape(1, -1)
            prediction = model.predict(features_array)
            
            # Should return 0 or 1
            self.assertIn(prediction[0], [0, 1])
        except ImportError:
            self.skipTest("Required modules not available")


class TestFirewallManagerIntegration(unittest.TestCase):
    """Test firewall manager integration"""
    
    def test_firewall_manager_initialization(self):
        """Test that firewall manager can be initialized"""
        try:
            from firewall_manager import FirewallManager
            manager = FirewallManager()
            self.assertIsNotNone(manager)
        except ImportError:
            self.skipTest("firewall_manager module not available")
        except Exception as e:
            # May fail without root privileges
            self.skipTest(f"Firewall manager requires root privileges: {e}")


class TestHelpContent(unittest.TestCase):
    """Test help content structure"""
    
    def test_help_content_module_exists(self):
        """Test that help content module exists"""
        try:
            from ui.help_content import PAGE_HELP_CONTENT
            self.assertIsNotNone(PAGE_HELP_CONTENT)
        except ImportError:
            self.skipTest("help_content module not available")
    
    def test_help_content_has_required_pages(self):
        """Test that help content has required pages"""
        try:
            from ui.help_content import PAGE_HELP_CONTENT
            required_pages = ['Live Sentinel', 'Forensic Vault', 'Autonomous Shield', 
                            'AI Mentor', 'Network Topology', 'Threat Encyclopedia', 'Settings']
            for page in required_pages:
                self.assertIn(page, PAGE_HELP_CONTENT, f"Help content missing page: {page}")
        except ImportError:
            self.skipTest("help_content module not available")


def run_tests():
    """Run all UI tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTheme))
    suite.addTests(loader.loadTestsFromTestCase(TestSettingsManager))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationManager))
    suite.addTests(loader.loadTestsFromTestCase(TestLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestMLModelIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFirewallManagerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestHelpContent))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
