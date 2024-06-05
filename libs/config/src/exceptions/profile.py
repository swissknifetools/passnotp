class ProfileNotFound(Exception):
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Profile {profile_name} not found")


class ProfileAlreadyExists(Exception):
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        super().__init__(f"Profile {profile_name} already exists")
