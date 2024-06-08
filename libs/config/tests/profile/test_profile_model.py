from libs.config.src.model.profile_model import ProfileConfigModel


def test_profile_config_model():
    profile = ProfileConfigModel(sqlite_url="localhost:1433", exit=False)

    assert profile.sqlite_url == "localhost:1433"
    assert profile.exit is False
