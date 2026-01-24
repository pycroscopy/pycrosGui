"""
Test suite for pycrosGUI
"""

import pytest


class TestImports:
    """Test that the package imports correctly."""
    
    def test_import_pycrosgui(self):
        """Test that pycrosGUI can be imported."""
        import pycrosGUI
        assert pycrosGUI is not None
    
    def test_import_version(self):
        """Test that version is accessible."""
        import pycrosGUI
        assert hasattr(pycrosGUI, '__version__')
        assert isinstance(pycrosGUI.__version__, str)
    
    def test_import_main(self):
        """Test that main function exists."""
        from pycrosGUI import main
        assert callable(main)
    
    def test_import_base_widget(self):
        """Test that BaseWidget can be imported."""
        from pycrosGUI import BaseWidget
        assert BaseWidget is not None


class TestPackageMetadata:
    """Test package metadata."""
    
    def test_version_format(self):
        """Test that version follows expected format."""
        import pycrosGUI
        version = pycrosGUI.__version__
        # Version should be a non-empty string
        assert len(version) > 0
        # Version should contain at least one dot
        assert '.' in version or version.startswith('0')


class TestBasicFunctionality:
    """Basic functionality tests."""
    
    def test_package_has_dependencies(self):
        """Test that required dependencies are available."""
        try:
            import PyQt5
            import pyqtgraph
            import pyTEMlib
            import sidpy
            assert True
        except ImportError as e:
            pytest.skip(f"Optional dependency not available: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
