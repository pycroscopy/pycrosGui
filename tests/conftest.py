"""
Configuration and fixtures for pytest
"""

import pytest


@pytest.fixture
def sample_data():
    """Fixture providing sample data for tests."""
    return {
        'test': 'data'
    }


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
