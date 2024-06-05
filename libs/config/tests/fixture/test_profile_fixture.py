import pytest

from libs.config.src.model.profile_model import ProfileConfigModel


@pytest.fixture(scope="session")
def profile_debug_false() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="DEBUG", exit=False)


@pytest.fixture(scope="session")
def profile_debug_true() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="DEBUG", exit=True)


@pytest.fixture(scope="session")
def profile_info_false() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="INFO", exit=False)


@pytest.fixture(scope="session")
def profile_info_true() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="INFO", exit=True)


@pytest.fixture(scope="session")
def profile_warning_false() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="WARNING", exit=False)


@pytest.fixture(scope="session")
def profile_warning_true() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="WARNING", exit=True)


@pytest.fixture(scope="session")
def profile_error_false() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="ERROR", exit=False)


@pytest.fixture(scope="session")
def profile_error_true() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="ERROR", exit=True)


@pytest.fixture(scope="session")
def profile_critical_false() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="CRITICAL", exit=False)


@pytest.fixture(scope="session")
def profile_critical_true() -> ProfileConfigModel:
    return ProfileConfigModel(sqlite_url="localhost:1433", log_level="CRITICAL", exit=True)
