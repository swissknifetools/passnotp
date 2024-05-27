import pytest


@pytest.fixture(scope='session')
def single_profile_default():
    return {
        "default": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        }
    }
    
@pytest.fixture(scope='session')
def single_profile_no_default():
    return {
        "prof": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        }
    }
    
@pytest.fixture(scope='session')
def multiple_profile_with_default():
    return {
        "default": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        },
        "prof": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        },
        "prof1": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        }
    }
    
@pytest.fixture(scope='session')
def multiple_profile_no_default():
    return {
        "prof3": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        },
        "prof": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        },
        "prof1": {
            "db_url": "",
            "log_level": "DEBUG",
            "exit": False
        }
    }