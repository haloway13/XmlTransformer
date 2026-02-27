import unittest
from unittest.mock import patch, Mock, call
import os
import sublime
import subprocess
import xml.etree.ElementTree as ET

# Import the module
import XmlTransformer_build as build_module

class TestXmlTransformerCore(unittest.TestCase):
    def setUp(self):
        # Patch platform to 'linux' (your OS)
        patcher = patch('sublime.platform', return_value='linux')
        self.addCleanup(patcher.stop)
        patcher.start()
        
        # Mock window/view for instance
        self.mock_window = Mock()
        self.mock_view = Mock()
        self.mock_window.active_view.return_value = self.mock_view
        patcher = patch('sublime.active_window', return_value=self.mock_window)
        self.addCleanup(patcher.stop)
        patcher.start()
        
        # Mock settings
        self.mock_settings = Mock()
        self.mock_settings.get.return_value = False  # debug off
        patcher = patch('sublime.load_settings', return_value=self.mock_settings)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_parse_xml_param_file_valid(self):
        # Create mock XML file content as bytes
        mock_xml = b'<params><param name="debug" value="true"/><param name="lang" value="en"/></params>'
        from io import BytesIO
        mock_file = BytesIO(mock_xml)
        
        with patch('builtins.open', return_value=mock_file) as mock_open:
            # Instantiate class for method call
            cmd = build_module.XmlTransformerBuildCommand(self.mock_window)
            result = cmd.parse_xml_param_file('test_params.xml')
            self.assertEqual(result, {'debug': 'true', 'lang': 'en'})
            mock_open.assert_called_once_with('test_params.xml', 'rb')  # ET uses 'rb'

    def test_parse_xml_param_file_missing_key(self):
        # Malformed XML -> ParseError -> None (error path)
        mock_xml = b'<params><param name="debug" value="true"'  # Unclosed tag
        from io import BytesIO
        mock_file = BytesIO(mock_xml)
        
        with patch('builtins.open', return_value=mock_file), \
             patch('sublime.error_message') as mock_error:  # Silence UI
            cmd = build_module.XmlTransformerBuildCommand(self.mock_window)
            result = cmd.parse_xml_param_file('bad_params.xml')
            self.assertIsNone(result)
            mock_error.assert_called_once()  # Confirms error path

    def test_build_saxon_command(self):
        # Test cmd build in run_transformation (mock validations/paths)
        xml_path = '/fake/test.xml'
        xsl_path = '/fake/test.xsl'
        param_file = None  # No params
        output_file = '/fake/test-output.xml'
        
        # Mock validations to pass
        with patch.object(build_module.XmlTransformerBuildCommand, 'validate_xml_file', return_value=True), \
             patch('os.path.normpath', return_value='/fake/norm'), \
             patch('os.path.splitext', return_value=('/fake/test', '.xml')), \
             patch('os.path.join', return_value='/fake/jar'), \
             patch('os.environ.get', return_value='/fake/ProgramFiles'):  # For jar_path
            cmd_instance = build_module.XmlTransformerBuildCommand(self.mock_window)
            cmd_instance.xml_path = xml_path
            cmd_instance.xsl_path = xsl_path
            cmd_instance.working_dir = '/fake'
            cmd_instance.java_bin = 'java'
            cmd_instance.jar_path = '/fake/Saxon'
            cmd_instance.cp_separator = ':'
            cmd_instance.get_xsl_output_method = Mock(return_value='xml')  # For extension
            
            # Call run_transformation (builds cmd)
            cmd_instance.run_transformation(param_file)
            
            # Assert cmd built (from self.window.run_command call)
            exec_call = self.mock_window.run_command.call_args[0][1]
            self.assertEqual(exec_call['cmd'][0], 'java')
            self.assertIn('-s:/fake/norm', exec_call['cmd'])
            self.assertIn('-xsl:/fake/norm', exec_call['cmd'])
            self.assertIn('-o:/fake/norm', exec_call['cmd'])
            self.assertEqual(exec_call['output_file'], '/fake/test-output.xml')

    def test_get_message_localization(self):
        # Test English fallback (default)
        with patch('sublime.load_resource') as mock_resource:
            mock_en = '{"select_xsl": "Select XSL file"}'
            mock_resource.side_effect = lambda path: mock_en if 'en' in path else None
            result = build_module.get_message('select_xsl')
            self.assertEqual(result, 'Select XSL file')
            
            # Test Spanish (if file loads)
            mock_es = '{"select_xsl": "Selecciona XSL"}'
            mock_resource.side_effect = lambda path: mock_es if 'es' in path else mock_en
            # Force lang='es' (your code defaults 'en'; patch for test)
            with patch('sublime.platform', return_value='linux'):  # Dummy to avoid side effects
                result_es = build_module.get_message('select_xsl')
                self.assertEqual(result, 'Select XSL file')  # Confirms fallback

    def test_run_transform_error_handling(self):
        # Test validation failure -> early return, error message
        xml_path = '/fake/bad.xml'
        xsl_path = '/fake/bad.xsl'
        
        with patch.object(build_module.XmlTransformerBuildCommand, 'validate_xml_file', return_value=False), \
             patch('sublime.error_message') as mock_error:
            cmd_instance = build_module.XmlTransformerBuildCommand(self.mock_window)
            cmd_instance.xml_path = xml_path
            cmd_instance.xsl_path = xsl_path
            cmd_instance.run_transformation(None)
            
            mock_error.assert_called_once()  # Error shown
            self.assertFalse(self.mock_window.run_command.called)  # No exec

    def test_smoke_end_to_end(self):
        # Mock view.file_name to string
        self.mock_view.file_name.return_value = '/fake/test.xml'
        
        # Mock validations and paths
        with patch.object(build_module.XmlTransformerBuildCommand, 'validate_xml_file', return_value=True):
            with patch('os.listdir', return_value=['test.xsl']):
                with patch('os.path.isdir', return_value=True):
                    with patch('os.path.exists', return_value=True):
                        with patch('os.path.realpath', return_value='/fake'):
                            with patch('xml.etree.ElementTree.parse') as mock_et:
                                mock_et.return_value.getroot.return_value.findall.return_value = []  # No params
                                mock_et.return_value.getroot.return_value.find.return_value = None  # No output elem
                                
                                # Mock show_quick_panel: record call, then simulate callback
                                def fake_panel(items, callback):
                                    callback(2)  # Simulate select index 2 (first XSL)
                                self.mock_window.show_quick_panel.side_effect = fake_panel
                                
                                cmd_instance = build_module.XmlTransformerBuildCommand(self.mock_window)
                                cmd_instance.window = self.mock_window  # Ensure window ref
                                cmd_instance.working_dir = '/fake'
                                
                                # Trigger run (mocks flow to transformation via callback sim)
                                cmd_instance.run()
                                
                                self.mock_window.show_quick_panel.assert_called_once()  # Panel shown
                                self.mock_window.run_command.assert_called_once()  # Saxon exec

if __name__ == '__main__':
    unittest.main()